"""
Welcome screen for the CMYK Retro Solana Vanity Generator
Displays main menu with essential functionality
"""

import pygame
import os
import logging
import math
import random
import time
import threading
from typing import Callable, List, Tuple, Dict, Any

from ui.components.retro_button import RetroButton
from utils.ascii_art import CMYKColors
from utils.config_manager import ConfigManager

class WelcomeScreen:
    """
    Welcome screen with retro CMYK aesthetic
    """
    
    def __init__(self, screen: pygame.Surface, on_menu_select: Callable[[str], None]):
        """
        Initialize the welcome screen
        
        Args:
            screen: Pygame surface to render on
            on_menu_select: Callback when a menu option is selected
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.on_menu_select = on_menu_select
        self.config = ConfigManager()
        
        # State tracking
        self.exit_screen = False
        self.connected_device = "Searching for devices..."
        self.device_found = False
        
        # Animation timing
        self.animation_time = 0
        
        # Load assets
        self.load_assets()
        
        # Create UI elements
        self.create_ui_components()
        
        # Start device detection in a separate thread
        self.detect_device_thread = threading.Thread(target=self.fetch_device_info, daemon=True)
        self.detect_device_thread.start()
    
    def load_assets(self):
        """Load screen assets"""
        # Get the project root directory
        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Load background
        try:
            bg_path = os.path.join(PROJECT_ROOT, "assets", "images", "background.png")
            self.background = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except (pygame.error, FileNotFoundError):
            logging.warning("Background image not found, creating procedural background.")
            self.background = self.create_procedural_background()
            
        # Load logo
        try:
            logo_path = os.path.join(PROJECT_ROOT, "assets", "images", "logo.png")
            self.logo = pygame.image.load(logo_path)
            logo_width = int(self.width * 0.6)
            logo_height = int(logo_width * self.logo.get_height() / self.logo.get_width())
            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
            self.logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 4))
        except (pygame.error, FileNotFoundError):
            logging.warning("Logo image not found, creating procedural logo.")
            self.logo = self.create_procedural_logo()
            self.logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 4))
        
        # Load fonts
        try:
            pixel_font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "pixel_font.ttf")
            if os.path.exists(pixel_font_path):
                self.title_font = pygame.font.Font(pixel_font_path, 32)
                self.font = pygame.font.Font(pixel_font_path, 24)
                self.small_font = pygame.font.Font(pixel_font_path, 18)
                self.tiny_font = pygame.font.Font(pixel_font_path, 14)
            else:
                self.title_font = pygame.font.SysFont("monospace", 32)
                self.font = pygame.font.SysFont("monospace", 24)
                self.small_font = pygame.font.SysFont("monospace", 18)
                self.tiny_font = pygame.font.SysFont("monospace", 14)
        except Exception as e:
            logging.warning(f"Font loading failed: {e}")
            self.title_font = pygame.font.SysFont("monospace", 32)
            self.font = pygame.font.SysFont("monospace", 24)
            self.small_font = pygame.font.SysFont("monospace", 18)
            self.tiny_font = pygame.font.SysFont("monospace", 14)
        
        # Load sounds
        try:
            button_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "keypress.wav")
            if os.path.exists(button_sound_path) and pygame.mixer.get_init():
                self.button_sound = pygame.mixer.Sound(button_sound_path)
                self.button_sound.set_volume(0.3)
            else:
                self.button_sound = None
        except Exception as e:
            logging.warning(f"Sound loading failed: {e}")
            self.button_sound = None
    
    def create_procedural_background(self) -> pygame.Surface:
        """Create a procedural CMYK-themed background"""
        surface = pygame.Surface((self.width, self.height))
        surface.fill((40, 40, 40))  # Dark gray base
        
        # Add CMYK dots
        for _ in range(300):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 4)
            color = random.choice([
                (0, 255, 255),      # Cyan
                (255, 0, 255),      # Magenta
                (255, 255, 0),      # Yellow
                (100, 100, 100)     # Key/Black
            ])
            
            # Draw dot
            pygame.draw.rect(surface, color, (x, y, size, size))
        
        # Add some scan lines for retro effect
        for y in range(0, self.height, 3):
            pygame.draw.line(
                surface, 
                (0, 0, 0), 
                (0, y), 
                (self.width, y)
            )
        
        return surface
    
    def create_procedural_logo(self) -> pygame.Surface:
        """Create a procedural CMYK logo if image can't be loaded"""
        logo_width = int(self.width * 0.6)
        logo_height = int(logo_width * 0.3)
        
        logo = pygame.Surface((logo_width, logo_height), pygame.SRCALPHA)
        
        # Draw CMYK colored boxes as a simple logo
        box_width = logo_width // 4
        
        # Cyan box
        pygame.draw.rect(
            logo, 
            (0, 255, 255), 
            (0, 0, box_width, logo_height)
        )
        
        # Magenta box
        pygame.draw.rect(
            logo, 
            (255, 0, 255), 
            (box_width, 0, box_width, logo_height)
        )
        
        # Yellow box
        pygame.draw.rect(
            logo, 
            (255, 255, 0), 
            (box_width * 2, 0, box_width, logo_height)
        )
        
        # Key (black) box
        pygame.draw.rect(
            logo, 
            (100, 100, 100), 
            (box_width * 3, 0, box_width, logo_height)
        )
        
        # Add text
        font = pygame.font.SysFont("monospace", 32, bold=True)
        text_surface = font.render("SOLANA VANITY", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(logo_width // 2, logo_height // 2))
        logo.blit(text_surface, text_rect)
        
        return logo
    
    def create_ui_components(self):
        """Create main menu buttons and UI components"""
        # Adjust button positioning to be more centered on the screen with bottom padding
        button_width = 300
        button_height = 50
        button_spacing = 20
        
        # Calculate total menu height
        total_buttons = 5
        total_menu_height = (button_height * total_buttons) + (button_spacing * (total_buttons - 1))
        
        # Center the buttons vertically, starting below the logo area
        # Ensure there is padding at the bottom
        bottom_padding = 80  # Increased bottom padding
        available_height = self.height - self.logo_rect.bottom - bottom_padding
        button_y_start = self.logo_rect.bottom + (available_height - total_menu_height) // 2

        # Main menu buttons - reordered to put device first
        self.device_button = RetroButton(
            (self.width - button_width) // 2,
            button_y_start,
            button_width,
            button_height,
            "Select Device",
            lambda: self.on_menu_select("devices"),
            color_scheme="cyan"
        )

        self.generate_button = RetroButton(
            (self.width - button_width) // 2,
            button_y_start + button_height + button_spacing,
            button_width,
            button_height,
            "Generate Address",
            lambda: self.on_menu_select("generate"),
            color_scheme="magenta"
        )

        self.settings_button = RetroButton(
            (self.width - button_width) // 2,
            button_y_start + (button_height + button_spacing) * 2,
            button_width,
            button_height,
            "Settings",
            lambda: self.on_menu_select("settings"),
            color_scheme="yellow"
        )
        
        self.info_button = RetroButton(
            (self.width - button_width) // 2,
            button_y_start + (button_height + button_spacing) * 3,
            button_width,
            button_height,
            "How To Use",
            lambda: self.on_menu_select("info"),
            color_scheme="cyan"
        )

        self.exit_button = RetroButton(
            (self.width - button_width) // 2,
            button_y_start + (button_height + button_spacing) * 4,
            button_width,
            button_height,
            "Exit",
            lambda: self.on_menu_select("exit"),
            color_scheme="white"
        )
    
    def fetch_device_info(self):
        """Get information about available devices"""
        try:
            # Import here to avoid circular imports
            from core.vangen import get_available_devices
            
            # Get device info
            devices_info = get_available_devices()
            
            if devices_info["success"]:
                devices = devices_info["devices"]
                if not devices:
                    self.connected_device = "No OpenCL devices found"
                else:
                    # Find the first GPU device
                    for platform in devices:
                        for device in platform["devices"]:
                            if "GPU" in device.get("device_type", ""):
                                self.connected_device = f"Connected: {device['device_name']}"
                                self.device_found = True
                                return
                            
                    # If no GPU found, use the first device
                    if devices[0]["devices"]:
                        device = devices[0]["devices"][0]
                        self.connected_device = f"Connected: {device['device_name']}"
                        self.device_found = True
                    else:
                        self.connected_device = "No suitable devices found"
            else:
                self.connected_device = "Error detecting devices"
        except Exception as e:
            logging.error(f"Error fetching device info: {e}")
            self.connected_device = "Error detecting devices"
    
    def draw_main_menu(self):
        """Draw the main menu screen with logo and buttons"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
            
        # Draw logo with pulsing glow effect
        glow_size = int(abs(math.sin(self.animation_time * 2.0)) * 15)
        
        if glow_size > 0:
            # Create a larger surface for the glow effect
            glow_surface = pygame.Surface((
                self.logo_rect.width + glow_size * 2,
                self.logo_rect.height + glow_size * 2
            ), pygame.SRCALPHA)
            
            # Draw multiple transparent rects for glow effect
            for i in range(glow_size, 0, -2):
                alpha = 12 - i  # Fade out as we get further from logo
                glow_surface.set_alpha(alpha)
                pygame.draw.rect(
                    glow_surface,
                    (0, 255, 255),  # Cyan glow
                    (
                        glow_size - i,
                        glow_size - i,
                        self.logo_rect.width + i * 2,
                        self.logo_rect.height + i * 2
                    ),
                    border_radius=10
                )
            
            # Blit glow first (behind logo)
            self.screen.blit(
                glow_surface,
                (self.logo_rect.x - glow_size, self.logo_rect.y - glow_size)
            )
        
        # Draw logo itself
        self.screen.blit(self.logo, self.logo_rect)
        
        # Draw subtitle with animation
        subtitle = "Retro Lo-Fi Edition v1.0"
        
        # Create rainbow color effect for subtitle
        rainbow_shift = int(self.animation_time * 30) % 4
        colors = [
            (0, 255, 255),      # Cyan
            (255, 0, 255),      # Magenta
            (255, 255, 0),      # Yellow
            (200, 200, 200)     # White/gray
        ]
        
        subtitle_color = colors[rainbow_shift]
        subtitle_surface = self.font.render(subtitle, True, subtitle_color)
        subtitle_rect = subtitle_surface.get_rect(
            center=(self.width // 2, self.logo_rect.bottom + 20)
        )
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw connected device info with blink effect for searching
        if not self.device_found and self.animation_time % 1.0 > 0.5:
            device_text = "Searching for devices..."
        else:
            device_text = self.connected_device
            
        device_color = (0, 255, 255) if self.device_found else (255, 255, 0)  # Cyan if found, yellow if searching
        device_surface = self.small_font.render(device_text, True, device_color)
        device_rect = device_surface.get_rect(
            center=(self.width // 2, subtitle_rect.bottom + 25)
        )
        self.screen.blit(device_surface, device_rect)
        
        # Draw animated horizontal line
        line_y = device_rect.bottom + 10
        line_width = 0.6 * self.width
        line_x_start = (self.width - line_width) / 2
        line_x_end = line_x_start + line_width
        
        # Create a gradient line with CMYK colors
        steps = int(line_width)
        for i in range(steps):
            progress = i / steps
            
            # Shift starting color based on time
            shift = (self.animation_time * 0.5) % 1.0
            progress = (progress + shift) % 1.0
            
            if progress < 0.25:
                # Cyan to Magenta
                ratio = progress * 4
                color = (
                    int(255 * ratio),       # R: 0 -> 255
                    int(255 * (1 - ratio)), # G: 255 -> 0
                    255                      # B: 255
                )
            elif progress < 0.5:
                # Magenta to Yellow
                ratio = (progress - 0.25) * 4
                color = (
                    255,                    # R: 255
                    int(255 * ratio),       # G: 0 -> 255
                    int(255 * (1 - ratio))  # B: 255 -> 0
                )
            elif progress < 0.75:
                # Yellow to Black
                ratio = (progress - 0.5) * 4
                color = (
                    int(255 * (1 - ratio)), # R: 255 -> 0
                    int(255 * (1 - ratio)), # G: 255 -> 0
                    0                       # B: 0
                )
            else:
                # Black to Cyan
                ratio = (progress - 0.75) * 4
                color = (
                    0,                     # R: 0
                    int(255 * ratio),      # G: 0 -> 255
                    int(255 * ratio)       # B: 0 -> 255
                )
            
            # Draw a single pixel of the line
            x_pos = int(line_x_start + i)
            pygame.draw.line(
                self.screen,
                color,
                (x_pos, line_y),
                (x_pos, line_y + 2)
            )
        
        # Draw buttons
        self.device_button.draw(self.screen)
        self.generate_button.draw(self.screen)
        self.settings_button.draw(self.screen)
        self.info_button.draw(self.screen)
        self.exit_button.draw(self.screen)
        
        # Draw footer info with pulsing effect
        footer_text = "Press [ESC] to exit"
        pulse = abs(math.sin(self.animation_time * 2)) * 50 + 150  # 150-200 range
        footer_color = (int(pulse), int(pulse), int(pulse))
        
        footer_surface = self.small_font.render(footer_text, True, footer_color)
        footer_rect = footer_surface.get_rect(center=(self.width // 2, self.height - 20))
        self.screen.blit(footer_surface, footer_rect)
    
    def update(self, delta_time: float):
        """Update animations and timing"""
        self.animation_time += delta_time
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if event was handled
        """
        # Handle button events
        if self.device_button.handle_event(event):
            return True
        if self.generate_button.handle_event(event):
            return True
        if self.settings_button.handle_event(event):
            return True
        if self.info_button.handle_event(event):
            return True
        if self.exit_button.handle_event(event):
            return True
            
        return False
    
    def set_exit(self):
        """Set the screen to exit on next run"""
        self.exit_screen = True
    
    def draw(self):
        """Draw the welcome screen"""
        self.draw_main_menu()
    
    def run(self) -> str:
        """
        Run the welcome screen logic
        
        Returns:
            str: Command for the main controller ('done' or 'exit')
        """
        if self.exit_screen:
            return "exit"
        return "done"  # Default result