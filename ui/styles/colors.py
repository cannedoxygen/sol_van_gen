"""
Color definitions for the CMYK Retro Lo-Fi Solana Vanity Generator
Contains constants and helper functions for the application's color scheme
"""

from typing import Tuple, Dict, List

# Basic CMYK color palette - RGB values
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
KEY_BLACK = (30, 30, 30)

# Secondary colors
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (180, 180, 180)

# Bright variants
BRIGHT_CYAN = (80, 255, 255)
BRIGHT_MAGENTA = (255, 80, 255)
BRIGHT_YELLOW = (255, 255, 80)

# Dark variants
DARK_CYAN = (0, 150, 150)
DARK_MAGENTA = (150, 0, 150)
DARK_YELLOW = (150, 150, 0)

# Special UI colors
BACKGROUND = (40, 40, 40)
TEXT_PRIMARY = (220, 220, 220)
TEXT_SECONDARY = (180, 180, 180)
ERROR = (255, 80, 80)
SUCCESS = (80, 255, 80)

# RGB Colors with alpha component
TRANSPARENT = (0, 0, 0, 0)
SEMI_TRANSPARENT_BLACK = (0, 0, 0, 128)
SEMI_TRANSPARENT_WHITE = (255, 255, 255, 128)

# Color schemes mapped by name
THEME_COLORS = {
    "cyan": {
        "primary": CYAN,
        "secondary": DARK_CYAN,
        "highlight": BRIGHT_CYAN,
        "text": WHITE,
        "background": (20, 50, 50),
        "active": (0, 200, 200),
        "border": (0, 255, 255),
        "shadow": (0, 100, 100, 150),
        "glow": (0, 255, 255, 100)
    },
    "magenta": {
        "primary": MAGENTA,
        "secondary": DARK_MAGENTA,
        "highlight": BRIGHT_MAGENTA,
        "text": WHITE,
        "background": (50, 20, 50),
        "active": (200, 0, 200),
        "border": (255, 0, 255),
        "shadow": (100, 0, 100, 150),
        "glow": (255, 0, 255, 100)
    },
    "yellow": {
        "primary": YELLOW,
        "secondary": DARK_YELLOW,
        "highlight": BRIGHT_YELLOW,
        "text": KEY_BLACK,
        "background": (50, 50, 20),
        "active": (200, 200, 0),
        "border": (255, 255, 0),
        "shadow": (100, 100, 0, 150),
        "glow": (255, 255, 0, 100)
    },
    "white": {
        "primary": WHITE,
        "secondary": LIGHT_GRAY,
        "highlight": WHITE,
        "text": KEY_BLACK,
        "background": (50, 50, 50),
        "active": (200, 200, 200),
        "border": (255, 255, 255),
        "shadow": (80, 80, 80, 150),
        "glow": (255, 255, 255, 100)
    },
    "cmyk": {
        "primary": CYAN,
        "secondary": MAGENTA,
        "tertiary": YELLOW,
        "quaternary": KEY_BLACK,
        "text": WHITE,
        "background": (30, 30, 30),
        "active": (80, 80, 80),
        "border": (180, 180, 180),
        "shadow": (0, 0, 0, 150),
        "glow": (255, 255, 255, 80)
    }
}

def get_color_gradient(color1: Tuple[int, int, int], 
                       color2: Tuple[int, int, int], 
                       steps: int) -> List[Tuple[int, int, int]]:
    """
    Generate a gradient between two colors
    
    Args:
        color1: Starting RGB color tuple
        color2: Ending RGB color tuple
        steps: Number of gradient steps to generate
        
    Returns:
        List of RGB color tuples forming a gradient
    """
    r_step = (color2[0] - color1[0]) / steps
    g_step = (color2[1] - color1[1]) / steps
    b_step = (color2[2] - color1[2]) / steps
    
    gradient = []
    for i in range(steps):
        r = int(color1[0] + r_step * i)
        g = int(color1[1] + g_step * i)
        b = int(color1[2] + b_step * i)
        gradient.append((r, g, b))
    
    return gradient

def get_cmyk_wave_colors(steps: int) -> List[Tuple[int, int, int]]:
    """
    Generate a color wave through CMYK colors
    
    Args:
        steps: Number of colors to generate
        
    Returns:
        List of RGB color tuples
    """
    # Create a list of the main colors
    color_points = [CYAN, MAGENTA, YELLOW, KEY_BLACK, CYAN]
    
    # Calculate how many steps between each color point
    steps_per_segment = steps // (len(color_points) - 1)
    
    # Generate the wave
    wave = []
    for i in range(len(color_points) - 1):
        segment = get_color_gradient(
            color_points[i],
            color_points[i+1],
            steps_per_segment
        )
        wave.extend(segment)
    
    return wave[:steps]  # Ensure we only return the requested number of steps

def get_theme_color(theme: str, color_name: str, default: Tuple[int, int, int] = None) -> Tuple:
    """
    Get a color from a specific theme
    
    Args:
        theme: Theme name ('cyan', 'magenta', 'yellow', 'white', 'cmyk')
        color_name: Name of the color in the theme
        default: Default color to return if not found
        
    Returns:
        RGB or RGBA color tuple
    """
    if theme in THEME_COLORS and color_name in THEME_COLORS[theme]:
        return THEME_COLORS[theme][color_name]
    return default or WHITE

def get_alpha_color(color: Tuple[int, int, int], alpha: int) -> Tuple[int, int, int, int]:
    """
    Add alpha channel to an RGB color
    
    Args:
        color: RGB color tuple
        alpha: Alpha value (0-255)
        
    Returns:
        RGBA color tuple
    """
    return (color[0], color[1], color[2], alpha)

def create_tint(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """
    Create a tinted (lighter) version of a color
    
    Args:
        color: RGB color tuple
        factor: Tint factor (0.0-1.0) where 1.0 = white
        
    Returns:
        Tinted RGB color tuple
    """
    r = int(color[0] + (255 - color[0]) * factor)
    g = int(color[1] + (255 - color[1]) * factor)
    b = int(color[2] + (255 - color[2]) * factor)
    return (r, g, b)

def create_shade(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """
    Create a shaded (darker) version of a color
    
    Args:
        color: RGB color tuple
        factor: Shade factor (0.0-1.0) where 1.0 = black
        
    Returns:
        Shaded RGB color tuple
    """
    r = int(color[0] * (1 - factor))
    g = int(color[1] * (1 - factor))
    b = int(color[2] * (1 - factor))
    return (r, g, b)