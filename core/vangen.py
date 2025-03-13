import json
import logging
import os
import platform
import secrets
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from math import ceil
from multiprocessing import Pool, set_start_method
from pathlib import Path

import pyopencl as cl
import numpy as np
from base58 import b58decode, b58encode
from nacl.signing import SigningKey

# Configure logging
logging.basicConfig(level="INFO", format="[%(levelname)s %(asctime)s] %(message)s")

# OpenCL environment setup
os.environ["PYOPENCL_COMPILER_OUTPUT"] = "1"
os.environ["PYOPENCL_NO_CACHE"] = "TRUE"

# Core class for generation settings
class HostSetting:
    def __init__(self, kernel_source: str, iteration_bits: int) -> None:
        self.iteration_bits = iteration_bits
        self.iteration_bytes = np.ubyte(ceil(iteration_bits / 8))
        self.global_work_size = 1 << iteration_bits
        self.local_work_size = 32
        self.key32 = self.generate_key32()
        self.kernel_source = kernel_source

    def generate_key32(self):
        token_bytes = (
            secrets.token_bytes(32 - self.iteration_bytes)
            + b"\x00" * self.iteration_bytes
        )
        key32 = np.array([x for x in token_bytes], dtype=np.ubyte)
        return key32

    def increase_key32(self):
        current_number = int.from_bytes(self.key32, "big")
        next_number = current_number + (1 << self.iteration_bits)
        new_key32 = np.frombuffer(next_number.to_bytes(32, "big"), dtype=np.ubyte)
    
        # Check if we need to reset the iteration bits
        if new_key32[-self.iteration_bytes:].any():
            new_key32[-self.iteration_bytes:] = 0

        self.key32[:] = new_key32


def check_character(name: str, character: str):
    """Validate if provided characters are valid Base58 encoding"""
    try:
        b58decode(character)
    except ValueError as e:
        logging.error(f"{str(e)} in {name}")
        sys.exit(1)
    except Exception as e:
        raise e


def get_kernel_source(starts_with: str, ends_with: str, cl):
    """Prepare OpenCL kernel with the specified prefix and suffix"""
    PREFIX_BYTES = list(bytes(starts_with.encode()))
    SUFFIX_BYTES = list(bytes(ends_with.encode()))

    # Get the kernel path based on whether we're running as executable or script
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        kernel_path = os.path.join(sys._MEIPASS, "kernel.cl")
    else:
        # Running as script
        kernel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kernel.cl")

    with open(kernel_path, "r") as f:
        source_lines = f.readlines()

    for i, s in enumerate(source_lines):
        if s.startswith("constant uchar PREFIX[]"):
            source_lines[i] = (
                f"constant uchar PREFIX[] = {{{', '.join(map(str, PREFIX_BYTES))}}};\n"
            )
        if s.startswith("constant uchar SUFFIX[]"):
            source_lines[i] = (
                f"constant uchar SUFFIX[] = {{{', '.join(map(str, SUFFIX_BYTES))}}};\n"
            )

    source_str = "".join(source_lines)

    # NVIDIA Windows-specific adjustments
    if "NVIDIA" in str(cl.get_platforms()) and platform.system() == "Windows":
        source_str = source_str.replace("#define __generic\n", "")

    # Newer OpenCL version adjustments
    if cl.get_cl_header_version()[0] != 1 and platform.system() != "Windows":
        source_str = source_str.replace("#define __generic\n", "")

    return source_str


def get_all_gpu_devices():
    """Get all available GPU devices for OpenCL"""
    devices = [
        device
        for platform in cl.get_platforms()
        for device in platform.get_devices(device_type=cl.device_type.GPU)
    ]
    return [d.int_ptr for d in devices]


def single_gpu_init(context, setting):
    """Initialize a single GPU for key search"""
    searcher = Searcher(
        kernel_source=setting.kernel_source,
        index=0,
        setting=setting,
        context=context,
    )
    return [searcher.find()]


def multi_gpu_init(index: int, setting: HostSetting):
    """Initialize multiple GPUs for parallel key search"""
    try:
        searcher = Searcher(
            kernel_source=setting.kernel_source,
            index=index,
            setting=setting,
        )
        return searcher.find()
    except Exception as e:
        logging.exception(e)
    return [0]


def save_result(outputs, output_dir):
    """Save found public/private key pairs to the output directory"""
    result_count = 0
    for output in outputs:
        if not output[0]:  # Skip if no valid result was found
            continue
        result_count += 1
        pv_bytes = bytes(output[1:])
        pv = SigningKey(pv_bytes)
        pb_bytes = bytes(pv.verify_key)
        pubkey = b58encode(pb_bytes).decode()

        logging.info(f"Found: {pubkey}")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(output_dir, f"{pubkey}.json").write_text(
            json.dumps(list(pv_bytes + pb_bytes))
        )
    return result_count


