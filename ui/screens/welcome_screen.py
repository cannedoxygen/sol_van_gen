"""
Welcome screen for the Solana Vanity Address Generator
Displays intro animation and main menu with retro CMYK aesthetics
"""

import pygame
import os
import logging
import math
import time
from typing import Callable, List, Tuple

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
        self.show_info = False
        self.info_page = 0
        self.max_info_pages = 3
        
        # Animation timing
        self.animation_time = 0
        
        # Load assets
        self.load_assets()
        
        # Create UI elements
        self.create_buttons()
        
        # Setup intro animation state
        self.setup_intro_animation()
    
    def load_assets(self):
        """Load screen assets"""
        # Load background
        try:
            bg_path = os.path.join(PROJECT_ROOT, "assets", "images", "background.png")
            self.background = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except (pygame.error, FileNotFoundError):
            logging.warning("Background image not found, using solid color.")
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill((40, 40, 40))  # Dark gray
            
            # Add some CMYK dots to the background
            for _ in range(500):
                x = pygame.Rect(
                    pygame.math.Vector2(
                        pygame.math.Vector2(
                            pygame.math.Vector2(
                                random.randint(0, self.width), 
                                random.randint(0, self.height)
                            )
                        )
                    ),
                    (3, 3)
                )
                color = random.choice([
                    (0, 255, 255, 128),  # Cyan
                    (255, 0, 255, 128),  # Magenta
                    (255, 255, 0, 128),  # Yellow
                    (30, 30, 30, 128)    # Key/Black
                ])
                pygame.draw.rect(self.background, color, x)
        
        # Load logo
        try:
            logo_path = os.path.join(PROJECT_ROOT, "assets", "images", "logo.png")
            self.logo = pygame.image.load(logo_path)
            logo_width = int(self.width * 0.6)
            logo_height = int(logo_width * self.logo.get_height() / self.logo.get_width())
            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
            self.logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 4))
        except (pygame.error, FileNotFoundError):
            logging.warning("Logo image not found.")
            # Create a simple text-based logo as a fallback
            self.logo_font = pygame.font.SysFont("monospace", 36, bold=True)
            
            # Use CMYK colors for the letters
            c_text = self.logo_font.render("C", True, (0, 255, 255))
            m_text = self.logo_font.render("M", True, (255, 0, 255))
            y_text = self.logo_font.render("Y", True, (255, 255, 0))
            k_text = self.logo_font.render("K", True, (180, 180, 180))
            
            # Logo width is the sum of all letter widths plus spacing
            logo_width = c_text.get_width() + m_text.get_width() + y_text.get_width() + k_text.get_width() + 20
            logo_height = max(c_text.get_height(), m_text.get_height(), y_text.get_height(), k_text.get_height())
            
            self.logo = pygame.Surface((logo_width, logo_height), pygame.SRCALPHA)
            
            # Position letters next to each other
            x_pos = 0
            self.logo.blit(c_text, (x_pos, 0))
            x_pos += c_text.get_width() + 5
            self.logo.blit(m_text, (x_pos, 0))
            x_pos += m_text.get_width() + 5
            self.logo.blit(y_text, (x_pos, 0))
            x_pos += y_text.get_width() + 5
            self.logo.blit(k_text, (x_pos, 0))
            
            self.logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 4))
        
        # Load fonts
        try:
            pixel_font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "pixel_font.ttf")
            if os.path.exists(pixel_font_path):
                self.font = pygame.font.Font(pixel_font_path, 24)
                self.title_font = pygame.font.Font(pixel_font_path, 36)
                self.small_font = pygame.font.Font(pixel_font_path, 18)
            else:
                self.font = pygame.font.SysFont("monospace", 24)
                self.title_font = pygame.font.SysFont("monospace", 36)
                self.small_font = pygame.font.SysFont("monospace", 18)
        except Exception:
            logging.warning("Font loading failed, using system fonts.")
            self.font = pygame.font.SysFont("monospace", 24)
            self.title_font = pygame.font.SysFont("monospace", 36)
            self.small_font = pygame.font.SysFont("monospace", 18)
        
        # Load sounds
        try:
            intro_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "success.wav")
            if os.path.exists(intro_sound_path):
                self.intro_sound = pygame.mixer.Sound(intro_sound_path)
            else:
                self.intro_sound = None
                
            button_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "keypress.wav")
            if os.path.exists(button_sound_path):
                self.button_sound = pygame.mixer.Sound(button_sound_path)
                self.button_sound.set_volume(0.3)
            else:
                self.button_sound = None
        except Exception:
            logging.warning("Sound loading failed.")
            self.intro_sound = None
            self.button_sound = None
    
    def setup_intro_animation(self):
        """Setup intro animation state"""
        self.intro_text = "Generating Unique Solana Addresses"
        self.intro_text_index = 0
        self.intro_text_surface = self.font.render("", True, (255, 255, 255))  # White color
        self.intro_sound_played = False
    
    def create_buttons(self):
        """Create main menu buttons"""
        # Import here to avoid circular imports
        from ui.components.retro_button import RetroButton
        
        # Adjust button positioning to be more centered on the screen
        button_width = 300
        button_height = 50
        button_spacing = 20
        
        # Calculate the total height of all buttons and spacing
        total_buttons_height = (button_height * 5) + (button_spacing * 4)  # 5 buttons now
        
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
        
        # Info panel navigation buttons
        nav_button_width = 120
        nav_button_height = 40
        nav_button_y = self.height - 80
        
        self.prev_button = RetroButton(
            self.width // 4 - nav_button_width // 2,
            nav_button_y,
            nav_button_width,
            nav_button_height,
            "Previous",
            self.prev_info_page,
            color_scheme="magenta"
        )
        
        self.close_info_button = RetroButton(
            self.width // 2 - nav_button_width // 2,
            nav_button_y,
            nav_button_width,
            nav_button_height,
            "Close Info",
            self.toggle_info,
            color_scheme="white"
        )
        
        self.next_button = RetroButton(
            3 * self.width // 4 - nav_button_width // 2,
            nav_button_y,
            nav_button_width,
            nav_button_height,
            "Next",
            self.next_info_page,
            color_scheme="cyan"
        )

    def toggle_info(self):
        """Toggle the info panel visibility"""
        self.show_info = not self.show_info
        if self.button_sound:
            self.button_sound.play()

    def next_info_page(self):
        """Go to the next info page"""
        if self.info_page < self.max_info_pages - 1:
            self.info_page += 1
            if self.button_sound:
                self.button_sound.play()

    def prev_info_page(self):
        """Go to the previous info page"""
        if self.info_page > 0:
            self.info_page -= 1
            if self.button_sound:
                self.button_sound.play()

    def draw_intro(self):
        """Draw the intro animation"""
        self.intro_text_index += 1

        if self.intro_text_index <= len(self.intro_text):
            self.intro_text_surface = self.font.render(
                self.intro_text[:self.intro_text_index],
                True,
                (255, 255, 255)  # White color
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
    
    def draw_pulsing_text(self, text, pos, base_color, pulse_amount=30, freq=2.0):
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
    
    def draw_info_panel(self):
        """Draw the information panel with paged content"""
        # Background panel
        panel_rect = pygame.Rect(
            self.width * 0.1,  # 10% margin on each side
            self.height * 0.15,  # 15% from top
            self.width * 0.8,  # 80% width
            self.height * 0.6   # 60% height
        )
        
        # Draw panel background with CMYK gradient
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        
        # Fill with semi-transparent background
        panel_surface.fill((20, 20, 20, 240))
        
        # Add CMYK border
        border_width = 3
        colors = [
            (0, 255, 255),     # Cyan - Top
            (255, 0, 255),     # Magenta - Right
            (255, 255, 0),     # Yellow - Bottom
            (180, 180, 180)    # Key/Black - Left
        ]
        
        # Draw colored borders
        pygame.draw.rect(panel_surface, colors[0], (0, 0, panel_rect.width, border_width))  # Top
        pygame.draw.rect(panel_surface, colors[1], (panel_rect.width - border_width, 0, border_width, panel_rect.height))  # Right
        pygame.draw.rect(panel_surface, colors[2], (0, panel_rect.height - border_width, panel_rect.width, border_width))  # Bottom
        pygame.draw.rect(panel_surface, colors[3], (0, 0, border_width, panel_rect.height))  # Left
        
        self.screen.blit(panel_surface, panel_rect)
        
        # Draw page title based on current page
        title_text = ""
        if self.info_page == 0:
            title_text = "What are Vanity Addresses?"
        elif self.info_page == 1:
            title_text = "How to Generate Addresses"
        elif self.info_page == 2:
            title_text = "Advanced Features"
        
        title_surface = self.font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.width // 2, panel_rect.y + 30))
        self.screen.blit(title_surface, title_rect)
        
        # Content area
        content_rect = pygame.Rect(
            panel_rect.x + 20,
            panel_rect.y + 60,
            panel_rect.width - 40,
            panel_rect.height - 100
        )
        
        # Draw content based on current page
        if self.info_page == 0:
            self.draw_info_page_1(content_rect)
        elif self.info_page == 1:
            self.draw_info_page_2(content_rect)
        elif self.info_page == 2:
            self.draw_info_page_3(content_rect)
        
        # Page indicator
        indicator_text = f"Page {self.info_page + 1}/{self.max_info_pages}"
        indicator_surface = self.small_font.render(indicator_text, True, (200, 200, 200))
        indicator_rect = indicator_surface.get_rect(center=(self.width // 2, panel_rect.y + panel_rect.height - 25))
        self.screen.blit(indicator_surface, indicator_rect)
        
        # Draw navigation buttons
        self.prev_button.draw(self.screen)
        self.close_info_button.draw(self.screen)
        self.next_button.draw(self.screen)
    
    def draw_info_page_1(self, rect):
        """Draw content for info page 1"""
        text_lines = [
            "Vanity addresses are custom cryptocurrency addresses",
            "that contain specific characters you choose.",
            "",
            "For example, you might want an address that:",
            "• Starts with your name: SOLjohn123...",
            "• Ends with special numbers: ...1337",
            "• Contains a word: ...COOL...",
            "",
            "Benefits:",
            "• Easier to recognize your own addresses",
            "• More memorable for recipients",
            "• Shows attention to detail",
            "",
            "The longer the custom pattern, the more",
            "computational work needed to find it."
        ]
        
        line_height = 28
        for i, line in enumerate(text_lines):
            color = (220, 220, 220)
            if line.startswith("•"):
                color = (0, 255, 255)  # Cyan for bullet points
            elif line and not line.startswith(" "):
                if i > 0 and not text_lines[i-1]:  # If preceded by an empty line
                    color = (255, 255, 0)  # Yellow for section headers
                
            text_surface = self.small_font.render(line, True, color)
            y_pos = rect.y + i * line_height
            self.screen.blit(text_surface, (rect.x, y_pos))
    
    def draw_info_page_2(self, rect):
        """Draw content for info page 2"""
        text_lines = [
            "How to Generate a Vanity Address:",
            "",
            "1. Click 'Generate Address' on the main menu",
            "",
            "2. Enter your desired prefix and/or suffix",
            "   • Prefix: Characters at the START of the address",
            "   • Suffix: Characters at the END of the address",
            "",
            "3. Set the number of addresses to generate",
            "",
            "4. Adjust the Iteration Complexity (16-28)",
            "   • Higher = Faster but uses more GPU memory",
            "   • Lower = Slower but uses less GPU memory",
            "",
            "5. Click Generate and wait for results"
        ]
        
        line_height = 28
        for i, line in enumerate(text_lines):
            color = (220, 220, 220)
            if line.startswith("•"):
                color = (0, 255, 255)  # Cyan for bullet points
            elif line.startswith("   •"):
                color = (255, 0, 255)  # Magenta for sub-bullets
            elif line and line[0].isdigit() and ". " in line:
                color = (255, 255, 0)  # Yellow for numbered steps
                
            text_surface = self.small_font.render(line, True, color)
            y_pos = rect.y + i * line_height
            self.screen.blit(text_surface, (rect.x, y_pos))
    
    def draw_info_page_3(self, rect):
        """Draw content for info page 3"""
        text_lines = [
            "Advanced Features:",
            "",
            "Device Selection:",
            "• Choose between multiple GPUs",
            "• View device specifications",
            "",
            "Settings:",
            "• Change the UI theme (CMYK colors)",
            "• Configure sound effects",
            "• Set custom output directory",
            "",
            "Export Options:",
            "• JSON format (for developer use)",
            "• HTML report (for easy viewing)",
            "",
            "Keys are saved securely on your device"
        ]
        
        line_height = 28
        for i, line in enumerate(text_lines):
            color = (220, 220, 220)
            if line.startswith("•"):
                color = (0, 255, 255)  # Cyan for bullet points
            elif line and not line.startswith(" ") and ":" in line:
                color = (255, 255, 0)  # Yellow for section headers
                
            text_surface = self.small_font.render(line, True, color)
            y_pos = rect.y + i * line_height
            self.screen.blit(text_surface, (rect.x, y_pos))

    def draw(self):
        """Draw the welcome screen"""
        self.screen.blit(self.background, (0, 0))

        if not self.intro_complete:
            self.draw_intro()
        else:
            # Draw logo with pulsing effect if not showing info
            if not self.show_info:
                # Add slight hover effect to logo
                pulse = abs(math.sin(self.animation_time * 2.0)) * 10
                logo_rect = self.logo_rect.copy()
                logo_rect.y -= int(pulse)
                self.screen.blit(self.logo, logo_rect)
                
                # Draw subtitle
                subtitle = "Retro Lo-Fi Edition v1.0"
                subtitle_surface = self.font.render(subtitle, True, (200, 200, 200))
                subtitle_rect = subtitle_surface.get_rect(
                    center=(self.width // 2, logo_rect.bottom + 20)
                )
                self.screen.blit(subtitle_surface, subtitle_rect)
                
                # Draw buttons
                self.generate_button.draw(self.screen)
                self.device_button.draw(self.screen)
                self.settings_button.draw(self.screen)
                self.info_button.draw(self.screen)
                self.exit_button.draw(self.screen)
                
                # Draw footer info
                self.draw_pulsing_text(
                    "Press [I] or click 'How To Use' for instructions", 
                    (self.width // 2, self.height - 40),
                    (180, 180, 180)
                )
            else:
                # Draw info panel when active
                self.draw_info_panel()
                
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
        # Skip events if intro animation is still playing
        if not self.intro_complete:
            # Allow spacebar or mouse click to skip intro
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.intro_complete = True
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.intro_complete = True
                return True
            return False
            
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
            self.prev_button.handle_event(event)
            self.close_info_button.handle_event(event)
            self.next_button.handle_event(event)
            return True
            
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
        Run the welcome screen loop
        
        Returns:
            str: Result of screen interaction (e.g., 'generate', 'settings', 'exit')
        """
        clock = pygame.time.Clock()
        
        while not self.exit_screen:
            # Calculate delta time for animations
            delta_time = clock.tick(60) / 1000.0  # Convert to seconds
            
            # Update animations
            self.update(delta_time)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
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