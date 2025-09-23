import pygame

#the purpose of this file is to simplyfy UI design.

screen = None
mouse_pos = ()
screen_width = 0#must be set during runtime
screen_height = 0#must be set during runtime
min_width = 10
y_padding = 10
display =  None#must be set during runtime
mpos = None

class text_box:
    def __init__(self, x, y, text):
        # Type checking
        if not isinstance(x, int):
            raise TypeError("x coordinate must be an integer")
        if not isinstance(y, int):
            raise TypeError("y coordinate must be an integer")
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        self.x = x
        self.y = y
        self.text = text

        # Set font and calculate text dimensions
        font_size = int(screen_height * 0.05)
        self.font = pygame.font.SysFont('Arial', font_size)
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_width, text_height = self.font.size(text)

        # Calculate box dimensions
        padding_x = min_width  # Use min_width as padding on each side
        self.width = text_width + 2 * padding_x  # Total width: text width + left and right padding
        self.height = int(screen_height * 0.1)  # Keep height as before, or adjust to text_height + padding

        # Check if mouse is over the text box
        self.hover = False
        if mpos is not None:
            mouse_x, mouse_y = mpos
            if (self.x <= mouse_x <= self.x + self.width and 
                self.y <= mouse_y <= self.y + self.height):
                self.hover = True

        # Draw the text box
        if self.hover:
            pygame.draw.rect(display, (0,50,255), (self.x, self.y, self.width, self.height))
            pygame.draw.rect(display, (255,215,0), (self.x, self.y, self.width, self.height), 5)
        else:
            pygame.draw.rect(display, (255,255,255), (self.x, self.y, self.width, self.height))
        
        # Render text with padding
        display.blit(text_surface, (self.x + padding_x, self.y + y_padding))
