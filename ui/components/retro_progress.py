"""
RetroProgress component for the CMYK lo-fi UI
A custom styled progress bar with retro aesthetics
"""

import pygame
import math
import random
import os
from typing import Tuple, Optional, List

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

class RetroProgress:
    """
    A retro-styled progress bar with CMYK color scheme and VHS/glitch aesthetics
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
        color_scheme: str = "cyan",
        border_width: int = 2,
        corner_radius: int = 4,
        segment_count: int = 20,
        show_percentage: bool = True,
        show_glitch: bool = True,
        animate: bool = True
    ):
        """
        Initialize a new RetroProgress instance
        
        Args:
            x: X coordinate position
            y: Y coordinate position
            width: Progress bar width
            height: Progress bar height
            color_scheme: Color theme ('cyan', 'magenta', 'yellow', 'white', 'cmyk')
            border_width: Width of progress bar border
            corner_radius: Radius of rounded corners
            segment_count: Number of segments for segmented progress bar
            show_percentage: Whether to display the percentage text
            show_glitch: Whether to show glitch effects
            animate: Whether to animate the progress bar
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border_width = border_width
        self.corner_radius = corner_radius
        self.segment_count = segment_count
        self.show_percentage = show_percentage
        self.show_glitch = show_glitch
        self.animate = animate
        
        # Progress state
        self.progress = 0.0  # 0.0 to 1.0
        self.target_progress = 0.0
        self.animation_speed = 0.02
        
        # VHS/glitch effect state
        self.glitch_timer = 0
        self.glitch_interval = random.uniform(2.0, 5.0)  # Time between glitches
        self.glitch_duration = 0
        self.glitch_segments = []
        self.noise_offset = 0
        
        # Set colors based on scheme
        self.set_color_scheme(color_scheme)
        
        # Animation properties
        self.anim_offset = 0
        self.anim_speed = 2  # Pixels per frame
        self.scan_line_offset = 0
        
        # Create noise texture for VHS effect
        self.noise_surface = self.create_noise_texture(width, height)
    
    def set_color_scheme(self, scheme: str):
        """Set progress bar colors based on the selected scheme"""
        if scheme == "cyan":
            self.bg_color = (20, 50, 50)
            self.border_color = (0, 200, 200)
            self.empty_color = (0, 60, 60)
            self.fill_colors = [(0, 150, 150), (0, 255, 255)]
            self.text_color = self.WHITE
            
        elif scheme == "magenta":
            self.bg_color = (50, 20, 50)
            self.border_color = (200, 0, 200)
            self.empty_color = (60, 0, 60)
            self.fill_colors = [(150, 0, 150), (255, 0, 255)]
            self.text_color = self.WHITE
            
        elif scheme == "yellow":
            self.bg_color = (50, 50, 20)
            self.border_color = (200, 200, 0)
            self.empty_color = (60, 60, 0)
            self.fill_colors = [(150, 150, 0), (255, 255, 0)]
            self.text_color = self.WHITE
            
        elif scheme == "cmyk":
            self.bg_color = (30, 30, 30)
            self.border_color = (220, 220, 220)
            self.empty_color = (50, 50, 50)
            self.fill_colors = [(0, 255, 255), (255, 0, 255), (255, 255, 0), (80, 80, 80)]
            self.text_color = self.WHITE
            
        else:  # Default white
            self.bg_color = (40, 40, 40)
            self.border_color = (180, 180, 180)
            self.empty_color = (60, 60, 60)
            self.fill_colors = [(150, 150, 150), (220, 220, 220)]
            self.text_color = self.WHITE
    
    def create_noise_texture(self, width: int, height: int) -> pygame.Surface:
        """Create a static noise texture for the VHS effect"""
        noise = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Fill with random static for the VHS effect
        for x in range(width):
            for y in range(height):
                if random.random() < 0.1:  # 10% of pixels have noise
                    alpha = random.randint(10, 40)  # Semi-transparent
                    color = (255, 255, 255, alpha)
                    noise.set_at((x, y), color)
        
        return noise
    
    def update(self, delta_time: float):
        """
        Update the progress bar animation
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Animate progress toward target
        if self.animate and self.progress != self.target_progress:
            if abs(self.progress - self.target_progress) < self.animation_speed:
                self.progress = self.target_progress
            elif self.progress < self.target_progress:
                self.progress += self.animation_speed
            else:
                self.progress -= self.animation_speed
        
        # Update animation offsets
        self.anim_offset = (self.anim_offset + self.anim_speed) % (self.width // 4)
        self.scan_line_offset = (self.scan_line_offset + 1) % (self.height * 2)
        
        # Update glitch effects
        if self.show_glitch:
            self.glitch_timer += delta_time
            
            if self.glitch_duration > 0:
                # During glitch effect
                self.glitch_duration -= delta_time
                
                # Reset glitch when duration expires
                if self.glitch_duration <= 0:
                    self.glitch_segments = []
                    self.noise_offset = 0
            
            elif self.glitch_timer >= self.glitch_interval:
                # Start a new glitch
                self.glitch_timer = 0
                self.glitch_interval = random.uniform(2.0, 5.0)
                self.glitch_duration = random.uniform(0.1, 0.3)
                
                # Generate random glitch segments
                self.glitch_segments = []
                num_segments = random.randint(1, 5)
                
                for _ in range(num_segments):
                    segment_height = random.randint(2, 10)
                    segment_y = random.randint(0, self.height - segment_height)
                    offset_x = random.randint(-10, 10)
                    
                    self.glitch_segments.append({
                        'height': segment_height,
                        'y': segment_y,
                        'offset_x': offset_x
                    })
                
                # Random noise offset
                self.noise_offset = random.randint(-5, 5)
    
    def set_progress(self, value: float):
        """
        Set the current progress value
        
        Args:
            value: Progress value between 0.0 and 1.0
        """
        self.target_progress = max(0.0, min(1.0, value))
        
        # If not animating, update immediately
        if not self.animate:
            self.progress = self.target_progress
    
    def get_progress(self) -> float:
        """Get the current progress value"""
        return self.progress
    
    def draw(self, surface: pygame.Surface):
        """
        Draw the progress bar on the specified surface
        
        Args:
            surface: Pygame surface to draw on
        """
        # Draw border
        pygame.draw.rect(
            surface,
            self.border_color,
            (self.x, self.y, self.width, self.height),
            border_radius=self.corner_radius
        )
        
        # Draw background
        inner_rect = (
            self.x + self.border_width,
            self.y + self.border_width,
            self.width - self.border_width * 2,
            self.height - self.border_width * 2
        )
        pygame.draw.rect(
            surface,
            self.bg_color,
            inner_rect,
            border_radius=max(0, self.corner_radius - self.border_width)
        )
        
        # Calculate progress width
        progress_width = int((inner_rect[2]) * self.progress)
        
        # Draw progress bar based on style
        if self.segment_count > 1:
            # Segmented progress bar
            self.draw_segmented_progress(surface, inner_rect, progress_width)
        else:
            # Continuous progress bar
            self.draw_continuous_progress(surface, inner_rect, progress_width)
        
        # Draw scan lines
        self.draw_scan_lines(surface, inner_rect)
        
        # Draw glitch effect
        if self.show_glitch and self.glitch_duration > 0:
            self.draw_glitch_effect(surface, inner_rect)
        
        # Draw percentage text if enabled
        if self.show_percentage:
            self.draw_percentage(surface)
    
    def draw_continuous_progress(self, surface: pygame.Surface, rect: Tuple[int, int, int, int], progress_width: int):
        """Draw a continuous progress bar"""
        if progress_width > 0:
            # Create a gradient effect
            for x in range(progress_width):
                # Calculate position ratio for gradient
                ratio = x / rect[2]
                
                # Use CMYK colors or scheme colors
                if len(self.fill_colors) == 4:  # CMYK mode
                    index = int((x / rect[2]) * 4) % 4
                    color = self.fill_colors[index]
                else:
                    # Interpolate between the two colors
                    color1 = self.fill_colors[0]
                    color2 = self.fill_colors[1]
                    
                    # Add wave effect
                    wave_offset = math.sin((x / 20) + self.anim_offset / 10) * 0.1
                    ratio = min(1.0, max(0.0, ratio + wave_offset))
                    
                    color = (
                        int(color1[0] + (color2[0] - color1[0]) * ratio),
                        int(color1[1] + (color2[1] - color1[1]) * ratio),
                        int(color1[2] + (color2[2] - color1[2]) * ratio)
                    )
                
                # Draw vertical line
                pygame.draw.line(
                    surface,
                    color,
                    (rect[0] + x, rect[1]),
                    (rect[0] + x, rect[1] + rect[3])
                )
    
    def draw_segmented_progress(self, surface: pygame.Surface, rect: Tuple[int, int, int, int], progress_width: int):
        """Draw a segmented progress bar"""
        segment_width = rect[2] / self.segment_count
        filled_segments = int(self.progress * self.segment_count)
        
        for i in range(self.segment_count):
            segment_x = rect[0] + i * segment_width
            
            # Determine segment color
            if i < filled_segments:
                # For filled segments
                if len(self.fill_colors) == 4:  # CMYK mode
                    color = self.fill_colors[i % 4]
                else:
                    # Alternate between the two colors
                    color = self.fill_colors[i % 2]
            else:
                # Empty segments
                color = self.empty_color
            
            # Draw segment with slight gap
            segment_rect = (
                segment_x + 2,
                rect[1] + 2,
                segment_width - 4,
                rect[3] - 4
            )
            pygame.draw.rect(surface, color, segment_rect)
    
    def draw_scan_lines(self, surface: pygame.Surface, rect: Tuple[int, int, int, int]):
        """Draw retro CRT scan lines"""
        scan_line_spacing = 4
        
        for y in range(rect[1], rect[1] + rect[3], scan_line_spacing):
            # Animate the scan line based on offset
            y_pos = (y + self.scan_line_offset) % (rect[1] + rect[3] * 2)
            if y_pos >= rect[1] + rect[3]:
                y_pos = rect[1] + rect[3] - (y_pos - (rect[1] + rect[3]))
            
            # Draw a semi-transparent scan line
            pygame.draw.line(
                surface,
                (0, 0, 0, 30),  # Very transparent black
                (rect[0], y_pos),
                (rect[0] + rect[2], y_pos)
            )
    
    def draw_glitch_effect(self, surface: pygame.Surface, rect: Tuple[int, int, int, int]):
        """Draw VHS glitch effects"""
        # Apply static noise
        noise_copy = self.noise_surface.copy()
        surface.blit(noise_copy, (rect[0] + self.noise_offset, rect[1]))
        
        # Draw glitch segments
        for segment in self.glitch_segments:
            segment_rect = pygame.Rect(
                rect[0] + segment['offset_x'],
                rect[1] + segment['y'],
                rect[2],
                segment['height']
            )
            
            # Get the segment from the screen
            try:
                segment_surf = surface.subsurface(segment_rect).copy()
                
                # Clear the original area
                pygame.draw.rect(surface, self.bg_color, segment_rect)
                
                # Blit with offset
                surface.blit(segment_surf, (rect[0] + segment['offset_x'], rect[1] + segment['y']))
            except ValueError:
                # subsurface might fail if outside bounds
                pass
    
    def draw_percentage(self, surface: pygame.Surface):
        """Draw the percentage text"""
        font = pygame.font.SysFont('monospace', 16)
        percent_text = f"{int(self.progress * 100)}%"
        
        text_surface = font.render(percent_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        
        surface.blit(text_surface, text_rect)
    
    def get_rect(self) -> pygame.Rect:
        """Get the progress bar's rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


