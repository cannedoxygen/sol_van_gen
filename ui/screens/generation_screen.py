"""
Generation Screen for the CMYK Retro Solana Vanity Address Generator
Handles the address generation process and UI
"""

import os
import pygame
import logging
import threading
from typing import Callable, Dict, Any

from ui.components.retro_input import RetroInput
from ui.components.retro_button import RetroButton
from ui.components.retro_progress import RetroProgress
from ui.components.retro_slider import RetroSlider

from core.vangen import search_vanity_addresses
from utils.config_manager import ConfigManager
from utils.output_formatter import print_progress, export_addresses_to_file

class GenerationScreen:
    """
    Screen for configuring and executing vanity address generation
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
        
        # Create UI components
        self.create_ui_components()
    
    def create_ui_components(self):
        """Create and initialize UI components for generation screen"""
        # Dimensions and positioning
        input_width = 400
        input_height = 40
        input_x = (self.width - input_width) // 2
        vertical_spacing = 20
        
        # Inputs for generation parameters
        self.prefix_input = RetroInput(
            input_x, 100, input_width, input_height, 
            "Enter Address Prefix (optional)", 
            self.config.get('prefix', ''),
            color_scheme="cyan"
        )
        
        self.suffix_input = RetroInput(
            input_x, 100 + input_height + vertical_spacing, 
            input_width, input_height, 
            "Enter Address Suffix (optional)", 
            self.config.get('suffix', ''),
            color_scheme="magenta"
        )
        
        # Count slider
        self.count_slider = RetroSlider(
            input_x, 100 + (input_height + vertical_spacing) * 2, 
            input_width, input_height, 
            "Number of Addresses", 
            min_value=1, 
            max_value=50, 
            initial_value=int(self.config.get('count', 1)),
            color_scheme="yellow"
        )
        
        # Iteration bits slider
        self.iteration_slider = RetroSlider(
            input_x, 100 + (input_height + vertical_spacing) * 3, 
            input_width, input_height, 
            "Iteration Complexity", 
            min_value=16, 
            max_value=28, 
            initial_value=int(self.config.get('iteration_bits', 24)),
            color_scheme="magenta"
        )
        
        # Buttons
        button_width = 180
        button_height = 50
        button_y = 100 + (input_height + vertical_spacing) * 4 + 20
        
        self.generate_button = RetroButton(
            (self.width - button_width * 2 - 20) // 2,
            button_y, 
            button_width, button_height, 
            "Generate", 
            self.start_generation, 
            color_scheme="cyan"
        )
        
        self.back_button = RetroButton(
            (self.width - button_width * 2 - 20) // 2 + button_width + 20,
            button_y, 
            button_width, button_height, 
            "Back", 
            self.on_back, 
            color_scheme="white"
        )
        
        # Progress bar (initially hidden)
        self.progress_bar = RetroProgress(
            input_x, button_y + button_height + 20, 
            input_width, 30, 
            color_scheme="cmyk"
        )
    
    def draw(self):
        """Draw the generation screen components"""
        # Clear the screen with a dark background
        self.screen.fill((40, 40, 40))
        
        # Draw title
        font = pygame.font.SysFont('monospace', 36, bold=True)
        title = font.render("Generate Vanity Address", True, (200, 200, 200))
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw inputs and buttons
        self.prefix_input.draw(self.screen)
        self.suffix_input.draw(self.screen)
        self.count_slider.draw(self.screen)
        self.iteration_slider.draw(self.screen)
        
        # If generation is in progress, draw status message and progress bar
        if self.generating:
            status_font = pygame.font.SysFont('monospace', 16)
            status_text = "Generating addresses... Please wait."
            status = status_font.render(status_text, True, (0, 255, 255))
            status_rect = status.get_rect(center=(self.width // 2, self.generate_button.y - 20))
            self.screen.blit(status, status_rect)
            self.progress_bar.draw(self.screen)
            
            # Disable generate button during generation
            self.generate_button.set_disabled(True)
        else:
            # Enable generate button when not generating
            self.generate_button.set_disabled(False)
            
        # Draw buttons
        self.generate_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        # If there's an error, display it
        if self.generation_error:
            error_font = pygame.font.SysFont('monospace', 14)
            error_text = f"Error: {self.generation_error}"
            error = error_font.render(error_text, True, (255, 50, 50))
            error_rect = error.get_rect(center=(self.width // 2, self.height - 50))
            self.screen.blit(error, error_rect)
    
    def update(self, delta_time: float):
        """
        Update screen state
        
        Args:
            delta_time: Time elapsed since last update
        """
        if self.generating:
            self.progress_bar.update(delta_time)
            
            # Check if generation thread is still alive
            if self.generation_thread and not self.generation_thread.is_alive():
                if self.generation_result:
                    # Generation completed successfully
                    self.generating = False
                    self.on_complete(self.generation_result)
                    self.generation_result = None
                    self.generation_thread = None
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if event was handled
        """
        # Skip input handling while generating
        if self.generating:
            # Still allow back button to cancel generation
            return self.back_button.handle_event(event)
        
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
        
        # Handle input events
        handled = False
        handled |= self.prefix_input.handle_event(event)
        handled |= self.suffix_input.handle_event(event)
        handled |= self.count_slider.handle_event(event)
        handled |= self.iteration_slider.handle_event(event)
        
        # Handle button events
        handled |= self.generate_button.handle_event(event)
        handled |= self.back_button.handle_event(event)
        
        return handled
    
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