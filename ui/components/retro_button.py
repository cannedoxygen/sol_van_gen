"""
RetroButton component for the CMYK lo-fi UI
A custom styled button with retro aesthetics
"""

import pygame
import pygame.freetype
import os
from typing import Callable, Tuple, Union, Optional

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

class RetroButton:
    """
    A retro-styled button with CMYK color scheme and pixel aesthetics
    """
    
    # Default color constants
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    YELLOW = (255, 255, 0)
    KEY_BLACK = (30, 30, 30)
    WHITE = (255, 255, 255)
    GRAY = (120, 120, 120)
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        action: Callable = None,
        color_scheme: str = "cyan",
        font_size: int = 12,
        sound_enabled: bool = True,
        border_width: int = 3,
        corner_radius: int = 5,
        shadow_offset: int = 4,
        glow_effect: bool = True
    ):
        """
        Initialize a new RetroButton instance
        
        Args:
            x: X coordinate position
            y: Y coordinate position
            width: Button width
            height: Button height
            text: Button text
            action: Callback function when button is clicked
            color_scheme: Color theme ('cyan', 'magenta', 'yellow', 'white')
            font_size: Size of the button text
            sound_enabled: Whether to play sound effects
            border_width: Width of button border
            corner_radius: Radius of rounded corners
            shadow_offset: Offset of drop shadow
            glow_effect: Whether to apply a glow effect
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        self.sound_enabled = sound_enabled
        self.border_width = border_width
        self.corner_radius = corner_radius
        self.shadow_offset = shadow_offset
        self.glow_effect = glow_effect
        
        # Button state
        self.hovered = False
        self.pressed = False
        self.disabled = False
        self.animation_state = 0  # For animated effects
        
        # Set colors based on scheme
        self.set_color_scheme(color_scheme)
        
        # Load font
        self.font_size = font_size
        self.font = self.load_font()
        
        # Load sound effects
        self.hover_sound = None
        self.click_sound = None
        self.load_sounds()
    
    def set_color_scheme(self, scheme: str):
        """Set button colors based on the selected scheme"""
        if scheme == "cyan":
            self.bg_color = (0, 200, 200)
            self.hover_color = (0, 220, 220)
            self.active_color = (0, 180, 180)
            self.border_color = (0, 255, 255)
            self.text_color = self.KEY_BLACK
            self.disabled_color = (100, 150, 150)
            self.shadow_color = (0, 100, 100, 150)
            self.glow_color = (0, 255, 255, 100)
            
        elif scheme == "magenta":
            self.bg_color = (200, 0, 200)
            self.hover_color = (220, 0, 220)
            self.active_color = (180, 0, 180)
            self.border_color = (255, 0, 255)
            self.text_color = self.WHITE
            self.disabled_color = (150, 100, 150)
            self.shadow_color = (100, 0, 100, 150)
            self.glow_color = (255, 0, 255, 100)
            
        elif scheme == "yellow":
            self.bg_color = (200, 200, 0)
            self.hover_color = (220, 220, 0)
            self.active_color = (180, 180, 0)
            self.border_color = (255, 255, 0)
            self.text_color = self.KEY_BLACK
            self.disabled_color = (150, 150, 100)
            self.shadow_color = (100, 100, 0, 150)
            self.glow_color = (255, 255, 0, 100)
            
        else:  # Default white
            self.bg_color = (200, 200, 200)
            self.hover_color = (220, 220, 220)
            self.active_color = (180, 180, 180)
            self.border_color = (255, 255, 255)
            self.text_color = self.KEY_BLACK
            self.disabled_color = (150, 150, 150)
            self.shadow_color = (80, 80, 80, 150)
            self.glow_color = (255, 255, 255, 100)
    
    def load_font(self) -> pygame.freetype.Font:
        """Load the pixel font for the button"""
        try:
            font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "pixel_font.ttf")
            return pygame.freetype.Font(font_path, self.font_size)
        except (pygame.error, FileNotFoundError):
            # Fall back to default font if custom font not found
            return pygame.freetype.SysFont("monospace", self.font_size)
    
    def load_sounds(self):
        """Load button sound effects"""
        try:
            if self.sound_enabled:
                hover_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "keypress.wav")
                click_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "success.wav")
                
                self.hover_sound = pygame.mixer.Sound(hover_sound_path)
                self.hover_sound.set_volume(0.3)
                
                self.click_sound = pygame.mixer.Sound(click_sound_path)
                self.click_sound.set_volume(0.5)
        except (pygame.error, FileNotFoundError):
            # Silently fail if sounds can't be loaded
            self.sound_enabled = False
    
    def draw(self, surface: pygame.Surface):
        """
        Draw the button on the specified surface
        
        Args:
            surface: Pygame surface to draw on
        """
        # Determine current colors based on state
        if self.disabled:
            current_bg = self.disabled_color
            current_border = self.disabled_color
        elif self.pressed:
            current_bg = self.active_color
            current_border = self.border_color
        elif self.hovered:
            current_bg = self.hover_color
            current_border = self.border_color
        else:
            current_bg = self.bg_color
            current_border = self.border_color
        
        # Create shadow surface if enabled
        if self.shadow_offset > 0 and not self.pressed and not self.disabled:
            shadow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(
                shadow_surface, 
                self.shadow_color,
                (0, 0, self.width, self.height),
                border_radius=self.corner_radius
            )
            surface.blit(shadow_surface, (self.x + self.shadow_offset, self.y + self.shadow_offset))
        
        # Create glow effect if enabled
        if self.glow_effect and self.hovered and not self.disabled:
            glow_size = 10
            glow_surface = pygame.Surface(
                (self.width + glow_size*2, self.height + glow_size*2), 
                pygame.SRCALPHA
            )
            
            # Draw multiple transparent rects for glow effect
            for i in range(glow_size, 0, -2):
                alpha = 20 - (i * 2)
                if alpha < 0:
                    alpha = 0
                glow_color = (*self.glow_color[:3], alpha)
                pygame.draw.rect(
                    glow_surface, 
                    glow_color,
                    (
                        glow_size - i,
                        glow_size - i,
                        self.width + i*2,
                        self.height + i*2
                    ),
                    border_radius=self.corner_radius + i
                )
            
            surface.blit(
                glow_surface, 
                (self.x - glow_size, self.y - glow_size)
            )
        
        # Draw button with border
        button_pos = (self.x, self.y) if not self.pressed else (self.x + 2, self.y + 2)
        
        # Draw border
        pygame.draw.rect(
            surface, 
            current_border,
            (*button_pos, self.width, self.height),
            border_radius=self.corner_radius
        )
        
        # Draw button background (slightly smaller to create border effect)
        pygame.draw.rect(
            surface, 
            current_bg,
            (
                button_pos[0] + self.border_width,
                button_pos[1] + self.border_width,
                self.width - self.border_width*2,
                self.height - self.border_width*2
            ),
            border_radius=max(0, self.corner_radius - self.border_width)
        )
        
        # Draw text
        text_surface, text_rect = self.font.render(
            self.text, 
            self.text_color if not self.disabled else self.GRAY
        )
        
        # Center text on button
        text_x = button_pos[0] + (self.width - text_rect.width) // 2
        text_y = button_pos[1] + (self.height - text_rect.height) // 2
        
        # Draw text with a subtle pixel shift when pressed
        if self.pressed:
            text_x += 1
            text_y += 1
            
        surface.blit(text_surface, (text_x, text_y))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the button
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if action was triggered, False otherwise
        """
        if self.disabled:
            return False
            
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is over button
        is_over = (
            self.x <= mouse_pos[0] <= self.x + self.width and
            self.y <= mouse_pos[1] <= self.y + self.height
        )
        
        # Handle mouse over state (hover)
        if is_over and not self.hovered:
            self.hovered = True
            if self.sound_enabled and self.hover_sound:
                self.hover_sound.play()
        elif not is_over:
            self.hovered = False
        
        # Handle mouse button events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and is_over:
            self.pressed = True
            return False
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            
            # If button was pressed and mouse is still over it, trigger the action
            if was_pressed and is_over and self.action:
                if self.sound_enabled and self.click_sound:
                    self.click_sound.play()
                self.action()
                return True
                
        return False
    
    def set_position(self, x: int, y: int):
        """Set button position"""
        self.x = x
        self.y = y
    
    def set_text(self, text: str):
        """Set button text"""
        self.text = text
    
    def set_disabled(self, disabled: bool):
        """Enable or disable the button"""
        self.disabled = disabled
    
    def set_action(self, action: Callable):
        """Set the button action callback"""
        self.action = action
    
    def get_rect(self) -> pygame.Rect:
        """Get the button's rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


# Example usage
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("RetroButton Test")
    clock = pygame.time.Clock()
    
    def button_action():
        print("Button clicked!")
    
    # Create test buttons with different color schemes
    cyan_button = RetroButton(100, 100, 200, 50, "Cyan Button", button_action, "cyan")
    magenta_button = RetroButton(100, 200, 200, 50, "Magenta Button", button_action, "magenta")
    yellow_button = RetroButton(100, 300, 200, 50, "Yellow Button", button_action, "yellow")
    
    # Create a disabled button for testing
    disabled_button = RetroButton(100, 400, 200, 50, "Disabled Button", button_action, "cyan")
    disabled_button.set_disabled(True)
    
    running = True
    while running:
        screen.fill((40, 40, 40))  # Dark background
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle button events
            cyan_button.handle_event(event)
            magenta_button.handle_event(event)
            yellow_button.handle_event(event)
            disabled_button.handle_event(event)
        
        # Draw buttons
        cyan_button.draw(screen)
        magenta_button.draw(screen)
        yellow_button.draw(screen)
        disabled_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()