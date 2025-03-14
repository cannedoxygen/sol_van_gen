"""
Main Window controller for the CMYK Retro Solana Vanity Generator
Manages screen transitions and overall application flow
"""

import os
import sys
import logging
import pygame
from typing import Dict, Any, Optional

from utils.config_manager import ConfigManager
from ui.screens.landing_screen import LandingScreen
from ui.screens.welcome_screen import WelcomeScreen
from ui.screens.generation_screen import GenerationScreen
from ui.screens.results_screen import ResultsScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.info_screen import InfoScreen

class MainWindow:
    """
    Main window controller that manages all screens and application state
    """
    
    # Screen identifiers
    SCREEN_LANDING = "landing"
    SCREEN_WELCOME = "welcome"
    SCREEN_GENERATION = "generation"
    SCREEN_RESULTS = "results"
    SCREEN_SETTINGS = "settings"
    SCREEN_INFO = "info"
    SCREEN_DEVICES = "devices"
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize the main window
        
        Args:
            width: Window width
            height: Window height
        """
        self.width = width
        self.height = height
        self.running = False
        self.current_screen = None
        self.screens = {}
        self.config = ConfigManager()
        
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
            
        # Set up the main pygame display
        if hasattr(pygame, 'SCALED'):
            # For high DPI displays (pygame 2.0+)
            self.screen = pygame.display.set_mode(
                (width, height),
                pygame.RESIZABLE | pygame.SCALED
            )
        else:
            # Fallback for pygame 1.9
            self.screen = pygame.display.set_mode(
                (width, height),
                pygame.RESIZABLE
            )
        
        # Set window title
        pygame.display.set_caption("CMYK Retro Solana Vanity Generator")
        
        # Set window icon
        self.set_window_icon()
        
        # Initialize screens
        self.initialize_screens()
        
        # Start with landing screen
        self.switch_screen(self.SCREEN_LANDING)
    
    def set_window_icon(self):
        """Set the application window icon"""
        try:
            # Get the project root directory
            if getattr(sys, 'frozen', False):
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            else:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            
            icon_path = os.path.join(base_path, "assets", "images", "logo.png")
            
            if os.path.exists(icon_path):
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
        except Exception as e:
            logging.warning(f"Could not set window icon: {e}")
    
    def initialize_screens(self):
        """Initialize all application screens"""
        # Landing screen (intro animation)
        self.screens[self.SCREEN_LANDING] = LandingScreen(
            self.screen,
            self.handle_landing_complete
        )
        
        # Welcome screen
        self.screens[self.SCREEN_WELCOME] = WelcomeScreen(
            self.screen,
            self.handle_welcome_menu
        )
        
        # Info screen (separated from welcome screen)
        self.screens[self.SCREEN_INFO] = InfoScreen(
            self.screen,
            lambda: self.switch_screen(self.SCREEN_WELCOME)
        )
        
        # Generation screen
        self.screens[self.SCREEN_GENERATION] = GenerationScreen(
            self.screen,
            lambda: self.switch_screen(self.SCREEN_WELCOME),
            self.handle_generation_complete
        )
        
        # Settings screen
        self.screens[self.SCREEN_SETTINGS] = SettingsScreen(
            self.screen,
            lambda: self.switch_screen(self.SCREEN_WELCOME)
        )
        
        # Results screen initialization is deferred until we have results
    
    def handle_landing_complete(self):
        """Handle completion of the landing screen animation"""
        logging.info("Landing screen animation complete")
        self.switch_screen(self.SCREEN_WELCOME)
    
    def handle_welcome_menu(self, option: str):
        """
        Handle menu selections from the welcome screen
        
        Args:
            option: Selected menu option
        """
        logging.info(f"Welcome menu option selected: {option}")
        
        if option == "generate":
            self.switch_screen(self.SCREEN_GENERATION)
        elif option == "devices":
            self.show_devices()
        elif option == "settings":
            self.switch_screen(self.SCREEN_SETTINGS)
        elif option == "info":
            self.switch_screen(self.SCREEN_INFO)
        elif option == "exit":
            self.running = False
    
    def handle_generation_complete(self, results: Dict[str, Any]):
        """
        Handle completion of address generation
        
        Args:
            results: Generation results
        """
        logging.info(f"Generation complete with {len(results.get('results', []))} results")
        
        # Initialize results screen with the generated data
        self.screens[self.SCREEN_RESULTS] = ResultsScreen(
            self.screen,
            results,
            lambda: self.switch_screen(self.SCREEN_WELCOME)
        )
        self.switch_screen(self.SCREEN_RESULTS)
    
    def show_devices(self):
        """Show available OpenCL devices and display in a more user-friendly way"""
        try:
            from core.vangen import get_available_devices
            devices_info = get_available_devices()
            
            if devices_info["success"]:
                devices = devices_info["devices"]
                if not devices:
                    logging.info("No OpenCL devices found")
                else:
                    # Log detailed info to terminal
                    logging.info("Available OpenCL devices:")
                    
                    # Keep track of best device for recommendation
                    best_device = None
                    best_score = -1
                    
                    for platform in devices:
                        logging.info(f"Platform: {platform['platform_name']}")
                        for device in platform["devices"]:
                            # Extract device details
                            device_name = device['device_name']
                            device_type = device['device_type']
                            compute_units = device['compute_units']
                            mem_size_mb = device['global_mem_size'] / (1024 * 1024)
                            
                            # Log device info
                            logging.info(f"  - Device: {device_name}")
                            logging.info(f"    Type: {device_type}")
                            logging.info(f"    Compute Units: {compute_units}")
                            logging.info(f"    Memory: {mem_size_mb:.2f} MB")
                            logging.info("")
                            
                            # Simple scoring to find "best" device
                            # Prefer GPUs, with more compute units and memory
                            device_type_score = 10 if "GPU" in device_type else 1
                            score = device_type_score * (compute_units + (mem_size_mb / 1024))
                            
                            if score > best_score:
                                best_score = score
                                best_device = device_name
                    
                    # If we found a best device, mention it
                    if best_device:
                        logging.info(f"Recommended device: {best_device}")
            else:
                logging.error(f"Error getting devices: {devices_info['error']}")
        except Exception as e:
            logging.error(f"Error showing devices: {e}")
        
        # After showing devices, go back to welcome screen
        self.switch_screen(self.SCREEN_WELCOME)
    
    def switch_screen(self, screen_name: str):
        """
        Switch to a different screen
        
        Args:
            screen_name: Name of the screen to switch to
        """
        if screen_name in self.screens:
            self.current_screen = screen_name
            logging.info(f"Switched to {screen_name} screen")
        else:
            logging.error(f"Screen {screen_name} not found")
    
    def handle_window_resize(self, new_size):
        """
        Handle window resize events
        
        Args:
            new_size: New window dimensions (width, height)
        """
        # Update window dimensions
        self.width, self.height = new_size
        
        # Reinitialize screens that need resizing
        if self.SCREEN_WELCOME in self.screens:
            # Store current screen to restore after reinitialization
            current_screen = self.current_screen
            
            # Reinitialize the welcome screen
            self.screens[self.SCREEN_WELCOME] = WelcomeScreen(
                self.screen,
                self.handle_welcome_menu
            )
            
            # Reinitialize other screens as needed
            if self.SCREEN_GENERATION in self.screens:
                self.screens[self.SCREEN_GENERATION] = GenerationScreen(
                    self.screen,
                    lambda: self.switch_screen(self.SCREEN_WELCOME),
                    self.handle_generation_complete
                )
                
            if self.SCREEN_SETTINGS in self.screens:
                self.screens[self.SCREEN_SETTINGS] = SettingsScreen(
                    self.screen,
                    lambda: self.switch_screen(self.SCREEN_WELCOME)
                )
                
            if self.SCREEN_INFO in self.screens:
                self.screens[self.SCREEN_INFO] = InfoScreen(
                    self.screen,
                    lambda: self.switch_screen(self.SCREEN_WELCOME)
                )
                
            if self.SCREEN_RESULTS in self.screens:
                # If results screen exists, we need to preserve the results data
                results_data = getattr(self.screens[self.SCREEN_RESULTS], 'results', None)
                if results_data:
                    self.screens[self.SCREEN_RESULTS] = ResultsScreen(
                        self.screen,
                        results_data,
                        lambda: self.switch_screen(self.SCREEN_WELCOME)
                    )
    
    def run(self) -> int:
        """
        Run the main application loop
        
        Returns:
            int: Exit code (0 for success)
        """
        self.running = True
        clock = pygame.time.Clock()
        last_time = pygame.time.get_ticks()
        
        try:
            while self.running:
                # Calculate delta time for animations
                current_time = pygame.time.get_ticks()
                delta_time = (current_time - last_time) / 1000.0  # Convert to seconds
                last_time = current_time
                
                # Process events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            # Escape key acts as a back button
                            if self.current_screen == self.SCREEN_LANDING:
                                # Skip intro animation if ESC is pressed
                                self.switch_screen(self.SCREEN_WELCOME)
                            elif self.current_screen == self.SCREEN_INFO:
                                # Go back to welcome screen from info screen
                                self.switch_screen(self.SCREEN_WELCOME)
                            elif self.current_screen != self.SCREEN_WELCOME:
                                self.switch_screen(self.SCREEN_WELCOME)
                            else:
                                # On welcome screen, ask if user wants to exit
                                self.screens[self.SCREEN_WELCOME].set_exit()
                    elif event.type == pygame.VIDEORESIZE:
                        # Handle window resize events
                        self.handle_window_resize(event.size)
                    
                    # Pass events to current screen
                    if self.current_screen:
                        current_screen_obj = self.screens[self.current_screen]
                        if hasattr(current_screen_obj, 'handle_event'):
                            current_screen_obj.handle_event(event)
                
                # Update current screen
                if self.current_screen:
                    current_screen_obj = self.screens[self.current_screen]
                    if hasattr(current_screen_obj, 'update'):
                        current_screen_obj.update(delta_time)
                
                # Draw current screen
                if self.current_screen:
                    current_screen_obj = self.screens[self.current_screen]
                    if hasattr(current_screen_obj, 'draw'):
                        current_screen_obj.draw()
                        pygame.display.flip()
                
                # Check for screen transitions
                if self.current_screen:
                    current_screen_obj = self.screens[self.current_screen]
                    if hasattr(current_screen_obj, 'run'):
                        result = current_screen_obj.run()
                        
                        # Handle screen result if any
                        if result == "done" and self.current_screen == self.SCREEN_LANDING:
                            # Landing screen animation is complete, switch to welcome screen
                            self.switch_screen(self.SCREEN_WELCOME)
                        elif result == "exit":
                            # Exit the application
                            self.running = False
                
                # Cap the frame rate
                clock.tick(60)
            
            return 0
        except Exception as e:
            logging.exception(f"Error in main loop: {e}")
            return 1


# For testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s %(asctime)s] %(message)s",
        handlers=[
            logging.FileHandler("vanity_generator.log"),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Starting CMYK Retro Lo-Fi Solana Vanity Address Generator")
    
    # Initialize pygame and mixer
    pygame.init()
    
    try:
        pygame.mixer.init()
    except Exception as e:
        logging.warning(f"Could not initialize sound mixer: {e}")
    
    # Create and run main window
    window = MainWindow()
    exit_code = window.run()
    
    # Clean up and exit
    pygame.quit()
    logging.info("Application exiting")
    sys.exit(exit_code)