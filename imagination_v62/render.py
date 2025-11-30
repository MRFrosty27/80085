from start import screen,screen_width,screen_height,screen
import pygame
from db import object_load,object_search_connected
#gate number- and:0 , or:1, nand:2, nor:3, xor:4, xnor:5, not:6
#Pygame coordinate note: +x = right, +y = down

obj_cache = []
inteconnect_cache = []
camera_pos = [0, 0]
cam_speed = 5
grid_size=screen_height//20
min_x = camera_pos[0] // grid_size
max_x = (camera_pos[0] + screen_width) // grid_size + 1
min_y = camera_pos[1] // grid_size
max_y = (camera_pos[1] + screen_height) // grid_size + 1

def draw_cell(x, y, gate_type, camera_pos):
    world_x = x * grid_size - camera_pos[0]
    world_y = y * grid_size - camera_pos[1]
    if 0 <= world_x < screen.get_width() and 0 <= world_y < screen.get_height():#only render cell if in view
        cell = pygame.Surface((grid_size,grid_size))
        cell.fill((255,255,255))
        font = pygame.font.SysFont('Arial', grid_size//2)
        cell.blit((font.render(('AND','OR','NAND','NOR','XOR','XNOR','NOT')[gate_type], True, (0,0,0))),(grid_size//4,grid_size//4))
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
    
    def __iter__(self):
        return self.__array
    
class interconnect_y_cloumn:
    def __init__(self):#format outx,outy,outslot
        self.__slot0 = []
        self.__slot1 = []
        self.__slot2 = []
        self.__slot3 = []
    
    def __len__(self):
        return len(self.__array)
    
    def load_row(self,inslot,outx,outy,outslot):#slot: 0-top left, 1-top right, 2-bottom left, 3-bottom right
        if inslot == 0:
            self.__slot0.append(outx,outy,outslot)
            self.__slot1.append(None)
            self.__slot2.append(None)
            self.__slot3.append(None)
        elif inslot == 1:
            self.__slot1.append(outx,outy,outslot)
            self.__slot0.append(None)
            self.__slot2.append(None)
            self.__slot3.append(None)
        elif inslot == 2:
            self.__slot2.append(outx,outy,outslot)
            self.__slot0.append(None)
            self.__slot1.append(None)
            self.__slot3.append(None)
        elif inslot == 3:
            self.__slot3.append(outx,outy,outslot)
            self.__slot0.append(None)
            self.__slot1.append(None)
            self.__slot2.append(None)
    
    def load_col(self,x,min_y,max_y):
        for y in range(min_y,max_y):
            if object_search_connected(x,y) is not None:
                inx,iny,outx,outy,inslot,outslot = object_search_connected(x,y)
                self.load_row(inslot,outx,outy,outslot)
                
    
    def render_up(self,x,y):
        if isinstance(x,int) == True and isinstance(y,int) == True:
            self.__slot0.pop(-1)
            self.__slot1.pop(-1)
            self.__slot2.pop(-1)
            self.__slot3.pop(-1)
            if object_search_connected(x,y) is not None:
                inx,iny,outx,outy,inslot,outslot = object_search_connected(x,y)
                if inslot == 0:
                    self.__slot0.insert(0,outx,outy,outslot)
                    self.__slot1.insert(0,None)
                    self.__slot2.insert(0,None)
                    self.__slot3.insert(0,None)
                elif inslot == 1:
                    self.__slot1.insert(outx,outy,outslot)
                    self.__slot0.insert(0,None)
                    self.__slot2.insert(0,None)
                    self.__slot3.insert(0,None)
                elif inslot == 2:
                    self.__slot2.insert(0,outx,outy,outslot)
                    self.__slot0.insert(0,None)
                    self.__slot1.insert(0,None)
                    self.__slot3.insert(0,None)
                elif inslot == 3:
                    self.__slot3.insert(0,outx,outy,outslot)
                    self.__slot0.insert(0,None)
                    self.__slot1.insert(0,None)
                    self.__slot2.insert(0,None)
            else:
                self.__slot0.insert(0,None)
                self.__slot1.insert(0,None)
                self.__slot2.insert(0,None)
                self.__slot3.insert(0,None)
        else: raise TypeError("arg x or y type not int")

    def render_down(self,x,y):
        if isinstance(x,int) == True and isinstance(y,int) == True:
            self.__slot0.pop(0)
            self.__slot1.pop(0)
            self.__slot2.pop(0)
            self.__slot3.pop(0)
            if object_search_connected(x,y) is not None:
                inx,iny,outx,outy,inslot,outslot = object_search_connected(x,y)
                self.load_row(inslot,outx,outy,outslot)
            else:
                self.__slot0.append(None)
                self.__slot1.append(None)
                self.__slot2.append(None)
                self.__slot3.append(None)
        else: raise TypeError("arg x or y type not int")

    def __getitem__(self, index):
        if index == 0:
            return self.__slot0
        elif index == 1:
            return self.__slot1
        elif index == 2:
            return self.__slot2
        elif index == 3:
            return self.__slot3
    
def render(new_x, new_y):
    global camera_pos, min_x, max_x, min_y, max_y
    x_offset = camera_pos[0] % grid_size
    y_offset = camera_pos[1] % grid_size
    for x in range(-x_offset, screen_width + grid_size, grid_size):
        pygame.draw.line(screen, (255,255,255), (x, 0), (x, screen_height))
    for y in range(-y_offset, screen_height + grid_size, grid_size):
        pygame.draw.line(screen, (255,255,255), (0, y), (screen_width, y))

    #here dx and dy represent the change is grid pos
    dx = (new_x - camera_pos[0]) // grid_size
    dy = (new_y - camera_pos[1]) // grid_size

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
                    draw_cell(min_x+x,min_y+y, obj_cache[x][y], screen, camera_pos)
    
    for x in inteconnect_cache:
            x_index = 0
            y_index = 0
            for y in x[0]:#access slot 1 in each col
                if inteconnect_cache[x][y] != None:
                    from_point = slot_coord(min_x+x_index,min_y+y_index,0)
                    to_point = slot_coord(inteconnect_cache[x][0][x_index],inteconnect_cache[x][y_index],0)
                    pygame.draw.line(screen,(255,255,255),from_point,to_point)
                y_index += 1
            for y in x[1]:#access slot 2 in each col
                if inteconnect_cache[x][y] != None:
                    from_point = slot_coord(min_x+x_index,min_y+y_index,1)
                    to_point = slot_coord(inteconnect_cache[x][0][x_index],inteconnect_cache[x][y_index],1)
                    pygame.draw.line(screen,(255,255,255),from_point,to_point)
                y_index += 1
            for y in x[2]:#access slot 3 in each col
                if inteconnect_cache[x][y] != None:
                    from_point = slot_coord(min_x+x_index,min_y+y_index,2)
                    to_point = slot_coord(inteconnect_cache[x][0][x_index],inteconnect_cache[x][y_index],2)
                    pygame.draw.line(screen,(255,255,255),from_point,to_point)
                y_index += 1
            for y in x[3]:#access slot 4 in each col
                if inteconnect_cache[x][y] != None:
                    from_point = slot_coord(min_x+x_index,min_y+y_index,3)
                    to_point = slot_coord(inteconnect_cache[x][0][x_index],inteconnect_cache[x][y_index],3)
                    pygame.draw.line(screen,(255,255,255),from_point,to_point)
                y_index += 1
            x_index += 1

            camera_pos = [new_x,new_y]