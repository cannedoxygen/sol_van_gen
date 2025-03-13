"""
Results Screen for the CMYK Retro Solana Vanity Address Generator
Displays generated vanity addresses and provides export options
"""

import os
import pygame
from typing import Dict, Any, Callable

from ui.components.retro_button import RetroButton
from ui.components.retro_input import RetroInput
from utils.output_formatter import format_address_table, export_addresses_to_file
from utils.config_manager import ConfigManager

class ResultsScreen:
    """
    Screen for displaying and managing generated vanity addresses
    """
    
    def __init__(
        self, 
        screen: pygame.Surface, 
        results: Dict[str, Any], 
        on_back: Callable[[], None]
    ):
        """
        Initialize the results screen
        
        Args:
            screen: Pygame surface to render on
            results: Dictionary containing generation results
            on_back: Callback to return to previous screen
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.results = results
        self.on_back = on_back
        
        # Configuration management
        self.config = ConfigManager()
        
        # Create UI components
        self.create_ui_components()
    
    def create_ui_components(self):
        """Create and initialize UI components for results screen"""
        # Buttons
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        # Export buttons
        self.json_export_button = RetroButton(
            (self.width - button_width) // 2, 
            self.height - button_height - 20, 
            button_width, 
            button_height, 
            "Export JSON", 
            lambda: self.export_results('json'), 
            color_scheme="cyan"
        )
        
        self.html_export_button = RetroButton(
            (self.width - button_width) // 2 - (button_width + button_spacing), 
            self.height - button_height - 20, 
            button_width, 
            button_height, 
            "Export HTML", 
            lambda: self.export_results('html'), 
            color_scheme="magenta"
        )
        
        self.back_button = RetroButton(
            (self.width - button_width) // 2 + (button_width + button_spacing), 
            self.height - button_height - 20, 
            button_width, 
            button_height, 
            "Back", 
            self.on_back, 
            color_scheme="white"
        )
    
    def draw(self):
        """Draw the results screen components"""
        # Clear the screen with a dark background
        self.screen.fill((40, 40, 40))
        
        # Draw title
        font = pygame.font.SysFont('monospace', 36, bold=True)
        title = font.render("Vanity Address Results", True, (200, 200, 200))
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Render address list
        if self.results.get('success', False):
            addresses = self.results.get('results', [])
            
            # Use a smaller font for addresses
            addr_font = pygame.font.SysFont('monospace', 16)
            
            # Render addresses
            for i, addr in enumerate(addresses):
                addr_text = f"{i+1}. {addr['pubkey']}"
                addr_surface = addr_font.render(addr_text, True, (180, 180, 180))
                addr_rect = addr_surface.get_rect(
                    centerx=self.width // 2, 
                    top=100 + i * 30
                )
                self.screen.blit(addr_surface, addr_rect)
        else:
            # Render error message
            error_font = pygame.font.SysFont('monospace', 24)
            error_text = self.results.get('error', 'Unknown error occurred')
            error_surface = error_font.render(error_text, True, (255, 100, 100))
            error_rect = error_surface.get_rect(center=(self.width // 2, 200))
            self.screen.blit(error_surface, error_rect)
        
        # Draw buttons
        self.json_export_button.draw(self.screen)
        self.html_export_button.draw(self.screen)
        self.back_button.draw(self.screen)
    
    def export_results(self, format_type: str):
        """
        Export results to specified format
        
        Args:
            format_type: Format to export ('json', 'html')
        """
        # Ensure output directory exists
        output_dir = self.config.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate export filename
        export_path = os.path.join(output_dir, f"vanity_addresses.{format_type}")
        
        # Export results
        try:
            success, message = export_addresses_to_file(self.results, format_type, export_path)
            
            # Display export result
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT, 
                    {
                        'type': 'export_result', 
                        'success': success, 
                        'message': message
                    }
                )
            )
        except Exception as e:
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT, 
                    {
                        'type': 'export_result', 
                        'success': False, 
                        'message': str(e)
                    }
                )
            )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if event was handled
        """
        # Handle export buttons
        self.json_export_button.handle_event(event)
        self.html_export_button.handle_event(event)
        self.back_button.handle_event(event)
        
        return True
    
    def run(self) -> str:
        """
        Run the results screen loop
        
        Returns:
            str: Result of screen interaction (e.g., 'back', 'exit')
        """
        clock = pygame.time.Clock()
        
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                
                # Custom export events
                if event.type == pygame.USEREVENT:
                    if event.dict['type'] == 'export_result':
                        # TODO: Add a notification mechanism for export results
                        success = event.dict['success']
                        message = event.dict['message']
                        print(f"Export {'succeeded' if success else 'failed'}: {message}")
                
                # Handle other events
                self.handle_event(event)
            
            # Draw
            self.draw()
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            clock.tick(60)


if __name__ == "__main__":
    # For standalone testing
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Solana Vanity Address Generator - Results")
    
    # Mock results for testing
    mock_results = {
        'success': True,
        'results': [
            {'pubkey': 'ABC123xyz', 'path': '/path/to/key1'},
            {'pubkey': 'DEF456abc', 'path': '/path/to/key2'}
        ]
    }
    
    def on_back():
        print("Back to previous screen")
    
    results_screen = ResultsScreen(screen, mock_results, on_back)
    results_screen.run()