"""
Key utilities for the CMYK Retro Lo-Fi Solana Vanity Generator
Provides functions for working with Solana keypairs
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path

import base58
from nacl.signing import SigningKey, VerifyKey

def generate_keypair() -> Tuple[bytes, bytes]:
    """
    Generate a new Solana keypair
    
    Returns:
        Tuple[bytes, bytes]: (private_key, public_key)
    """
    signing_key = SigningKey.generate()
    private_key = bytes(signing_key)
    public_key = bytes(signing_key.verify_key)
    
    return private_key, public_key

def derive_public_key(private_key: bytes) -> bytes:
    """
    Derive a public key from a private key
    
    Args:
        private_key: Ed25519 private key bytes
        
    Returns:
        bytes: Ed25519 public key bytes
    """
    if len(private_key) != 32:
        raise ValueError(f"Invalid private key length: {len(private_key)}, expected 32")
    
    signing_key = SigningKey(private_key)
    return bytes(signing_key.verify_key)

def public_key_to_base58(public_key: bytes) -> str:
    """
    Convert a public key from bytes to Base58 string
    
    Args:
        public_key: Ed25519 public key bytes
        
    Returns:
        str: Base58-encoded public key (Solana address)
    """
    return base58.b58encode(public_key).decode('utf-8')

def private_key_to_base58(private_key: bytes) -> str:
    """
    Convert a private key from bytes to Base58 string
    
    Args:
        private_key: Ed25519 private key bytes
        
    Returns:
        str: Base58-encoded private key
    """
    return base58.b58encode(private_key).decode('utf-8')

def base58_to_private_key(base58_key: str) -> bytes:
    """
    Convert a Base58 private key to bytes
    
    Args:
        base58_key: Base58-encoded private key
        
    Returns:
        bytes: Ed25519 private key bytes
        
    Raises:
        ValueError: If the key is invalid
    """
    try:
        private_key = base58.b58decode(base58_key)
        if len(private_key) != 32:
            raise ValueError(f"Invalid private key length: {len(private_key)}, expected 32")
        return private_key
    except Exception as e:
        raise ValueError(f"Invalid Base58 key: {str(e)}")

def base58_to_public_key(base58_address: str) -> bytes:
    """
    Convert a Base58 Solana address to public key bytes
    
    Args:
        base58_address: Base58-encoded Solana address
        
    Returns:
        bytes: Ed25519 public key bytes
        
    Raises:
        ValueError: If the address is invalid
    """
    try:
        public_key = base58.b58decode(base58_address)
        if len(public_key) != 32:
            raise ValueError(f"Invalid public key length: {len(public_key)}, expected 32")
        return public_key
    except Exception as e:
        raise ValueError(f"Invalid Base58 address: {str(e)}")

def is_valid_solana_address(address: str) -> bool:
    """
    Validate a Solana address
    
    Args:
        address: Base58-encoded Solana address
        
    Returns:
        bool: True if the address is valid
    """
    try:
        public_key = base58.b58decode(address)
        return len(public_key) == 32
    except:
        return False

def save_keypair_to_file(private_key: bytes, output_path: str, format: str = "json") -> str:
    """
    Save a keypair to a file
    
    Args:
        private_key: Ed25519 private key bytes
        output_path: Path to save the file
        format: Output format ('json', 'base58')
        
    Returns:
        str: Path to the saved file
        
    Raises:
        ValueError: If the key or format is invalid
    """
    if len(private_key) != 32:
        raise ValueError(f"Invalid private key length: {len(private_key)}, expected 32")
    
    # Derive public key
    public_key = derive_public_key(private_key)
    public_key_b58 = public_key_to_base58(public_key)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    if format == "json":
        # Save in Solana CLI JSON format (combined key)
        combined_bytes = private_key + public_key
        json_data = list(combined_bytes)
        
        with open(output_path, 'w') as f:
            json.dump(json_data, f)
            
    elif format == "base58":
        # Save as Base58-encoded private key
        private_key_b58 = private_key_to_base58(private_key)
        
        with open(output_path, 'w') as f:
            f.write(private_key_b58)
            
    else:
        raise ValueError(f"Unsupported key format: {format}")
    
    return output_path

def load_keypair_from_file(file_path: str) -> Tuple[bytes, bytes]:
    """
    Load a keypair from a file
    
    Args:
        file_path: Path to the keypair file
        
    Returns:
        Tuple[bytes, bytes]: (private_key, public_key)
        
    Raises:
        ValueError: If the file is invalid
    """
    try:
        with open(file_path, 'r') as f:
            # Try to parse as JSON first
            try:
                data = json.load(f)
                
                if isinstance(data, list):
                    # Standard Solana CLI format (list of integers)
                    if len(data) >= 64:
                        private_key = bytes(data[:32])
                        public_key = bytes(data[32:64])
                        return private_key, public_key
                    else:
                        raise ValueError("Invalid JSON keypair: too short")
                    
                elif isinstance(data, dict) and "privateKey" in data and "publicKey" in data:
                    # Alternative format with explicit key fields
                    private_key = bytes(data["privateKey"])
                    public_key = bytes(data["publicKey"])
                    return private_key, public_key
                    
                else:
                    raise ValueError("Unrecognized JSON keypair format")
                    
            except json.JSONDecodeError:
                # Not JSON, try Base58 format
                f.seek(0)
                content = f.read().strip()
                
                try:
                    private_key = base58.b58decode(content)
                    if len(private_key) != 32:
                        raise ValueError(f"Invalid private key length: {len(private_key)}, expected 32")
                    
                    # Derive public key
                    public_key = derive_public_key(private_key)
                    return private_key, public_key
                    
                except Exception as e:
                    raise ValueError(f"Invalid Base58 key: {str(e)}")
                
    except Exception as e:
        raise ValueError(f"Failed to load keypair: {str(e)}")

def check_key_matches_pattern(public_key: bytes, prefix: str = "", suffix: str = "") -> bool:
    """
    Check if a public key matches the given pattern
    
    Args:
        public_key: Ed25519 public key bytes
        prefix: Expected prefix (case-sensitive)
        suffix: Expected suffix (case-sensitive)
        
    Returns:
        bool: True if the key matches the pattern
    """
    # Convert to Base58
    address = public_key_to_base58(public_key)
    
    # Check prefix and suffix
    matches = True
    if prefix and not address.startswith(prefix):
        matches = False
    if suffix and not address.endswith(suffix):
        matches = False
        
    return matches

def keypair_to_json(private_key: bytes, public_key: bytes) -> Dict[str, Any]:
    """
    Convert a keypair to a JSON-serializable dictionary
    
    Args:
        private_key: Ed25519 private key bytes
        public_key: Ed25519 public key bytes
        
    Returns:
        Dict[str, Any]: JSON-serializable dictionary
    """
    return {
        "privateKey": list(private_key),
        "publicKey": list(public_key),
        "privateKeyBase58": private_key_to_base58(private_key),
        "publicKeyBase58": public_key_to_base58(public_key)
    }

def keypair_to_wallet_connect_format(private_key: bytes) -> Dict[str, Any]:
    """
    Convert a keypair to WalletConnect format
    
    Args:
        private_key: Ed25519 private key bytes
        
    Returns:
        Dict[str, Any]: WalletConnect-compatible dictionary
    """
    public_key = derive_public_key(private_key)
    return {
        "privateKey": private_key.hex(),
        "publicKey": public_key.hex(),
        "address": public_key_to_base58(public_key)
    }

def matches_vanity_pattern(address: str, prefix: str = "", suffix: str = "") -> bool:
    """
    Check if an address matches the given vanity pattern
    
    Args:
        address: Base58-encoded Solana address
        prefix: Expected prefix (case-sensitive)
        suffix: Expected suffix (case-sensitive)
        
    Returns:
        bool: True if the address matches the pattern
    """
    if not address:
        return False
        
    matches = True
    if prefix and not address.startswith(prefix):
        matches = False
    if suffix and not address.endswith(suffix):
        matches = False
        
    return matches

def is_valid_vanity_pattern(pattern: str) -> bool:
    """
    Check if a vanity pattern is valid
    
    Args:
        pattern: Vanity pattern to check
        
    Returns:
        bool: True if the pattern is valid
    """
    try:
        # Check if pattern contains only Base58 characters
        base58_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
        for char in pattern:
            if char not in base58_chars:
                return False
        return True
    except:
        return False

def estimate_search_difficulty(pattern: str, is_prefix: bool = True) -> float:
    """
    Estimate the difficulty of finding a vanity address with the given pattern
    
    Args:
        pattern: Vanity pattern to search for
        is_prefix: Whether the pattern is a prefix (True) or suffix (False)
        
    Returns:
        float: Estimated number of attempts needed
    """
    if not pattern:
        return 1.0
        
    # Base58 has 58 possible characters
    attempts = 58 ** len(pattern)
    
    # Adjust for case-sensitivity and specific characters
    # This is a rough approximation
    for char in pattern:
        if char.isdigit():
            # Digits are less common in Base58
            attempts *= 1.2
        elif char.isupper():
            # Uppercase letters are less common
            attempts *= 1.1
    
    return attempts

def get_key_details(private_key: bytes, public_key: Optional[bytes] = None) -> Dict[str, Any]:
    """
    Get detailed information about a keypair
    
    Args:
        private_key: Ed25519 private key bytes
        public_key: Ed25519 public key bytes (optional, will be derived if not provided)
        
    Returns:
        Dict[str, Any]: Detailed key information
    """
    if public_key is None:
        public_key = derive_public_key(private_key)
        
    address = public_key_to_base58(public_key)
    
    return {
        "address": address,
        "publicKey": public_key.hex(),
        "privateKey": private_key.hex(),
        "privateKeyBase58": private_key_to_base58(private_key),
        "keyLength": len(private_key),
        "addressLength": len(address),
        "firstChar": address[0] if address else "",
        "lastChar": address[-1] if address else ""
    }