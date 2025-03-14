def draw_info_panel(self):
        """Draw the scrollable information panel"""
        # Create main panel surface with alpha
        panel_surface = pygame.Surface(
            (self.info_panel_rect.width, self.info_panel_rect.height),
            pygame.SRCALPHA
        )
        
        # Fill with semi-transparent background
        panel_surface.fill((20, 20, 20, 240))
        
        # Draw CMYK border with animation
        border_width = 3
        colors = [
            (0, 255, 255),     # Cyan
            (255, 0, 255),     # Magenta
            (255, 255, 0),     # Yellow
            (180, 180, 180)    # Key/Black
        ]
        
        # Animate border colors by shifting starting position
        color_shift = int(self.animation_time * 5) % 4
        
        # Draw each edge with different colors
        edges = [
            ((0, 0), (self.info_panel_rect.width, 0)),                          # Top
            ((self.info_panel_rect.width - border_width, 0), 
             (self.info_panel_rect.width - border_width, self.info_panel_rect.height)),  # Right
            ((0, self.info_panel_rect.height - border_width), 
             (self.info_panel_rect.width, self.info_panel_rect.height - border_width)),  # Bottom
            ((0, 0), (0, self.info_panel_rect.height))                          # Left
        ]
        
        for i, (start, end) in enumerate(edges):
            color_index = (i + color_shift) % 4
            pygame.draw.line(
                panel_surface,
                colors[color_index],
                start,
                end,
                border_width
            )
        
        # Draw title area
        # Get page title based on current page
        title_text = ""
        if self.info_page == 0:
            title_text = "What are Vanity Addresses?"
            title_color = (0, 255, 255)  # Cyan
        elif self.info_page == 1:
            title_text = "How to Generate Addresses"
            title_color = (255, 0, 255)  # Magenta
        elif self.info_page == 2:
            title_text = "Advanced Features"
            title_color = (255, 255, 0)  # Yellow
        
        # Draw title background
        title_bg_rect = pygame.Rect(
            0,
            0,
            self.info_panel_rect.width,
            self.info_title_rect.height - self.info_panel_rect.y
        )
        pygame.draw.rect(
            panel_surface,
            (40, 40, 50),
            title_bg_rect
        )
        
        # Draw divider line under title
        pygame.draw.line(
            panel_surface,
            title_color,
            (20, self.info_title_rect.height - self.info_panel_rect.y - 2),
            (self.info_panel_rect.width - 20, self.info_title_rect.height - self.info_panel_rect.y - 2),
            2
        )
        
        # Draw title text
        title_surface = self.font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(
            self.info_panel_rect.width // 2,
            self.info_title_rect.height // 2 - self.info_panel_rect.y // 2
        ))
        panel_surface.blit(title_surface, title_rect)
        
        # Draw footer area
        footer_bg_rect = pygame.Rect(
            0,
            self.info_panel_rect.height - (self.info_footer_rect.height),
            self.info_panel_rect.width,
            self.info_footer_rect.height
        )
        pygame.draw.rect(
            panel_surface,
            (40, 40, 50),
            footer_bg_rect
        )
        
        # Draw divider line above footer
        pygame.draw.line(
            panel_surface,
            (180, 180, 180),
            (20, self.info_panel_rect.height - self.info_footer_rect.height + 2),
            (self.info_panel_rect.width - 20, self.info_panel_rect.height - self.info_footer_rect.height + 2),
            2
        )
        
        # Clear the scrollable content surface
        self.info_scroll_surface.fill((30, 30, 40))
        
        # Draw appropriate content based on current page
        if self.info_page == 0:
            self.draw_info_page_1()
        elif self.info_page == 1:
            self.draw_info_page_2()
        elif self.info_page == 2:
            self.draw_info_page_3()
        
        # Blit the visible portion of the scroll surface to the panel
        content_area_height = self.info_content_rect.height - (self.info_content_rect.y - self.info_panel_rect.y)
        
        panel_surface.blit(
            self.info_scroll_surface,
            (0, self.info_title_rect.height - self.info_panel_rect.y),
            (0, self.scroll_position, self.info_content_rect.width, content_area_height)
        )
        
        # Draw scrollbar if needed
        if self.max_scroll > 0:
            # Calculate scrollbar position relative to panel
            scrollbar_x = self.info_panel_rect.width - 15
            scrollbar_y = (self.info_title_rect.height - self.info_panel_rect.y)
            scrollbar_height = self.info_panel_rect.height - self.info_title_rect.height - self.info_footer_rect.height + self.info_panel_rect.y
            
            # Draw scrollbar background
            pygame.draw.rect(
                panel_surface, 
                (60, 60, 60), 
                (scrollbar_x, scrollbar_y, 10, scrollbar_height),
                border_radius=5
            )
            
            # Calculate handle size and position
            handle_height = max(30, int(scrollbar_height * (content_area_height / self.viewport_height)))
            handle_y = scrollbar_y + int(self.scroll_position * (scrollbar_height - handle_height) / self.max_scroll)
            
            # Draw scrollbar handle
            pygame.draw.rect(
                panel_surface, 
                (0, 255, 255) if self.scrollbar_dragging else (120, 120, 120),
                (scrollbar_x, handle_y, 10, handle_height),
                border_radius=5
            )
        
        # Update scrollbar handle rect for event handling
        scrollbar_abs_x = self.info_panel_rect.right - 15
        scrollbar_abs_y = self.info_title_rect.bottom + int(self.scroll_position * 
                                                          (self.info_content_rect.height - 30) / self.max_scroll)
        self.scrollbar_handle_rect = pygame.Rect(scrollbar_abs_x, scrollbar_abs_y, 10, 30)
        
        # Blit the entire panel to the screen
        self.screen.blit(panel_surface, self.info_panel_rect)
        
        # Draw navigation buttons (directly on the screen)
        self.prev_button.draw(self.screen)
        self.close_info_button.draw(self.screen)
        self.next_button.draw(self.screen)
        
        # Update button states
        self.prev_button.set_disabled(self.info_page == 0)
        self.next_button.set_disabled(self.info_page == self.max_info_pages - 1)
        
        # Draw page indicator
        indicator_text = f"Page {self.info_page + 1}/{self.max_info_pages}"
        indicator_surface = self.small_font.render(indicator_text, True, (200, 200, 200))
        indicator_rect = indicator_surface.get_rect(center=(
            self.width // 2,
            self.info_footer_rect.centery + 15
        ))
        self.screen.blit(indicator_surface, indicator_rect)
    
    def draw_info_page_1(self):
        """Draw content for info page 1 on the scroll surface"""
        text_lines = [
            ("Vanity Addresses", (255, 255, 0), True),
            ("", None, False),
            ("Vanity addresses are custom cryptocurrency addresses", (220, 220, 220), False),
            ("that contain specific characters you choose.", (220, 220, 220), False),
            ("", None, False),
            ("For example, you might want an address that:", (220, 220, 220), False),
            ("• Starts with your name: SOLjohn123...", (0, 255, 255), False),
            ("• Ends with special numbers: ...1337", (0, 255, 255), False),
            ("• Contains a word: ...COOL...", (0, 255, 255), False),
            ("", None, False),
            ("Benefits:", (255, 0, 255), True),
            ("", None, False),
            ("• Easier to recognize your own addresses", (220, 220, 220), False),
            ("• More memorable for recipients", (220, 220, 220), False),
            ("• Shows attention to detail", (220, 220, 220), False),
            ("", None, False),
            ("Important Considerations:", (255, 0, 255), True),
            ("", None, False),
            ("• The longer the custom pattern, the more", (220, 220, 220), False),
            ("  computational work needed to find it", (220, 220, 220), False),
            ("", None, False),
            ("• Each character added exponentially increases", (220, 220, 220), False),
            ("  the time needed to find a matching address", (220, 220, 220), False),
            ("", None, False),
            ("• Valid characters include:", (220, 220, 220), False),
            ("  - Uppercase letters (A-Z except I, O)", (255, 255, 0), False),
            ("  - Lowercase letters (a-z except l)", (255, 255, 0), False),
            ("  - Numbers (1-9, excluding 0)", (255, 255, 0), False),
            ("", None, False),
            ("Technical Details:", (255, 0, 255), True),
            ("", None, False),
            ("• Solana addresses use Base58 encoding", (220, 220, 220), False),
            ("• Patterns are case-sensitive", (220, 220, 220), False),
            ("• Generated keypairs are cryptographically secure", (220, 220, 220), False),
            ("• Generation uses your GPU for maximum speed", (220, 220, 220), False),
            ("", None, False),
            ("Example Addresses:", (255, 0, 255), True),
            ("", None, False),
            ("JAKE5GvU8ZYDYc4KveB1RHKNeBG67Kpjw3tT5CLv3", (0, 255, 255), False),
            ("H58MEZCoYZ9iKwkHjK37rU4QW8PK3YaMfEWhK21Qxxxx", (0, 255, 255), False),
            ("DEVkgEgfMULw5i5QnuocgJbJ1EFfxWENXFAryUTDcool", (0, 255, 255), False),
        ]
        
        self.draw_content_with_sections(text_lines)
    
    def draw_info_page_2(self):
        """Draw content for info page 2 on the scroll surface"""
        text_lines = [
            ("Generation Process", (255, 255, 0), True),
            ("", None, False),
            ("1. Click 'Generate Address' on the main menu", (255, 255, 255), False),
            ("", None, False),
            ("2. Enter your desired pattern:", (220, 220, 220), False),
            ("   • Prefix: Characters at the START of the address", (0, 255, 255), False),
            ("   • Suffix: Characters at the END of the address", (0, 255, 255), False),
            ("   • You must specify at least one of these", (255, 0, 255), False),
            ("", None, False),
            ("3. Set the number of addresses to generate", (220, 220, 220), False),
            ("   • You can generate multiple addresses in one batch", (220, 220, 220), False),
            ("", None, False),
            ("4. Adjust the Iteration Complexity (16-28)", (220, 220, 220), False),
            ("   • Higher = Faster but uses more GPU memory", (0, 255, 255), False),
            ("   • Lower = Slower but uses less GPU memory", (0, 255, 255), False),
            ("   • Recommended: 24 for most GPUs", (0, 255, 255), False),
            ("", None, False),
            ("5. Click Generate and wait for results", (220, 220, 220), False),
            ("", None, False),
            ("Performance Tips:", (255, 0, 255), True),
            ("", None, False),
            ("• Short patterns (1-3 chars): Nearly instant", (220, 220, 220), False),
            ("• Medium patterns (4-5 chars): Minutes to hours", (220, 220, 220), False),
            ("• Long patterns (6+ chars): Hours to days", (220, 220, 220), False),
            ("", None, False),
            ("• Using modern GPUs will dramatically increase speed", (220, 220, 220), False),
            ("• Start with short patterns to test performance", (220, 220, 220), False),
            ("", None, False),
            ("During Generation:", (255, 0, 255), True),
            ("", None, False),
            ("• A progress bar will show estimated completion", (220, 220, 220), False),
            ("• You can click 'Cancel' at any time to stop", (220, 220, 220), False),
            ("• Performance statistics will be displayed", (220, 220, 220), False),
            ("", None, False),
            ("After Generation:", (255, 0, 255), True),
            ("", None, False),
            ("• Generated addresses will be displayed in the results screen", (220, 220, 220), False),
            ("• Keys are automatically saved to your specified directory", (220, 220, 220), False),
            ("• You can export results in various formats", (220, 220, 220), False),
        ]
        
        self.draw_content_with_sections(text_lines)
    
    def draw_info_page_3(self):
        """Draw content for info page 3 on the scroll surface"""
        text_lines = [
            ("Advanced Features", (255, 255, 0), True),
            ("", None, False),
            ("Device Selection:", (255, 0, 255), True),
            ("", None, False),
            ("• View all compatible OpenCL devices", (220, 220, 220), False),
            ("• Choose between multiple GPUs if available", (220, 220, 220), False),
            ("• See detailed specifications of each device", (220, 220, 220), False),
            ("", None, False),
            ("Settings:", (255, 0, 255), True),
            ("", None, False),
            ("• Change the UI theme (CMYK colors)", (220, 220, 220), False),
            ("  - Cyan, Magenta, Yellow, Key, or combined CMYK", (0, 255, 255), False),
            ("", None, False),
            ("• Configure sound effects", (220, 220, 220), False),
            ("  - Toggle sounds on/off", (0, 255, 255), False),
            ("", None, False),
            ("• Set custom output directory", (220, 220, 220), False),
            ("  - Choose where to save generated keys", (0, 255, 255), False),
            ("", None, False),
            ("• Default iteration complexity", (220, 220, 220), False),
            ("  - Set default value for generation speed", (0, 255, 255), False),
            ("", None, False),
            ("Export Options:", (255, 0, 255), True),
            ("", None, False),
            ("• JSON format (for developer use)", (220, 220, 220), False),
            ("  - Compatible with Solana tools", (0, 255, 255), False),
            ("", None, False),
            ("• HTML report (for easy viewing)", (220, 220, 220), False),
            ("  - Styled output with CMYK theme", (0, 255, 255), False),
            ("", None, False),
            ("• CSV format (for spreadsheets)", (220, 220, 220), False),
            ("  - Import into Excel or other tools", (0, 255, 255), False),
            ("", None, False),
            ("• TXT format (for simple output)", (220, 220, 220), False),
            ("  - Plain text list of addresses", (0, 255, 255), False),
            ("", None, False),
            ("Security Notes:", (255, 0, 255), True),
            ("", None, False),
            ("• Keys are saved securely on your device", (220, 220, 220), False),
            ("• No data is sent to external servers", (220, 220, 220), False),
            ("• Keep your private keys safe", (220, 220, 220), False),
        ]
        
        self.draw_content_with_sections(text_lines)
    
    def draw_content_with_sections(self, text_lines):
        """Draw content with proper formatting and sections on the scroll surface"""
        line_height = 28
        padding_x = 20
        
        # Draw each line with appropriate formatting
        for i, (line, color, is_header) in enumerate(text_lines):
            # Skip if line is empty or color is None
            if not line or color is None:
                continue
                
            # Use appropriate font based on if it's a header
            font = self.font if is_header else self.small_font
            
            # Render the text
            text_surface = font.render(line, True, color)
            
            # Position
            y_pos = i * line_height
            x_pos = padding_x
            
            # Add indentation for bullet points
            if line.startswith("•") or line.startswith("-"):
                x_pos += 10
            elif line.startswith("  -") or line.startswith("   •"):
                x_pos += 30
            
            # Blit to scroll surface
            self.info_scroll_surface.blit(text_surface, (x_pos, y_pos))
        
        # Update the total content height and max scroll position
        self.viewport_height = max(len(text_lines) * line_height + 60, self.info_content_rect.height)
        self.max_scroll = max(0, self.viewport_height - self.info_content_rect.height)
    
    def draw_pulsing_text(self, text: str, pos: Tuple[int, int], base_color: Tuple[int, int, int], 
                          pulse_amount: int = 30, freq: float = 2.0):
        """Draw text with a pulsing effect"""
        # Calculate pulse effect based on time
        pulse = abs(math.sin(self.animation_time * freq)) * pulse_amount
        color = (
            min(255, base_color[0] + pulse),
            min(255, base_color[1] + pulse),
            min(255, base_color[2] + pulse)
        )
        
        text_surface = self.small_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=pos)
        self.screen.blit(text_surface, text_rect)
    
    def draw_particles(self):
        """Draw particle effects"""
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle['color'][:3],  # Use RGB components only
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
    
    def draw(self):
        """Draw the welcome screen"""
        if self.show_info:
            # Info panel is showing
            self.screen.blit(self.background, (0, 0))
            self.draw_particles()
            self.draw_info_panel()
        else:
            # Main menu is showing
            self.draw_main_menu()
    
    def handle_scrolling(self, event):
        """Handle scrolling events for the info panel"""
        if not self.show_info:
            return False
            
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
                scroll_ratio = self.viewport_height / self.info_content_rect.height
                self.scroll_position = max(0, min(self.max_scroll, 
                                                 self.scroll_position + delta_y * scroll_ratio))
                return True
        
        return False
    
    def update(self, delta_time: float):
        """Update animations and timing"""
        self.animation_time += delta_time
        
        # Update particles
        self.update_particles(delta_time)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if event was handled
        """
        # Handle scrolling for info panel
        if self.handle_scrolling(event):
            return True
            
        # Handle info panel toggle with I key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            self.toggle_info()
            return True
            
        # Handle navigation in info panel
        if self.show_info:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.show_info = False
                    return True
                elif event.key == pygame.K_LEFT:
                    self.prev_info_page()
                    return True
                elif event.key == pygame.K_RIGHT:
                    self.next_info_page()
                    return True
            
            # Handle info panel buttons
            if self.prev_button.handle_event(event):
                return True
            if self.close_info_button.handle_event(event):
                return True
            if self.next_button.handle_event(event):
                return True
                
            return True  # Consume all events when info panel is open
            
        # Handle button events in main menu
        if self.generate_button.handle_event(event):
            return True
        if self.device_button.handle_event(event):
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
    
    def run(self) -> str:
        """
        Run the welcome screen logic
        
        Returns:
            str: Command for the main controller ('done' or 'exit')
        """
        if self.exit_screen:
            return "exit"
        return "done"  # Default result"""
