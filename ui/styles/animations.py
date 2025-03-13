"""
Animation utilities for the CMYK Retro Lo-Fi Solana Vanity Generator
Provides animation effects and helper functions for UI components
"""

import math
import random
import time
from typing import Tuple, List, Dict, Any, Callable

import pygame

class AnimationValue:
    """
    A value that can be animated over time with easing
    """
    
    # Easing function types
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    
    def __init__(
        self, 
        start_value: float,
        end_value: float = None,
        duration: float = 1.0,
        easing: str = LINEAR,
        loop: bool = False,
        auto_start: bool = True,
        on_complete: Callable = None
    ):
        """
        Initialize an animated value
        
        Args:
            start_value: Initial value
            end_value: Target value (if None, will use start_value)
            duration: Animation duration in seconds
            easing: Easing function to use
            loop: Whether to loop the animation
            auto_start: Whether to start animation immediately
            on_complete: Callback function when animation completes
        """
        self.start_value = start_value
        self.end_value = end_value if end_value is not None else start_value
        self.current_value = start_value
        self.duration = max(0.01, duration)  # Prevent division by zero
        self.easing = easing
        self.loop = loop
        self.on_complete = on_complete
        
        # Animation state
        self.playing = auto_start
        self.start_time = time.time() if auto_start else 0
        self.elapsed_time = 0 if auto_start else -1
        self.completed = False
    
    def start(self):
        """Start or restart the animation"""
        self.playing = True
        self.start_time = time.time()
        self.elapsed_time = 0
        self.completed = False
        self.current_value = self.start_value
    
    def pause(self):
        """Pause the animation"""
        self.playing = False
    
    def resume(self):
        """Resume the animation"""
        if not self.playing and not self.completed:
            self.playing = True
            # Adjust start time to maintain elapsed progress
            self.start_time = time.time() - self.elapsed_time
    
    def stop(self):
        """Stop the animation and reset to start value"""
        self.playing = False
        self.elapsed_time = 0
        self.completed = False
        self.current_value = self.start_value
    
    def set_values(self, start_value: float, end_value: float, restart: bool = True):
        """
        Set new start and end values
        
        Args:
            start_value: New start value
            end_value: New end value
            restart: Whether to restart the animation
        """
        self.start_value = start_value
        self.end_value = end_value
        if restart:
            self.start()
        else:
            self.current_value = start_value
    
    def update(self, delta_time: float = None) -> float:
        """
        Update the animation state
        
        Args:
            delta_time: Time elapsed since last update (None = auto-calculate)
            
        Returns:
            float: Current value
        """
        if not self.playing:
            return self.current_value
        
        # Calculate elapsed time
        current_time = time.time()
        if delta_time is None:
            self.elapsed_time = current_time - self.start_time
        else:
            self.elapsed_time += delta_time
        
        # Check if animation is complete
        if self.elapsed_time >= self.duration:
            if self.loop:
                # Loop back to start
                self.elapsed_time %= self.duration
                self.start_time = current_time - self.elapsed_time
            else:
                # Complete animation
                self.elapsed_time = self.duration
                self.playing = False
                self.completed = True
                self.current_value = self.end_value
                
                # Trigger completion callback
                if self.on_complete:
                    self.on_complete()
                
                return self.current_value
        
        # Calculate progress ratio (0.0 to 1.0)
        progress = self.elapsed_time / self.duration
        
        # Apply easing function
        progress = self.apply_easing(progress)
        
        # Calculate current value
        self.current_value = self.start_value + (self.end_value - self.start_value) * progress
        
        return self.current_value
    
    def apply_easing(self, progress: float) -> float:
        """
        Apply easing function to progress value
        
        Args:
            progress: Linear progress (0.0 to 1.0)
            
        Returns:
            float: Eased progress value
        """
        if self.easing == self.LINEAR:
            return progress
        elif self.easing == self.EASE_IN:
            return progress * progress
        elif self.easing == self.EASE_OUT:
            return -(progress * (progress - 2))
        elif self.easing == self.EASE_IN_OUT:
            progress *= 2
            if progress < 1:
                return 0.5 * progress * progress
            progress -= 1
            return -0.5 * (progress * (progress - 2) - 1)
        elif self.easing == self.BOUNCE:
            if progress < (1/2.75):
                return 7.5625 * progress * progress
            elif progress < (2/2.75):
                progress -= (1.5/2.75)
                return 7.5625 * progress * progress + 0.75
            elif progress < (2.5/2.75):
                progress -= (2.25/2.75)
                return 7.5625 * progress * progress + 0.9375
            else:
                progress -= (2.625/2.75)
                return 7.5625 * progress * progress + 0.984375
        elif self.easing == self.ELASTIC:
            if progress == 0 or progress == 1:
                return progress
            progress = progress * 2 - 1
            p = 0.3
            s = p / 4
            return 2**(-10 * progress) * math.sin((progress - s) * (2 * math.pi) / p) + 1
        
        # Default to linear if easing type is unknown
        return progress


