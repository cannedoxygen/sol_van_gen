"""
ASCII Art module for the retro CMYK theme
Provides ASCII art banners and decorative elements for the application
"""

import random
import time
import sys
from typing import List, Tuple

# ANSI color codes for CMYK theme
class CMYKColors:
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    YELLOW = "\033[33m"
    BLACK = "\033[30m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_YELLOW = "\033[93m"
    GRAY = "\033[90m"
    RESET = "\033[0m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

# Main application logo
SOLANA_VANITY_LOGO = f"""
{CMYKColors.BRIGHT_CYAN}  ██████╗{CMYKColors.BRIGHT_MAGENTA}███╗   ███╗{CMYKColors.BRIGHT_YELLOW}██╗   ██╗{CMYKColors.GRAY}██╗  ██╗{CMYKColors.RESET}
{CMYKColors.BRIGHT_CYAN} ██╔════╝{CMYKColors.BRIGHT_MAGENTA}████╗ ████║{CMYKColors.BRIGHT_YELLOW}╚██╗ ██╔╝{CMYKColors.GRAY}██║ ██╔╝{CMYKColors.RESET}
{CMYKColors.BRIGHT_CYAN} ╚█████╗ {CMYKColors.BRIGHT_MAGENTA}██╔████╔██║{CMYKColors.BRIGHT_YELLOW} ╚████╔╝ {CMYKColors.GRAY}█████═╝ {CMYKColors.RESET}
{CMYKColors.BRIGHT_CYAN} ██╔══██╗{CMYKColors.BRIGHT_MAGENTA}██║╚██╔╝██║{CMYKColors.BRIGHT_YELLOW}  ╚██╔╝  {CMYKColors.GRAY}██╔═██╗ {CMYKColors.RESET}
{CMYKColors.BRIGHT_CYAN} ╚██████╔{CMYKColors.BRIGHT_MAGENTA}██║ ╚═╝ ██║{CMYKColors.BRIGHT_YELLOW}   ██║   {CMYKColors.GRAY}██║ ╚██╗{CMYKColors.RESET}
{CMYKColors.BRIGHT_CYAN}  ╚═════╝{CMYKColors.BRIGHT_MAGENTA}╚═╝     ╚═╝{CMYKColors.BRIGHT_YELLOW}   ╚═╝   {CMYKColors.GRAY}╚═╝  ╚═╝{CMYKColors.RESET}

{CMYKColors.BOLD}{CMYKColors.WHITE}  SOLANA VANITY ADDRESS GENERATOR  {CMYKColors.RESET}
{CMYKColors.DIM}{CMYKColors.WHITE}       RETRO LO-FI EDITION v1.0     {CMYKColors.RESET}
"""

# Loading animation frames
LOADING_FRAMES = [
    f"{CMYKColors.BRIGHT_CYAN}▓{CMYKColors.RESET}",
    f"{CMYKColors.BRIGHT_MAGENTA}▒{CMYKColors.RESET}",
    f"{CMYKColors.BRIGHT_YELLOW}░{CMYKColors.RESET}",
    f"{CMYKColors.GRAY}█{CMYKColors.RESET}"
]

# Box drawing characters
BOX_CHARS = {
    "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
    "h": "═", "v": "║", "vl": "╠", "vr": "╣",
    "hd": "╦", "hu": "╩", "c": "╬"
}

def display_ascii_art():
    """Display the main application logo with a retro effect"""
    print()
    # Display logo character by character for retro effect
    for line in SOLANA_VANITY_LOGO.split('\n'):
        for char in line:
            print(char, end='', flush=True)
            time.sleep(0.001)  # Slight delay for typing effect
        print()
    print()

def draw_retro_box(width: int, height: int, title: str = None) -> List[str]:
    """Create a retro-style box with optional title"""
    box = []
    
    # Top border with title
    if title:
        title_space = " " + title + " "
        title_len = len(title_space)
        if title_len > width - 4:
            title_space = " " + title[:width-6] + "... "
            title_len = len(title_space)
        
        left_border = (width - title_len) // 2
        if left_border < 2:
            left_border = 2
        right_border = width - left_border - title_len
        
        box.append(f"{BOX_CHARS['tl']}{BOX_CHARS['h'] * (left_border-1)}" +
                  f"{title_space}" +
                  f"{BOX_CHARS['h'] * (right_border-1)}{BOX_CHARS['tr']}")
    else:
        box.append(f"{BOX_CHARS['tl']}{BOX_CHARS['h'] * (width-2)}{BOX_CHARS['tr']}")
    
    # Middle rows
    for _ in range(height - 2):
        box.append(f"{BOX_CHARS['v']}{' ' * (width-2)}{BOX_CHARS['v']}")
    
    # Bottom border
    box.append(f"{BOX_CHARS['bl']}{BOX_CHARS['h'] * (width-2)}{BOX_CHARS['br']}")
    
    return box

def print_retro_box(width: int, height: int, title: str = None, color: str = CMYKColors.BRIGHT_CYAN):
    """Print a retro-style box with the specified color"""
    box = draw_retro_box(width, height, title)
    for line in box:
        print(f"{color}{line}{CMYKColors.RESET}")

def display_animated_progress(progress: float, width: int = 50, message: str = "Processing"):
    """Display an animated progress bar with CMYK color theme"""
    filled_width = int(width * progress)
    bar = ""
    
    # Create animated progress bar with CMYK colors
    for i in range(width):
        if i < filled_width:
            if i % 4 == 0:
                bar += f"{CMYKColors.BRIGHT_CYAN}█{CMYKColors.RESET}"
            elif i % 4 == 1:
                bar += f"{CMYKColors.BRIGHT_MAGENTA}█{CMYKColors.RESET}"
            elif i % 4 == 2:
                bar += f"{CMYKColors.BRIGHT_YELLOW}█{CMYKColors.RESET}"
            else:
                bar += f"{CMYKColors.GRAY}█{CMYKColors.RESET}"
        else:
            bar += f"{CMYKColors.DIM}░{CMYKColors.RESET}"
    
    percent = int(progress * 100)
    print(f"\r{message}: [{bar}] {percent}%", end="")
    sys.stdout.flush()

def display_typing_effect(text: str, speed: float = 0.02, color: str = CMYKColors.WHITE):
    """Display text with a typewriter effect"""
    for char in text:
        print(f"{color}{char}{CMYKColors.RESET}", end='', flush=True)
        time.sleep(speed)
    print()

def display_glitch_effect(text: str, iterations: int = 5, speed: float = 0.1):
    """Display text with a glitch effect"""
    glitch_chars = "!@#$%^&*()_+-=[]{}|;:,./<>?`~"
    original_chars = list(text)
    
    for _ in range(iterations):
        # Create glitched version
        glitched_text = list(text)
        num_glitches = random.randint(1, max(1, len(text) // 5))
        
        for _ in range(num_glitches):
            idx = random.randint(0, len(text) - 1)
            glitched_text[idx] = random.choice(glitch_chars)
        
        # Print the glitched version
        print("\r" + "".join(glitched_text), end="", flush=True)
        time.sleep(speed)
    
    # Restore original text
    print("\r" + "".join(original_chars), flush=True)

def retro_banner(title: str, width: int = 60, color: str = CMYKColors.BRIGHT_CYAN):
    """Create a retro-style banner with a title"""
    padding = (width - len(title) - 2) // 2
    banner = f"{color}╔{'═' * width}╗\n"
    banner += f"║{' ' * padding}{title}{' ' * (width - len(title) - padding)}║\n"
    banner += f"╚{'═' * width}╝{CMYKColors.RESET}"
    print(banner)

def display_retro_menu(options: List[Tuple[str, str]], title: str = "MAIN MENU", width: int = 60):
    """Display a retro-style menu with options and key bindings"""
    retro_banner(title, width)
    print()
    
    for key, option in options:
        print(f"  {CMYKColors.BRIGHT_YELLOW}[{key}]{CMYKColors.RESET} {option}")
    
    print("\n" + f"{CMYKColors.BRIGHT_CYAN}{'═' * width}{CMYKColors.RESET}")
    
    choice = input(f"\n{CMYKColors.BRIGHT_MAGENTA}Select an option: {CMYKColors.RESET}")
    return choice

def display_address_result(address: str, message: str = "Generated Address"):
    """Display a generated vanity address in a stylized box"""
    box_width = max(len(address) + 8, len(message) + 8)
    
    print(f"{CMYKColors.BRIGHT_MAGENTA}╔{'═' * box_width}╗{CMYKColors.RESET}")
    print(f"{CMYKColors.BRIGHT_MAGENTA}║{' ' * ((box_width - len(message)) // 2)}{message}{' ' * ((box_width - len(message) + 1) // 2)}║{CMYKColors.RESET}")
    print(f"{CMYKColors.BRIGHT_MAGENTA}╠{'═' * box_width}╣{CMYKColors.RESET}")
    print(f"{CMYKColors.BRIGHT_MAGENTA}║{' ' * ((box_width - len(address)) // 2)}{CMYKColors.BRIGHT_CYAN}{address}{CMYKColors.BRIGHT_MAGENTA}{' ' * ((box_width - len(address) + 1) // 2)}║{CMYKColors.RESET}")
    print(f"{CMYKColors.BRIGHT_MAGENTA}╚{'═' * box_width}╝{CMYKColors.RESET}")

def spinner(duration=5, message="Processing"):
    """Display a retro CMYK spinner animation"""
    frames = ["◢", "◣", "◤", "◥"]
    colors = [CMYKColors.BRIGHT_CYAN, CMYKColors.BRIGHT_MAGENTA, 
              CMYKColors.BRIGHT_YELLOW, CMYKColors.GRAY]
    
    end_time = time.time() + duration
    i = 0
    
    while time.time() < end_time:
        color = colors[i % len(colors)]
        frame = frames[i % len(frames)]
        print(f"\r{message} {color}{frame}{CMYKColors.RESET}", end="")
        time.sleep(0.1)
        i += 1
    
    print("\r" + " " * (len(message) + 2), end="\r")

if __name__ == "__main__":
    # Test the ASCII art functions
    display_ascii_art()
    time.sleep(1)
    
    print("Testing progress bar:")
    for i in range(101):
        display_animated_progress(i/100, message="Generating keys")
        time.sleep(0.01)
    print("\n")
    
    display_typing_effect("Welcome to the Solana Vanity Generator...", 
                         color=CMYKColors.BRIGHT_CYAN)
    time.sleep(0.5)
    
    options = [
        ("1", "Generate Vanity Address"),
        ("2", "Show Available Devices"),
        ("3", "Settings"),
        ("4", "Exit")
    ]
    display_retro_menu(options)
    
    spinner(3, "Testing spinner animation")
    print()
    
    display_address_result("ABcde12345XyZabcDefGHijk")