class Searcher:
    """Main class responsible for searching vanity addresses on GPU"""
    def __init__(
        self, *, kernel_source, index: int, setting: HostSetting, context=None
    ):
        device_ids = get_all_gpu_devices()
        # Context and command queue setup
        if context:
            self.context = context
            self.gpu_chunks = 1
        else:
            self.context = cl.Context(
                [cl.Device.from_int_ptr(device_ids[index])],
            )
            self.gpu_chunks = len(device_ids)
        self.command_queue = cl.CommandQueue(self.context)

        self.setting = setting
        self.index = index

        # Build program and kernel
        program = cl.Program(self.context, kernel_source).build()
        self.program = program
        self.kernel = cl.Kernel(program, "generate_pubkey")

    def filter_valid_result(self, outputs):
        """Filter valid results from the search"""
        valid_outputs = []
        for output in outputs:
            if not output[0]:
                continue
            valid_outputs.append(output)
        return valid_outputs

    def find(self):
        """Execute the GPU kernel to find matching vanity addresses"""
        # Create OpenCL memory buffers
        memobj_key32 = cl.Buffer(
            self.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            32 * np.ubyte().itemsize,
            hostbuf=self.setting.key32,
        )
        memobj_output = cl.Buffer(
            self.context, cl.mem_flags.READ_WRITE, 33 * np.ubyte().itemsize
        )

        memobj_occupied_bytes = cl.Buffer(
            self.context,
            cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=np.array([self.setting.iteration_bytes]),
        )
        memobj_group_offset = cl.Buffer(
            self.context,
            cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=np.array([self.index]),
        )
        output = np.zeros(33, dtype=np.ubyte)
        
        # Set kernel arguments
        self.kernel.set_arg(0, memobj_key32)
        self.kernel.set_arg(1, memobj_output)
        self.kernel.set_arg(2, memobj_occupied_bytes)
        self.kernel.set_arg(3, memobj_group_offset)

        # Execute kernel and measure performance
        st = time.time()
        global_worker_size = self.setting.global_work_size // self.gpu_chunks
        cl.enqueue_nd_range_kernel(
            self.command_queue,
            self.kernel,
            (global_worker_size,),
            (self.setting.local_work_size,),
        )
        cl._enqueue_read_buffer(self.command_queue, memobj_output, output).wait()
        
        # Log performance stats
        hash_rate = global_worker_size / ((time.time() - st) * 10**6)
        logging.info(f"GPU {self.index} Speed: {hash_rate:.2f} MH/s")

        return output


