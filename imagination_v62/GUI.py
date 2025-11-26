import pygame
from start import settings,save

#the purpose of this file is to simplyfy UI design.

screen = None
mouse_pos = ()
screen_width = 0#must be set during runtime
screen_height = 0#must be set during runtime
min_width = 10
y_padding = 10
display =  None#must be set during runtime
mpos = None 
font_type = 'Arial'
font_size = screen_height* 0.05
font = pygame.font.SysFont(font_type, font_type)
message_queue = []

def render_text(surface,text,x,y):
    if isinstance(text,str) == True:
        surface.blit(font.render(f"{text}",True,(0,0,0)),(x,y))

def message(text,duration):#duration is in seconds
    message_queue.append((text,duration*settings["fps"]))

class text_box:#used in main menu

    def __init__(self, x, y, text,code,typeable):
        # Type checking
        if not isinstance(x, int):
            raise TypeError("x coordinate must be an integer")
        if not isinstance(y, int):
            raise TypeError("y coordinate must be an integer")
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if not isinstance(typeable, bool):
            raise TypeError("typeable must be a bool")
        elif typeable == None or typeable == False: self.__typeable == False
        else: self.__typeable == True

        self.__x = x
        self.__y = y
        self.__text = text
        self.__hover = False
        if typeable:
            if not isinstance(typeable,bool):
                raise TypeError("code must be a bool")
            self.__typeable = typeable
            self.__selected = False#marks when the user can type
            self.__input = ''
        elif code:#becomes static
            if not isinstance(code, str):
                raise TypeError("code must be a string")
            self.__code_click = code
            text_surface = self.__text.render(self.__text, True, (0, 0, 0))
            text_width, text_height = text_surface.size()

            # Calculate box dimensions
            self.__width = text_width + 2 * min_width  # Total width: text width + left and right padding
            self.__height = text_height + 2 * y_padding # Keep height as before, or adjust to text_height + padding
            self.__static_surface_selected = pygame.Surface()
            #when mouse is hovering over text box
            pygame.draw.rect(self.__static_surface_selected,(255,255,255),(0,0,self.__width, self.__height))
            pygame.draw.rect(self.__static_surface_selected,(255,255,255),(0,0,self.__width, self.__height),5)
            self.__static_surface_selected.blit(text_surface,(min_width,y_padding))
            #when mouse is not hovering over text box
            self.__static_surface = pygame.Surface()
            pygame.draw.rect(self.__static_surface, (200,200,200), (0,0, self.__width, self.__height))
            self.__static_surface.blit(text_surface,(min_width,y_padding))
        else:raise Warning("text box was neither defined for static or typeable")
    
    def hover(self):# Check if mouse is over the text box
        if mpos is not None:
            mouse_x, mouse_y = mpos
            if (self.__x <= mouse_x <= self.__x + self.__width and 
                self.__y <= mouse_y <= self.__y + self.__height):
                self.__hover = True
            else: self.__hover = False

    def render(self):
        # Draw the text box
        if self.__typeable:
            # Set font and calculate text dimensions
            
            if len(self.__input) > 0:
                text_surface = font.render(self.__input, True, (0, 0, 0))
                text_width, text_height = text_surface.size()

                # Calculate box dimensions
                self.__width = text_width + 2 * min_width  # Total width: text width + left and right padding
                self.__height = text_height  # Keep height as before, or adjust to text_height + padding
                display.blit(text_surface,(self.__x+min_width, self.__y))
            else:
                text_surface = font.render(self.__text, True, (0, 0, 0))
                text_width, text_height = text_surface.size()

                # Calculate box dimensions
                self.__width = text_width + 2 * min_width  # Total width: text width + left and right padding
                self.__height = text_height  # Keep height as before, or adjust to text_height + padding
            if self.__hover:
                pygame.draw.rect(display, (255,255,255), (self.__x, self.__y, self.__width, self.__height))
                pygame.draw.rect(display, (255,215,0), (self.__x, self.__y, self.__width, self.__height), 5)
            else: pygame.draw.rect(display, (200,200,200), (self.__x, self.__y, self.__width, self.__height))
        else:
            if self.__hover: display.blit(self.__static_surface_selected, (self.__x + min_width, self.__y + y_padding))
            else: display.blit(self.__static_surface, (self.__x + min_width, self.__y + y_padding))

    def click(self):
        if self.__typeable == False:
            exec(self.__code_click)
        else:
            if self.__hover:
                self.__selected = True
            else:self.__selected = False

    def move(self,dx,dy):
        self.__x += dx
        self.__y += dy

    def change_text(self,text):
        self.__text == text
        text_surface = self.__text.render(self.__text, True, (0, 0, 0))
        text_width, text_height = text_surface.size()

        # Calculate box dimensions
        self.__width = text_width + 2 * min_width  # Total width: text width + left and right padding
        self.__height = text_height + 2 * y_padding # Keep height as before, or adjust to text_height + padding
        self.__static_surface_selected = pygame.Surface()
        #when mouse is hovering over text box
        pygame.draw.rect(self.__static_surface_selected,(255,255,255),(0,0,self.__width, self.__height))
        pygame.draw.rect(self.__static_surface_selected,(255,255,255),(0,0,self.__width, self.__height),5)
        self.__static_surface_selected.blit(text_surface,(min_width,y_padding))
        #when mouse is not hovering over text box
        self.__static_surface = pygame.Surface()
        pygame.draw.rect(self.__static_surface, (200,200,200), (0,0, self.__width, self.__height))
        self.__static_surface.blit(text_surface,(min_width,y_padding))

    def input_add(self,user_input):
        if self.__typeable == True and self.__selected == True:
            self.__input.append(str(user_input))
        else:raise Warning("called input_add() for non typeable text box")

    def input_remove(self):
        if self.__typeable == True and self.__selected == True:
            self.__input[:-1]# Remove last character
        else:raise Warning("called input_remove() for non typeable text box")

    def input_get(self):
        return self.__input

    def submit(self):
        if self.__typeable:
            self.__input = ''#reset input
        else:raise Warning("cannot submit non typeable text box")

class option_menu:
    def __init__(self):
        self.__num_options = 0
        self.__option = []#format: title,function
        self.__surface = pygame.Surface(screen_width*0.1,1).fill((255,255,255))

    def option_add(self,title,function):
        if not isinstance(title, str) and not isinstance(function, str): return print('can not add option: option title or function not string type')
        self.__num_options += 1
        self.__option.append(title,function)
        self.__surface = pygame.Surface(screen_width*0.1,self.__num_options * font_size).fill((255,255,255))
        for n in range(len(self.__option)):
            render_text(self.__surface,self.__option[n][0],0,n*font_size)

    def render(self,x,y):
        display.blit(self.__surface,(x,y))

    def option_execute(self,index):
        exec(self.__num_options[1][index])

#create option menus
obj_option_menu = option_menu()
obj_option_menu.option_add('Remove',"""
db.object_remove(x,y)
""")
interconnect_option_menu = option_menu()
interconnect_option_menu.option_add('Remove',"""
db.interconnect_remove(x,y)
""")

tb1 = text_box(screen_width*0.01,screen_height*0.01,f"Width: {settings["screen_width"]}",True)
tb2 = text_box(screen_width*0.01,screen_height*0.01 + font_size,f"height: {settings["screen_height"]}",True)
tb3 = text_box(screen_width*0.01,screen_height*0.01 + (2*font_size),"New project name",True)
tb4 = text_box(screen_width*0.01,screen_height*0.01 + (3*font_size),"Exit")