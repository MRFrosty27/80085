import pygame
from start import screen,screen_width,screen_height
from render import grid_size

#the purpose of this file is to simplyfy UI design.

mouse_pos = ()
min_width = 10
y_padding = 10
screen_width_20th = screen_width//20
screen_height_20th = screen_height//20
mpos = None 
font_type = "Arial"
font_size = screen_height//20
font = pygame.font.SysFont(font_type, font_size)
message_queue = []
white = (255,255,255)
black = (0,0,0)
plat = (200,225,255)
grey = (200,200,200)
#project_list
border = 5
font_size_project_list = screen_height//50
font_project_list = pygame.font.SysFont(font_type, font_size_project_list)
project_list_dim = [screen_width * 0.5+border,font_size_project_list + screen_height_20th,screen_width * 0.5 - screen_height_20th, font_size_project_list*2 + screen_height_20th]#index 1 and 3 are calc during runtime. index 0 and 1 are positions and index 3 and 4 are distance
del_x_pos = screen_width-screen_width_20th-font_size_project_list*2

def message(text,duration):#duration is in seconds
    message_queue.append((text,duration*60))

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
        elif typeable == None or typeable == False: self.__typeable = False
        else: self.__typeable = True

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
        else:#becomes static
            if not isinstance(code, str):
                raise TypeError("code must be a string")
            self.__code_click = code
            text_surface = font.render(self.__text, True, (0, 0, 0))
            text_width, text_height = text_surface.get_size()

            # Calculate box dimensions
            self.__width = text_width + 2 * min_width  # Total width: text width + left and right padding
            self.__height = text_height + 2 * y_padding # Keep height as before, or adjust to text_height + padding
            self.__static_surface_hover = pygame.Surface((self.__width,self.__height))
            #when mouse is hovering over text box
            self.__static_surface_hover.fill(white)
            pygame.draw.rect(self.__static_surface_hover,plat,(0,0,self.__width, self.__height),border)
            self.__static_surface_hover.blit(text_surface,(min_width,y_padding))
            #when mouse is not hovering over text box
            self.__static_surface = pygame.Surface((self.__width,self.__height))
            self.__static_surface.fill(grey)
            self.__static_surface.blit(text_surface,(min_width,y_padding))
    
    def hover(self):# Check if mouse is over the text box
        if mpos is not None:
            mouse_x, mouse_y = mpos
            if (self.__x <= mouse_x <= self.__x + self.__width and 
                self.__y <= mouse_y <= self.__y + self.__height):
                self.__hover = True
            else: 
                self.__hover = False


    def render(self):
        # Draw the text box
        if self.__typeable:
            # Set font and calculate text dimensions
            
            if len(self.__input) > 0:
                text_surface = font.render(self.__input, True, (0, 0, 0))
                text_width, text_height = text_surface.get_size()

                # Calculate box dimensions
                self.__width = text_width + 2 * min_width  # Total width: text width + left and right padding
                self.__height = text_height  # Keep height as before, or adjust to text_height + padding
                self.hover()
                if self.__hover:
                    pygame.draw.rect(screen, white, (self.__x, self.__y, self.__width, self.__height))
                    pygame.draw.rect(screen, plat, (self.__x, self.__y, self.__width, self.__height), border)
                else: pygame.draw.rect(screen, grey, (self.__x, self.__y, self.__width, self.__height))
                
                screen.blit(text_surface,(self.__x+min_width, self.__y))
            else:
                text_surface = font.render(self.__text, True, (0, 0, 0))
                text_width, text_height = text_surface.get_size()

                # Calculate box dimensions
                self.__width = text_width + 2 * min_width  # Total width: text width + left and right padding
                self.__height = text_height  # Keep height as before, or adjust to text_height + padding
                self.hover()
                if self.__hover:
                    pygame.draw.rect(screen, white, (self.__x, self.__y, self.__width, self.__height))
                    pygame.draw.rect(screen, plat, (self.__x, self.__y, self.__width, self.__height), border)
                else: pygame.draw.rect(screen, grey, (self.__x, self.__y, self.__width, self.__height))

                screen.blit(text_surface,(self.__x+min_width, self.__y))
        else:
            self.hover()
            if self.__hover: screen.blit(self.__static_surface_hover, (self.__x , self.__y ))
            else: screen.blit(self.__static_surface, (self.__x , self.__y ))

    def click(self):
        if self.__typeable == False:
            exec(self.__code_click)
        else:
            if self.__hover:
                self.__selected = True
            else:
                self.__selected = False
                self.__input = ''

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
        pygame.draw.rect(self.__static_surface_selected,(255,255,255),(0,0,self.__width, self.__height),border)
        self.__static_surface_selected.blit(text_surface,(min_width,y_padding))
        #when mouse is not hovering over text box
        self.__static_surface = pygame.Surface()
        pygame.draw.rect(self.__static_surface, (200,200,200), (0,0, self.__width, self.__height))
        self.__static_surface.blit(text_surface,(min_width,y_padding))

    def input_add(self,user_input):
        if self.__typeable == True:
            if self.__selected == True:
                self.__input += user_input
        else:raise Warning(f"called input_add() for non typeable text box: {self.__text}")

    def input_remove(self):
        if self.__typeable == True:
            if len(self.__input) > 0:
                self.__input[:-1]# Remove last character
        else:raise Warning("called input_remove() for non typeable text box")

    def input_get(self):
        return self.__input
    
    def selected_get(self):
        return self.__selected
    
    def input_get(self):
        return self.__input

    def input_reset(self):
        if self.__typeable:

            self.__input = ''#reset input
        else:raise Warning("cannot submit non typeable text box")

