"""
Welcome screen for the Solana Vanity Address Generator
Displays intro animation and main menu with retro CMYK aesthetics
"""

import pygame
import os
import random
import time
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
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.on_menu_select = on_menu_select
        
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
    
    def load_assets(self):
        """Load screen assets"""
        # Load background image
        try:
            bg_path = os.path.join(PROJECT_ROOT, "assets", "images", "background.png")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except (pygame.error, FileNotFoundError):
            # Create a fallback background if image not found
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
            
        # Load logo
        try:
            logo_path = os.path.join(PROJECT_ROOT, "assets", "images", "logo.png")
            self.logo = pygame.image.load(logo_path).convert_alpha()
            logo_width = int(self.width * 0.6)
            logo_height = int(logo_width * self.logo.get_height() / self.logo.get_width())
            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
            self.logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 4))
        except (pygame.error, FileNotFoundError):
            # Create a fallback logo
            self.logo = self.create_fallback_logo()
            self.logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 4))
        
        # Load font
        try:
            font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "pixel_font.ttf")
            self.font = pygame.font.Font(font_path, 24)
            self.title_font = pygame.font.Font(font_path, 36)
        except (pygame.error, FileNotFoundError):
            # Fallback to system font
            self.font = pygame.font.SysFont("monospace", 24)
            self.title_font = pygame.font.SysFont("monospace", 36)
        
        # Load sounds
        try:
            self.intro_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "assets", "sounds", "success.wav"))
        except (pygame.error, FileNotFoundError):
            self.intro_sound = None
    
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
    
    def create_buttons(self):
        """Create menu buttons"""
        button_width = 300
        button_height = 50
        button_spacing = 20
        start_y = self.height // 2 + 50
        
        self.buttons = {
            "generate": RetroButton(
                self.width // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "Generate Vanity Address",
                lambda: self.on_menu_select("generate"),
                "cyan"
            ),
            "devices": RetroButton(
                self.width // 2 - button_width // 2,
                start_y + button_height + button_spacing,
                button_width,
                button_height,
                "Show Available Devices",
                lambda: self.on_menu_select("devices"),
                "magenta"
            ),
            "settings": RetroButton(
                self.width // 2 - button_width // 2,
                start_y + (button_height + button_spacing) * 2,
                button_width,
                button_height,
                "Settings",
                lambda: self.on_menu_select("settings"),
                "yellow"
            ),
            "exit": RetroButton(
                self.width // 2 - button_width // 2,
                start_y + (button_height + button_spacing) * 3,
                button_width,
                button_height,
                "Exit",
                lambda: self.on_menu_select("exit"),
                "white"
            )
        }
    
    def setup_intro_animation(self):
        """Setup state for intro animation"""
        # Animation timing
        self.intro_duration = 3.0  # seconds
        self.logo_fade_in_duration = 1.5
        self.buttons_appear_time = 2.0
        
        # Logo animation state
        self.logo_alpha = 0
        self.offset_y = -100
        
        # VHS scan line effect
        self.scan_line_pos = 0
        
        # Glitch effect
        self.glitch_lines = []
        self.next_glitch_time = random.uniform(0.5, 1.5)
        
        # Play intro sound
        if self.intro_sound and not self.intro_complete:
            self.intro_sound.play()
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        # Skip intro on any key/click
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN) and not self.intro_complete:
            self.intro_complete = True
            return
        
        # Handle button events
        if self.intro_complete:
            for button in self.buttons.values():
                button.handle_event(event)
    
    def update(self, delta_time: float):
        """
        Update screen state
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        current_time = time.time() - self.start_time
        
        # Update intro animation
        if not self.intro_complete:
            # Calculate animation progress
            progress = min(current_time / self.intro_duration, 1.0)
            
            # Update logo fade-in and position
            if current_time < self.logo_fade_in_duration:
                fade_progress = current_time / self.logo_fade_in_duration
                self.logo_alpha = int(255 * fade_progress)
                self.offset_y = -100 * (1 - fade_progress)
            else:
                self.logo_alpha = 255
                self.offset_y = 0
            
            # Auto-complete intro after duration
            if progress >= 1.0:
                self.intro_complete = True
            
            # Update VHS scan line effect
            self.scan_line_pos = (self.scan_line_pos + int(200 * delta_time)) % (self.height * 2)
            
            # Update glitch effect
            if current_time >= self.next_glitch_time:
                # Create new glitch
                self.glitch_lines = []
                num_lines = random.randint(1, 5)
                
                for _ in range(num_lines):
                    line_y = random.randint(0, self.height)
                    line_height = random.randint(2, 10)
                    x_offset = random.randint(-20, 20)
                    
                    self.glitch_lines.append({
                        'y': line_y,
                        'height': line_height,
                        'x_offset': x_offset,
                        'duration': random.uniform(0.05, 0.2)
                    })
                
                self.next_glitch_time = current_time + random.uniform(0.5, 1.5)
            
            # Update duration of existing glitch lines
            for line in self.glitch_lines[:]:
                line['duration'] -= delta_time
                if line['duration'] <= 0:
                    self.glitch_lines.remove(line)
        
        # Check if we should show buttons
        if current_time >= self.buttons_appear_time or self.intro_complete:
            # Update buttons
            for button in self.buttons.values():
                # Add subtle hover animation when intro is complete
                if self.intro_complete:
                    hover_offset = int(math.sin(current_time * 4) * 2)
                    button.shadow_offset = 4 + hover_offset
    
    def draw(self):
        """Draw screen elements"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Apply VHS style scan lines
        self.draw_scan_lines()
        
        # Draw logo with current alpha
        if not self.intro_complete:
            # Create a copy with current alpha
            logo_with_alpha = self.logo.copy()
            logo_with_alpha.set_alpha(self.logo_alpha)
            
            # Position with vertical offset
            logo_pos = (self.logo_rect.x, self.logo_rect.y + self.offset_y)
            self.screen.blit(logo_with_alpha, logo_pos)
            
            # Draw glitch effect
            self.draw_glitch_effect()
        else:
            # Logo is fully visible in normal state
            self.screen.blit(self.logo, self.logo_rect)
        
        # Draw buttons if intro is complete or we've reached the button appear time
        current_time = time.time() - self.start_time
        if self.intro_complete or current_time >= self.buttons_appear_time:
            for button in self.buttons.values():
                button.draw(self.screen)
        
        # Draw version and footer
        version_text = self.font.render("v1.0 | Retro Lo-Fi Edition", True, (180, 180, 180))
        version_rect = version_text.get_rect(bottomright=(self.width - 20, self.height - 20))
        self.screen.blit(version_text, version_rect)
        
        # Draw GPU info
        try:
            import pyopencl as cl
            platform = cl.get_platforms()[0]
            devices = platform.get_devices()
            device_name = devices[0].name
            gpu_text = self.font.render(f"GPU: {device_name[:30]}", True, (150, 150, 150))
            gpu_rect = gpu_text.get_rect(bottomleft=(20, self.height - 20))
            self.screen.blit(gpu_text, gpu_rect)
        except:
            pass
    
    def draw_scan_lines(self):
        """Draw CRT/VHS scan lines effect"""
        scan_line_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        line_spacing = 4
        line_alpha = 30  # Transparency of scan lines
        
        for y in range(0, self.height * 2, line_spacing):
            # Calculate current position with animation
            current_y = (y + self.scan_line_pos) % (self.height * 2)
            if current_y >= self.height:
                continue
                
            # Draw a semi-transparent line
            pygame.draw.line(
                scan_line_surface,
                (0, 0, 0, line_alpha),
                (0, current_y),
                (self.width, current_y)
            )
        
        self.screen.blit(scan_line_surface, (0, 0))
    
    def draw_glitch_effect(self):
        """Draw VHS glitch effect during intro"""
        # Skip if no glitch lines or intro is complete
        if not self.glitch_lines or self.intro_complete:
            return
        
        # Create a copy of the screen for glitch manipulation
        screen_copy = self.screen.copy()
        
        for line in self.glitch_lines:
            y = line['y']
            height = line['height']
            x_offset = line['x_offset']
            
            # Define the line rect
            line_rect = pygame.Rect(0, y, self.width, height)
            
            try:
                # Get the portion of screen
                line_surf = screen_copy.subsurface(line_rect).copy()
                
                # Clear the original area
                pygame.draw.rect(self.screen, (0, 0, 0), line_rect)
                
                # Draw with offset
                offset_rect = line_rect.copy()
                offset_rect.x += x_offset
                
                # Ensure we don't draw outside the screen
                if offset_rect.x < 0:
                    line_surf = line_surf.subsurface((-offset_rect.x, 0, line_surf.get_width() + offset_rect.x, height))
                    offset_rect.width = line_surf.get_width()
                    offset_rect.x = 0
                elif offset_rect.right > self.width:
                    line_surf = line_surf.subsurface((0, 0, self.width - offset_rect.x, height))
                    offset_rect.width = line_surf.get_width()
                
                self.screen.blit(line_surf, offset_rect)
            except ValueError:
                # Skip if subsurface is out of bounds
                pass
    
    def draw_cmyk_overlay(self):
        """Draw a CMYK color overlay for retro effect"""
        overlay_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Create subtle CMYK color channels that are slightly offset
        cyan_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        magenta_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        yellow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Fill with very transparent colors
        cyan_surface.fill((0, 255, 255, 10))
        magenta_surface.fill((255, 0, 255, 10))
        yellow_surface.fill((255, 255, 0, 10))
        
        # Apply each with slight offset
        overlay_surface.blit(cyan_surface, (2, 0))
        overlay_surface.blit(magenta_surface, (0, 0))
        overlay_surface.blit(yellow_surface, (-2, 0))
        
        self.screen.blit(overlay_surface, (0, 0))
    
    def run(self) -> str:
        """
        Run the welcome screen loop
        
        Returns:
            str: Selected menu option or 'exit'
        """
        clock = pygame.time.Clock()
        last_time = time.time()
        
        # Main screen loop
        while not self.exit_screen:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                
                self.handle_event(event)
            
            # Update and draw
            self.update(delta_time)
            self.draw()
            
            pygame.display.flip()
            clock.tick(60)
        
        return "exit"
    
    def set_exit(self):
        """Signal the screen to exit"""
        self.exit_screen = True

# For standalone testing
if __name__ == "__main__":
    import math  # Required for hover animation
    
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Solana Vanity Generator - Welcome")
    
    def on_menu_select(option):
        print(f"Selected menu option: {option}")
        if option == "exit":
            pygame.quit()
            exit()
    
    welcome = WelcomeScreen(screen, on_menu_select)
    welcome.run()