"""
Settings Screen for the CMYK Retro Solana Vanity Address Generator
Allows configuring application preferences with a scrollable interface
"""

import os
import pygame
import logging
import math
import random
from typing import Callable, Dict, Any, List, Tuple

from ui.components.retro_button import RetroButton
from ui.components.retro_input import RetroInput
from ui.components.retro_slider import RetroSlider
from utils.config_manager import ConfigManager
from utils.ascii_art import CMYKColors

class SettingsScreen:
    """
    Screen for configuring application settings
    with a scrollable layout to avoid overlapping containers
    """
    
    def __init__(
        self, 
        screen: pygame.Surface, 
        on_back: Callable[[], None]
    ):
        """
        Initialize the settings screen
        
        Args:
            screen: Pygame surface to render on
            on_back: Callback when returning to previous screen
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.on_back = on_back
        
        # Configuration management
        self.config = ConfigManager()
        
        # Animation state
        self.animation_time = 0
        self.particles = []
        
        # UI state
        self.status_message = ""
        self.status_color = (0, 255, 0)
        self.status_timer = 0
        self.show_advanced = False
        
        # Scrolling state
        self.scroll_position = 0
        self.viewport_height = 1000  # Virtual height of content area
        self.scrollbar_dragging = False
        self.last_mouse_y = 0
        
        # Load fonts
        self.load_fonts()
        
        # Create scroll surface for content
        self.create_scroll_surface()
        
        # Create UI components
        self.create_ui_components()
        
        # Initialize the particles
        self.create_particles(20)
    
    def load_fonts(self):
        """Load fonts for the screen"""
        try:
            # Get the project root directory
            PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            
            pixel_font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "pixel_font.ttf")
            if os.path.exists(pixel_font_path):
                self.title_font = pygame.font.Font(pixel_font_path, 32)
                self.font = pygame.font.Font(pixel_font_path, 20)
                self.small_font = pygame.font.Font(pixel_font_path, 16)
                self.tiny_font = pygame.font.Font(pixel_font_path, 12)
            else:
                self.title_font = pygame.font.SysFont("monospace", 32)
                self.font = pygame.font.SysFont("monospace", 20)
                self.small_font = pygame.font.SysFont("monospace", 16)
                self.tiny_font = pygame.font.SysFont("monospace", 12)
        except Exception as e:
            logging.warning(f"Font loading failed: {e}")
            self.title_font = pygame.font.SysFont("monospace", 32)
            self.font = pygame.font.SysFont("monospace", 20)
            self.small_font = pygame.font.SysFont("monospace", 16)
            self.tiny_font = pygame.font.SysFont("monospace", 12)
    
    def create_scroll_surface(self):
        """Create the scrollable surface for content"""
        # Fixed areas
        self.title_rect = pygame.Rect(0, 0, self.width, 60)
        self.footer_rect = pygame.Rect(0, self.height - 80, self.width, 80)
        
        # Content area (between title and footer)
        self.content_rect = pygame.Rect(
            0, 
            self.title_rect.height, 
            self.width, 
            self.height - self.title_rect.height - self.footer_rect.height
        )
        
        # Create the scrollable surface
        self.scroll_surface = pygame.Surface((self.width, self.viewport_height))
        
        # Calculate max scroll
        self.max_scroll = max(0, self.viewport_height - self.content_rect.height)
        
        # Scrollbar rect
        scrollbar_width = 10
        self.scrollbar_bg_rect = pygame.Rect(
            self.width - scrollbar_width - 5,
            self.content_rect.y,
            scrollbar_width,
            self.content_rect.height
        )
        
        # Scrollbar handle (will be updated during drawing)
        self.scrollbar_handle_rect = pygame.Rect(0, 0, scrollbar_width, 30)
    
    def create_ui_components(self):
        """Create and initialize UI components for the settings screen"""
        # Default margins
        side_margin = 30
        section_margin = 20
        
        # Calculate usable width
        usable_width = self.width - (side_margin * 2)
        
        # Y position tracker for vertical layout
        current_y = 30  # Start with some padding at top of scroll surface
        
        # 1. THEME SECTION
        # ----------------------------
        # Section heading
        self.theme_heading_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            30
        )
        current_y += self.theme_heading_rect.height + 20
        
        # Theme buttons
        theme_names = ["cyan", "magenta", "yellow", "white", "cmyk"]
        theme_labels = ["Cyan", "Magenta", "Yellow", "White", "CMYK"]
        theme_button_width = 120
        theme_button_height = 40
        theme_spacing = 20
        
        self.theme_buttons = []
        
        # Calculate the total width of all theme buttons
        total_theme_width = (theme_button_width * len(theme_names)) + (theme_spacing * (len(theme_names) - 1))
        
        # Center buttons horizontally
        theme_start_x = side_margin + (usable_width - total_theme_width) // 2
        
        for i, (theme_name, theme_label) in enumerate(zip(theme_names, theme_labels)):
            button_x = theme_start_x + (theme_button_width + theme_spacing) * i
            button = RetroButton(
                button_x, current_y,
                theme_button_width, theme_button_height,
                theme_label,
                lambda t=theme_name: self.set_theme(t),
                color_scheme=theme_name
            )
            self.theme_buttons.append(button)
        
        current_y += theme_button_height + 20
        
        # Theme preview section
        self.theme_preview_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            40
        )
        current_y += self.theme_preview_rect.height + 10
        
        # Define the theme section rect for drawing
        self.theme_section_rect = pygame.Rect(
            side_margin - 10,  # Extra padding for border
            self.theme_heading_rect.y - 10,
            usable_width + 20,  # Extra padding for border
            current_y - self.theme_heading_rect.y  # Total height of section
        )
        
        # Add margin between sections
        current_y += section_margin
        
        # 2. GENERAL SETTINGS SECTION
        # ----------------------------
        # Section heading
        self.general_heading_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            30
        )
        current_y += self.general_heading_rect.height + 20
        
        # Output directory input
        input_height = 40
        self.output_dir_input = RetroInput(
            side_margin, 
            current_y,
            usable_width, 
            input_height,
            "Output Directory",
            self.config.get_output_dir(),
            color_scheme="cyan"
        )
        current_y += input_height + 30  # Space for help text
        
        # Sound toggle button
        sound_enabled = self.config.get('sound_enabled', True)
        self.sound_button = RetroButton(
            side_margin, 
            current_y,
            usable_width, 
            input_height,
            f"Sound Effects: {'ON' if sound_enabled else 'OFF'}",
            self.toggle_sound,
            color_scheme="yellow"
        )
        current_y += input_height + 30  # Space for help text
        
        # Define the general section rect for drawing
        self.general_section_rect = pygame.Rect(
            side_margin - 10,  # Extra padding for border
            self.general_heading_rect.y - 10,
            usable_width + 20,  # Extra padding for border
            current_y - self.general_heading_rect.y  # Total height of section
        )
        
        # Add margin between sections
        current_y += section_margin
        
        # 3. ADVANCED SETTINGS SECTION
        # ----------------------------
        # Section heading
        self.advanced_heading_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            30
        )
        current_y += self.advanced_heading_rect.height + 10
        
        # Toggle button for advanced settings
        toggle_width = 200
        toggle_height = 40
        toggle_x = side_margin + (usable_width - toggle_width) // 2
        
        self.advanced_toggle = RetroButton(
            toggle_x,
            current_y,
            toggle_width, 
            toggle_height,
            "Show Advanced Settings" if not self.show_advanced else "Hide Advanced Settings",
            self.toggle_advanced,
            color_scheme="magenta"
        )
        current_y += toggle_height + 20
        
        # Advanced settings content area - initially hidden
        self.advanced_content_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            200  # Fixed height
        )
        
        # Default complexity slider
        self.default_complexity_slider = RetroSlider(
            side_margin, 
            current_y,
            usable_width, 
            input_height,
            "Default Iteration Complexity",
            min_value=16,
            max_value=28,
            initial_value=int(self.config.get('iteration_bits', 24)),
            color_scheme="cyan"
        )
        current_y += input_height + 30  # Space for help text
        
        # Automatically select device option
        self.auto_device_button = RetroButton(
            side_margin, 
            current_y,
            usable_width, 
            input_height,
            f"Auto Select Device: {'YES' if not self.config.get('select_device', False) else 'NO'}",
            self.toggle_auto_device,
            color_scheme="magenta"
        )
        current_y += input_height + 30  # Space for help text
        
        # Reset all settings button
        self.reset_button = RetroButton(
            side_margin, 
            current_y,
            usable_width, 
            input_height,
            "Reset All Settings",
            self.reset_settings,
            color_scheme="white"
        )
        current_y += input_height + 10
        
        # Define the advanced section rect for drawing
        self.advanced_section_rect = pygame.Rect(
            side_margin - 10,  # Extra padding for border
            self.advanced_heading_rect.y - 10,
            usable_width + 20,  # Extra padding for border
            current_y - self.advanced_heading_rect.y  # Total height of section
        )
        
        # Update viewport height to match content
        self.viewport_height = max(current_y + 30, self.content_rect.height)  # Add bottom padding
        self.max_scroll = max(0, self.viewport_height - self.content_rect.height)
        
        # 4. BOTTOM BUTTONS (fixed, not on scroll surface)
        # ----------------------------
        # Buttons in footer
        button_width = 180
        button_height = 50
        button_spacing = 30
        
        # The total width needed for both buttons plus spacing
        total_buttons_width = (button_width * 2) + button_spacing
        
        # Calculate starting X to center the buttons in the footer
        button_start_x = (self.width - total_buttons_width) // 2
        button_y = self.height - 65  # Centered in footer
        
        self.save_button = RetroButton(
            button_start_x,
            button_y,
            button_width, 
            button_height, 
            "Save Settings", 
            self.save_settings, 
            color_scheme="cyan"
        )
        
        self.back_button = RetroButton(
            button_start_x + button_width + button_spacing,
            button_y,
            button_width, 
            button_height, 
            "Back", 
            self.on_back, 
            color_scheme="white"
        )
    
    def toggle_advanced(self):
        """Toggle advanced settings visibility"""
        self.show_advanced = not self.show_advanced
        self.advanced_toggle.set_text("Hide Advanced Settings" if self.show_advanced else "Show Advanced Settings")
    
    def toggle_sound(self):
        """Toggle sound enabled/disabled"""
        sound_enabled = self.config.toggle_sound()
        self.sound_button.set_text(f"Sound Effects: {'ON' if sound_enabled else 'OFF'}")
        self.show_status("Sound settings updated", (0, 255, 255))
    
    def toggle_auto_device(self):
        """Toggle automatic device selection"""
        current = self.config.get('select_device', False)
        self.config.set('select_device', not current)
        self.auto_device_button.set_text(f"Auto Select Device: {'YES' if not self.config.get('select_device', False) else 'NO'}")
        self.show_status("Device selection mode updated", (255, 0, 255))
    
    def set_theme(self, theme_name: str):
        """
        Set the application theme
        
        Args:
            theme_name: Name of the theme to set
        """
        self.config.set_theme(theme_name)
        self.show_status(f"Theme changed to {theme_name.capitalize()}", (0, 255, 255))
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        # Confirm before resetting
        self.config.reset()
        
        # Update UI to reflect defaults
        self.output_dir_input.set_text(self.config.get_output_dir())
        
        sound_enabled = self.config.get('sound_enabled', True)
        self.sound_button.set_text(f"Sound Effects: {'ON' if sound_enabled else 'OFF'}")
        
        self.default_complexity_slider.set_value(int(self.config.get('iteration_bits', 24)))
        
        self.auto_device_button.set_text(f"Auto Select Device: {'YES' if not self.config.get('select_device', False) else 'NO'}")
        
        self.show_status("All settings reset to defaults", (255, 255, 0))
    
    def save_settings(self):
        """Save all current settings"""
        # Save output directory
        output_dir = self.output_dir_input.get_text().strip()
        if output_dir:
            self.config.set_output_dir(output_dir)
        
        # Save default complexity
        iteration_bits = self.default_complexity_slider.get_value()
        self.config.set('iteration_bits', iteration_bits)
        
        # Save config file
        self.config.save_config()
        
        # Show confirmation
        self.show_status("Settings saved successfully!", (0, 255, 0))
    
    def show_status(self, message: str, color: tuple):
        """
        Show a status message
        
        Args:
            message: Message to display
            color: RGB color tuple for the message
        """
        self.status_message = message
        self.status_color = color
        self.status_timer = 3.0  # Show for 3 seconds
    
    def create_particles(self, count=5):
        """Create particles for animation effects"""
        for _ in range(count):
            particle = {
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.uniform(1, 3),
                'speed': random.uniform(10, 30),
                'angle': random.uniform(0, math.pi * 2),
                'color': random.choice([
                    (0, 255, 255, 128),  # Cyan
                    (255, 0, 255, 128),  # Magenta
                    (255, 255, 0, 128),  # Yellow
                    (220, 220, 220, 128)  # Light Gray
                ])
            }
            self.particles.append(particle)
    
    def update_particles(self, delta_time):
        """Update particle positions"""
        for particle in self.particles[:]:
            # Move particle
            particle['x'] += math.cos(particle['angle']) * particle['speed'] * delta_time
            particle['y'] += math.sin(particle['angle']) * particle['speed'] * delta_time
            
            # Remove if out of bounds
            if (particle['x'] < -10 or particle['x'] > self.width + 10 or
                particle['y'] < -10 or particle['y'] > self.height + 10):
                self.particles.remove(particle)
    
    def draw_title_section(self):
        """Draw the title section of the screen (fixed at top)"""
        # Title background
        pygame.draw.rect(
            self.screen,
            (30, 30, 30),
            self.title_rect
        )
        
        # Draw pulsing CMYK border below title
        border_height = 3
        segment_width = self.width // 4
        
        # Shift the colors based on time for animated effect
        shift = int(self.animation_time * 20) % segment_width
        
        for i in range(4):
            color_index = (i + int(self.animation_time)) % 4
            colors = [(0, 255, 255), (255, 0, 255), (255, 255, 0), (180, 180, 180)]
            color = colors[color_index]
            
            segment_rect = pygame.Rect(
                ((i * segment_width) - shift) % self.width,
                self.title_rect.bottom,
                segment_width,
                border_height
            )
            pygame.draw.rect(self.screen, color, segment_rect)
        
        # Title text
        title_text = "Settings"
        title_surface = self.title_font.render(title_text, True, (220, 220, 220))
        title_rect = title_surface.get_rect(center=(self.width // 2, self.title_rect.height // 2))
        self.screen.blit(title_surface, title_rect)
    
    def draw_footer_section(self):
        """Draw the footer section with buttons (fixed at bottom)"""
        # Footer background
        pygame.draw.rect(
            self.screen,
            (30, 30, 30),
            self.footer_rect
        )
        
        # Draw animated border
        border_width = 2
        rect = self.footer_rect.copy()
        
        # Create a surface for the border
        border_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Draw the gradient border
        colors = [
            (0, 255, 255),      # Cyan
            (255, 0, 255),      # Magenta
            (255, 255, 0),      # Yellow
            (180, 180, 180)     # Gray
        ]
        
        # Number of segments in the border
        segments = 40
        segment_length = (2 * rect.width + 2 * rect.height) / segments
        
        # Animate the border colors
        color_shift = int(self.animation_time * 10) % len(colors)
        
        for i in range(segments):
            # Get the color for this segment with shifting
            color_index = (i + color_shift) % len(colors)
            color = colors[color_index]
            
            # Calculate start and end positions
            start_pos = i * segment_length
            end_pos = min((i + 1) * segment_length, 2 * rect.width + 2 * rect.height)
            
            # Convert positions to coordinates
            if start_pos < rect.width:
                # Top edge
                start_x = start_pos
                start_y = 0
            elif start_pos < rect.width + rect.height:
                # Right edge
                start_x = rect.width
                start_y = start_pos - rect.width
            elif start_pos < 2 * rect.width + rect.height:
                # Bottom edge
                start_x = rect.width - (start_pos - rect.width - rect.height)
                start_y = rect.height
            else:
                # Left edge
                start_x = 0
                start_y = rect.height - (start_pos - 2 * rect.width - rect.height)
                
            if end_pos < rect.width:
                # Top edge
                end_x = end_pos
                end_y = 0
            elif end_pos < rect.width + rect.height:
                # Right edge
                end_x = rect.width
                end_y = end_pos - rect.width
            elif end_pos < 2 * rect.width + rect.height:
                # Bottom edge
                end_x = rect.width - (end_pos - rect.width - rect.height)
                end_y = rect.height
            else:
                # Left edge
                end_x = 0
                end_y = rect.height - (end_pos - 2 * rect.width - rect.height)
            
            # Draw segment
            pygame.draw.line(
                border_surface,
                color,
                (int(start_x), int(start_y)),
                (int(end_x), int(end_y)),
                border_width
            )
        
        # Blit the border to the screen
        self.screen.blit(border_surface, rect)
        
        # Draw buttons
        self.save_button.draw(self.screen)
        self.back_button.draw(self.screen)
    
    def draw_scrollbar(self):
        """Draw the scrollbar for the content area"""
        # Only draw scrollbar if content is scrollable
        if self.max_scroll > 0:
            # Draw scrollbar background
            pygame.draw.rect(
                self.screen, 
                (60, 60, 60), 
                self.scrollbar_bg_rect,
                border_radius=5
            )
            
            # Calculate scrollbar handle size and position
            handle_height = max(30, int(self.content_rect.height * (self.content_rect.height / self.viewport_height)))
            handle_y = self.content_rect.y + int(self.scroll_position * (self.content_rect.height - handle_height) / self.max_scroll)
            
            # Update handle rect
            self.scrollbar_handle_rect = pygame.Rect(
                self.scrollbar_bg_rect.x,
                handle_y,
                self.scrollbar_bg_rect.width,
                handle_height
            )
            
            # Draw scrollbar handle
            handle_color = (0, 255, 255) if self.scrollbar_dragging else (120, 120, 120)
            pygame.draw.rect(
                self.screen, 
                handle_color, 
                self.scrollbar_handle_rect,
                border_radius=5
            )
    
    def draw_theme_section(self):
        """Draw the theme selection section on the scroll surface"""
        # Section border
        pygame.draw.rect(
            self.scroll_surface,
            (60, 60, 60),
            self.theme_section_rect,
            2,
            border_radius=5
        )
        
        # Section heading
        heading_text = "Theme Selection"
        heading_surface = self.font.render(heading_text, True, (0, 255, 255))
        heading_rect = heading_surface.get_rect(midleft=(self.theme_heading_rect.x, self.theme_heading_rect.centery))
        self.scroll_surface.blit(heading_surface, heading_rect)
        
        # Draw theme buttons
        for button in self.theme_buttons:
            button.draw(self.scroll_surface)
        
        # Draw current theme indicator
        current_theme = self.config.get_theme()
        if current_theme in ["cyan", "magenta", "yellow", "white", "cmyk"]:
            current_theme_index = ["cyan", "magenta", "yellow", "white", "cmyk"].index(current_theme)
            current_button = self.theme_buttons[current_theme_index]
            
            # Draw indicator arrow above selected theme
            indicator_text = "▲"
            indicator_color = {
                "cyan": (0, 255, 255),
                "magenta": (255, 0, 255),
                "yellow": (255, 255, 0),
                "white": (220, 220, 220),
                "cmyk": (180, 180, 180)
            }.get(current_theme, (220, 220, 220))
            
            indicator_surface = self.font.render(indicator_text, True, indicator_color)
            indicator_rect = indicator_surface.get_rect(
                midtop=(current_button.x + current_button.width // 2, current_button.y - 15)
            )
            self.scroll_surface.blit(indicator_surface, indicator_rect)
        
        # Draw theme preview
        preview_text = "CMYK Retro Lo-Fi Aesthetic"
        
        # Use the current theme's colors
        preview_color = {
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "yellow": (255, 255, 0),
            "white": (220, 220, 220),
            "cmyk": (180, 180, 180)
        }.get(current_theme, (220, 220, 220))
        
        preview_surface = self.font.render(preview_text, True, preview_color)
        preview_rect = preview_surface.get_rect(center=(
            self.theme_preview_rect.centerx,
            self.theme_preview_rect.centery
        ))
        self.scroll_surface.blit(preview_surface, preview_rect)
    
    def draw_general_section(self):
        """Draw the general settings section on the scroll surface"""
        # Section border
        pygame.draw.rect(
            self.scroll_surface,
            (60, 60, 60),
            self.general_section_rect,
            2,
            border_radius=5
        )
        
        # Section heading
        heading_text = "General Settings"
        heading_surface = self.font.render(heading_text, True, (255, 0, 255))
        heading_rect = heading_surface.get_rect(midleft=(self.general_heading_rect.x, self.general_heading_rect.centery))
        self.scroll_surface.blit(heading_surface, heading_rect)
        
        # Draw outputs and buttons
        self.output_dir_input.draw(self.scroll_surface)
        
        # Draw help text for output directory
        help_text = "Directory where generated addresses will be saved"
        help_surface = self.small_font.render(help_text, True, (180, 180, 180))
        help_y = self.output_dir_input.y + self.output_dir_input.height + 5
        self.scroll_surface.blit(help_surface, (self.output_dir_input.x + 10, help_y))
        
        # Draw sound button
        self.sound_button.draw(self.scroll_surface)
        
        # Draw help text for sound toggle
        help_text = "Toggle sound effects on/off for the application"
        help_surface = self.small_font.render(help_text, True, (180, 180, 180))
        help_y = self.sound_button.y + self.sound_button.height + 5
        self.scroll_surface.blit(help_surface, (self.sound_button.x + 10, help_y))
    
    def draw_advanced_section(self):
        """Draw the advanced settings section on the scroll surface"""
        # Section border
        pygame.draw.rect(
            self.scroll_surface,
            (60, 60, 60),
            self.advanced_section_rect,
            2,
            border_radius=5
        )
        
        # Section heading
        heading_text = "Advanced Settings"
        heading_surface = self.font.render(heading_text, True, (255, 255, 0))
        heading_rect = heading_surface.get_rect(midleft=(self.advanced_heading_rect.x, self.advanced_heading_rect.centery))
        self.scroll_surface.blit(heading_surface, heading_rect)
        
        # Draw toggle button
        self.advanced_toggle.draw(self.scroll_surface)
        
        # Draw advanced settings if expanded
        if self.show_advanced:
            # Complexity slider
            self.default_complexity_slider.draw(self.scroll_surface)
            
            # Add help text
            help_text = "Controls generation speed and GPU memory usage"
            help_surface = self.small_font.render(help_text, True, (180, 180, 180))
            help_y = self.default_complexity_slider.y + self.default_complexity_slider.height + 5
            self.scroll_surface.blit(help_surface, (self.default_complexity_slider.x + 10, help_y))
            
            # Device selection
            self.auto_device_button.draw(self.scroll_surface)
            
            # Add help text
            help_text = "Choose whether to auto-select GPU or manually select device"
            help_surface = self.small_font.render(help_text, True, (180, 180, 180))
            help_y = self.auto_device_button.y + self.auto_device_button.height + 5
            self.scroll_surface.blit(help_surface, (self.auto_device_button.x + 10, help_y))
            
            # Reset button
            self.reset_button.draw(self.scroll_surface)
            
            # Add help text
            help_text = "Reset all settings to default values"
            help_surface = self.small_font.render(help_text, True, (180, 180, 180))
            help_y = self.reset_button.y + self.reset_button.height + 5
            self.scroll_surface.blit(help_surface, (self.reset_button.x + 10, help_y))
        else:
            # Show a message to expand
            hint_text = "Click 'Show Advanced Settings' to view more options"
            hint_surface = self.small_font.render(hint_text, True, (180, 180, 180))
            hint_rect = hint_surface.get_rect(
                center=(self.advanced_content_rect.centerx, self.advanced_content_rect.y + 40)
            )
            self.scroll_surface.blit(hint_surface, hint_rect)
    
    def draw_particles(self):
        """Draw particle effects"""
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
    
    def draw_status_message(self):
        """Draw status message if active"""
        if self.status_message and self.status_timer > 0:
            # Create a semi-transparent surface
            message_surface = pygame.Surface((self.width, 40), pygame.SRCALPHA)
            message_surface.fill((0, 0, 0, 180))
            
            # Render the text
            message_text = self.font.render(self.status_message, True, self.status_color)
            text_rect = message_text.get_rect(center=(message_surface.get_width() // 2, message_surface.get_height() // 2))
            message_surface.blit(message_text, text_rect)
            
            # Position at the bottom of the screen
            self.screen.blit(message_surface, (0, self.height - 40))
    
    def draw(self):
        """Draw the settings screen components"""
        # Clear the main screen with a dark background
        self.screen.fill((40, 40, 40))
        
        # Draw particles first (background layer)
        self.draw_particles()
        
        # Clear the scroll surface
        self.scroll_surface.fill((40, 40, 40))
        
        # Draw scrollable content onto scroll surface
        self.draw_theme_section()
        self.draw_general_section()
        self.draw_advanced_section()
        
        # Blit the visible portion of the scroll surface to the screen
        # (adjusted for scroll position)
        self.screen.blit(
            self.scroll_surface,
            (0, self.content_rect.y),  # Position at content area
            (0, self.scroll_position, self.width, self.content_rect.height)  # Visible portion
        )
        
        # Draw fixed elements
        self.draw_title_section()  # Fixed at top
        self.draw_footer_section()  # Fixed at bottom
        
        # Draw scrollbar
        self.draw_scrollbar()
        
        # Draw status message
        self.draw_status_message()
    
    def update(self, delta_time: float):
        """
        Update screen state
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Update animation time
        self.animation_time += delta_time
        
        # Update status message timer
        if self.status_timer > 0:
            self.status_timer -= delta_time
        
        # Update UI components that need animation
        if self.show_advanced:
            self.default_complexity_slider.update(delta_time)
        
        # Update particles and occasionally create new ones
        self.update_particles(delta_time)
        if random.random() < delta_time * 2:  # Average 2 particles per second
            self.create_particles(1)
    
    def handle_scrolling(self, event):
        """Handle scrolling events"""
        if event.type == pygame.MOUSEWHEEL:
            # Scroll using mouse wheel
            self.scroll_position = max(0, min(self.max_scroll, 
                                             self.scroll_position - event.y * 30))
            return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle scrollbar dragging
            if event.button == 1 and self.scrollbar_handle_rect.collidepoint(event.pos):
                self.scrollbar_dragging = True
                self.last_mouse_y = event.pos[1]
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop scrollbar dragging
            if event.button == 1 and self.scrollbar_dragging:
                self.scrollbar_dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            # Update scroll position during scrollbar dragging
            if self.scrollbar_dragging:
                delta_y = event.pos[1] - self.last_mouse_y
                self.last_mouse_y = event.pos[1]
                
                # Calculate scroll amount based on content/viewport ratio
                scroll_ratio = self.viewport_height / self.content_rect.height
                self.scroll_position = max(0, min(self.max_scroll, 
                                                 self.scroll_position + delta_y * scroll_ratio))
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
        # Handle scrolling (for any event that might affect scrolling)
        if self.handle_scrolling(event):
            return True
        
        # Handle advanced toggle with A key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            self.toggle_advanced()
            return True
        
        # Check if event is in the fixed areas (non-scrollable)
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
            # Check if in footer area (buttons)
            if self.footer_rect.collidepoint(mouse_pos):
                if self.save_button.handle_event(event):
                    return True
                if self.back_button.handle_event(event):
                    return True
                return False
            
            # Check if in content area (scrollable)
            elif self.content_rect.collidepoint(mouse_pos):
                # Adjust mouse position for scroll
                scroll_adjusted_event = pygame.event.Event(
                    event.type,
                    {**event.dict, 'pos': (mouse_pos[0], mouse_pos[1] - self.content_rect.y + self.scroll_position)}
                )
                adjusted_pos = scroll_adjusted_event.pos
                
                # Handle input events in scrollable area
                handled = False
                
                # Theme section
                if self.theme_section_rect.collidepoint(adjusted_pos):
                    for button in self.theme_buttons:
                        if button.handle_event(scroll_adjusted_event):
                            handled = True
                            break
                
                # General section
                if self.general_section_rect.collidepoint(adjusted_pos):
                    if self.output_dir_input.handle_event(scroll_adjusted_event):
                        handled = True
                    if self.sound_button.handle_event(scroll_adjusted_event):
                        handled = True
                
                # Advanced section
                if self.advanced_section_rect.collidepoint(adjusted_pos):
                    if self.advanced_toggle.handle_event(scroll_adjusted_event):
                        handled = True
                    
                    if self.show_advanced:
                        if self.default_complexity_slider.handle_event(scroll_adjusted_event):
                            handled = True
                        if self.auto_device_button.handle_event(scroll_adjusted_event):
                            handled = True
                        if self.reset_button.handle_event(scroll_adjusted_event):
                            handled = True
                
                return handled
        
        return False