class ScanlineEffect:
    """
    Creates a CRT scanline effect for retro displays
    """
    
    def __init__(
        self,
        width: int,
        height: int,
        color: Tuple[int, int, int] = (0, 0, 0),
        alpha: int = 30,
        speed: float = 100, 
        spacing: int = 4
    ):
        """
        Initialize the scanline effect
        
        Args:
            width: Surface width
            height: Surface height
            color: Line color (RGB)
            alpha: Line transparency (0-255)
            speed: Vertical movement speed in pixels per second
            spacing: Pixels between each line
        """
        self.width = width
        self.height = height
        self.color = color
        self.alpha = alpha
        self.speed = speed
        self.spacing = spacing
        
        # Create the scanline surface
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Track animation offset
        self.offset = 0
    
    def update(self, delta_time: float):
        """
        Update the animation
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Update offset based on time and speed
        self.offset = (self.offset + self.speed * delta_time) % (self.spacing * 2)
    
    def draw(self, target_surface: pygame.Surface, x: int = 0, y: int = 0):
        """
        Draw the scanline effect
        
        Args:
            target_surface: Surface to draw on
            x: X position
            y: Y position
        """
        # Clear the surface
        self.surface.fill((0, 0, 0, 0))
        
        # Draw horizontal scanlines
        line_color = (*self.color, self.alpha)
        
        for line_y in range(-int(self.offset), self.height, self.spacing):
            pygame.draw.line(
                self.surface,
                line_color,
                (0, line_y),
                (self.width, line_y)
            )
        
        # Draw the effect on the target surface
        target_surface.blit(self.surface, (x, y))


class GlitchEffect:
    """
    Creates a VHS/glitch effect for retro displays
    """
    
    def __init__(
        self,
        width: int,
        height: int,
        glitch_frequency: float = 0.2,  # Probability per second
        glitch_duration: Tuple[float, float] = (0.05, 0.2),  # Min/max duration
        max_glitch_offset: int = 10,
        max_segments: int = 5
    ):
        """
        Initialize the glitch effect
        
        Args:
            width: Surface width
            height: Surface height
            glitch_frequency: How often glitches occur (probability per second)
            glitch_duration: Min/max duration range for glitches
            max_glitch_offset: Maximum horizontal pixel offset
            max_segments: Maximum number of glitch segments
        """
        self.width = width
        self.height = height
        self.glitch_frequency = glitch_frequency
        self.min_duration, self.max_duration = glitch_duration
        self.max_glitch_offset = max_glitch_offset
        self.max_segments = max_segments
        
        # Glitch state
        self.glitching = False
        self.glitch_end_time = 0
        self.glitch_segments = []
        self.noise_offset = 0
        
        # Create noise texture for effect
        self.noise_texture = self.create_noise_texture()
    
    def create_noise_texture(self) -> pygame.Surface:
        """Create a static noise texture for VHS effect"""
        noise = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Fill with random static
        for x in range(self.width):
            for y in range(self.height):
                if random.random() < 0.1:  # 10% of pixels have noise
                    alpha = random.randint(10, 40)  # Semi-transparent
                    color = (255, 255, 255, alpha)
                    noise.set_at((x, y), color)
        
        return noise
    
    def start_glitch(self):
        """Start a new glitch effect"""
        self.glitching = True
        
        # Set glitch duration
        duration = random.uniform(self.min_duration, self.max_duration)
        self.glitch_end_time = time.time() + duration
        
        # Create random glitch segments
        self.glitch_segments = []
        num_segments = random.randint(1, self.max_segments)
        
        for _ in range(num_segments):
            segment_height = random.randint(2, 10)
            segment_y = random.randint(0, self.height - segment_height)
            offset_x = random.randint(-self.max_glitch_offset, self.max_glitch_offset)
            
            self.glitch_segments.append({
                'height': segment_height,
                'y': segment_y,
                'offset_x': offset_x
            })
        
        # Random noise offset
        self.noise_offset = random.randint(-5, 5)
    
    def update(self, delta_time: float):
        """
        Update the glitch effect
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        current_time = time.time()
        
        # Check if current glitch has ended
        if self.glitching and current_time >= self.glitch_end_time:
            self.glitching = False
            self.glitch_segments = []
        
        # Randomly start a new glitch
        if not self.glitching and random.random() < self.glitch_frequency * delta_time:
            self.start_glitch()
    
    def draw(self, target_surface: pygame.Surface):
        """
        Draw the glitch effect
        
        Args:
            target_surface: Surface to draw on
        """
        if not self.glitching:
            return
        
        # Make a copy of the target surface
        surface_copy = target_surface.copy()
        
        # Apply static noise
        if self.noise_offset != 0:
            noise_copy = self.noise_texture.copy()
            target_surface.blit(noise_copy, (self.noise_offset, 0))
        
        # Apply segment offsets
        for segment in self.glitch_segments:
            y = segment['y']
            height = segment['height']
            x_offset = segment['offset_x']
            
            # Define segment rectangle
            segment_rect = pygame.Rect(0, y, self.width, height)
            
            try:
                # Get the segment from the copied surface
                segment_surf = surface_copy.subsurface(segment_rect).copy()
                
                # Clear the original area
                pygame.draw.rect(target_surface, (0, 0, 0), segment_rect)
                
                # Create offset rectangle
                offset_rect = segment_rect.copy()
                offset_rect.x += x_offset
                
                # Ensure we don't draw outside the surface
                if offset_rect.x < 0:
                    segment_surf = segment_surf.subsurface((-offset_rect.x, 0, 
                                                           segment_surf.get_width() + offset_rect.x, 
                                                           height))
                    offset_rect.width = segment_surf.get_width()
                    offset_rect.x = 0
                elif offset_rect.right > self.width:
                    segment_surf = segment_surf.subsurface((0, 0, 
                                                           self.width - offset_rect.x, 
                                                           height))
                    offset_rect.width = segment_surf.get_width()
                
                # Draw the offset segment
                target_surface.blit(segment_surf, offset_rect)
            except ValueError:
                # Skip if subsurface is out of bounds
                pass


