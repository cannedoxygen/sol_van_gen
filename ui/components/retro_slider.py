"""
RetroSlider component for the CMYK lo-fi UI
A custom styled slider with retro aesthetics
"""

import pygame
import math
import os
from typing import Callable, Optional, Tuple

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

class RetroSlider:
    """
    A retro-styled slider with CMYK color scheme and pixel aesthetics
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
        label: str = "",
        min_value: int = 0,
        max_value: int = 100,
        initial_value: int = 50,
        step: int = 1,
        on_change: Callable[[int], None] = None,
        color_scheme: str = "cyan",
        sound_enabled: bool = True
    ):
        """
        Initialize a new RetroSlider instance
        
        Args:
            x: X coordinate position
            y: Y coordinate position
            width: Slider width
            height: Slider height
            label: Text label for the slider
            min_value: Minimum value
            max_value: Maximum value
            initial_value: Initial slider value
            step: Step size for incrementing/decrementing
            on_change: Callback when value changes
            color_scheme: Color theme ('cyan', 'magenta', 'yellow', 'white')
            sound_enabled: Whether to play sound effects
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.value = max(min_value, min(max_value, initial_value))  # Clamp to range
        self.step = step
        self.on_change = on_change
        self.sound_enabled = sound_enabled
        
        # Slider state
        self.dragging = False
        self.hovered = False
        self.hover_alpha = 0
        self.glow_effect = 0
        
        # Animation properties
        self.tick_positions = []
        self.anim_offset = 0
        self.scan_line_offset = 0
        
        # Calculate handle dimensions and position
        self.handle_width = 16
        self.handle_height = int(height * 1.4)
        self.track_height = height // 3
        self.handle_y = y + (height - self.handle_height) // 2
        self.update_handle_position()
        
        # Set colors based on scheme
        self.set_color_scheme(color_scheme)
        
        # Load font
        self.font_size = 16
        self.font = self.load_font()
        
        # Load sound effects
        self.tick_sound = None
        self.drag_sound = None
        self.load_sounds()
        
        # Generate tick positions
        self.generate_tick_positions()
    
    def set_color_scheme(self, scheme: str):
        """Set slider colors based on the selected scheme"""
        if scheme == "cyan":
            self.track_bg_color = (20, 60, 60)
            self.track_fill_color = (0, 180, 180)
            self.handle_color = (0, 220, 220)
            self.handle_border_color = (0, 255, 255)
            self.tick_color = (0, 100, 100)
            self.label_color = (200, 255, 255)
            self.value_color = (0, 255, 255)
            self.hover_color = (0, 255, 255, 30)  # Semi-transparent cyan
            
        elif scheme == "magenta":
            self.track_bg_color = (60, 20, 60)
            self.track_fill_color = (180, 0, 180)
            self.handle_color = (220, 0, 220)
            self.handle_border_color = (255, 0, 255)
            self.tick_color = (100, 0, 100)
            self.label_color = (255, 200, 255)
            self.value_color = (255, 0, 255)
            self.hover_color = (255, 0, 255, 30)  # Semi-transparent magenta
            
        elif scheme == "yellow":
            self.track_bg_color = (60, 60, 20)
            self.track_fill_color = (180, 180, 0)
            self.handle_color = (220, 220, 0)
            self.handle_border_color = (255, 255, 0)
            self.tick_color = (100, 100, 0)
            self.label_color = (255, 255, 200)
            self.value_color = (255, 255, 0)
            self.hover_color = (255, 255, 0, 30)  # Semi-transparent yellow
            
        else:  # Default white
            self.track_bg_color = (50, 50, 50)
            self.track_fill_color = (150, 150, 150)
            self.handle_color = (200, 200, 200)
            self.handle_border_color = (255, 255, 255)
            self.tick_color = (100, 100, 100)
            self.label_color = (220, 220, 220)
            self.value_color = (255, 255, 255)
            self.hover_color = (255, 255, 255, 30)  # Semi-transparent white
    
    def load_font(self) -> pygame.font.Font:
        """Load the pixel font for the slider"""
        try:
            font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "pixel_font.ttf")
            return pygame.font.Font(font_path, self.font_size)
        except (pygame.error, FileNotFoundError):
            # Fall back to default font if custom font not found
            return pygame.font.SysFont("monospace", self.font_size)
    
    def load_sounds(self):
        """Load slider sound effects"""
        try:
            if self.sound_enabled:
                tick_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "keypress.wav")
                drag_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "success.wav")
                
                self.tick_sound = pygame.mixer.Sound(tick_sound_path)
                self.tick_sound.set_volume(0.1)
                
                self.drag_sound = pygame.mixer.Sound(drag_sound_path)
                self.drag_sound.set_volume(0.2)
        except (pygame.error, FileNotFoundError):
            # Silently fail if sounds can't be loaded
            self.sound_enabled = False
    
    def update_handle_position(self):
        """Update the handle position based on current value"""
        value_range = self.max_value - self.min_value
        if value_range > 0:
            value_ratio = (self.value - self.min_value) / value_range
            self.handle_x = int(self.x + value_ratio * (self.width - self.handle_width))
        else:
            self.handle_x = self.x
    
    def generate_tick_positions(self):
        """Generate positions for tick marks"""
        self.tick_positions = []
        
        # Maximum number of ticks to show
        max_ticks = min(10, self.max_value - self.min_value + 1)
        
        if max_ticks > 1:
            # Calculate tick interval
            tick_interval = (self.max_value - self.min_value) / (max_ticks - 1)
            
            for i in range(max_ticks):
                tick_value = self.min_value + i * tick_interval
                value_ratio = (tick_value - self.min_value) / (self.max_value - self.min_value)
                tick_x = int(self.x + value_ratio * self.width)
                self.tick_positions.append((tick_x, tick_value))
    
    def set_value(self, value: int, trigger_callback: bool = True):
        """
        Set the slider value
        
        Args:
            value: New value (will be clamped to slider range)
            trigger_callback: Whether to trigger the on_change callback
        """
        # Clamp value to range and snap to steps
        value = max(self.min_value, min(self.max_value, value))
        
        # Snap to nearest step
        if self.step > 0:
            value = round((value - self.min_value) / self.step) * self.step + self.min_value
            # Make sure we don't exceed max_value due to rounding
            value = min(value, self.max_value)
        
        if value != self.value:
            old_value = self.value
            self.value = value
            self.update_handle_position()
            
            # Play tick sound on discrete changes
            if self.sound_enabled and self.tick_sound and abs(old_value - value) >= self.step:
                self.tick_sound.play()
            
            # Trigger callback
            if trigger_callback and self.on_change:
                self.on_change(self.value)
    
    def get_value(self) -> int:
        """Get the current slider value"""
        return self.value
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the slider
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is over handle or track
        handle_rect = pygame.Rect(self.handle_x, self.handle_y, self.handle_width, self.handle_height)
        track_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Update hover state
        was_hovered = self.hovered
        self.hovered = handle_rect.collidepoint(mouse_pos) or track_rect.collidepoint(mouse_pos)
        
        # Play sound on hover start
        if not was_hovered and self.hovered and self.sound_enabled and self.tick_sound:
            self.tick_sound.play()
        
        # Handle mouse button events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handle_rect.collidepoint(mouse_pos):
                # Start dragging handle
                self.dragging = True
                
                # Play drag start sound
                if self.sound_enabled and self.drag_sound:
                    self.drag_sound.play()
                
                return True
            elif track_rect.collidepoint(mouse_pos):
                # Click on track - move handle to that position
                value_ratio = (mouse_pos[0] - self.x) / self.width
                new_value = self.min_value + value_ratio * (self.max_value - self.min_value)
                self.set_value(int(new_value))
                
                # Start dragging
                self.dragging = True
                
                # Play drag start sound
                if self.sound_enabled and self.drag_sound:
                    self.drag_sound.play()
                
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update value based on mouse position
            value_ratio = (mouse_pos[0] - self.x) / self.width
            value_ratio = max(0, min(1, value_ratio))  # Clamp to 0-1
            new_value = self.min_value + value_ratio * (self.max_value - self.min_value)
            self.set_value(int(new_value))
            return True
        
        return False
    
    def update(self, delta_time: float):
        """
        Update slider animation effects
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Update hover animation
        target_alpha = 150 if self.hovered or self.dragging else 0
        alpha_diff = target_alpha - self.hover_alpha
        self.hover_alpha += alpha_diff * delta_time * 5  # Smooth transition
        
        # Update glow effect
        if self.hovered or self.dragging:
            self.glow_effect = (self.glow_effect + delta_time * 2) % (math.pi * 2)
        
        # Update scan line animation
        self.scan_line_offset = (self.scan_line_offset + int(100 * delta_time)) % self.height
        
        # Update track animation
        self.anim_offset = (self.anim_offset + delta_time * 20) % 20
    
    def draw(self, surface: pygame.Surface):
        """
        Draw the slider on the specified surface
        
        Args:
            surface: Pygame surface to draw on
        """
        # Draw label if provided
        if self.label:
            label_surface = self.font.render(self.label, True, self.label_color)
            label_x = self.x
            label_y = self.y - label_surface.get_height() - 5
            surface.blit(label_surface, (label_x, label_y))
        
        # Draw track background
        track_rect = pygame.Rect(
            self.x,
            self.y + (self.height - self.track_height) // 2,
            self.width,
            self.track_height
        )
        pygame.draw.rect(
            surface,
            self.track_bg_color,
            track_rect,
            border_radius=self.track_height // 2
        )
        
        # Draw filled track portion
        if self.value > self.min_value:
            fill_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.width)
            fill_rect = pygame.Rect(
                self.x,
                self.y + (self.height - self.track_height) // 2,
                fill_width,
                self.track_height
            )
            pygame.draw.rect(
                surface,
                self.track_fill_color,
                fill_rect,
                border_radius=self.track_height // 2
            )
            
            # Draw animated track fill pattern
            pattern_surface = pygame.Surface((fill_width, self.track_height), pygame.SRCALPHA)
            pattern_segment_width = 10
            
            for i in range(0, fill_width + pattern_segment_width, pattern_segment_width * 2):
                segment_x = int(i - self.anim_offset) % (fill_width + pattern_segment_width * 2) - pattern_segment_width
                if segment_x < fill_width:
                    segment_width = min(pattern_segment_width, fill_width - segment_x)
                    if segment_x >= 0 and segment_width > 0:
                        pygame.draw.rect(
                            pattern_surface,
                            (255, 255, 255, 30),  # Semi-transparent white
                            (segment_x, 0, segment_width, self.track_height)
                        )
            
            surface.blit(pattern_surface, fill_rect)
        
        # Draw tick marks
        for tick_x, tick_value in self.tick_positions:
            # Draw tick mark
            tick_height = self.track_height * 1.5
            tick_y = self.y + (self.height - tick_height) // 2
            
            pygame.draw.line(
                surface,
                self.tick_color,
                (tick_x, tick_y),
                (tick_x, tick_y + tick_height),
                1
            )
            
            # Draw tick value
            if tick_value.is_integer():
                tick_label = str(int(tick_value))
            else:
                tick_label = f"{tick_value:.1f}"
                
            value_surface = self.font.render(tick_label, True, self.tick_color)
            value_x = tick_x - value_surface.get_width() // 2
            value_y = tick_y + tick_height + 2
            surface.blit(value_surface, (value_x, value_y))
        
        # Draw slider handle
        handle_rect = pygame.Rect(self.handle_x, self.handle_y, self.handle_width, self.handle_height)
        
        # Draw handle shadow if hovered or dragging
        if self.hovered or self.dragging:
            shadow_size = 5 + int(math.sin(self.glow_effect) * 2)
            shadow_rect = handle_rect.inflate(shadow_size * 2, shadow_size * 2)
            shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
            
            # Create a gradient shadow effect
            for i in range(shadow_size, 0, -1):
                alpha = int(40 * (i / shadow_size))
                shadow_color = (*self.handle_border_color[:3], alpha)
                shadow_rect_shrink = shadow_rect.inflate(-i*2, -i*2)
                shadow_rect_pos = (shadow_rect_shrink.width // 2, shadow_rect_shrink.height // 2)
                pygame.draw.rect(
                    shadow_surface,
                    shadow_color,
                    pygame.Rect(
                        shadow_size - i,
                        shadow_size - i,
                        shadow_rect_shrink.width,
                        shadow_rect_shrink.height
                    ),
                    border_radius=4
                )
            
            # Draw shadow
            shadow_pos = (handle_rect.x - shadow_size, handle_rect.y - shadow_size)
            surface.blit(shadow_surface, shadow_pos)
        
        # Draw handle background
        pygame.draw.rect(
            surface,
            self.handle_color,
            handle_rect,
            border_radius=4
        )
        
        # Draw handle border
        pygame.draw.rect(
            surface,
            self.handle_border_color,
            handle_rect,
            border_radius=4,
            width=2
        )
        
        # Draw scan line effect on handle
        if self.hovered or self.dragging:
            scan_y = (self.handle_y + self.scan_line_offset) % (self.handle_y + self.handle_height)
            if scan_y >= self.handle_y and scan_y < self.handle_y + self.handle_height:
                pygame.draw.line(
                    surface,
                    (255, 255, 255, 100),  # Semi-transparent white
                    (self.handle_x, scan_y),
                    (self.handle_x + self.handle_width, scan_y),
                    1
                )
        
        # Draw current value
        value_text = str(self.value)
        value_surface = self.font.render(value_text, True, self.value_color)
        
        # Position value text at the top right of the slider
        value_x = self.x + self.width - value_surface.get_width()
        value_y = self.y - value_surface.get_height() - 5
        
        surface.blit(value_surface, (value_x, value_y))
    
    def get_rect(self) -> pygame.Rect:
        """Get the slider's rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


