from GUI import text
from start import screen_width,screen_height,screen
import pygame
from db import object_load,object_search_connected
#gate number- and:0 , or:1, nand:2, nor:3, xor:4, xnor:5, not:6
#Pygame coordinate note: +x = right, +y = down

obj_cache = []
inteconnect_cache = []
message_queue = []
camera_pos = [0, 0]
cam_speed = 5
grid_size=screen_height//20
min_x = camera_pos[0] // grid_size
max_x = (camera_pos[0] + screen_width) // grid_size + 1
min_y = camera_pos[1] // grid_size
max_y = (camera_pos[1] + screen_height) // grid_size + 1

def draw_cell(x, y, gate_type, screen, camera_pos):
    world_x = x * grid_size - camera_pos[0]
    world_y = y * grid_size - camera_pos[1]
    if 0 <= world_x < screen.get_width() and 0 <= world_y < screen.get_height():#only render cell if in view
        cell = pygame.Surface((grid_size,grid_size))
        cell.fill((255,255,255))
        font = pygame.font.SysFont('Arial', grid_size//2)
        cell.blit((font.render(['AND','OR','NAND','NOR','XOR','XNOR','NOT'][gate_type], True, (0,0,0))),(grid_size//4,grid_size//4))
        screen.blit(cell,(world_x, world_y))
        screen.blit(cell, (world_x, world_y))

def slot_coord(x,y,slot_code):#only used in calc the path of an interconnect
    if slot_code == 0:
        slot_x = x * grid_size - camera_pos[0] + (grid_size/4)
        slot_y = y * grid_size - camera_pos[0] + (grid_size/4)
        return slot_x,slot_y
    elif slot_code == 1:
        slot_x = x * grid_size - camera_pos[0] + (grid_size/4*3)
        slot_y = y * grid_size - camera_pos[0] + (grid_size/4)
        return slot_x,slot_y
    elif slot_code == 2:
        slot_x = x * grid_size - camera_pos[0] + (grid_size/4)
        slot_y = y * grid_size - camera_pos[0] + (grid_size/4*3)
        return slot_x,slot_y
    elif slot_code == 3:
        slot_x = x * grid_size - camera_pos[0] + (grid_size/4*3)
        slot_y = y * grid_size - camera_pos[0] + (grid_size/4*3)
        return slot_x,slot_y
    
def message(text,duration):#duration is in seconds
    for message_text,message_duration in message_queue:
        if text == message_text:
            return None
    message_queue.append([text,duration*settings["fps"]])

class obj_y_cloumn:
    def __init__(self):
        self.__array = []
    
    def __len__(self):
        return len(self.__array)
    
    def render(self,x,min_y,max_y):
        for y in range(min_y,max_y):
            self.__array.append(object_load(x,y))
    
    def render_up(self,x,y):
        if isinstance(x,int) == True and isinstance(y,int) == True:
            self.__array.pop(-1)
            self.__array.insert(0,object_load(x,y))
        else: raise TypeError("arg x or y type not int")

    def render_down(self,x,y):
        if isinstance(x,int) == True and isinstance(y,int) == True:
            self.__array.pop(0)
            self.__array.append(object_load(x,y))
        else: raise TypeError("arg x or y type not int")

    def __getitem__(self, index):
        return self.__array[index]
    
class interconnect_y_cloumn:
    def __init__(self):
        self.__array = []
    
    def __len__(self):
        return len(self.__array)
    
    def render(self,x,min_y,max_y):
        for y in range(min_y,max_y):
            if object_search_connected(x,y) is not None:
                inx,iny,outx,outy,inslot,outslot = object_search_connected(x,y)
                self.__array.append(inslot,outx,outy,outslot)
            else: self.__array.append(None)
    
    def render_up(self,x,y):
        if isinstance(x,int) == True and isinstance(y,int) == True:
            self.__array.pop(-1)
            if object_search_connected(x,y) is not None:
                inx,iny,outx,outy,inslot,outslot = object_search_connected(x,y)
                self.__array.insert(0,(inslot,outx,outy,outslot))
            else: self.__array.insert(0,None)
        else: raise TypeError("arg x or y type not int")

    def render_down(self,x,y):
        if isinstance(x,int) == True and isinstance(y,int) == True:
            self.__array.pop(0)
            if object_search_connected(x,y) is not None:
                inx,iny,outx,outy,inslot,outslot = object_search_connected(x,y)
                self.__array.append(inslot,outx,outy,outslot)
            else: self.__array.append(None)
        else: raise TypeError("arg x or y type not int")

    def __getitem__(self, index):
        return self.__array[index]
    
def render(dx,dy):
    x_offset = camera_pos[0] % grid_size
    y_offset = camera_pos[1] % grid_size
    for x in range(-x_offset, screen_width + grid_size, grid_size):
        pygame.draw.line(screen, (255,255,255), (x, 0), (x, screen_height))
    for y in range(-y_offset, screen_height + grid_size, grid_size):
        pygame.draw.line(screen, (255,255,255), (0, y), (screen_width, y))

    x_range = max_x - min_x
    y_range = max_y - min_y

    if dx > 0:#right
        for n in range(dx):
            obj_cache.pop(0)
            inteconnect_cache.pop(0)
            obj = obj_y_cloumn()
            obj.render(max_x+n)
            obj_cache.append(obj)
            interconnect = interconnect_y_cloumn()
            interconnect.render(max_x+n)
            inteconnect_cache.append(interconnect)

    else:
        dx *= -1#change to positive value
        for n in range(dx):
            obj_cache.pop(-1)
            inteconnect_cache.pop(-1)
            obj = obj_y_cloumn()
            obj.render(min_x-n)
            obj_cache.insert(0,obj)
            interconnect = interconnect_y_cloumn()
            interconnect.render(min_x-n)
            inteconnect_cache.insert(0,interconnect)
    if dy > 0:#down
        for n in range(dy):
            x = min_x
            for col in obj_cache:
                col.render_down(x,max_y+n)
                x += 1
    else:
        dy *= -1#change to positive value
        for n in range(dy):
            x = min_x
            for col in obj_cache:
                col.render_up(x,min_y-n)
                x += 1
    
    for x in range(len(obj_cache)):
            for y in range(len(obj_cache[x])):
                if obj_cache[x][y] == None:pass
                else:
                    draw_cell(min_x+x,min_y+y, obj_cache[x][y], screen, camera_pos, text)
    
    for x in range(len(inteconnect_cache)):
            for y in range(len(inteconnect_cache[x])):
                if inteconnect_cache[x][y] == None:pass
                else:
                    pygame.draw.line(screen,(255,255,255),slot_coord(min_x+x,min_y+y,inteconnect_cache[x][y][0]),slot_coord(inteconnect_cache[x][y][1],inteconnect_cache[x][y][2],inteconnect_cache[x][y][3]))