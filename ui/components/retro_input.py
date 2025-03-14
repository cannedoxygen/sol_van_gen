"""
RetroInput component for the CMYK lo-fi UI
A custom styled text input with retro aesthetics
"""

import pygame
import pygame.freetype
import os
import time
import math
from typing import Callable, Tuple, Optional

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

class RetroInput:
    """
    A retro-styled text input with CMYK color scheme and terminal-like aesthetics
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
        placeholder: str = "",
        initial_text: str = "",
        color_scheme: str = "cyan",
        font_size: int = 12,
        max_length: int = 50,
        border_width: int = 2,
        corner_radius: int = 4,
        padding: int = 8,
        on_change: Callable[[str], None] = None,
        sound_enabled: bool = True,
        cursor_blink_rate: float = 0.5,
        password_mode: bool = False
    ):
        """
        Initialize a new RetroInput instance
        
        Args:
            x: X coordinate position
            y: Y coordinate position
            width: Input width
            height: Input height
            placeholder: Placeholder text shown when empty
            initial_text: Initial input value
            color_scheme: Color theme ('cyan', 'magenta', 'yellow', 'white')
            font_size: Size of the text
            max_length: Maximum number of characters
            border_width: Width of input border
            corner_radius: Radius of rounded corners
            padding: Internal padding
            on_change: Callback when text changes
            sound_enabled: Whether to play sound effects
            cursor_blink_rate: Speed of cursor blinking
            password_mode: Whether to mask text input
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.placeholder = placeholder
        self.text = initial_text
        self.max_length = max_length
        self.border_width = border_width
        self.corner_radius = corner_radius
        self.padding = padding
        self.on_change = on_change
        self.sound_enabled = sound_enabled
        self.cursor_blink_rate = cursor_blink_rate
        self.password_mode = password_mode
        
        # Input state
        self.active = False
        self.cursor_pos = len(initial_text)
        self.cursor_visible = True
        self.last_blink_time = time.time()
        self.selection_start = None
        self.selection_end = None
        
        # Set colors based on scheme
        self.set_color_scheme(color_scheme)
        
        # Load font
        self.font_size = font_size
        self.font = self.load_font()
        
        # Load sound effects
        self.key_sound = None
        self.activate_sound = None
        self.load_sounds()
        
        # Repeat key timing
        self.repeat_key = None
        self.repeat_start_time = 0
        self.repeat_interval = 0.05  # seconds between repeats
        self.repeat_delay = 0.4  # delay before repeating starts
    
    def set_color_scheme(self, scheme: str):
        """Set input colors based on the selected scheme"""
        if scheme == "cyan":
            self.bg_color = (20, 50, 50)
            self.active_bg_color = (30, 60, 60)
            self.border_color = (0, 200, 200)
            self.active_border_color = (0, 255, 255)
            self.text_color = self.WHITE
            self.placeholder_color = (100, 150, 150)
            self.cursor_color = (0, 255, 255)
            self.selection_color = (0, 100, 100)
            
        elif scheme == "magenta":
            self.bg_color = (50, 20, 50)
            self.active_bg_color = (60, 30, 60)
            self.border_color = (200, 0, 200)
            self.active_border_color = (255, 0, 255)
            self.text_color = self.WHITE
            self.placeholder_color = (150, 100, 150)
            self.cursor_color = (255, 0, 255)
            self.selection_color = (100, 0, 100)
            
        elif scheme == "yellow":
            self.bg_color = (50, 50, 20)
            self.active_bg_color = (60, 60, 30)
            self.border_color = (200, 200, 0)
            self.active_border_color = (255, 255, 0)
            self.text_color = self.WHITE
            self.placeholder_color = (150, 150, 100)
            self.cursor_color = (255, 255, 0)
            self.selection_color = (100, 100, 0)
            
        else:  # Default white
            self.bg_color = (40, 40, 40)
            self.active_bg_color = (50, 50, 50)
            self.border_color = (150, 150, 150)
            self.active_border_color = (200, 200, 200)
            self.text_color = self.WHITE
            self.placeholder_color = (120, 120, 120)
            self.cursor_color = (220, 220, 220)
            self.selection_color = (80, 80, 80)
    
    def load_font(self) -> pygame.freetype.Font:
        """Load the terminal font for the input"""
        try:
            font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "terminal_font.ttf")
            return pygame.freetype.Font(font_path, self.font_size)
        except (pygame.error, FileNotFoundError):
            # Fall back to default font if custom font not found
            return pygame.freetype.SysFont("courier", self.font_size)
    
    def load_sounds(self):
        """Load input sound effects"""
        try:
            if self.sound_enabled:
                key_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "keypress.wav")
                activate_sound_path = os.path.join(PROJECT_ROOT, "assets", "sounds", "success.wav")
                
                self.key_sound = pygame.mixer.Sound(key_sound_path)
                self.key_sound.set_volume(0.2)
                
                self.activate_sound = pygame.mixer.Sound(activate_sound_path)
                self.activate_sound.set_volume(0.3)
        except (pygame.error, FileNotFoundError):
            # Silently fail if sounds can't be loaded
            self.sound_enabled = False
    
    def draw(self, surface: pygame.Surface):
        """
        Draw the input field on the specified surface
        
        Args:
            surface: Pygame surface to draw on
        """
        # Update cursor blink state
        current_time = time.time()
        if current_time - self.last_blink_time > self.cursor_blink_rate:
            self.cursor_visible = not self.cursor_visible
            self.last_blink_time = current_time
        
        # Determine current colors based on state
        border_color = self.active_border_color if self.active else self.border_color
        bg_color = self.active_bg_color if self.active else self.bg_color
        
        # Draw border
        pygame.draw.rect(
            surface,
            border_color,
            (self.x, self.y, self.width, self.height),
            border_radius=self.corner_radius
        )
        
        # Draw background
        pygame.draw.rect(
            surface,
            bg_color,
            (
                self.x + self.border_width,
                self.y + self.border_width,
                self.width - self.border_width * 2,
                self.height - self.border_width * 2
            ),
            border_radius=max(0, self.corner_radius - self.border_width)
        )
        
        # Calculate text area
        text_area_rect = pygame.Rect(
            self.x + self.padding,
            self.y + self.padding,
            self.width - self.padding * 2,
            self.height - self.padding * 2
        )
        
        # Prepare display text (masked if password mode)
        display_text = '*' * len(self.text) if self.password_mode else self.text
        
        # Draw placeholder text if empty
        if not self.text and not self.active:
            placeholder_surface, _ = self.font.render(
                self.placeholder,
                self.placeholder_color
            )
            surface.blit(placeholder_surface, (text_area_rect.x, text_area_rect.y))
        
        # Draw text if not empty
        if self.text:
            # Measure text width to handle scrolling for long text
            text_surface, text_rect = self.font.render(display_text, self.text_color)
            
            # Handle text that's too wide for the input
            if text_rect.width > text_area_rect.width:
                # Calculate cursor position in pixels
                cursor_text = display_text[:self.cursor_pos]
                cursor_surface, cursor_rect = self.font.render(cursor_text, self.text_color)
                cursor_x = cursor_rect.width
                
                # Scroll text to keep cursor visible
                if cursor_x > text_area_rect.width:
                    # Scroll right to show cursor
                    scroll_offset = cursor_x - text_area_rect.width + 10  # 10px buffer
                    text_x = text_area_rect.x - scroll_offset
                else:
                    # Align text to left
                    text_x = text_area_rect.x
            else:
                # Text fits, no scrolling needed
                text_x = text_area_rect.x
            
            # Draw text with current scroll position
            surface.blit(text_surface, (text_x, text_area_rect.y))
            
            # Draw selection highlight if there's a selection
            if self.selection_start is not None and self.selection_end is not None:
                sel_start = min(self.selection_start, self.selection_end)
                sel_end = max(self.selection_start, self.selection_end)
                
                if sel_start != sel_end:
                    # Get text dimensions before selection
                    pre_sel_text = display_text[:sel_start]
                    pre_sel_surface, pre_sel_rect = self.font.render(pre_sel_text, self.text_color)
                    
                    # Get selected text dimensions
                    sel_text = display_text[sel_start:sel_end]
                    sel_surface, sel_rect = self.font.render(sel_text, self.text_color)
                    
                    # Calculate selection rectangle
                    sel_x = text_x + pre_sel_rect.width
                    sel_width = sel_rect.width
                    
                    # Draw selection highlight
                    pygame.draw.rect(
                        surface,
                        self.selection_color,
                        (sel_x, text_area_rect.y, sel_width, text_rect.height)
                    )
                    
                    # Redraw selected text over highlight
                    surface.blit(sel_surface, (sel_x, text_area_rect.y))
            
            # Draw cursor if active and visible
            if self.active and self.cursor_visible:
                # Calculate cursor position
                cursor_text = display_text[:self.cursor_pos]
                cursor_surface, cursor_rect = self.font.render(cursor_text, self.text_color)
                cursor_x = text_x + cursor_rect.width
                
                # Draw cursor line
                pygame.draw.line(
                    surface,
                    self.cursor_color,
                    (cursor_x, text_area_rect.y),
                    (cursor_x, text_area_rect.y + text_rect.height),
                    2
                )
        else:
            # Draw just the cursor when text is empty
            if self.active and self.cursor_visible:
                pygame.draw.line(
                    surface,
                    self.cursor_color,
                    (text_area_rect.x, text_area_rect.y),
                    (text_area_rect.x, text_area_rect.y + self.font_size),
                    2
                )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the input field
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        # Check if mouse is over input field
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            input_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            
            # Toggle active state based on click location
            was_active = self.active
            self.active = input_rect.collidepoint(mouse_pos)
            
            # Play activation sound if becoming active
            if not was_active and self.active and self.sound_enabled and self.activate_sound:
                self.activate_sound.play()
            
            # Set cursor position based on click location if active
            if self.active:
                # Calculate horizontal position in text
                text_x = mouse_pos[0] - (self.x + self.padding)
                
                # Find closest character position
                if self.text:
                    # Measure each character to find closest position
                    best_pos = 0
                    min_diff = float('inf')
                    
                    for i in range(len(self.text) + 1):
                        text_segment = self.text[:i]
                        text_surface, text_rect = self.font.render(text_segment, self.text_color)
                        pos_x = text_rect.width
                        diff = abs(text_x - pos_x)
                        
                        if diff < min_diff:
                            min_diff = diff
                            best_pos = i
                    
                    self.cursor_pos = best_pos
                    
                    # Start selection if shift is held
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        if self.selection_start is None:
                            self.selection_start = self.cursor_pos
                        self.selection_end = self.cursor_pos
                    else:
                        # Clear selection if shift is not held
                        self.selection_start = None
                        self.selection_end = None
                else:
                    self.cursor_pos = 0
            
            return self.active
            
        # Handle key events when active
        elif self.active and event.type == pygame.KEYDOWN:
            # Reset cursor blink on any key press
            self.cursor_visible = True
            self.last_blink_time = time.time()
            
            # Setup key repeat
            self.repeat_key = event.key
            self.repeat_start_time = time.time()
            
            # Handle selection with shift + arrow keys
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_HOME, pygame.K_END):
                shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT
                
                # Initialize selection if shift just pressed
                if shift_held and self.selection_start is None:
                    self.selection_start = self.cursor_pos
            
            # Handle special keys
            if event.key == pygame.K_BACKSPACE:
                if self.selection_start is not None and self.selection_end is not None:
                    # Delete selection
                    sel_start = min(self.selection_start, self.selection_end)
                    sel_end = max(self.selection_start, self.selection_end)
                    self.text = self.text[:sel_start] + self.text[sel_end:]
                    self.cursor_pos = sel_start
                    self.selection_start = None
                    self.selection_end = None
                elif self.cursor_pos > 0:
                    # Delete character before cursor
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                
                # Play key sound
                if self.sound_enabled and self.key_sound:
                    self.key_sound.play()
                
                # Trigger onChange callback
                if self.on_change:
                    self.on_change(self.text)
                
                return True
                
            elif event.key == pygame.K_DELETE:
                if self.selection_start is not None and self.selection_end is not None:
                    # Delete selection
                    sel_start = min(self.selection_start, self.selection_end)
                    sel_end = max(self.selection_start, self.selection_end)
                    self.text = self.text[:sel_start] + self.text[sel_end:]
                    self.cursor_pos = sel_start
                    self.selection_start = None
                    self.selection_end = None
                elif self.cursor_pos < len(self.text):
                    # Delete character after cursor
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                
                # Play key sound
                if self.sound_enabled and self.key_sound:
                    self.key_sound.play()
                
                # Trigger onChange callback
                if self.on_change:
                    self.on_change(self.text)
                
                return True
                
            elif event.key == pygame.K_LEFT:
                # Move cursor left
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                
                # Update selection
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selection_end = self.cursor_pos
                else:
                    self.selection_start = None
                    self.selection_end = None
                
                return True
                
            elif event.key == pygame.K_RIGHT:
                # Move cursor right
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                
                # Update selection
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selection_end = self.cursor_pos
                else:
                    self.selection_start = None
                    self.selection_end = None
                
                return True
                
            elif event.key == pygame.K_HOME:
                # Move cursor to start
                self.cursor_pos = 0
                
                # Update selection
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selection_end = self.cursor_pos
                else:
                    self.selection_start = None
                    self.selection_end = None
                
                return True
                
            elif event.key == pygame.K_END:
                # Move cursor to end
                self.cursor_pos = len(self.text)
                
                # Update selection
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selection_end = self.cursor_pos
                else:
                    self.selection_start = None
                    self.selection_end = None
                
                return True
                
            elif event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Select all
                self.selection_start = 0
                self.selection_end = len(self.text)
                self.cursor_pos = len(self.text)
                return True
                
            elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Copy to clipboard
                if self.selection_start is not None and self.selection_end is not None:
                    sel_start = min(self.selection_start, self.selection_end)
                    sel_end = max(self.selection_start, self.selection_end)
                    selected_text = self.text[sel_start:sel_end]
                    pygame.scrap.put(pygame.SCRAP_TEXT, selected_text.encode())
                return True
                
            elif event.key == pygame.K_x and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Cut to clipboard
                if self.selection_start is not None and self.selection_end is not None:
                    sel_start = min(self.selection_start, self.selection_end)
                    sel_end = max(self.selection_start, self.selection_end)
                    selected_text = self.text[sel_start:sel_end]
                    pygame.scrap.put(pygame.SCRAP_TEXT, selected_text.encode())
                    
                    # Delete selection
                    self.text = self.text[:sel_start] + self.text[sel_end:]
                    self.cursor_pos = sel_start
                    self.selection_start = None
                    self.selection_end = None
                    
                    # Trigger onChange callback
                    if self.on_change:
                        self.on_change(self.text)
                return True
                
            elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Paste from clipboard
                try:
                    if pygame.scrap.has_type(pygame.SCRAP_TEXT):
                        clipboard_text = pygame.scrap.get(pygame.SCRAP_TEXT).decode().strip('\0')
                        
                        # Delete selection if exists
                        if self.selection_start is not None and self.selection_end is not None:
                            sel_start = min(self.selection_start, self.selection_end)
                            sel_end = max(self.selection_start, self.selection_end)
                            self.text = self.text[:sel_start] + self.text[sel_end:]
                            self.cursor_pos = sel_start
                        
                        # Insert at cursor position
                        new_text = self.text[:self.cursor_pos] + clipboard_text + self.text[self.cursor_pos:]
                        
                        # Check max length
                        if len(new_text) <= self.max_length:
                            self.text = new_text
                            self.cursor_pos += len(clipboard_text)
                        
                        # Clear selection
                        self.selection_start = None
                        self.selection_end = None
                        
                        # Trigger onChange callback
                        if self.on_change:
                            self.on_change(self.text)
                except:
                    pass  # Clipboard operations can fail
                
                return True
                
            elif event.key == pygame.K_RETURN:
                # Submit input
                self.active = False
                return True
                
            elif event.key == pygame.K_ESCAPE:
                # Cancel input
                self.active = False
                return True
                
            elif event.key == pygame.K_TAB:
                # Tab to next input (should be handled by parent container)
                self.active = False
                return True
                
            else:
                # Input character
                if event.unicode and len(self.text) < self.max_length:
                    # Delete selection if exists
                    if self.selection_start is not None and self.selection_end is not None:
                        sel_start = min(self.selection_start, self.selection_end)
                        sel_end = max(self.selection_start, self.selection_end)
                        self.text = self.text[:sel_start] + self.text[sel_end:]
                        self.cursor_pos = sel_start
                        self.selection_start = None
                        self.selection_end = None
                    
                    # Insert character
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += len(event.unicode)
                    
                    # Play key sound
                    if self.sound_enabled and self.key_sound:
                        self.key_sound.play()
                    
                    # Trigger onChange callback
                    if self.on_change:
                        self.on_change(self.text)
                    
                    return True
        
        # Handle key repeat
        elif self.active and event.type == pygame.KEYUP:
            if event.key == self.repeat_key:
                self.repeat_key = None
        
        return False
    
    def update(self):
        """Update the input state (handle key repeats, etc.)"""
        # Handle key repeats
        if self.active and self.repeat_key is not None:
            current_time = time.time()
            if current_time - self.repeat_start_time > self.repeat_delay:
                # Create a synthetic key event
                repeat_event = pygame.event.Event(
                    pygame.KEYDOWN,
                    key=self.repeat_key,
                    unicode=''  # Only navigation keys repeat
                )
                self.handle_event(repeat_event)
                
                # Reset repeat timer
                self.repeat_start_time = current_time - self.repeat_delay + self.repeat_interval
    
    def get_text(self) -> str:
        """Get the current input text"""
        return self.text
    
    def set_text(self, text: str):
        """Set the input text"""
        self.text = text[:self.max_length]
        self.cursor_pos = min(len(self.text), self.cursor_pos)
        
        if self.on_change:
            self.on_change(self.text)
    
    def clear(self):
        """Clear the input text"""
        self.text = ""
        self.cursor_pos = 0
        self.selection_start = None
        self.selection_end = None
        
        if self.on_change:
            self.on_change(self.text)
    
    def set_active(self, active: bool):
        """Set the active state"""
        was_active = self.active
        self.active = active
        
        if not was_active and active and self.sound_enabled and self.activate_sound:
            self.activate_sound.play()
    
    def is_active(self) -> bool:
        """Check if the input is active"""
        return self.active
    
    def get_rect(self) -> pygame.Rect:
        """Get the input's rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


# Example usage
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    pygame.scrap.init()  # Initialize clipboard
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("RetroInput Test")
    clock = pygame.time.Clock()
    
    def on_text_change(text):
        print(f"Text changed: {text}")
    
    # Create test inputs with different color schemes
    cyan_input = RetroInput(100, 100, 300, 40, "Enter Solana Address Prefix", "", "cyan", on_change=on_text_change)
    magenta_input = RetroInput(100, 170, 300, 40, "Enter Solana Address Suffix", "", "magenta", on_change=on_text_change)
    yellow_input = RetroInput(100, 240, 300, 40, "Enter # of Addresses to Generate", "", "yellow", on_change=on_text_change)
    password_input = RetroInput(100, 310, 300, 40, "Password Input", "", "cyan", password_mode=True)
    
    running = True
    while running:
        screen.fill((40, 40, 40))  # Dark background
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle input events
            cyan_input.handle_event(event)
            magenta_input.handle_event(event)
            yellow_input.handle_event(event)
            password_input.handle_event(event)
        
        # Update inputs
        cyan_input.update()
        magenta_input.update()
        yellow_input.update()
        password_input.update()
        
        # Draw inputs
        cyan_input.draw(screen)
        magenta_input.draw(screen)
        yellow_input.draw(screen)
        password_input.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()