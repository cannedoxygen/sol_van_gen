"""
Landing screen for the CMYK Retro Solana Vanity Generator
Displays intro animation with typewriter effect and CMYK styling
"""

import pygame
import os
import logging
import math
import random
import time
from typing import Callable, List, Tuple, Dict, Any

from utils.ascii_art import CMYKColors
from utils.config_manager import ConfigManager

class LandingScreen:
    """
    Landing screen with animated intro sequence and retro CMYK aesthetics
    """
    
    def __init__(self, screen: pygame.Surface, on_complete: Callable[[], None]):
        """
        Initialize the landing screen
        
        Args:
            screen: Pygame surface to render on
            on_complete: Callback when intro is complete
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.on_complete = on_complete
        self.config = ConfigManager()
        
        # Ensure mixer is initialized
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception as e:
                logging.warning(f"Could not initialize sound mixer: {e}")
        
        # Animation timing
        self.animation_time = 0
        self.animation_complete = False
        self.particles = []
        
        # Load assets
        self.load_assets()
        
        # Setup intro animation state
        self.setup_intro_animation()
        
        # Create particles
        self.create_particles(20)
    
    def load_assets(self):
        """Load screen assets"""
        # Get the project root directory
        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Load fonts
        try:
            pixel_font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "pixel_font.ttf")
            if os.path.exists(pixel_font_path):
                self.title_font = pygame.font.Font(pixel_font_path, 32)
                self.font = pygame.font.Font(pixel_font_path, 24)
                self.small_font = pygame.font.Font(pixel_font_path, 18)
            else:
                self.title_font = pygame.font.SysFont("monospace", 32)
                self.font = pygame.font.SysFont("monospace", 24)
                self.small_font = pygame.font.SysFont("monospace", 18)
        except Exception as e:
            logging.warning(f"Font loading failed: {e}")
            self.title_font = pygame.font.SysFont("monospace", 32)
            self.font = pygame.font.SysFont("monospace", 24)
            self.small_font = pygame.font.SysFont("monospace", 18)
        
        # Load sounds
        try:
            intro_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "success.wav")
            if os.path.exists(intro_sound_path):
                self.intro_sound = pygame.mixer.Sound(intro_sound_path)
                self.intro_sound.set_volume(0.5)
            else:
                self.intro_sound = None
        except Exception as e:
            logging.warning(f"Sound loading failed: {e}")
            self.intro_sound = None
    
    def setup_intro_animation(self):
        """Setup intro animation state"""
        self.intro_text = "Generating Unique Solana Addresses"
        self.intro_text_index = 0
        self.intro_text_surface = self.font.render("", True, (255, 255, 255))
        self.intro_sound_played = False
        self.continue_text_visible = False
        self.start_time = time.time()
        self.animation_duration = 5.0  # Duration in seconds
    
    def create_particles(self, count=10):
        """Create particles for animation effects"""
        for _ in range(count):
            particle = {
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.uniform(1, 3),
                'speed': random.uniform(10, 30),
                'angle': random.uniform(0, math.pi * 2),
                'color': (
                    random.choice([0, 255]),  # R
                    random.choice([0, 255]),  # G
                    random.choice([0, 255]),  # B
                    random.randint(50, 150)   # A
                )
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
        if random.random() < delta_time * 3:  # Average 3 particles per second
            self.create_particles(1)
    
    def draw_intro(self):
        """Draw the intro animation"""
        # Create a gradient background for intro
        intro_surface = pygame.Surface((self.width, self.height))
        intro_surface.fill((0, 0, 30))  # Dark blue base
        
        # Add scan lines
        for y in range(0, self.height, 2):
            pygame.draw.line(
                intro_surface,
                (0, 0, 0),  # Black
                (0, y),
                (self.width, y),
                1
            )
        
        # Add static/noise effect
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 2)
            color = (random.randint(180, 255), random.randint(180, 255), random.randint(180, 255))
            pygame.draw.rect(intro_surface, color, (x, y, size, size))
        
        # Gradually reveal the text
        self.intro_text_index += 1

        if self.intro_text_index <= len(self.intro_text):
            displayed_text = self.intro_text[:self.intro_text_index]
            if self.intro_text_index < len(self.intro_text):
                displayed_text += "█"  # Add cursor character
            
            self.intro_text_surface = self.font.render(
                displayed_text,
                True,
                (0, 255, 255)  # Cyan color
            )
        else:
            # Keep the full text without cursor after done typing
            self.intro_text_surface = self.font.render(
                self.intro_text,
                True,
                (0, 255, 255)  # Cyan color
            )
            
            # Add a pulsing "Press any key to continue" message
            if time.time() - self.start_time >= 2.0:  # Show after 2 seconds of completed text
                self.continue_text_visible = True
                pulse = abs(math.sin(self.animation_time * 4)) * 255
                continue_color = (pulse, pulse, pulse)
                continue_text = self.small_font.render(
                    "Press any key to continue",
                    True,
                    continue_color
                )
                continue_rect = continue_text.get_rect(
                    center=(self.width // 2, self.height // 2 + 100)
                )
                intro_surface.blit(continue_text, continue_rect)
            
            # Play completion sound once
            if self.intro_sound and not self.intro_sound_played:
                self.intro_sound.play()
                self.intro_sound_played = True

        # Create text "scanning" effect
        if self.intro_text_index > 5:
            scan_y = int(self.animation_time * 200) % self.height
            pygame.draw.line(
                intro_surface,
                (0, 255, 255, 80),  # Semi-transparent cyan
                (0, scan_y),
                (self.width, scan_y),
                1
            )

        # Add "CMYK" in corners with pulsing effect
        corner_text_size = 24
        corner_margin = 20
        
        c_text = self.font.render("C", True, (0, 255, 255))
        m_text = self.font.render("M", True, (255, 0, 255))
        y_text = self.font.render("Y", True, (255, 255, 0))
        k_text = self.font.render("K", True, (255, 255, 255))
        
        intro_surface.blit(c_text, (corner_margin, corner_margin))
        intro_surface.blit(m_text, (self.width - corner_margin - corner_text_size, corner_margin))
        intro_surface.blit(y_text, (corner_margin, self.height - corner_margin - corner_text_size))
        intro_surface.blit(k_text, (self.width - corner_margin - corner_text_size, 
                                   self.height - corner_margin - corner_text_size))

        # Position and blit the main text
        intro_text_rect = self.intro_text_surface.get_rect(
            center=(self.width // 2, self.height // 2)
        )
        intro_surface.blit(self.intro_text_surface, intro_text_rect)
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(
                intro_surface,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
            
        # Finally blit the entire intro surface to the screen
        self.screen.blit(intro_surface, (0, 0))
    
    def update(self, delta_time: float):
        """Update animations and timing"""
        self.animation_time += delta_time
        
        # Update particles
        self.update_particles(delta_time)
        
        # Auto-complete the animation after the set duration
        if not self.animation_complete and time.time() - self.start_time >= self.animation_duration:
            if self.intro_text_index < len(self.intro_text):
                # Skip to end of text
                self.intro_text_index = len(self.intro_text)
            elif not self.continue_text_visible:
                # Show continue text
                self.continue_text_visible = True
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if event was handled
        """
        # Skip animation with any key/click once text is fully displayed
        if self.intro_text_index >= len(self.intro_text):
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.animation_complete = True
                if self.on_complete:
                    self.on_complete()
                return True
        # Skip to the end of text with any key/click
        elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.intro_text_index = len(self.intro_text)
            return True
            
        return False
    
    def draw(self):
        """Draw the landing screen"""
        self.draw_intro()
    
    def run(self) -> str:
        """
        Run the landing screen logic
        
        Returns:
            str: Command for the main controller ('done' or 'exit')
        """
        if self.animation_complete:
            return "done"
        return ""