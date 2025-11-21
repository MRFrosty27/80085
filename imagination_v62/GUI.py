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
text_font = 'Arial'
text_size = screen_height* 0.05
text = pygame.font.SysFont(text_font, text_size)

def render_text(surface,text,x,y):
    if isinstance(text,str) == True:
        surface.blit((text).render(f"{text}",True,(0,0,0)),(x,y))

class text_box:#used in main menu
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
        text_surface = text.render(text, True, (0, 0, 0))
        text_width, text_height = text.size(text)

        # Calculate box dimensions
        padding_x = min_width  # Use min_width as padding on each side
        self.width = text_width + 2 * padding_x  # Total width: text width + left and right padding
        self.height = text_height  # Keep height as before, or adjust to text_height + padding

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

class option_menu:
    def __init__(self):
        self.__num_options = 0
        self.__option = []#format: title,function
        self.__surface = pygame.Surface(screen_width*0.1,1).fill((255,255,255))

    def option_add(self,title,function):
        if not isinstance(title, str) and not isinstance(function, str): return print('can not add option: option title or function not string type')
        self.__num_options += 1
        self.__option.append(title,function)
        self.__surface = pygame.Surface(screen_width*0.1,self.__num_options * text_size).fill((255,255,255))
        for n in range(len(self.__option)):
            render_text(self.__surface,self.__option[n][0],0,n*text_size)

    def render(self,x,y):
        display.blit(self.__surface,(x,y))

    def option_execute(self,index):
        exec(self.__num_options[1][index])

obj_option_menu = option_menu()
obj_option_menu.option_add('Remove',"""
db.object_remove(x,y)
""")
interconnect_option_menu = option_menu()
interconnect_option_menu.option_add('Remove',"""
db.interconnect_remove(x,y)
""")