Welcome screen for the CMYK Retro Solana Vanity Address Generator
Displays main menu with retro CMYK aesthetics and scrollable info panel
"""

import pygame
import os
import logging
import math
import random
import time
from typing import Callable, List, Tuple, Dict, Any

from ui.components.retro_button import RetroButton
from ui.components.retro_input import RetroInput
from utils.ascii_art import CMYKColors
from utils.config_manager import ConfigManager

class WelcomeScreen:
    """
    Welcome screen with retro CMYK aesthetic and scrollable info panel
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
        
        # Ensure mixer is initialized
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception as e:
                logging.warning(f"Could not initialize sound mixer: {e}")
        
        # State tracking
        self.exit_screen = False
        self.show_info = False
        self.info_page = 0
        self.max_info_pages = 3
        
        # Animation timing
        self.animation_time = 0
        self.particles = []
        
        # Scrolling state for info panel
        self.scroll_position = 0
        self.viewport_height = 1200  # Virtual height of info content
        self.scrollbar_dragging = False
        self.last_mouse_y = 0
        self.max_scroll = 0
        
        # Load assets
        self.load_assets()
        
        # Create UI elements
        self.create_ui_components()
        
        # Create particles
        self.create_particles(20)
    
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
            if os.path.exists(button_sound_path):
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
                (0, 0, 0, 30), 
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
        # Adjust button positioning to be more centered on the screen
        button_width = 300
        button_height = 50
        button_spacing = 20
        
        # Center the buttons vertically, starting below the logo area
        button_y_start = self.height // 2 - 20

        # Main menu buttons
        self.generate_button = RetroButton(
            (self.width - button_width) // 2,
            button_y_start,
            button_width,
            button_height,
            "Generate Address",
            lambda: self.on_menu_select("generate"),
            color_scheme="cyan"
        )

        self.device_button = RetroButton(
            (self.width - button_width) // 2,
            button_y_start + button_height + button_spacing,
            button_width,
            button_height,
            "Select Device",
            lambda: self.on_menu_select("devices"),
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
            self.toggle_info,
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
        
        # Create the info panel components
        self.create_info_panel_components()
    
    def create_info_panel_components(self):
        """Create components for the scrollable info panel"""
        # Info panel dimensions
        self.info_panel_rect = pygame.Rect(
            self.width * 0.1,  # 10% margin on each side
            self.height * 0.15,  # 15% from top
            self.width * 0.8,  # 80% width
            self.height * 0.7   # 70% height
        )
        
        # Fixed areas within info panel
        self.info_title_rect = pygame.Rect(
            self.info_panel_rect.x,
            self.info_panel_rect.y,
            self.info_panel_rect.width,
            60  # Fixed height for title area
        )
        
        self.info_footer_rect = pygame.Rect(
            self.info_panel_rect.x,
            self.info_panel_rect.bottom - 60,
            self.info_panel_rect.width,
            60  # Fixed height for footer/navigation area
        )
        
        # Content area (between title and footer)
        self.info_content_rect = pygame.Rect(
            self.info_panel_rect.x,
            self.info_title_rect.bottom,
            self.info_panel_rect.width,
            self.info_panel_rect.height - self.info_title_rect.height - self.info_footer_rect.height
        )
        
        # Create the scrollable surface for info content
        self.info_scroll_surface = pygame.Surface((self.info_content_rect.width, self.viewport_height))
        
        # Calculate max scroll
        self.max_scroll = max(0, self.viewport_height - self.info_content_rect.height)
        
        # Scrollbar rect
        scrollbar_width = 10
        self.scrollbar_bg_rect = pygame.Rect(
            self.info_panel_rect.right - scrollbar_width - 10,
            self.info_content_rect.y,
            scrollbar_width,
            self.info_content_rect.height
        )
        
        # Scrollbar handle (will be updated during drawing)
        self.scrollbar_handle_rect = pygame.Rect(0, 0, scrollbar_width, 30)
        
        # Navigation buttons
        nav_button_width = 120
        nav_button_height = 40
        
        self.prev_button = RetroButton(
            self.info_footer_rect.x + 20,
            self.info_footer_rect.centery - nav_button_height // 2,
            nav_button_width,
            nav_button_height,
            "Previous",
            self.prev_info_page,
            color_scheme="magenta"
        )
        
        self.close_info_button = RetroButton(
            self.info_footer_rect.centerx - nav_button_width // 2,
            self.info_footer_rect.centery - nav_button_height // 2,
            nav_button_width,
            nav_button_height,
            "Close Info",
            self.toggle_info,
            color_scheme="white"
        )
        
        self.next_button = RetroButton(
            self.info_footer_rect.right - nav_button_width - 20,
            self.info_footer_rect.centery - nav_button_height // 2,
            nav_button_width,
            nav_button_height,
            "Next",
            self.next_info_page,
            color_scheme="cyan"
        )
    
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
        
        # Add new particles occasionally
        if random.random() < delta_time * 2:  # Average 2 particles per second
            self.create_particles(1)
    
    def toggle_info(self):
        """Toggle the info panel visibility"""
        self.show_info = not self.show_info
        self.scroll_position = 0  # Reset scroll position
        if self.button_sound:
            self.button_sound.play()

    def next_info_page(self):
        """Go to the next info page"""
        if self.info_page < self.max_info_pages - 1:
            self.info_page += 1
            self.scroll_position = 0  # Reset scroll position
            if self.button_sound:
                self.button_sound.play()

    def prev_info_page(self):
        """Go to the previous info page"""
        if self.info_page > 0:
            self.info_page -= 1
            self.scroll_position = 0  # Reset scroll position
            if self.button_sound:
                self.button_sound.play()
    
    def draw_main_menu(self):
        """Draw the main menu screen with logo and buttons"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle['color'][:3],  # Use RGB components only
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
            
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
        
        # Draw animated horizontal line
        line_y = subtitle_rect.bottom + 10
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
            
            # Cycle through CMYK colors
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
        self.generate_button.draw(self.screen)
        self.device_button.draw(self.screen)
        self.settings_button.draw(self.screen)
        self.info_button.draw(self.screen)
        self.exit_button.draw(self.screen)
        
        # Draw footer info with pulsing effect
        footer_text = "Press [I] for instructions | Press [ESC] to exit"
        pulse = abs(math.sin(self.animation_time * 2)) * 50 + 150  # 150-200 range
        footer_color = (pulse, pulse, pulse)
        
        footer_surface = self.small_font.render(footer_text, True, footer_color)
        footer_rect = footer_surface.get_rect(center=(self.width // 2, self.height - 20))
        self.screen.blit(footer_surface, footer_rect)