class option_menu:
    def __init__(self):
        self.__option = []#format: title,function
        surface = pygame.Surface((screen_width_20th,1))
        surface.fill((255,255,255))
        self.__surface = surface
        self.__open = False
        self.__pos = [None,None]

    def option_add(self,title,function):
        if not isinstance(title, str) and not isinstance(function, str): return print('can not add option: option title or function not string type')
        self.__option.append((title,function))
        self.__surface = pygame.Surface((screen_width_20th,len(self.__option) * font_size))
        self.__surface.fill((255,255,255))
        for n in range(len(self.__option)):
            self.__surface.blit(pygame.font.SysFont(font_type, font_size).render(f"{self.__option[n][0]}",True,(0,0,0)),(0,n*font_size))

    def render(self):
        if self.__pos[0] == None or self.__pos[1] == None: raise TypeError(f'cannot render when self.__pos is nontype\nself__open: {self.open_get}')
        else: screen.blit(self.__surface,(self.__pos[0],self.__pos[1]))

    def option_execute(self,index):
        exec(self.__option[index][1])

    def open_get(self):
        return self.__open
    
    def click(self):
        if self.__open == False:
            self.__open = True
            self.__pos = mouse_pos
        else:
            if self.__pos[0] <= mouse_pos[0] <= self.__pos[0] + self.__surface.get_size()[0] and self.__pos[1] <= mouse_pos[1] <= self.__pos[1] + self.__surface.get_size()[1]:
                top,bottom = self.__pos,self.__pos + font_size
                for option_number in range(len(self.__option)):
                    if top <= mouse_pos[1] <= bottom:
                        exec(self.__option[option_number][1])
                        break
                    else: 
                        top += font_size
                        bottom += font_size
            else:
                self.__open = False
                self.__pos = None

#create option menus
obj_option_menu = option_menu()
obj_option_menu.option_add('Remove component',"""
db.object_remove(x,y)
""")
interconnect_option_menu = option_menu()
interconnect_option_menu.option_add('Remove',"""
db.interconnect_remove(x,y)
""")

tb3 = text_box(screen_width_20th,screen_height_20th,"New project name",'',True)
tb4 = text_box(screen_width_20th,screen_height_20th + (font_size * 3//2),"Exit",'',False)

AND_surface = pygame.Surface((grid_size,grid_size))
AND_surface.fill(white)
AND_surface.blit(pygame.font.SysFont(font_type, grid_size//2).render("AND",True,(0,0,0)),(0,grid_size//4))
OR_surface = pygame.Surface((grid_size,grid_size))
OR_surface.fill(white)
OR_surface.blit(pygame.font.SysFont(font_type, grid_size//2).render("OR",True,(0,0,0)),(0,grid_size//4))
NAND_surface = pygame.Surface((grid_size,grid_size))
NAND_surface.fill(white)
NAND_surface.blit(pygame.font.SysFont(font_type, grid_size//2).render("NAND",True,(0,0,0)),(0,grid_size//4))
NOR_surface = pygame.Surface((grid_size,grid_size))
NOR_surface.fill(white)
NOR_surface.blit(pygame.font.SysFont(font_type, grid_size//2).render("NOR",True,(0,0,0)),(0,grid_size//4))
XOR_surface = pygame.Surface((grid_size,grid_size))
XOR_surface.fill(white)
XOR_surface.blit(pygame.font.SysFont(font_type, grid_size//2).render("XOR",True,(0,0,0)),(0,grid_size//4))
XNOR_surface = pygame.Surface((grid_size,grid_size))
XNOR_surface.fill(white)
XNOR_surface.blit(pygame.font.SysFont(font_type, grid_size//2).render("XNOR",True,(0,0,0)),(0,grid_size//4))
NOT_surface = pygame.Surface((grid_size,grid_size))
NOT_surface.fill(white)
NOT_surface.blit(pygame.font.SysFont(font_type, grid_size//2).render("NOT",True,(0,0,0)),(0,grid_size//4))
interconnect_surface = pygame.Surface((grid_size,grid_size))
interconnect_surface.fill(white)
pygame.draw.line(interconnect_surface,(0,0,0),(0,grid_size//2),(grid_size,grid_size//2))
pygame.draw.line(interconnect_surface,(0,0,0),(grid_size//2,0),(grid_size//2,grid_size))