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
        self.device_details = ""
        
        # Scrolling state
        self.scroll_position = 0
        self.total_content_height = 0
        self.max_scroll = 0
        self.scrolling = False
        self.last_mouse_y = 0
        
        # Animation timing
        self.animation_time = 0
        
        # Load assets
        self.load_assets()
        
        # Create UI elements
        self.create_ui_components()
        
        # Calculate total content height for scrolling
        self.calculate_content_height()
        
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
        except (pygame.error, FileNotFoundError):
            logging.warning("Logo image not found, creating procedural logo.")
            self.logo = self.create_procedural_logo()
        
        # Set logo rect to be positioned later
        self.logo_rect = self.logo.get_rect()
        
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
        # Define button dimensions
        button_width = 300
        button_height = 50
        button_spacing = 20
        
        # Create a content container that will be scrollable
        self.content_rect = pygame.Rect(0, 0, self.width, self.height)
        
        # Create spacing for the content
        top_margin = 50
        
        # Determine logo position at the top of the content
        logo_y = top_margin
        self.logo_rect = self.logo.get_rect(centerx=self.width // 2, y=logo_y)
        
        # Calculate position for the subtitle (below logo)
        subtitle_y = self.logo_rect.bottom + 20
        
        # Determine device info position (below subtitle)
        device_info_y = subtitle_y + 30
        
        # Calculate horizontal line position (below device info)
        line_y = device_info_y + 40
        
        # Calculate button positions starting below the line
        button_start_y = line_y + 20
        
        # Main menu buttons - ordered from top to bottom
        self.device_button = RetroButton(
            (self.width - button_width) // 2,
            button_start_y,
            button_width,
            button_height,
            "Select Device",
            lambda: self.on_menu_select("devices"),
            color_scheme="cyan"
        )

        self.generate_button = RetroButton(
            (self.width - button_width) // 2,
            button_start_y + (button_height + button_spacing),
            button_width,
            button_height,
            "Generate Address",
            lambda: self.on_menu_select("generate"),
            color_scheme="magenta"
        )

        self.settings_button = RetroButton(
            (self.width - button_width) // 2,
            button_start_y + (button_height + button_spacing) * 2,
            button_width,
            button_height,
            "Settings",
            lambda: self.on_menu_select("settings"),
            color_scheme="yellow"
        )
        
        self.info_button = RetroButton(
            (self.width - button_width) // 2,
            button_start_y + (button_height + button_spacing) * 3,
            button_width,
            button_height,
            "How To Use",
            lambda: self.on_menu_select("info"),
            color_scheme="cyan"
        )

        self.exit_button = RetroButton(
            (self.width - button_width) // 2,
            button_start_y + (button_height + button_spacing) * 4,
            button_width,
            button_height,
            "Exit",
            lambda: self.on_menu_select("exit"),
            color_scheme="white"
        )
        
        # Store UI component positions for scrolling calculations
        self.ui_positions = {
            "logo_y": logo_y,
            "subtitle_y": subtitle_y,
            "device_info_y": device_info_y,
            "line_y": line_y,
            "button_start_y": button_start_y
        }
        
        # Create a modal for displaying device details
        self.device_modal_active = False
        self.device_modal_rect = pygame.Rect(
            self.width // 4,
            self.height // 4,
            self.width // 2,
            self.height // 2
        )
        
        # Create a close button for the device modal
        self.device_modal_close_button = RetroButton(
            self.device_modal_rect.centerx - 50,
            self.device_modal_rect.bottom - 60,
            100,
            40,
            "Close",
            self.close_device_modal,
            color_scheme="white"
        )
    
    def calculate_content_height(self):
        """Calculate the total height of content for scrolling"""
        if not hasattr(self, 'exit_button'):
            return
        
        # Calculate height from top to bottom of the last button
        self.total_content_height = self.exit_button.y + self.exit_button.height + 40  # Add footer padding
        
        # Calculate maximum scroll position (if content is taller than screen)
        self.max_scroll = max(0, self.total_content_height - self.height)
    
    def update_ui_positions(self):
        """Update UI component positions based on scroll position"""
        scroll_offset = -self.scroll_position
        
        # Update logo position
        logo_y = self.ui_positions["logo_y"] + scroll_offset
        self.logo_rect = self.logo.get_rect(centerx=self.width // 2, y=logo_y)
        
        # Update button positions
        button_start_y = self.ui_positions["button_start_y"] + scroll_offset
        
        self.device_button.y = button_start_y
        self.generate_button.y = button_start_y + (self.device_button.height + 20)
        self.settings_button.y = button_start_y + (self.device_button.height + 20) * 2
        self.info_button.y = button_start_y + (self.device_button.height + 20) * 3
        self.exit_button.y = button_start_y + (self.device_button.height + 20) * 4
    
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
                                
                                # Store detailed device info for modal display
                                self.device_details = self.format_device_details(devices_info)
                                return
                            
                    # If no GPU found, use the first device
                    if devices[0]["devices"]:
                        device = devices[0]["devices"][0]
                        self.connected_device = f"Connected: {device['device_name']}"
                        self.device_found = True
                        
                        # Store detailed device info for modal display
                        self.device_details = self.format_device_details(devices_info)
                    else:
                        self.connected_device = "No suitable devices found"
            else:
                self.connected_device = "Error detecting devices"
        except Exception as e:
            logging.error(f"Error fetching device info: {e}")
            self.connected_device = "Error detecting devices"
    
    def format_device_details(self, devices_info: Dict) -> str:
        """Format device information for display in the modal"""
        if not devices_info["success"] or not devices_info.get("devices"):
            return "No device information available."
        
        details = []
        details.append("Available OpenCL Devices:")
        details.append("")
        
        for platform in devices_info["devices"]:
            details.append(f"Platform: {platform['platform_name']}")
            
            for device in platform["devices"]:
                details.append(f"  - Device: {device['device_name']}")
                details.append(f"    Type: {device['device_type']}")
                details.append(f"    Compute Units: {device['compute_units']}")
                
                # Convert memory to MB for readability
                mem_size_mb = device['global_mem_size'] / (1024 * 1024)
                details.append(f"    Memory: {mem_size_mb:.2f} MB")
                details.append("")
        
        return "\n".join(details)
    
    def show_device_modal(self):
        """Show the modal with detailed device information"""
        self.device_modal_active = True
    
    def close_device_modal(self):
        """Close the device details modal"""
        self.device_modal_active = False
    
    def draw_device_modal(self):
        """Draw the modal with device details"""
        if not self.device_modal_active:
            return
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw modal background
        pygame.draw.rect(
            self.screen,
            (40, 40, 50),
            self.device_modal_rect,
            border_radius=10
        )
        
        # Draw border with animation
        border_colors = [
            (0, 255, 255),     # Cyan
            (255, 0, 255),     # Magenta
            (255, 255, 0),     # Yellow
            (200, 200, 200)    # White/gray
        ]
        
        color_index = int(self.animation_time * 3) % len(border_colors)
        pygame.draw.rect(
            self.screen,
            border_colors[color_index],
            self.device_modal_rect,
            width=2,
            border_radius=10
        )
        
        # Draw title
        title_text = "Device Information"
        title_surface = self.font.render(title_text, True, (0, 255, 255))
        title_rect = title_surface.get_rect(centerx=self.device_modal_rect.centerx, y=self.device_modal_rect.y + 20)
        self.screen.blit(title_surface, title_rect)
        
        # Draw content with line wrapping
        content_rect = pygame.Rect(
            self.device_modal_rect.x + 20,
            title_rect.bottom + 20,
            self.device_modal_rect.width - 40,
            self.device_modal_rect.height - 100
        )
        
        # Split content into lines and render
        lines = self.device_details.split('\n')
        y_offset = 0
        line_height = 20
        
        for line in lines:
            # Skip if we're out of space
            if y_offset + line_height > content_rect.height:
                break
                
            # Render each line
            color = (255, 255, 255)
            if "Platform:" in line:
                color = (255, 255, 0)  # Yellow for platforms
            elif "Device:" in line:
                color = (0, 255, 255)  # Cyan for devices
            
            # Indent device details with spaces
            text_surface = self.small_font.render(line, True, color)
            text_rect = text_surface.get_rect(x=content_rect.x, y=content_rect.y + y_offset)
            self.screen.blit(text_surface, text_rect)
            
            y_offset += line_height
        
        # Draw close button
        self.device_modal_close_button.draw(self.screen)
    
    def draw_main_menu(self):
        """Draw the main menu screen with logo and buttons"""
        # Update UI positions based on scroll
        self.update_ui_positions()
        
        # Draw background
        self.screen.blit(self.background, (0, 0))
            
        # Draw logo with pulsing glow effect
        glow_size = int(abs(math.sin(self.animation_time * 2.0)) * 15)
        
        if glow_size > 0 and self.logo_rect.bottom > 0 and self.logo_rect.y < self.height:
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
        
        # Draw logo only if it's at least partially on screen
        if self.logo_rect.bottom > 0 and self.logo_rect.y < self.height:
            self.screen.blit(self.logo, self.logo_rect)
        
        # Draw subtitle with animation
        subtitle_y = self.ui_positions["subtitle_y"] - self.scroll_position
        if subtitle_y > 0 and subtitle_y < self.height:
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
            subtitle_rect = subtitle_surface.get_rect(center=(self.width // 2, subtitle_y))
            self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw connected device info with blink effect for searching
        device_y = self.ui_positions["device_info_y"] - self.scroll_position
        if device_y > 0 and device_y < self.height:
            if not self.device_found and self.animation_time % 1.0 > 0.5:
                device_text = "Searching for devices..."
            else:
                device_text = self.connected_device
                
            device_color = (0, 255, 255) if self.device_found else (255, 255, 0)  # Cyan if found, yellow if searching
            device_surface = self.small_font.render(device_text, True, device_color)
            device_rect = device_surface.get_rect(center=(self.width // 2, device_y))
            self.screen.blit(device_surface, device_rect)
            
            # Add a clickable effect for device info
            if self.device_found:
                info_text = "Click for details"
                info_surface = self.tiny_font.render(info_text, True, (150, 150, 150))
                info_rect = info_surface.get_rect(center=(self.width // 2, device_y + 20))
                self.screen.blit(info_surface, info_rect)
                
                # Store device info rect for click detection
                self.device_info_rect = pygame.Rect(
                    device_rect.x - 10,
                    device_rect.y - 5,
                    device_rect.width + 20,
                    device_rect.height + info_rect.height + 10
                )
        
        # Draw animated horizontal line
        line_y = self.ui_positions["line_y"] - self.scroll_position
        if line_y > 0 and line_y < self.height:
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
        
        # Draw buttons if they're in view
        if self.device_button.y + self.device_button.height > 0 and self.device_button.y < self.height:
            self.device_button.draw(self.screen)
            
        if self.generate_button.y + self.generate_button.height > 0 and self.generate_button.y < self.height:
            self.generate_button.draw(self.screen)
            
        if self.settings_button.y + self.settings_button.height > 0 and self.settings_button.y < self.height:
            self.settings_button.draw(self.screen)
            
        if self.info_button.y + self.info_button.height > 0 and self.info_button.y < self.height:
            self.info_button.draw(self.screen)
            
        if self.exit_button.y + self.exit_button.height > 0 and self.exit_button.y < self.height:
            self.exit_button.draw(self.screen)
        
        # Draw footer info with pulsing effect
        footer_text = "Press [ESC] to exit"
        pulse = abs(math.sin(self.animation_time * 2)) * 50 + 150  # 150-200 range
        footer_color = (int(pulse), int(pulse), int(pulse))
        
        footer_surface = self.small_font.render(footer_text, True, footer_color)
        footer_rect = footer_surface.get_rect(center=(self.width // 2, self.height - 20))
        self.screen.blit(footer_surface, footer_rect)
        
        # Draw scrollbar if content is taller than the screen
        if self.max_scroll > 0:
            scrollbar_width = 8
            scrollbar_height = int(self.height * (self.height / self.total_content_height))
            scrollbar_x = self.width - scrollbar_width - 10
            scrollbar_y = int((self.height - scrollbar_height) * (self.scroll_position / self.max_scroll))
            
            # Draw scrollbar track
            pygame.draw.rect(
                self.screen,
                (60, 60, 60),
                (scrollbar_x, 0, scrollbar_width, self.height),
                border_radius=4
            )
            
            # Draw scrollbar handle
            pygame.draw.rect(
                self.screen,
                (150, 150, 150),
                (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height),
                border_radius=4
            )
        
        # Draw device modal on top if active
        if self.device_modal_active:
            self.draw_device_modal()
    
    def update(self, delta_time: float):
        """Update animations and timing"""
        self.animation_time += delta_time
    
    def handle_scroll(self, event: pygame.event.Event) -> bool:
        """Handle scrolling events"""
        if self.device_modal_active:
            return False
            
        if event.type == pygame.MOUSEWHEEL:
            # Mouse wheel scrolling
            self.scroll_position = max(0, min(self.max_scroll, self.scroll_position - event.y * 30))
            return True
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Check if clicking on scrollbar area
                scrollbar_x = self.width - 18
                if event.pos[0] >= scrollbar_x:
                    self.scrolling = True
                    self.last_mouse_y = event.pos[1]
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.scrolling = False
                return False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.scrolling:
                # Calculate scroll amount based on mouse movement
                delta_y = event.pos[1] - self.last_mouse_y
                self.last_mouse_y = event.pos[1]
                
                # Scale the movement based on content/view ratio
                scroll_factor = self.total_content_height / self.height
                self.scroll_position = max(0, min(self.max_scroll, 
                                                 self.scroll_position + delta_y * scroll_factor))
                return True
                
        return False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if event was handled
        """
        # Handle device modal events if it's active
        if self.device_modal_active:
            if self.device_modal_close_button.handle_event(event):
                return True
                
            # Close modal on escape key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.close_device_modal()
                return True
                
            # Close modal if clicking outside the modal
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.device_modal_rect.collidepoint(event.pos):
                    self.close_device_modal()
                    return True
                    
            return False
        
        # Handle scrolling
        if self.handle_scroll(event):
            return True
        
        # Handle clicking on device info to show details
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self, 'device_info_rect') and self.device_info_rect.collidepoint(event.pos):
                if self.device_found:
                    self.show_device_modal()
                    return True
        
        # Handle button events - use adjusted y-coordinates for hit testing
        # We need to adjust event position to account for scrolling
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            # Create a modified event with adjusted position for button hit testing
            adjusted_event = pygame.event.Event(
                event.type,
                {**event.dict, 'pos': (event.pos[0], event.pos[1] + self.scroll_position)}
            )
            
            if self.device_button.handle_event(adjusted_event):
                return True
            if self.generate_button.handle_event(adjusted_event):
                return True
            if self.settings_button.handle_event(adjusted_event):
                return True
            if self.info_button.handle_event(adjusted_event):
                return True
            if self.exit_button.handle_event(adjusted_event):
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