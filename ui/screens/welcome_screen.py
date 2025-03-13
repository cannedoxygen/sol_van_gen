"""
Welcome screen for the Solana Vanity Address Generator
Displays intro animation and main menu with retro CMYK aesthetics
"""

import pygame
import os
import random
import time
import math
import logging
from typing import Callable, Dict, List, Tuple

from ui.components.retro_button import RetroButton
from utils.ascii_art import CMYKColors
from utils.config_manager import ConfigManager

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

class WelcomeScreen:
    """
    Welcome screen with retro CMYK aesthetic and intro animation
    """
    
    def __init__(self, screen: pygame.Surface, on_menu_select: Callable[[str], None]):
        """
        Initialize the welcome screen
        
        Args:
            screen: Pygame surface to render on
            on_menu_select: Callback when a menu option is selected
        """
        try:
            self.screen = screen
            self.width, self.height = screen.get_size()
            self.on_menu_select = on_menu_select
            
            # Ensure mixer is initialized
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init()
                except Exception as e:
                    logging.warning(f"Could not initialize sound mixer: {e}")
            
            # State tracking
            self.intro_complete = False
            self.exit_screen = False
            self.start_time = time.time()
            
            # Load config
            self.config = ConfigManager()
            
            # Load assets
            self.load_assets()
            
            # Create UI elements
            self.create_buttons()
            
            # Setup intro animation state
            self.setup_intro_animation()
        
        except Exception as e:
            logging.error(f"Error initializing welcome screen: {e}")
            raise
    
    def create_fallback_logo(self) -> pygame.Surface:
        """Create a fallback logo if image is not found"""
        logo_width, logo_height = 400, 120
        logo = pygame.Surface((logo_width, logo_height), pygame.SRCALPHA)
        
        # Draw 'CMYK' in respective colors
        c_text = self.title_font.render("C", True, (0, 255, 255))
        m_text = self.title_font.render("M", True, (255, 0, 255))
        y_text = self.title_font.render("Y", True, (255, 255, 0))
        k_text = self.title_font.render("K", True, (200, 200, 200))
        
        logo.blit(c_text, (50, 30))
        logo.blit(m_text, (90, 30))
        logo.blit(y_text, (140, 30))
        logo.blit(k_text, (180, 30))
        
        # Add subtitle
        subtitle = self.font.render("Solana Vanity Generator", True, (255, 255, 255))
        logo.blit(subtitle, (20, 80))
        
        return logo
    
    def load_assets(self):
        """Load screen assets with robust error handling"""
        try:
            # Load background image
            try:
                bg_path = os.path.join(PROJECT_ROOT, "assets", "images", "background.png")
                bg_paths_to_try = [
                    bg_path,
                    bg_path.replace(".png", ".jpg"),
                    bg_path.replace(".png", ".jpeg")
                ]
                
                background_loaded = False
                for try_path in bg_paths_to_try:
                    if os.path.exists(try_path):
                        try:
                            self.background = pygame.image.load(try_path)
                            self.background = pygame.transform.scale(self.background, (self.width, self.height))
                            background_loaded = True
                            break
                        except pygame.error:
                            logging.warning(f"Could not load background from {try_path}")
                
                if not background_loaded:
                    # Create a procedural background
                    logging.warning("No valid background image found")
                    self.background = pygame.Surface((self.width, self.height))
                    self.background.fill((40, 40, 40))  # Dark gray
                    
                    # Add some random 'pixel noise' to simulate retro bg
                    for _ in range(1000):
                        x = random.randint(0, self.width - 1)
                        y = random.randint(0, self.height - 1)
                        color = random.choice([
                            (0, 255, 255, 50),    # Cyan
                            (255, 0, 255, 50),    # Magenta
                            (255, 255, 0, 50),    # Yellow
                            (60, 60, 60, 50)      # Key (Black)
                        ])
                        pygame.draw.rect(self.background, color, (x, y, 2, 2))
            
            except Exception as img_error:
                logging.error(f"Error loading background image: {img_error}")
                # Fallback background
                self.background = pygame.Surface((self.width, self.height))
                self.background.fill((40, 40, 40))
            
            # Load logo
            try:
                logo_path = os.path.join(PROJECT_ROOT, "assets", "images", "logo.png")
                logo_paths_to_try = [
                    logo_path,
                    logo_path.replace(".png", ".jpg"),
                    logo_path.replace(".png", ".jpeg")
                ]
                
                logo_loaded = False
                for try_path in logo_paths_to_try:
                    if os.path.exists(try_path):
                        try:
                            self.logo = pygame.image.load(try_path)
                            logo_width = int(self.width * 0.6)
                            logo_height = int(logo_width * self.logo.get_height() / self.logo.get_width())
                            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
                            self.logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 4))
                            logo_loaded = True
                            break
                        except pygame.error:
                            logging.warning(f"Could not load logo from {try_path}")
                
                if not logo_loaded:
                    # Create a fallback logo
                    logging.warning("No valid logo image found")
                    self.logo = self.create_fallback_logo()
                    self.logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 4))
            
            except Exception as logo_error:
                logging.error(f"Error loading logo: {logo_error}")
                self.logo = self.create_fallback_logo()
                self.logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 4))
            
            # Load fonts
            try:
                pixel_font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "pixel_font.ttf")
                
                if os.path.exists(pixel_font_path):
                    self.font = pygame.font.Font(pixel_font_path, 24)
                    self.title_font = pygame.font.Font(pixel_font_path, 36)
                else:
                    logging.warning(f"Pixel font not found: {pixel_font_path}")
                    self.font = pygame.font.SysFont("monospace", 24)
                    self.title_font = pygame.font.SysFont("monospace", 36)
            
            except Exception as font_error:
                logging.error(f"Error loading fonts: {font_error}")
                self.font = pygame.font.SysFont("monospace", 24)
                self.title_font = pygame.font.SysFont("monospace", 36)
            
            # Load sounds
            try:
                intro_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "success.wav")
                
                if os.path.exists(intro_sound_path):
                    self.intro_sound = pygame.mixer.Sound(intro_sound_path)
                else:
                    logging.warning(f"Intro sound not found: {intro_sound_path}")
                    self.intro_sound = None
            
            except Exception as sound_error:
                logging.error(f"Error loading sounds: {sound_error}")
                self.intro_sound = None
        
        except Exception as e:
            logging.error(f"Comprehensive asset loading error: {e}")
            raise