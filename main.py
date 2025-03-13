#!/usr/bin/env python3
"""
CMYK Retro Lo-Fi Solana Vanity Address Generator
Main application entry point
"""

import os
import sys
import logging
import pygame
import time

# Configure logging
def setup_logging():
    """Configure application logging"""
    log_format = "[%(levelname)s %(asctime)s] %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("vanity_generator.log")
        ]
    )

def check_dependencies():
    """
    Check if all required dependencies are installed
    
    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    try:
        import pygame
        import pyopencl
        import numpy
        import base58
        import nacl.signing
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install all required dependencies using:")
        print("pip install -r requirements.txt")
        return False

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logging.info("Starting CMYK Retro Lo-Fi Solana Vanity Address Generator")
    
    # Display ASCII art banner
    try:
        from utils.ascii_art import display_ascii_art
        display_ascii_art()
    except ImportError:
        pass
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return 1
    
    # Initialize pygame
    try:
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("CMYK Solana Vanity Generator")
        
        # Set up clipboard for copy/paste in input fields
        if hasattr(pygame, 'scrap'):
            pygame.scrap.init()
        
        # Import and create main window
        from ui.main_window import MainWindow
        main_window = MainWindow(width=800, height=600)
        
        # Run the application
        exit_code = main_window.run()
        
        # Clean up
        pygame.quit()
        
        return exit_code
    except Exception as e:
        logging.exception("Unhandled exception in main loop")
        print(f"An error occurred: {e}")
        print(f"Check vanity_generator.log for details")
        return 1
    finally:
        logging.info("Application exiting")

if __name__ == "__main__":
    # Handle frozen executable (PyInstaller)
    if getattr(sys, 'frozen', False):
        # Get the path to the directory containing the executable
        os.chdir(os.path.dirname(sys.executable))
    
    # Run the application
    sys.exit(main())