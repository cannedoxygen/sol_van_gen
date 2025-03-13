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
                    raise FileNotFoundError(f"Pixel font not found: {pixel_font_path}")
            
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
    
    def setup_intro_animation(self):
        """Setup intro animation state"""
        self.intro_text = "Generating Unique Solana Addresses"
        self.intro_text_index = 0
        self.intro_text_surface = self.font.render("", True, CMYKColors.WHITE)
        self.intro_sound_played = False
    
    def create_buttons(self):
        """Create main menu buttons"""
        button_width = 300
        button_height = 50
        button_y = self.height // 2 + 40
        button_spacing = 20

        self.generate_button = RetroButton(
            (self.width - button_width) // 2,
            button_y,
            button_width,
            button_height,
            "Generate Address",
            lambda: self.on_menu_select("generate"),
            color_scheme="cyan"
        )

        self.device_button = RetroButton(
            (self.width - button_width) // 2,
            button_y + button_height + button_spacing,
            button_width,
            button_height,
            "Select Device",
            lambda: self.on_menu_select("devices"),
            color_scheme="magenta"
        )

        self.settings_button = RetroButton(
            (self.width - button_width) // 2,
            button_y + (button_height + button_spacing) * 2,
            button_width,
            button_height,
            "Settings",
            lambda: self.on_menu_select("settings"),
            color_scheme="yellow"
        )

        self.exit_button = RetroButton(
            (self.width - button_width) // 2,
            button_y + (button_height + button_spacing) * 3,
            button_width,
            button_height,
            "Exit",
            lambda: self.on_menu_select("exit"),
            color_scheme="white"
        )

    def draw_intro(self):
        """Draw the intro animation"""
        self.intro_text_index += 1

        if self.intro_text_index <= len(self.intro_text):
            self.intro_text_surface = self.font.render(
                self.intro_text[:self.intro_text_index],
                True,
                CMYKColors.WHITE
            )
        else:
            self.intro_complete = True
            if self.intro_sound and not self.intro_sound_played:
                self.intro_sound.play()
                self.intro_sound_played = True

        intro_text_rect = self.intro_text_surface.get_rect(
            center=(self.width // 2, self.height // 2)
        )
        self.screen.blit(self.intro_text_surface, intro_text_rect)

    def draw(self):
        """Draw the welcome screen"""
        self.screen.blit(self.background, (0, 0))

        if not self.intro_complete:
            self.draw_intro()
        else:
            self.screen.blit(self.logo, self.logo_rect)
            self.generate_button.draw(self.screen)
            self.device_button.draw(self.screen)
            self.settings_button.draw(self.screen)
            self.exit_button.draw(self.screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if event was handled
        """
        if self.intro_complete:
            self.generate_button.handle_event(event)
            self.device_button.handle_event(event)
            self.settings_button.handle_event(event)
            self.exit_button.handle_event(event)
        return False
    
    def set_exit(self):
        """Set the screen to exit on next run"""
        self.exit_screen = True
    
    def run(self) -> str:
        """
        Run the welcome screen loop
        
        Returns:
            str: Result of screen interaction (e.g., 'generate', 'settings', 'exit')
        """
        clock = pygame.time.Clock()
        
        while not self.exit_screen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_screen = True
                else:
                    self.handle_event(event)
            
            self.draw()
            pygame.display.flip()
            
            if self.intro_complete:
                clock.tick(60)  # Limit to 60 FPS
            else:
                clock.tick(15)  # Slower rate for intro animation
        
        if self.exit_screen:
            return "exit"
        
        return ""  # Default empty result


if __name__ == "__main__":
    # For standalone testing
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Solana Vanity Address Generator")
    
    def on_menu_select(selection):
        print(f"Menu selection: {selection}")
    
    welcome_screen = WelcomeScreen(screen, on_menu_select)
    result = welcome_screen.run()
    print(f"Welcome screen result: {result}")
    
    pygame.quit()