# Function accessible by UI for vanity address search
def search_vanity_addresses(
    starts_with="", 
    ends_with="", 
    count=1, 
    output_dir="./", 
    select_device=False, 
    iteration_bits=24,
    callback=None
):
    """
    Primary function for searching vanity addresses
    
    Args:
        starts_with: Prefix for the address
        ends_with: Suffix for the address
        count: Number of addresses to generate
        output_dir: Directory to save the generated keys
        select_device: Whether to manually select OpenCL device
        iteration_bits: Number of iteration bits for generation
        callback: Optional callback function for progress updates
    
    Returns:
        Dictionary with success status and results/error message
    """
    try:
        # Validate input
        if not starts_with and not ends_with:
            return {"success": False, "error": "Please provide at least a prefix or suffix"}

        check_character("starts_with", starts_with)
        check_character("ends_with", ends_with)

        logging.info(
            f"Searching Solana pubkey that starts with '{starts_with}' and ends with '{ends_with}'"
        )
        
        # Get GPU count
        with Pool() as pool:
            gpu_counts = len(pool.apply(get_all_gpu_devices))
        
        if gpu_counts == 0:
            return {"success": False, "error": "No compatible GPU devices found"}

        # Prepare kernel and settings
        kernel_source = get_kernel_source(starts_with, ends_with, cl)
        setting = HostSetting(kernel_source, iteration_bits)
        result_count = 0
        found_keys = []

        logging.info(f"Searching with {gpu_counts} OpenCL devices")
        
        # Handle single device selection
        if select_device:
            with ThreadPoolExecutor(max_workers=1) as executor:
                context = cl.create_some_context()
                while result_count < count:
                    if callback:
                        callback({"status": "searching", "progress": result_count / count})
                    
                    future = executor.submit(single_gpu_init, context, setting)
                    result = future.result()
                    
                    # Process and save results
                    for output in result:
                        if not output[0]:
                            continue
                        
                        # Convert and save key
                        pv_bytes = bytes(output[1:])
                        pv = SigningKey(pv_bytes)
                        pb_bytes = bytes(pv.verify_key)
                        pubkey = b58encode(pb_bytes).decode()
                        
                        logging.info(f"Found: {pubkey}")
                        Path(output_dir).mkdir(parents=True, exist_ok=True)
                        key_path = Path(output_dir, f"{pubkey}.json")
                        key_path.write_text(json.dumps(list(pv_bytes + pb_bytes)))
                        
                        found_keys.append({
                            "pubkey": pubkey,
                            "path": str(key_path)
                        })
                        
                        result_count += 1
                        if result_count >= count:
                            break
                    
                    setting.increase_key32()
                    time.sleep(0.1)
        else:
            # Parallel GPU processing
            with Pool(processes=gpu_counts) as pool:
                while result_count < count:
                    if callback:
                        callback({"status": "searching", "progress": result_count / count})
                    
                    results = pool.starmap(
                        multi_gpu_init, [(x, setting) for x in range(gpu_counts)]
                    )
                    
                    # Process and save results
                    for output in results:
                        if not output[0]:
                            continue
                        
                        # Convert and save key
                        pv_bytes = bytes(output[1:])
                        pv = SigningKey(pv_bytes)
                        pb_bytes = bytes(pv.verify_key)
                        pubkey = b58encode(pb_bytes).decode()
                        
                        logging.info(f"Found: {pubkey}")
                        Path(output_dir).mkdir(parents=True, exist_ok=True)
                        key_path = Path(output_dir, f"{pubkey}.json")
                        key_path.write_text(json.dumps(list(pv_bytes + pb_bytes)))
                        
                        found_keys.append({
                            "pubkey": pubkey,
                            "path": str(key_path)
                        })
                        
                        result_count += 1
                        if result_count >= count:
                            break
                    
                    setting.increase_key32()
                    time.sleep(0.1)
        
        if callback:
            callback({"status": "complete", "progress": 1.0})
            
        return {
            "success": True, 
            "results": found_keys,
            "count": result_count
        }
            
    except Exception as e:
        error_msg = f"Error in search_vanity_addresses: {str(e)}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        if callback:
            callback({"status": "error", "error": error_msg})
        return {"success": False, "error": error_msg}


def get_available_devices():
    """Get information about available OpenCL devices"""
    try:
        platforms = cl.get_platforms()
        devices_info = []
        
        for p_index, platform in enumerate(platforms):
            platform_info = {
                "platform_index": p_index,
                "platform_name": platform.name,
                "devices": []
            }
            
            devices = platform.get_devices()
            for d_index, device in enumerate(devices):
                device_info = {
                    "device_index": d_index,
                    "device_name": device.name,
                    "device_type": cl.device_type.to_string(device.type),
                    "compute_units": device.max_compute_units,
                    "global_mem_size": device.global_mem_size,
                }
                platform_info["devices"].append(device_info)
            
            devices_info.append(platform_info)
        
        return {"success": True, "devices": devices_info}
    except Exception as e:
        error_msg = f"Error getting OpenCL devices: {str(e)}"
        logging.error(error_msg)
        return {"success": False, "error": error_msg}


# CLI entry point (for testing)
def cli_entry_point():
    """Command-line interface for the vanity address generator"""
    if getattr(sys, 'frozen', False):
        set_start_method('spawn')
    
    try:
        from utils.ascii_art import display_ascii_art
        display_ascii_art()
        
        starts_with = input("Enter prefix (starts with, default ''): ") or ""
        ends_with = input("Enter suffix (ends with, default ''): ") or ""
        count = input("Enter count of pubkeys to generate (default 1): ")
        count = int(count) if count else 1
        output_dir = input("Enter output directory (default ./): ") or "./"
        select_device = input("Select OpenCL device manually? (y/n, default n): ").lower() == 'y'
        iteration_bits = input("Enter number of iteration bits (default 24): ")
        iteration_bits = int(iteration_bits) if iteration_bits else 24
        
        result = search_vanity_addresses(
            starts_with=starts_with,
            ends_with=ends_with,
            count=count,
            output_dir=output_dir,
            select_device=select_device,
            iteration_bits=iteration_bits
        )
        
        if result["success"]:
            print(f"Successfully generated {len(result['results'])} keys:")
            for key in result["results"]:
                print(f"  - {key['pubkey']} (saved to {key['path']})")
        else:
            print(f"Error: {result['error']}")
            
    except KeyboardInterrupt:
        print("\nOperation canceled by user")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        input("Press Enter to continue...")


if __name__ == "__main__":
    cli_entry_point()