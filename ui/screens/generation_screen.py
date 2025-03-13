"""
Generation Screen for the CMYK Retro Solana Vanity Address Generator
Handles the address generation process and UI
"""

import os
import pygame
import logging
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
        button_width = 200
        button_height = 50
        button_y = 100 + (input_height + vertical_spacing) * 4 + 20
        
        self.generate_button = RetroButton(
            input_x, button_y, 
            button_width, button_height, 
            "Generate", 
            self.start_generation, 
            color_scheme="cyan"
        )
        
        self.back_button = RetroButton(
            input_x + button_width + 20, button_y, 
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
        self.generate_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        # Draw progress bar if generating
        if self.generating:
            self.progress_bar.draw(self.screen)
    
    def update(self, delta_time: float):
        """
        Update screen state
        
        Args:
            delta_time: Time elapsed since last update
        """
        if self.generating:
            self.progress_bar.update(delta_time)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if event was handled
        """
        if self.generating:
            return False
        
        # Handle input events
        self.prefix_input.handle_event(event)
        self.suffix_input.handle_event(event)
        self.count_slider.handle_event(event)
        self.iteration_slider.handle_event(event)
        
        # Handle button events
        self.generate_button.handle_event(event)
        self.back_button.handle_event(event)
        
        return True
    
    def start_generation(self):
        """Initiate the vanity address generation process"""
        # Validate inputs
        prefix = self.prefix_input.get_text().strip()
        suffix = self.suffix_input.get_text().strip()
        count = self.count_slider.get_value()
        iteration_bits = self.iteration_slider.get_value()
        
        if not prefix and not suffix:
            logging.error("Please provide at least a prefix or suffix")
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
        import threading
        generation_thread = threading.Thread(
            target=self.run_generation, 
            args=(prefix, suffix, count, output_dir, iteration_bits)
        )
        generation_thread.start()
    
    def run_generation(self, prefix, suffix, count, output_dir, iteration_bits):
        """
        Actual generation process to run in a separate thread
        
        Args:
            prefix: Address prefix
            suffix: Address suffix
            count: Number of addresses to generate
            output_dir: Directory to save generated addresses
            iteration_bits: Complexity of generation
        """
        try:
            def progress_callback(progress_data):
                """
                Callback to update UI during generation
                
                Args:
                    progress_data: Dictionary with generation progress
                """
                if isinstance(progress_data, dict):
                    # Update progress bar on main thread
                    pygame.event.post(
                        pygame.event.Event(
                            pygame.USEREVENT, 
                            {'type': 'generation_progress', 
                             'progress': progress_data.get('progress', 0)}
                        )
                    )
            
            # Perform generation
            result = search_vanity_addresses(
                starts_with=prefix,
                ends_with=suffix,
                count=count,
                output_dir=output_dir,
                iteration_bits=iteration_bits,
                callback=progress_callback
            )
            
            # Export results to different formats
            export_formats = ['json', 'html']
            for format_type in export_formats:
                export_addresses_to_file(
                    result, 
                    format_type, 
                    os.path.join(output_dir, f"vanity_addresses.{format_type}")
                )
            
            # Post generation complete event
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT, 
                    {'type': 'generation_complete', 
                     'result': result}
                )
            )
        
        except Exception as e:
            # Post error event
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT, 
                    {'type': 'generation_error', 
                     'error': str(e)}
                )
            )
    
    def run(self) -> str:
        """
        Run the generation screen loop
        
        Returns:
            str: Result of screen interaction (e.g., 'back', 'exit')
        """
        clock = pygame.time.Clock()
        
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                
                # Custom generation events
                if event.type == pygame.USEREVENT:
                    if event.dict['type'] == 'generation_progress':
                        # Update progress bar
                        progress = event.dict['progress']
                        self.progress_bar.set_progress(progress)
                    
                    elif event.dict['type'] == 'generation_complete':
                        # Stop generation, pass results to callback
                        self.generating = False
                        result = event.dict['result']
                        self.on_complete(result)
                        return "done"
                    
                    elif event.dict['type'] == 'generation_error':
                        # Handle generation error
                        error = event.dict['error']
                        logging.error(f"Generation error: {error}")
                        self.generating = False
                
                # Handle other events
                if not self.generating:
                    self.handle_event(event)
            
            # Update
            delta_time = clock.tick(60) / 1000.0  # Convert to seconds
            self.update(delta_time)
            
            # Draw
            self.draw()
            
            # Update display
            pygame.display.flip()


if __name__ == "__main__":
    # For standalone testing
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Solana Vanity Address Generator")
    
    def on_back():
        print("Back button pressed")
    
    def on_complete(results):
        print("Generation complete with results:", results)
    
    generation_screen = GenerationScreen(screen, on_back, on_complete)
    generation_screen.run()