"""
Theme management for the CMYK Retro Lo-Fi Solana Vanity Generator
Provides consistent styling across the application
"""

import pygame
from typing import Dict, Tuple, Any, List, Optional

from ui.styles.colors import THEME_COLORS, get_theme_color
from utils.config_manager import ConfigManager

class Theme:
    """
    Theme class for storing and applying visual styles
    """
    
    def __init__(self, theme_name: str = "cyan"):
        """
        Initialize a theme
        
        Args:
            theme_name: Name of the theme ('cyan', 'magenta', 'yellow', 'white', 'cmyk')
        """
        self.name = theme_name
        self.colors = THEME_COLORS.get(theme_name, THEME_COLORS["cyan"])
        
        # Load fonts
        self.load_fonts()
    
    def load_fonts(self):
        """Load theme fonts"""
        try:
            import os
            
            # Get base paths
            if getattr(pygame, 'SCALED', False):
                # For frozen applications
                base_path = getattr(pygame, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            else:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            
            # Font paths
            pixel_font_path = os.path.join(base_path, "assets", "fonts", "pixel_font.ttf")
            terminal_font_path = os.path.join(base_path, "assets", "fonts", "terminal_font.ttf")
            
            # Create fonts dictionary
            self.fonts = {
                "title": {
                    "regular": pygame.font.Font(pixel_font_path, 28),
                    "large": pygame.font.Font(pixel_font_path, 36),
                    "small": pygame.font.Font(pixel_font_path, 22)
                },
                "body": {
                    "regular": pygame.font.Font(terminal_font_path, 16),
                    "large": pygame.font.Font(terminal_font_path, 20),
                    "small": pygame.font.Font(terminal_font_path, 12)
                }
            }
        except (pygame.error, FileNotFoundError, ImportError):
            # Fallback to system fonts
            self.fonts = {
                "title": {
                    "regular": pygame.font.SysFont("monospace", 28, bold=True),
                    "large": pygame.font.SysFont("monospace", 36, bold=True),
                    "small": pygame.font.SysFont("monospace", 22, bold=True)
                },
                "body": {
                    "regular": pygame.font.SysFont("courier", 16),
                    "large": pygame.font.SysFont("courier", 20),
                    "small": pygame.font.SysFont("courier", 12)
                }
            }
    
    def get_color(self, color_name: str, default: Tuple[int, int, int] = None) -> Tuple:
        """
        Get a color from the theme
        
        Args:
            color_name: Name of the color in the theme
            default: Default color to return if not found
            
        Returns:
            RGB or RGBA color tuple
        """
        return get_theme_color(self.name, color_name, default)
    
    def get_font(self, font_type: str = "body", size: str = "regular") -> pygame.font.Font:
        """
        Get a font from the theme
        
        Args:
            font_type: Type of font ('title', 'body')
            size: Font size ('regular', 'large', 'small')
            
        Returns:
            pygame.font.Font: Font object
        """
        try:
            return self.fonts[font_type][size]
        except KeyError:
            # Fallback to default font
            return self.fonts["body"]["regular"]
    
    def render_text(self, 
                   text: str, 
                   font_type: str = "body", 
                   size: str = "regular", 
                   color_name: str = "text",
                   antialias: bool = True) -> pygame.Surface:
        """
        Render text using the theme's fonts and colors
        
        Args:
            text: Text to render
            font_type: Type of font ('title', 'body')
            size: Font size ('regular', 'large', 'small')
            color_name: Name of the color in the theme
            antialias: Whether to use antialiasing
            
        Returns:
            pygame.Surface: Rendered text surface
        """
        font = self.get_font(font_type, size)
        color = self.get_color(color_name)
        return font.render(text, antialias, color)
    
    def draw_box(self, 
                surface: pygame.Surface, 
                rect: pygame.Rect, 
                border_color_name: str = "border",
                bg_color_name: str = "background",
                border_width: int = 2,
                border_radius: int = 5,
                alpha: int = 255) -> None:
        """
        Draw a themed box on a surface
        
        Args:
            surface: Surface to draw on
            rect: Rectangle defining the box
            border_color_name: Name of the border color in the theme
            bg_color_name: Name of the background color in the theme
            border_width: Width of the border
            border_radius: Radius of rounded corners
            alpha: Transparency (0-255)
        """
        # Get colors
        border_color = self.get_color(border_color_name)
        bg_color = self.get_color(bg_color_name)
        
        # Create a surface with alpha channel
        box_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(
            box_surface,
            (*bg_color[:3], alpha),
            (0, 0, rect.width, rect.height),
            border_radius=border_radius
        )
        
        # Draw border
        if border_width > 0:
            pygame.draw.rect(
                box_surface,
                (*border_color[:3], alpha),
                (0, 0, rect.width, rect.height),
                width=border_width,
                border_radius=border_radius
            )
        
        # Blit the box to the target surface
        surface.blit(box_surface, rect)


class ThemeManager:
    """
    Manages theme selection and application
    """
    
    # Available theme names
    THEME_CYAN = "cyan"
    THEME_MAGENTA = "magenta"
    THEME_YELLOW = "yellow"
    THEME_WHITE = "white"
    THEME_CMYK = "cmyk"
    
    # Available themes list
    AVAILABLE_THEMES = [THEME_CYAN, THEME_MAGENTA, THEME_YELLOW, THEME_WHITE, THEME_CMYK]
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Initialize the theme manager
        
        Args:
            config: Optional ConfigManager instance
        """
        self.config = config or ConfigManager()
        
        # Get theme from config
        theme_name = self.config.get("theme", "cyan")
        if theme_name not in self.AVAILABLE_THEMES:
            theme_name = "cyan"
        
        # Create theme
        self.current_theme = Theme(theme_name)
    
    def get_theme(self) -> Theme:
        """
        Get the current theme
        
        Returns:
            Theme: Current theme
        """
        return self.current_theme
    
    def set_theme(self, theme_name: str) -> Theme:
        """
        Set the current theme
        
        Args:
            theme_name: Name of the theme to use
            
        Returns:
            Theme: New theme
        """
        if theme_name in self.AVAILABLE_THEMES:
            self.current_theme = Theme(theme_name)
            
            # Save to config
            if self.config:
                self.config.set("theme", theme_name)
        
        return self.current_theme
    
    def cycle_theme(self) -> Theme:
        """
        Cycle to the next theme
        
        Returns:
            Theme: New theme
        """
        current_index = self.AVAILABLE_THEMES.index(self.current_theme.name)
        next_index = (current_index + 1) % len(self.AVAILABLE_THEMES)
        return self.set_theme(self.AVAILABLE_THEMES[next_index])
    
    def get_available_themes(self) -> List[str]:
        """
        Get a list of available theme names
        
        Returns:
            List[str]: Available theme names
        """
        return self.AVAILABLE_THEMES.copy()


# Global theme manager instance
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """
    Get the global theme manager instance
    
    Returns:
        ThemeManager: Global theme manager
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager