"""
Results Screen for the CMYK Retro Solana Vanity Address Generator
Displays generated vanity addresses with a scrollable layout
"""

import os
import pygame
import logging
import math
import random
import time
from typing import Dict, Any, Callable, List, Tuple

from ui.components.retro_button import RetroButton
from ui.components.retro_input import RetroInput
from utils.output_formatter import format_address_table, export_addresses_to_file
from utils.config_manager import ConfigManager

class ResultsScreen:
    """
    Screen for displaying and managing generated vanity addresses
    with a scrollable layout to avoid overlapping containers
    """
    
    def __init__(
        self, 
        screen: pygame.Surface, 
        results: Dict[str, Any], 
        on_back: Callable[[], None]
    ):
        """
        Initialize the results screen
        
        Args:
            screen: Pygame surface to render on
            results: Dictionary containing generation results
            on_back: Callback to return to previous screen
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.results = results
        self.on_back = on_back
        
        # Configuration management
        self.config = ConfigManager()
        
        # Animation state
        self.animation_time = 0
        self.particles = []
        self.scanning_effect = 0
        self.highlight_index = -1
        self.selected_index = -1
        
        # UI state
        self.status_message = ""
        self.status_color = (0, 255, 0)
        self.status_timer = 0
        self.export_format = "json"
        
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
                self.address_font = pygame.font.Font(pixel_font_path, 18)
                self.small_font = pygame.font.Font(pixel_font_path, 16)
                self.tiny_font = pygame.font.Font(pixel_font_path, 12)
            else:
                self.title_font = pygame.font.SysFont("monospace", 32)
                self.font = pygame.font.SysFont("monospace", 20)
                self.address_font = pygame.font.SysFont("monospace", 18)
                self.small_font = pygame.font.SysFont("monospace", 16)
                self.tiny_font = pygame.font.SysFont("monospace", 12)
        except Exception as e:
            logging.warning(f"Font loading failed: {e}")
            self.title_font = pygame.font.SysFont("monospace", 32)
            self.font = pygame.font.SysFont("monospace", 20)
            self.address_font = pygame.font.SysFont("monospace", 18)
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
        """Create and initialize UI components for the results screen"""
        # Default margins
        side_margin = 30
        section_margin = 20
        
        # Calculate usable width
        usable_width = self.width - (side_margin * 2)
        
        # Y position tracker for vertical layout
        current_y = 30  # Start with some padding at top of scroll surface
        
        # 1. STATS SECTION
        # ----------------------------
        # Stats section heading
        self.stats_heading_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            30
        )
        current_y += self.stats_heading_rect.height + 10
        
        # Stats content area
        self.stats_content_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            80  # Fixed height for stats content
        )
        current_y += self.stats_content_rect.height + 10
        
        # Export format buttons
        format_button_width = 110
        format_button_height = 30
        format_button_y = current_y
        
        self.format_buttons = []
        formats = ["JSON", "HTML", "CSV", "TXT"]
        button_spacing = 10
        
        # Calculate total width for all format buttons
        total_format_width = (format_button_width * len(formats)) + (button_spacing * (len(formats) - 1))
        format_start_x = side_margin + (usable_width - total_format_width) // 2
        
        for i, format_name in enumerate(formats):
            button_x = format_start_x + i * (format_button_width + button_spacing)
            color_scheme = "cyan" if i % 2 == 0 else "magenta"
            
            button = RetroButton(
                button_x, format_button_y,
                format_button_width, format_button_height,
                format_name,
                lambda f=format_name.lower(): self.set_export_format(f),
                color_scheme=color_scheme
            )
            self.format_buttons.append(button)
        
        current_y += format_button_height + 20
        
        # Define the stats section rect for drawing
        self.stats_section_rect = pygame.Rect(
            side_margin - 10,  # Extra padding for border
            self.stats_heading_rect.y - 10,
            usable_width + 20,  # Extra padding for border
            current_y - self.stats_heading_rect.y  # Total height of section
        )
        
        # Add margin between sections
        current_y += section_margin
        
        # 2. ADDRESSES SECTION
        # ----------------------------
        # Addresses section heading
        self.addresses_heading_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            30
        )
        current_y += self.addresses_heading_rect.height + 10
        
        # Get address list
        addresses = self.results.get('results', [])
        
        # Calculate space needed for addresses
        address_height = 40
        address_spacing = 10
        total_address_height = (address_height + address_spacing) * len(addresses)
        if total_address_height < 200:  # Ensure minimum height
            total_address_height = 200
        
        # Addresses list area
        self.addresses_list_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            total_address_height
        )
        current_y += total_address_height + 10
        
        # Pagination controls
        pagination_height = 30
        self.pagination_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            pagination_height
        )
        
        # Add pagination buttons if needed
        nav_button_width = 100
        nav_button_height = 30
        
        self.prev_button = RetroButton(
            side_margin,
            current_y,
            nav_button_width, nav_button_height,
            "Previous",
            self.prev_page,
            color_scheme="magenta"
        )
        
        self.next_button = RetroButton(
            side_margin + usable_width - nav_button_width,
            current_y,
            nav_button_width, nav_button_height,
            "Next",
            self.next_page,
            color_scheme="cyan"
        )
        
        current_y += pagination_height + 10
        
        # Define the addresses section rect for drawing
        self.addresses_section_rect = pygame.Rect(
            side_margin - 10,  # Extra padding for border
            self.addresses_heading_rect.y - 10,
            usable_width + 20,  # Extra padding for border
            current_y - self.addresses_heading_rect.y + 10  # Extra padding for border
        )
        
        # Add margin between sections
        current_y += section_margin
        
        # 3. ADDRESS DETAILS SECTION
        # ----------------------------
        # Details section heading
        self.details_heading_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            30
        )
        current_y += self.details_heading_rect.height + 10
        
        # Details content area
        self.details_content_rect = pygame.Rect(
            side_margin,
            current_y,
            usable_width,
            200  # Fixed height for details
        )
        current_y += self.details_content_rect.height + 10
        
        # Define the details section rect for drawing
        self.details_section_rect = pygame.Rect(
            side_margin - 10,  # Extra padding for border
            self.details_heading_rect.y - 10,
            usable_width + 20,  # Extra padding for border
            current_y - self.details_heading_rect.y + 10  # Extra padding for border
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
        
        self.export_button = RetroButton(
            button_start_x,
            button_y,
            button_width, 
            button_height, 
            "Export Addresses", 
            self.export_results, 
            color_scheme="cyan"
        )
        
        self.back_button = RetroButton(
            button_start_x + button_width + button_spacing,
            button_y,
            button_width, 
            button_height, 
            "Back to Menu", 
            self.on_back, 
            color_scheme="white"
        )
        
        # Calculate addresses per page for pagination
        self.addresses_per_page = 8  # Fixed number of addresses per page
        self.current_page = 0  # Start at first page
    
    def set_export_format(self, format_type: str):
        """Set the export format"""
        self.export_format = format_type
        self.show_status(f"Export format set to {format_type.upper()}", (0, 255, 255))
    
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
    
    def prev_page(self):
        """Go to the previous page of addresses"""
        if self.current_page > 0:
            self.current_page -= 1
            # Reset selection when changing pages
            self.selected_index = -1
    
    def next_page(self):
        """Go to the next page of addresses"""
        addresses = self.results.get('results', [])
        max_pages = (len(addresses) + self.addresses_per_page - 1) // self.addresses_per_page
        
        if self.current_page < max_pages - 1:
            self.current_page += 1
            # Reset selection when changing pages
            self.selected_index = -1
    
    def select_address(self, index: int):
        """Select an address from the list"""
        addresses = self.results.get('results', [])
        if 0 <= index < len(addresses):
            self.selected_index = index
    
    def export_results(self):
        """Export results to the selected format"""
        output_dir = self.config.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate export filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        export_path = os.path.join(output_dir, f"vanity_addresses_{timestamp}.{self.export_format}")
        
        # Export results
        try:
            success, message = export_addresses_to_file(self.results, self.export_format, export_path)
            self.show_status(message, (0, 255, 0) if success else (255, 0, 0))
        except Exception as e:
            self.show_status(f"Export failed: {str(e)}", (255, 0, 0))
    
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
        title_text = "Generated Vanity Addresses"
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
        self.export_button.draw(self.screen)
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
    
    def draw_stats_section(self):
        """Draw the stats section with generation information"""
        # Section border
        pygame.draw.rect(
            self.scroll_surface,
            (60, 60, 60),
            self.stats_section_rect,
            2,
            border_radius=5
        )
        
        # Section heading
        heading_text = "Generation Summary"
        heading_surface = self.font.render(heading_text, True, (0, 255, 255))
        heading_rect = heading_surface.get_rect(midleft=(self.stats_heading_rect.x, self.stats_heading_rect.centery))
        self.scroll_surface.blit(heading_surface, heading_rect)
        
        # Get stats from results
        addresses = self.results.get('results', [])
        address_count = len(addresses)
        
        # Draw address count
        count_text = f"Total Addresses: {address_count}"
        count_surface = self.font.render(count_text, True, (255, 255, 0))
        self.scroll_surface.blit(count_surface, (self.stats_content_rect.x + 15, self.stats_content_rect.y + 15))
        
        # Draw pattern information if available
        if address_count > 0 and addresses[0].get('pubkey'):
            # Get prefix/suffix from the result
            prefix = self.results.get('prefix', '')
            suffix = self.results.get('suffix', '')
            
            if prefix or suffix:
                pattern_text = "Pattern: "
                if prefix:
                    pattern_text += f"Prefix='{prefix}' "
                if suffix:
                    pattern_text += f"Suffix='{suffix}'"
                
                pattern_surface = self.small_font.render(pattern_text, True, (0, 255, 255))
                self.scroll_surface.blit(pattern_surface, (self.stats_content_rect.x + 15, self.stats_content_rect.y + 45))
        
        # Draw export format label
        format_label = "Export Format:"
        format_label_surface = self.small_font.render(format_label, True, (255, 0, 255))
        format_x = self.stats_content_rect.x + 15
        format_y = self.stats_content_rect.bottom - 35
        self.scroll_surface.blit(format_label_surface, (format_x, format_y))
        
        # Draw format buttons
        for button in self.format_buttons:
            button.draw(self.scroll_surface)
            
            # Highlight the selected format
            if button.text.lower() == self.export_format:
                # Draw indicator below selected format
                pygame.draw.rect(
                    self.scroll_surface,
                    (255, 255, 255),
                    (button.x, button.y + button.height - 2, button.width, 2)
                )
    
    def draw_addresses_section(self):
        """Draw the address list section"""
        # Section border
        pygame.draw.rect(
            self.scroll_surface,
            (60, 60, 60),
            self.addresses_section_rect,
            2,
            border_radius=5
        )
        
        # Section heading
        heading_text = "Address List"
        heading_surface = self.font.render(heading_text, True, (255, 0, 255))
        heading_rect = heading_surface.get_rect(midleft=(self.addresses_heading_rect.x, self.addresses_heading_rect.centery))
        self.scroll_surface.blit(heading_surface, heading_rect)
        
        # Get address list
        addresses = self.results.get('results', [])
        
        # Draw addresses
        if addresses:
            # Calculate pagination
            start_idx = self.current_page * self.addresses_per_page
            end_idx = min(start_idx + self.addresses_per_page, len(addresses))
            visible_addresses = addresses[start_idx:end_idx]
            
            # Draw each address in the current page
            address_height = 30
            address_spacing = 10
            
            for i, address in enumerate(visible_addresses):
                # Calculate position
                addr_y = self.addresses_list_rect.y + (i * (address_height + address_spacing))
                
                # Adjusted index for highlighting/selection
                global_index = start_idx + i
                
                # Address rectangle
                addr_rect = pygame.Rect(
                    self.addresses_list_rect.x,
                    addr_y,
                    self.addresses_list_rect.width,
                    address_height
                )
                
                # Background color based on selection
                bg_color = (50, 50, 50)
                if global_index == self.selected_index:
                    bg_color = (60, 60, 80)  # Highlight selected
                elif global_index == self.highlight_index:
                    bg_color = (60, 70, 60)  # Highlight hovered
                
                pygame.draw.rect(
                    self.scroll_surface,
                    bg_color,
                    addr_rect,
                    border_radius=4
                )
                
                # Draw index number
                idx_text = f"{global_index + 1}."
                idx_surface = self.small_font.render(idx_text, True, (180, 180, 180))
                self.scroll_surface.blit(idx_surface, (addr_rect.x + 10, addr_rect.centery - idx_surface.get_height() // 2))
                
                # Draw address text
                pubkey = address.get('pubkey', 'Unknown')
                
                # Truncate address for display if needed
                if len(pubkey) > 40:
                    display_text = pubkey[:20] + "..." + pubkey[-17:]
                else:
                    display_text = pubkey
                
                # Draw address with highlighting for prefix/suffix if applicable
                prefix = self.results.get('prefix', '')
                suffix = self.results.get('suffix', '')
                
                # Position for address text (after index)
                addr_text_x = addr_rect.x + 50
                
                if prefix and pubkey.startswith(prefix):
                    # Draw address in parts to highlight prefix
                    prefix_surface = self.address_font.render(display_text[:len(prefix)], True, (0, 255, 255))
                    rest_surface = self.address_font.render(display_text[len(prefix):], True, (220, 220, 220))
                    
                    # Blit text parts
                    self.scroll_surface.blit(prefix_surface, (addr_text_x, addr_rect.centery - prefix_surface.get_height() // 2))
                    self.scroll_surface.blit(rest_surface, (addr_text_x + prefix_surface.get_width(), addr_rect.centery - rest_surface.get_height() // 2))
                elif suffix and pubkey.endswith(suffix):
                    # Draw address in parts to highlight suffix
                    suffix_start = len(display_text) - len(suffix)
                    prefix_surface = self.address_font.render(display_text[:suffix_start], True, (220, 220, 220))
                    suffix_surface = self.address_font.render(display_text[suffix_start:], True, (255, 0, 255))
                    
                    # Blit text parts
                    self.scroll_surface.blit(prefix_surface, (addr_text_x, addr_rect.centery - prefix_surface.get_height() // 2))
                    self.scroll_surface.blit(suffix_surface, (addr_text_x + prefix_surface.get_width(), addr_rect.centery - suffix_surface.get_height() // 2))
                else:
                    # Draw regular address
                    addr_surface = self.address_font.render(display_text, True, (220, 220, 220))
                    self.scroll_surface.blit(addr_surface, (addr_text_x, addr_rect.centery - addr_surface.get_height() // 2))
                
                # Draw selection indicator
                if global_index == self.selected_index:
                    pygame.draw.rect(
                        self.scroll_surface,
                        (0, 255, 255),
                        addr_rect,
                        width=2,
                        border_radius=4
                    )
            
            # Draw pagination info and controls
            if len(addresses) > self.addresses_per_page:
                # Draw page info
                current_page = self.current_page + 1
                total_pages = (len(addresses) + self.addresses_per_page - 1) // self.addresses_per_page
                page_text = f"Page {current_page} of {total_pages}"
                page_surface = self.small_font.render(page_text, True, (180, 180, 180))
                page_x = self.pagination_rect.centerx - page_surface.get_width() // 2
                self.scroll_surface.blit(page_surface, (page_x, self.pagination_rect.y + 5))
                
                # Draw navigation buttons
                self.prev_button.draw(self.scroll_surface)
                self.next_button.draw(self.scroll_surface)
                
                # Update button states
                self.prev_button.set_disabled(self.current_page == 0)
                self.next_button.set_disabled(self.current_page >= total_pages - 1)
        else:
            # No addresses generated
            no_addr_text = "No addresses generated"
            no_addr_surface = self.font.render(no_addr_text, True, (180, 180, 180))
            no_addr_rect = no_addr_surface.get_rect(center=(
                self.addresses_list_rect.centerx,
                self.addresses_list_rect.centery
            ))
            self.scroll_surface.blit(no_addr_surface, no_addr_rect)
    
    def draw_details_section(self):
        """Draw the details section for the selected address"""
        # Section border
        pygame.draw.rect(
            self.scroll_surface,
            (60, 60, 60),
            self.details_section_rect,
            2,
            border_radius=5
        )
        
        # Section heading
        heading_text = "Selected Address Details"
        heading_surface = self.font.render(heading_text, True, (255, 255, 0))
        heading_rect = heading_surface.get_rect(midleft=(self.details_heading_rect.x, self.details_heading_rect.centery))
        self.scroll_surface.blit(heading_surface, heading_rect)
        
        addresses = self.results.get('results', [])
        
        if addresses and 0 <= self.selected_index < len(addresses):
            # Get the selected address
            address = addresses[self.selected_index]
            pubkey = address.get('pubkey', 'Unknown')
            key_path = address.get('path', 'Unknown')
            
            # Draw selected address box
            selected_bg_rect = pygame.Rect(
                self.details_content_rect.x + 10,
                self.details_content_rect.y + 10,
                self.details_content_rect.width - 20,
                70
            )
            pygame.draw.rect(
                self.scroll_surface,
                (40, 40, 50),
                selected_bg_rect,
                border_radius=5
            )
            
            # Address label
            label_text = "Full Address:"
            label_surface = self.small_font.render(label_text, True, (0, 255, 255))
            self.scroll_surface.blit(label_surface, (selected_bg_rect.x + 10, selected_bg_rect.y + 10))
            
            # Draw wrapped address
            wrapped_address = self.wrap_text(pubkey, self.address_font, selected_bg_rect.width - 30)
            addr_y = selected_bg_rect.y + 35
            
            for line in wrapped_address:
                line_surface = self.address_font.render(line, True, (220, 220, 220))
                self.scroll_surface.blit(line_surface, (selected_bg_rect.x + 15, addr_y))
                addr_y += line_surface.get_height() + 2
            
            # Draw file path box
            path_bg_rect = pygame.Rect(
                self.details_content_rect.x + 10,
                selected_bg_rect.bottom + 15,
                self.details_content_rect.width - 20,
                70
            )
            pygame.draw.rect(
                self.scroll_surface,
                (40, 50, 40),
                path_bg_rect,
                border_radius=5
            )
            
            # Path label
            path_label_text = "Saved File Path:"
            path_label_surface = self.small_font.render(path_label_text, True, (255, 255, 0))
            self.scroll_surface.blit(path_label_surface, (path_bg_rect.x + 10, path_bg_rect.y + 10))
            
            # Draw wrapped path
            wrapped_path = self.wrap_text(key_path, self.small_font, path_bg_rect.width - 30)
            path_y = path_bg_rect.y + 35
            
            for line in wrapped_path:
                line_surface = self.small_font.render(line, True, (180, 180, 180))
                self.scroll_surface.blit(line_surface, (path_bg_rect.x + 15, path_y))
                path_y += line_surface.get_height() + 2
            
            # Draw scanning effect on the selected address
            scan_y = selected_bg_rect.y + 35 + int(self.scanning_effect * 40) % 40
            
            scan_rect = pygame.Rect(
                selected_bg_rect.x + 5, 
                scan_y,
                selected_bg_rect.width - 10,
                2
            )
            pygame.draw.rect(self.scroll_surface, (0, 255, 255, 128), scan_rect)
        else:
            # No address selected
            no_select_text = "Select an address from the list above"
            no_select_surface = self.font.render(no_select_text, True, (180, 180, 180))
            no_select_rect = no_select_surface.get_rect(center=(
                self.details_content_rect.centerx,
                self.details_content_rect.centery
            ))
            self.scroll_surface.blit(no_select_surface, no_select_rect)
            
            # Draw arrow pointing up
            arrow_text = "↑"
            arrow_surface = self.title_font.render(arrow_text, True, (180, 180, 180))
            arrow_rect = arrow_surface.get_rect(center=(
                self.details_content_rect.centerx,
                self.details_content_rect.y + 30
            ))
            self.scroll_surface.blit(arrow_surface, arrow_rect)
    
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
    
    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """
        Wrap text to fit within a specified width
        
        Args:
            text: Text to wrap
            font: Font to use for measuring text
            max_width: Maximum width for each line
            
        Returns:
            List of text lines that fit within the max_width
        """
        words = text.split(' ')
        lines = []
        current_line = []
        
        # Special case for very long text without spaces (like addresses)
        if len(words) == 1 and font.size(text)[0] > max_width:
            # Break into chunks
            chars_per_chunk = 1
            test_chunk = text[:chars_per_chunk]
            
            # Find how many characters can fit within the maximum width
            while font.size(test_chunk)[0] < max_width and chars_per_chunk < len(text):
                chars_per_chunk += 1
                test_chunk = text[:chars_per_chunk]
            
            # Adjust down to be safe
            chars_per_chunk -= 1
            
            # Split the text into chunks
            for i in range(0, len(text), chars_per_chunk):
                lines.append(text[i:i+chars_per_chunk])
            
            return lines
        
        # Normal word wrapping for spaces
        for word in words:
            test_line = ' '.join(current_line + [word])
            # If the line with this word is too long, start a new line
            if font.size(test_line)[0] > max_width:
                if current_line:  # Only add a line if we have words
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long for a single line
                    lines.append(word)
            else:
                current_line.append(word)
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw(self):
        """Draw the results screen components"""
        # Clear the main screen with a dark background
        self.screen.fill((40, 40, 40))
        
        # Draw particles first (background layer)
        self.draw_particles()
        
        # Clear the scroll surface
        self.scroll_surface.fill((40, 40, 40))
        
        # Draw scrollable content onto scroll surface
        self.draw_stats_section()
        self.draw_addresses_section()
        self.draw_details_section()
        
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
        
        # Update scanning effect
        self.scanning_effect = (self.scanning_effect + delta_time) % 1.0
        
        # Update status message timer
        if self.status_timer > 0:
            self.status_timer -= delta_time
        
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
    
    def handle_address_click(self, event, adjusted_pos):
        """Handle clicks on addresses in the list"""
        # Get address list
        addresses = self.results.get('results', [])
        
        if not addresses:
            return False
            
        # Calculate pagination
        start_idx = self.current_page * self.addresses_per_page
        end_idx = min(start_idx + self.addresses_per_page, len(addresses))
        
        # Check if click is within the address list area
        address_height = 30
        address_spacing = 10
        
        # Check each address rect
        for i in range(end_idx - start_idx):
            # Calculate position
            addr_y = self.addresses_list_rect.y + (i * (address_height + address_spacing))
            
            addr_rect = pygame.Rect(
                self.addresses_list_rect.x,
                addr_y,
                self.addresses_list_rect.width,
                address_height
            )
            
            if addr_rect.collidepoint(adjusted_pos):
                # Select the address
                self.select_address(start_idx + i)
                return True
                
        return False
    
    def handle_address_hover(self, event, adjusted_pos):
        """Handle mouse hover over addresses in the list"""
        # Get address list
        addresses = self.results.get('results', [])
        
        if not addresses:
            return False
            
        # Calculate pagination
        start_idx = self.current_page * self.addresses_per_page
        end_idx = min(start_idx + self.addresses_per_page, len(addresses))
        
        # Check if hover is within the address list area
        address_height = 30
        address_spacing = 10
        
        # Reset highlight
        self.highlight_index = -1
        
        # Check each address rect
        for i in range(end_idx - start_idx):
            # Calculate position
            addr_y = self.addresses_list_rect.y + (i * (address_height + address_spacing))
            
            addr_rect = pygame.Rect(
                self.addresses_list_rect.x,
                addr_y,
                self.addresses_list_rect.width,
                address_height
            )
            
            if addr_rect.collidepoint(adjusted_pos):
                # Highlight the address
                self.highlight_index = start_idx + i
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
        
        # Check if event is in the fixed areas (non-scrollable)
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
            # Check if in footer area (buttons)
            if self.footer_rect.collidepoint(mouse_pos):
                if self.export_button.handle_event(event):
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
                
                # Stats section - format buttons
                if self.stats_section_rect.collidepoint(adjusted_pos):
                    for button in self.format_buttons:
                        if button.handle_event(scroll_adjusted_event):
                            handled = True
                            break
                
                # Address list section - clicking addresses
                if event.type == pygame.MOUSEBUTTONDOWN and self.addresses_section_rect.collidepoint(adjusted_pos):
                    # Check for address clicks
                    if self.handle_address_click(event, adjusted_pos):
                        handled = True
                    # Check for pagination button clicks
                    elif self.prev_button.handle_event(scroll_adjusted_event) or self.next_button.handle_event(scroll_adjusted_event):
                        handled = True
                
                # Handle hover effects in address list
                if event.type == pygame.MOUSEMOTION and self.addresses_section_rect.collidepoint(adjusted_pos):
                    if self.handle_address_hover(event, adjusted_pos):
                        handled = True
                
                return handled
        
        # Handle keyboard navigation
        elif event.type == pygame.KEYDOWN:
            addresses = self.results.get('results', [])
            if addresses:
                if event.key == pygame.K_UP:
                    # Select previous address
                    if self.selected_index > 0:
                        self.select_address(self.selected_index - 1)
                        
                        # Switch page if necessary
                        if self.selected_index < self.current_page * self.addresses_per_page:
                            self.current_page = self.selected_index // self.addresses_per_page
                        
                        return True
                elif event.key == pygame.K_DOWN:
                    # Select next address
                    if self.selected_index < len(addresses) - 1:
                        self.select_address(self.selected_index + 1)
                        
                        # Switch page if necessary
                        if self.selected_index >= (self.current_page + 1) * self.addresses_per_page:
                            self.current_page = self.selected_index // self.addresses_per_page
                        
                        return True
                elif event.key == pygame.K_PAGEUP:
                    # Previous page
                    if self.current_page > 0:
                        self.current_page -= 1
                        # Select first address on new page
                        self.selected_index = self.current_page * self.addresses_per_page
                    return True
                elif event.key == pygame.K_PAGEDOWN:
                    # Next page
                    max_pages = (len(addresses) + self.addresses_per_page - 1) // self.addresses_per_page
                    if self.current_page < max_pages - 1:
                        self.current_page += 1
                        # Select first address on new page
                        self.selected_index = self.current_page * self.addresses_per_page
                    return True
        
        return False