# Example usage
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("RetroSlider Test")
    clock = pygame.time.Clock()
    
    def on_slider_change(value):
        print(f"Slider value changed to: {value}")
    
    # Create test sliders with different color schemes
    cyan_slider = RetroSlider(100, 100, 600, 30, "Cyan Slider", 0, 100, 50, on_change=on_slider_change, color_scheme="cyan")
    magenta_slider = RetroSlider(100, 200, 600, 30, "Magenta Slider", 0, 10, 5, step=1, on_change=on_slider_change, color_scheme="magenta")
    yellow_slider = RetroSlider(100, 300, 600, 30, "Yellow Slider", 16, 28, 24, step=1, on_change=on_slider_change, color_scheme="yellow")
    white_slider = RetroSlider(100, 400, 600, 30, "White Slider", -50, 50, 0, step=10, on_change=on_slider_change, color_scheme="white")
    
    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0  # Delta time in seconds
        
        screen.fill((40, 40, 40))  # Dark background
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle slider events
            cyan_slider.handle_event(event)
            magenta_slider.handle_event(event)
            yellow_slider.handle_event(event)
            white_slider.handle_event(event)
        
        # Update sliders
        cyan_slider.update(delta_time)
        magenta_slider.update(delta_time)
        yellow_slider.update(delta_time)
        white_slider.update(delta_time)
        
        # Draw sliders
        cyan_slider.draw(screen)
        magenta_slider.draw(screen)
        yellow_slider.draw(screen)
        white_slider.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()