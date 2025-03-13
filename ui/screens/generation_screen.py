"""
Generation Screen for the CMYK Retro Solana Vanity Address Generator
Handles the address generation process and UI with a scrollable layout
"""

import os
import pygame
import logging
import threading
import time
import math
import random
from typing import Callable, Dict, Any, Tuple

from ui.components.retro_input import RetroInput
from ui.components.retro_button import RetroButton
from ui.components.retro_progress import RetroProgress
from ui.components.retro_slider import RetroSlider

from core.vangen import search_vanity_addresses
from utils.config_manager import ConfigManager
from utils.output_formatter import print_progress, export_addresses_to_file
from utils.ascii_art import CMYKColors

class GenerationScreen:
    """
    Screen for configuring and executing vanity address generation
    with a scrollable layout to avoid overlapping containers
    """
    
    def __init__(
        self, 
        screen: pygame.Surface, 
        on_back: Callable[[], None], 
        on_complete: Callable[[Dict[str, Any]], None]
    ):
        """
        Initialize the generation screen
        
        Args:
            screen: Pygame surface to render on
            on_back: Callback when returning to previous screen
            on_complete: Callback when generation is complete
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.on_back = on_back
        self.on_complete = on_complete
        
        # Configuration management
        self.config = ConfigManager()
        
        # Generation state
        self.generating = False
        self.generation_progress = 0.0
        self.generation_result = None
        self.generation_error = None
        self.generation_thread = None
        self.show_help = False
        
        # Animation state
        self.animation_time = 0
        self.particles = []
        
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
        
        # Create example addresses
        self.example_addresses = [
            "7CYNayUWiXQZWJsMA1WkZ9hwC6N4D1yQjoMbnBtPYcLu",
            "CooLisQKNMcL2QFBPqEZFP2oPBwq5x7YeTXbsWRKXWX",
            "32cMhC5vK3YJKKi9QwMCpG7NrMFVHsMyWvbF4KE5GX7Z",
            "E8kZAzcgpjRFkJrMQYZSmCf9T6ELSA22yYXNGwP1Vann"
        ]
    
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
        """Create and initialize UI components for generation screen"""
        # Default margins
        side_margin = 30
        section_margin = 20
        
        # Calculate usable width
        usable_width = self.width - (side_margin * 2)
        
        # Y position tracker for vertical layout
        current_y = 30  # Start with some padding at top of scroll surface
        
        # 1. ADDRESS PARAMETERS SECTION
        # ----------------------------
        # Section heading
        self.params_heading_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            30
        )
        current_y += self.params_heading_rect.height + 10
        
        # Prefix input
        input_height = 40
        self.prefix_input = RetroInput(
            side_margin, 
            current_y, 
            usable_width, 
            input_height, 
            "Enter Address Prefix (optional)", 
            self.config.get('prefix', ''),
            color_scheme="cyan"
        )
        current_y += input_height + 30  # Add space for help text
        
        # Suffix input
        self.suffix_input = RetroInput(
            side_margin, 
            current_y, 
            usable_width, 
            input_height, 
            "Enter Address Suffix (optional)", 
            self.config.get('suffix', ''),
            color_scheme="magenta"
        )
        current_y += input_height + 30  # Add space for help text
        
        # Count slider
        self.count_slider = RetroSlider(
            side_margin, 
            current_y, 
            usable_width, 
            input_height, 
            "Number of Addresses", 
            min_value=1, 
            max_value=50, 
            initial_value=int(self.config.get('count', 1)),
            color_scheme="yellow"
        )
        current_y += input_height + 30  # Add space for help text
        
        # Iteration bits slider
        self.iteration_slider = RetroSlider(
            side_margin, 
            current_y, 
            usable_width, 
            input_height, 
            "Iteration Complexity", 
            min_value=16, 
            max_value=28, 
            initial_value=int(self.config.get('iteration_bits', 24)),
            color_scheme="magenta"
        )
        current_y += input_height + 30  # Add space for help text
        
        # Define the parameters section rect for drawing
        self.params_section_rect = pygame.Rect(
            side_margin - 10,  # Extra padding for border
            self.params_heading_rect.y - 10,
            usable_width + 20,  # Extra padding for border
            current_y - self.params_heading_rect.y + 10  # Extra padding for border
        )
        
        # Add margin between sections
        current_y += section_margin
        
        # 2. PREVIEW SECTION
        # ----------------------------
        # Section heading
        self.preview_heading_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            30
        )
        current_y += self.preview_heading_rect.height + 10
        
        # Example addresses section
        self.examples_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            120
        )
        current_y += self.examples_rect.height + 10
        
        # Define the preview section rect for drawing
        self.preview_section_rect = pygame.Rect(
            side_margin - 10,  # Extra padding for border
            self.preview_heading_rect.y - 10,
            usable_width + 20,  # Extra padding for border
            current_y - self.preview_heading_rect.y + 10  # Extra padding for border
        )
        
        # Add margin between sections
        current_y += section_margin
        
        # 3. INFORMATION SECTION
        # ----------------------------
        # Section heading
        self.info_heading_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            30
        )
        current_y += self.info_heading_rect.height + 10
        
        # Help content area
        self.help_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            200  # Fixed height for help content
        )
        current_y += self.help_rect.height + 10
        
        # Define the info section rect for drawing
        self.info_section_rect = pygame.Rect(
            side_margin - 10,  # Extra padding for border
            self.info_heading_rect.y - 10,
            usable_width + 20,  # Extra padding for border
            current_y - self.info_heading_rect.y + 10  # Extra padding for border
        )
        
        # Help toggle button
        help_button_width = 120
        help_button_height = 30
        self.help_button = RetroButton(
            self.info_heading_rect.right - help_button_width,
            self.info_heading_rect.y,
            help_button_width,
            help_button_height,
            "Show Help",
            self.toggle_help,
            color_scheme="cyan"
        )
        
        # Update viewport height to match content
        self.viewport_height = max(current_y + 30, self.content_rect.height)  # Add bottom padding
        self.max_scroll = max(0, self.viewport_height - self.content_rect.height)
        
        # 4. BOTTOM BUTTONS (fixed, not on scroll surface)
        # ----------------------------
        # Buttons
        button_width = 180
        button_height = 50
        button_spacing = 30
        
        # The total width needed for both buttons plus spacing
        total_buttons_width = (button_width * 2) + button_spacing
        
        # Calculate starting X to center the buttons in the footer
        button_start_x = (self.width - total_buttons_width) // 2
        button_y = self.height - 65  # Centered in footer
        
        self.generate_button = RetroButton(
            button_start_x,
            button_y,
            button_width, 
            button_height, 
            "Generate", 
            self.start_generation, 
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
        
        # Progress bar (used during generation, appears in footer)
        self.progress_bar = RetroProgress(
            (self.width - 400) // 2,  # Centered
            button_y + (button_height - 30) // 2,  # Centered vertically with buttons
            400,  # Fixed width
            30, 
            color_scheme="cmyk"
        )
    
    def toggle_help(self):
        """Toggle the help information visibility"""
        self.show_help = not self.show_help
        self.help_button.set_text("Hide Help" if self.show_help else "Show Help")
    
    def create_particles(self, count=10):
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
        title_text = "Generate Vanity Address"
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
        
        # Draw buttons or progress bar based on state
        if self.generating:
            # Draw progress bar
            self.progress_bar.draw(self.screen)
            
            # Draw cancel button (reuse back button)
            self.back_button.set_text("Cancel")
            self.back_button.draw(self.screen)
        else:
            # Draw normal buttons
            self.back_button.set_text("Back")
            self.generate_button.draw(self.screen)
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
    
    def draw_params_section(self):
        """Draw the parameters section on the scroll surface"""
        # Section border
        pygame.draw.rect(
            self.scroll_surface,
            (60, 60, 60),
            self.params_section_rect,
            2,
            border_radius=5
        )
        
        # Section heading
        heading_text = "Address Parameters"
        heading_surface = self.font.render(heading_text, True, (0, 255, 255))
        heading_rect = heading_surface.get_rect(midleft=(self.params_heading_rect.x, self.params_heading_rect.centery))
        self.scroll_surface.blit(heading_surface, heading_rect)
        
        # Draw inputs
        self.prefix_input.x = self.prefix_input.x  # On scroll surface, no adjustment needed
        self.prefix_input.y = self.prefix_input.y  # On scroll surface, no adjustment needed
        self.prefix_input.draw(self.scroll_surface)
        
        self.suffix_input.x = self.suffix_input.x  # On scroll surface, no adjustment needed
        self.suffix_input.y = self.suffix_input.y  # On scroll surface, no adjustment needed
        self.suffix_input.draw(self.scroll_surface)
        
        self.count_slider.x = self.count_slider.x  # On scroll surface, no adjustment needed
        self.count_slider.y = self.count_slider.y  # On scroll surface, no adjustment needed
        self.count_slider.draw(self.scroll_surface)
        
        self.iteration_slider.x = self.iteration_slider.x  # On scroll surface, no adjustment needed
        self.iteration_slider.y = self.iteration_slider.y  # On scroll surface, no adjustment needed
        self.iteration_slider.draw(self.scroll_surface)
        
        # Draw help text for parameters if help is enabled
        if self.show_help:
            # Prefix help
            help_y = self.prefix_input.y + self.prefix_input.height + 5
            help_text = "Base58 characters to appear at the START of address"
            help_surface = self.tiny_font.render(help_text, True, (180, 180, 180))
            self.scroll_surface.blit(help_surface, (self.prefix_input.x + 10, help_y))
            
            # Suffix help
            help_y = self.suffix_input.y + self.suffix_input.height + 5
            help_text = "Base58 characters to appear at the END of address"
            help_surface = self.tiny_font.render(help_text, True, (180, 180, 180))
            self.scroll_surface.blit(help_surface, (self.suffix_input.x + 10, help_y))
            
            # Count help
            help_y = self.count_slider.y + self.count_slider.height + 5
            help_text = "How many matching addresses to generate"
            help_surface = self.tiny_font.render(help_text, True, (180, 180, 180))
            self.scroll_surface.blit(help_surface, (self.count_slider.x + 10, help_y))
            
            # Iteration help
            help_y = self.iteration_slider.y + self.iteration_slider.height + 5
            help_text = "Higher = faster but uses more GPU memory"
            help_surface = self.tiny_font.render(help_text, True, (180, 180, 180))
            self.scroll_surface.blit(help_surface, (self.iteration_slider.x + 10, help_y))
    
    def draw_preview_section(self):
        """Draw the preview section on the scroll surface"""
        # Section border
        pygame.draw.rect(
            self.scroll_surface,
            (60, 60, 60),
            self.preview_section_rect,
            2,
            border_radius=5
        )
        
        # Section heading
        heading_text = "Preview & Examples"
        heading_surface = self.font.render(heading_text, True, (255, 0, 255))
        heading_rect = heading_surface.get_rect(midleft=(self.preview_heading_rect.x, self.preview_heading_rect.centery))
        self.scroll_surface.blit(heading_surface, heading_rect)
        
        # Get current prefix and suffix
        prefix = self.prefix_input.get_text().strip()
        suffix = self.suffix_input.get_text().strip()
        
        # Draw example addresses with highlighting
        for i, address in enumerate(self.example_addresses):
            y_pos = self.examples_rect.y + 10 + (i * 25)
            
            # Special case: create a "preview" address if user entered patterns
            if i == 0 and (prefix or suffix):
                # Use user's actual input for preview
                display_addr = address
                if prefix:
                    # Replace start with prefix (keep original length)
                    display_addr = prefix + address[len(prefix):]
                if suffix:
                    # Replace end with suffix (keep original length)
                    suffix_start = len(display_addr) - len(suffix)
                    display_addr = display_addr[:suffix_start] + suffix
                
                # Highlight the custom parts
                parts = []
                if prefix:
                    # Cyan for prefix
                    prefix_surface = self.small_font.render(
                        display_addr[:len(prefix)], True, (0, 255, 255)
                    )
                    parts.append((prefix_surface, self.examples_rect.x))
                    
                    # White for middle
                    middle_start = len(prefix)
                    middle_end = len(display_addr) - (len(suffix) if suffix else 0)
                    middle_surface = self.small_font.render(
                        display_addr[middle_start:middle_end], True, (220, 220, 220)
                    )
                    parts.append((middle_surface, self.examples_rect.x + prefix_surface.get_width()))
                    
                    if suffix:
                        # Magenta for suffix
                        suffix_surface = self.small_font.render(
                            display_addr[-len(suffix):], True, (255, 0, 255)
                        )
                        parts.append((
                            suffix_surface, 
                            self.examples_rect.x + prefix_surface.get_width() + middle_surface.get_width()
                        ))
                elif suffix:
                    # White for start
                    start_end = len(display_addr) - len(suffix)
                    start_surface = self.small_font.render(
                        display_addr[:start_end], True, (220, 220, 220)
                    )
                    parts.append((start_surface, self.examples_rect.x))
                    
                    # Magenta for suffix
                    suffix_surface = self.small_font.render(
                        display_addr[-len(suffix):], True, (255, 0, 255)
                    )
                    parts.append((suffix_surface, self.examples_rect.x + start_surface.get_width()))
                
                # Draw all parts
                for part_surface, x_pos in parts:
                    self.scroll_surface.blit(part_surface, (x_pos, y_pos))
                
                # Label as preview
                preview_text = "[PREVIEW]"
                preview_surface = self.tiny_font.render(preview_text, True, (255, 255, 0))
                self.scroll_surface.blit(
                    preview_surface, 
                    (self.examples_rect.right - preview_surface.get_width() - 5, y_pos)
                )
            else:
                # Regular example address
                addr_surface = self.small_font.render(address, True, (200, 200, 200))
                self.scroll_surface.blit(addr_surface, (self.examples_rect.x, y_pos))
    
    def draw_info_section(self):
        """Draw the information section on the scroll surface"""
        # Section border
        pygame.draw.rect(
            self.scroll_surface,
            (60, 60, 60),
            self.info_section_rect,
            2,
            border_radius=5
        )
        
        # Section heading
        heading_text = "Information & Help"
        heading_surface = self.font.render(heading_text, True, (255, 255, 0))
        heading_rect = heading_surface.get_rect(midleft=(self.info_heading_rect.x, self.info_heading_rect.centery))
        self.scroll_surface.blit(heading_surface, heading_rect)
        
        # Draw help button (on scroll surface)
        self.help_button.x = self.info_heading_rect.right - self.help_button.width
        self.help_button.y = self.info_heading_rect.y
        self.help_button.draw(self.scroll_surface)
        
        # Draw help content or general info based on help toggle
        if self.show_help:
            self.draw_help_content()
        else:
            self.draw_general_info()
    
    def draw_help_content(self):
        """Draw the extended help information"""
        help_lines = [
            ("Vanity Address Tips:", (255, 255, 0)),
            ("", None),
            ("• Pattern Length: Each character added increases", (0, 255, 255)),
            ("  generation time exponentially.", None),
            ("", None),
            ("• Iteration Complexity: Controls how many keys", (0, 255, 255)),
            ("  are processed in parallel. Higher values use", None),
            ("  more GPU memory but generate addresses faster.", None),
            ("", None),
            ("• Valid Characters: Solana addresses use Base58", (0, 255, 255)),
            ("  format (A-Z, a-z, 0-9 except I, O, l, 0).", None),
            ("", None),
            ("• Case Sensitive: 'abc' and 'ABC' are different.", (0, 255, 255)),
        ]
        
        line_height = 22
        for i, (line, color) in enumerate(help_lines):
            if not line:
                continue
                
            text_color = color if color else (200, 200, 200)
            line_surface = self.small_font.render(line, True, text_color)
            y_pos = self.help_rect.y + (i * line_height)
            self.scroll_surface.blit(line_surface, (self.help_rect.x, y_pos))
    
    def draw_general_info(self):
        """Draw the general information section (when help is not shown)"""
        # Only draw this if not currently generating
        if self.generating:
            return
            
        info_lines = [
            ("Generation Performance:", (255, 255, 0)),
            ("", None),
            ("• 1-2 Characters: Nearly instant generation", (0, 255, 255)),
            ("• 3-4 Characters: Few seconds to minutes", (0, 255, 255)),
            ("• 5+ Characters: Could take hours or days", (0, 255, 255)),
            ("", None),
            ("Tips:", (255, 255, 0)),
            ("Click 'Show Help' for more information", (200, 200, 200)),
            ("Try a short pattern first to test speed", (200, 200, 200)),
        ]
        
        line_height = 22
        for i, (line, color) in enumerate(info_lines):
            if not line:
                continue
                
            text_color = color if color else (200, 200, 200)
            line_surface = self.small_font.render(line, True, text_color)
            y_pos = self.help_rect.y + (i * line_height)
            self.scroll_surface.blit(line_surface, (self.help_rect.x, y_pos))
            
        # Calculate and show estimated time
        prefix = self.prefix_input.get_text().strip()
        suffix = self.suffix_input.get_text().strip()
        
        if prefix or suffix:
            pattern_length = len(prefix) + len(suffix)
            estimate_text = "Estimated time: "
            
            if pattern_length <= 2:
                estimate_text += "Less than a minute"
                estimate_color = (0, 255, 0)  # Green
            elif pattern_length <= 4:
                estimate_text += "Minutes to hours"
                estimate_color = (255, 255, 0)  # Yellow
            else:
                estimate_text += "Hours to days"
                estimate_color = (255, 100, 100)  # Red
            
            estimate_surface = self.small_font.render(estimate_text, True, estimate_color)
            y_pos = self.help_rect.y + (len(info_lines) + 1) * line_height
            self.scroll_surface.blit(estimate_surface, (self.help_rect.x, y_pos))
    
    def draw_particles(self):
        """Draw particle effects"""
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
    
    def draw_error_message(self):
        """Draw error message if there is one"""
        if self.generation_error:
            error_surface = pygame.Surface((self.width, 40), pygame.SRCALPHA)
            error_surface.fill((40, 0, 0, 200))  # Semi-transparent red background
            
            error_text = self.small_font.render(f"Error: {self.generation_error}", True, (255, 100, 100))
            error_rect = error_text.get_rect(center=(error_surface.get_width() // 2, error_surface.get_height() // 2))
            error_surface.blit(error_text, error_rect)
            
            # Position at the top of the content area
            self.screen.blit(error_surface, (0, self.title_rect.bottom))
    
    def draw(self):
        """Draw the generation screen components"""
        # Clear the main screen with a dark background
        self.screen.fill((40, 40, 40))
        
        # Draw particles first (background layer)
        self.draw_particles()
        
        # Clear the scroll surface
        self.scroll_surface.fill((40, 40, 40))
        
        # Draw scrollable content onto scroll surface
        self.draw_params_section()
        self.draw_preview_section()
        self.draw_info_section()
        
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
        
        # Draw error message
        self.draw_error_message()
    
    def update(self, delta_time: float):
        """
        Update screen state
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Update animation time
        self.animation_time += delta_time
        
        # Update UI components
        if self.generating:
            self.progress_bar.update(delta_time)
        
        # Update slider animations
        self.count_slider.update(delta_time)
        self.iteration_slider.update(delta_time)
        
        # Update particles and occasionally create new ones
        self.update_particles(delta_time)
        if random.random() < delta_time * 2:  # Average 2 particles per second
            self.create_particles(1)
            
        # Check if generation thread is still alive
        if self.generating and self.generation_thread and not self.generation_thread.is_alive():
            if self.generation_result:
                # Generation completed successfully
                self.generating = False
                self.on_complete(self.generation_result)
                self.generation_result = None
                self.generation_thread = None
    
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
        
        # Skip input handling while generating
        if self.generating:
            # Still allow back button to cancel generation
            return self.back_button.handle_event(event)
        
        # Handle help toggle with H key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            self.toggle_help()
            return True
        
        # Handle custom events for generation progress and completion
        if event.type == pygame.USEREVENT:
            if hasattr(event, 'dict') and 'type' in event.dict:
                if event.dict['type'] == 'generation_progress':
                    # Update progress bar
                    progress = event.dict.get('progress', 0)
                    self.progress_bar.set_progress(progress)
                    return True
                
                elif event.dict['type'] == 'generation_complete':
                    # Store the result and let update() handle it
                    self.generation_result = event.dict.get('result')
                    return True
                
                elif event.dict['type'] == 'generation_error':
                    # Store the error message
                    self.generation_error = event.dict.get('error')
                    self.generating = False
                    return True
        
        # Check if event is in the fixed areas (non-scrollable)
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
            # Check if in footer area (buttons)
            if self.footer_rect.collidepoint(mouse_pos):
                if self.generate_button.handle_event(event):
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
                
                # Handle input events in scrollable area
                handled = False
                
                # Parameters section
                if self.params_section_rect.collidepoint(scroll_adjusted_event.pos):
                    handled |= self.prefix_input.handle_event(scroll_adjusted_event)
                    handled |= self.suffix_input.handle_event(scroll_adjusted_event)
                    handled |= self.count_slider.handle_event(scroll_adjusted_event)
                    handled |= self.iteration_slider.handle_event(scroll_adjusted_event)
                
                # Info section
                if self.info_section_rect.collidepoint(scroll_adjusted_event.pos):
                    handled |= self.help_button.handle_event(scroll_adjusted_event)
                
                return handled
                
        return False
    
    def start_generation(self):
        """Initiate the vanity address generation process"""
        # Clear any previous errors
        self.generation_error = None
        
        # Validate inputs
        prefix = self.prefix_input.get_text().strip()
        suffix = self.suffix_input.get_text().strip()
        count = self.count_slider.get_value()
        iteration_bits = self.iteration_slider.get_value()
        
        if not prefix and not suffix:
            self.generation_error = "Please provide at least a prefix or suffix"
            logging.error(self.generation_error)
            return
        
        # Update configuration
        self.config.set('prefix', prefix)
        self.config.set('suffix', suffix)
        self.config.set('count', str(count))
        self.config.set('iteration_bits', iteration_bits)
        
        # Prepare output directory
        output_dir = self.config.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        
        # Start generation
        self.generating = True
        self.progress_bar.set_progress(0)
        
        # Run generation in a separate thread to keep UI responsive
        self.generation_thread = threading.Thread(
            target=self.run_generation, 
            args=(prefix, suffix, count, output_dir, iteration_bits),
            daemon=True  # Ensure thread doesn't prevent application exit
        )
        self.generation_thread.start()
    
    def run_generation(self, prefix, suffix, count, output_dir, iteration_bits):
        """
        Execute the address generation process in a background thread
        
        Args:
            prefix: Address prefix
            suffix: Address suffix
            count: Number of addresses to generate
            output_dir: Directory to save keys
            iteration_bits: Iteration complexity bits
        """
        try:
            # Create a callback to update progress
            def progress_callback(status):
                # Post a custom event to update UI from the main thread
                event = pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        'type': 'generation_progress',
                        'progress': status.get('progress', 0)
                    }
                )
                pygame.event.post(event)
            
            # Execute the generator
            result = search_vanity_addresses(
                starts_with=prefix,
                ends_with=suffix,
                count=count,
                output_dir=output_dir,
                iteration_bits=iteration_bits,
                callback=progress_callback
            )
            
            # Post result to main thread
            if result["success"]:
                event = pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        'type': 'generation_complete',
                        'result': result
                    }
                )
            else:
                event = pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        'type': 'generation_error',
                        'error': result.get('error', 'Unknown error')
                    }
                )
            
            pygame.event.post(event)
        
        except Exception as e:
            # Post error to main thread
            error_event = pygame.event.Event(
                pygame.USEREVENT,
                {
                    'type': 'generation_error',
                    'error': str(e)
                }
            )
            pygame.event.post(error_event)
            logging.exception("Error in generation thread")