class VHSEffect:
    """
    Combines multiple effects for a full VHS-style retro look
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize the VHS effect
        
        Args:
            width: Surface width
            height: Surface height
        """
        self.width = width
        self.height = height
        
        # Create sub-effects
        self.scanlines = ScanlineEffect(width, height)
        self.glitch = GlitchEffect(width, height)
        
        # Create effect surface
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    def update(self, delta_time: float):
        """
        Update all effects
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        self.scanlines.update(delta_time)
        self.glitch.update(delta_time)
    
    def draw(self, target_surface: pygame.Surface):
        """
        Apply all effects to the target surface
        
        Args:
            target_surface: Surface to apply effects to
        """
        # Glitch effect is applied directly to the target
        self.glitch.draw(target_surface)
        
        # Scanlines are applied after glitch
        self.scanlines.draw(target_surface)
        
        # Add slight color aberration (RGB shift)
        self.apply_rgb_shift(target_surface)
    
    def apply_rgb_shift(self, target_surface: pygame.Surface):
        """
        Apply RGB shift effect (chromatic aberration)
        
        Args:
            target_surface: Surface to apply effect to
        """
        if not self.glitch.glitching:
            return
            
        # This is a simplified version that only works well
        # if the glitch is already happening
        
        # Create separate channel surfaces
        r_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        g_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        b_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Fill with each channel
        for x in range(self.width):
            for y in range(self.height):
                color = target_surface.get_at((x, y))
                r_surf.set_at((x, y), (color[0], 0, 0, color[3] // 3))
                g_surf.set_at((x, y), (0, color[1], 0, color[3] // 3))
                b_surf.set_at((x, y), (0, 0, color[2], color[3] // 3))
        
        # Apply slight offset to red and blue channels
        r_offset = random.randint(-2, 2)
        b_offset = random.randint(-2, 2)
        
        # Blit back with offsets
        target_surface.blit(r_surf, (r_offset, 0), special_flags=pygame.BLEND_RGB_ADD)
        target_surface.blit(b_surf, (b_offset, 0), special_flags=pygame.BLEND_RGB_ADD)