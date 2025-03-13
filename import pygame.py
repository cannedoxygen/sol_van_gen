import pygame
import random
import os

def create_background(width=1600, height=900, output_path='assets/images/background.png'):
    """
    Create a procedural background image with CMYK-inspired pixel noise
    """
    # Initialize Pygame
    pygame.init()
    
    # Create a surface
    surface = pygame.Surface((width, height))
    
    # Dark background color
    surface.fill((40, 40, 40))  # Dark gray
    
    # CMYK-inspired colors for noise
    cmyk_colors = [
        (0, 255, 255, 50),    # Cyan
        (255, 0, 255, 50),    # Magenta
        (255, 255, 0, 50),    # Yellow
        (60, 60, 60, 50)      # Key (Black)
    ]
    
    # Add some random 'pixel noise'
    for _ in range(5000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        color = random.choice(cmyk_colors)
        pygame.draw.rect(surface, color, (x, y, 2, 2))
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the image
    pygame.image.save(surface, output_path)
    
    print(f"Background image saved to {output_path}")
    
    # Cleanup
    pygame.quit()

# Run the function
create_background()