# CMYK Retro Lo-Fi Solana Vanity Address Generator

A stylish, retro-themed Solana vanity address generator with a CMYK color scheme and lo-fi aesthetics. Generate custom Solana wallet addresses that start or end with specific characters.

![Screenshot](screenshot.png)

## Features

- **GPU-Accelerated Generation**: Utilizes OpenCL for fast vanity address generation
- **Retro UI**: Nostalgic CMYK color scheme with pixel art and retro effects
- **Customizable**: Generate addresses with specific prefixes or suffixes
- **Multi-Device Support**: Works with multiple GPU devices for parallel processing
- **Export Options**: Save and export your generated addresses
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.7+
- OpenCL-compatible GPU
- OpenCL drivers installed for your GPU

## Installation

### From PyPI

```bash
pip install cmyk-solana-vanity
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/cmyk-solana-vanity.git
cd cmyk-solana-vanity

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### OpenCL Setup

Make sure you have the appropriate OpenCL drivers installed for your GPU:

- **NVIDIA**: Install the latest NVIDIA drivers which include OpenCL support
- **AMD**: Install the AMD APP SDK or the latest AMD drivers
- **Intel**: Install the Intel OpenCL Runtime

## Usage

### Graphical Interface

Simply run the application:

```bash
cmyk-vanity
```

Or if installed from source:

```bash
python -m main
```

### Command Line (Advanced Users)

For direct command-line usage:

```bash
python -m core.vangen
```

## Generating Vanity Addresses

1. Start the application
2. Enter your desired prefix and/or suffix
3. Select the number of addresses to generate
4. Choose your output directory 
5. Adjust iteration bits (higher = faster but more GPU memory)
6. Click "Start Generation"
7. Wait for the generation process to complete
8. View and export your generated addresses

## Understanding Settings

- **Prefix/Suffix**: Characters that your address should start/end with
- **Iteration Bits**: Controls the balance between speed and memory usage
  - Higher values (24-28) are faster but use more GPU memory
  - Lower values (16-20) use less memory but are slower
- **Device Selection**: Manually select which GPU to use (useful for multi-GPU systems)

## Building Executable

You can create standalone executables using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --add-data "assets:assets" --add-data "core/kernel.cl:core" main.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the Solana community
- Built with PyGame and PyOpenCL
- Inspired by retro computing and CMYK printing aesthetics

## Security Notes

- Always backup your private keys 
- Use caution when handling wallet files
- This tool generates valid Solana keypairs, handle them with appropriate security