# Example usage
if __name__ == "__main__":
    pygame.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("RetroProgress Test")
    clock = pygame.time.Clock()
    
    # Create test progress bars with different color schemes
    cyan_progress = RetroProgress(100, 100, 600, 30, "cyan")
    magenta_progress = RetroProgress(100, 150, 600, 30, "magenta", segment_count=10)
    yellow_progress = RetroProgress(100, 200, 600, 30, "yellow")
    cmyk_progress = RetroProgress(100, 250, 600, 30, "cmyk", segment_count=20)
    white_progress = RetroProgress(100, 300, 600, 30, "white", show_glitch=False)
    
    # Current progress values
    progress_value = 0.0
    progress_direction = 0.005
    
    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0  # Delta time in seconds
        
        screen.fill((40, 40, 40))  # Dark background
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update progress value
        progress_value += progress_direction
        if progress_value >= 1.0 or progress_value <= 0.0:
            progress_direction *= -1
            progress_value = max(0.0, min(1.0, progress_value))
        
        # Set progress for all bars
        cyan_progress.set_progress(progress_value)
        magenta_progress.set_progress(progress_value * 0.8)  # Slightly behind
        yellow_progress.set_progress(progress_value * 0.6)   # More behind
        cmyk_progress.set_progress(progress_value * 0.4)    # Even more behind
        white_progress.set_progress(progress_value * 0.2)   # Most behind
        
        # Update and draw progress bars
        cyan_progress.update(delta_time)
        magenta_progress.update(delta_time)
        yellow_progress.update(delta_time)
        cmyk_progress.update(delta_time)
        white_progress.update(delta_time)
        
        cyan_progress.draw(screen)
        magenta_progress.draw(screen)
        yellow_progress.draw(screen)
        cmyk_progress.draw(screen)
        white_progress.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()