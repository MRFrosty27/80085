from start import screen,screen_width,screen_height,screen
import pygame,array
from db import object_load,object_search_connected, object_add
from collections import deque
#gate number- none:0 and:1 , or:2, nand:3, nor:4, xor:5, xnor:6, not:7
#Pygame coordinate note: +x = right, +y = down

process_pool = None#defined in main.py
obj_cache = deque([])
inteconnect_cache = deque([])
camera_pos = [0, 0]
x_offset = None
y_offset = None
cam_speed = 5
grid_size=screen_height//50
min_x = camera_pos[0] // grid_size
max_x = (camera_pos[0] + screen_width) // grid_size + 1
min_y = camera_pos[1] // grid_size
max_y = (camera_pos[1] + screen_height) // grid_size + 1
display_slots = False

def draw_cell(x, y, gate_type):
    global camera_pos
    local_x = x * grid_size - camera_pos[0]
    local_y = y * grid_size - camera_pos[1]
    if 0 <= local_x < screen.get_width() and 0 <= local_y < screen.get_height():#only render cell if in view
        if display_slots :
            cell = pygame.Surface((grid_size,grid_size))
            cell.fill((255,255,255))
            font = pygame.font.SysFont('Arial', cell.get_width()//2)
            cell.blit((font.render(('None','AND','OR','NAND','NOR','XOR','XNOR','NOT')[gate_type], True, (0,0,0))),(cell.get_width()//4,cell.get_height()//4))
            pygame.draw.circle(cell,(50,50,50),(cell.get_width()//4,cell.get_height()//4),grid_size//8)
            pygame.draw.circle(cell,(50,50,50),(cell.get_width()//4,cell.get_height()//4*3),grid_size//8)
            pygame.draw.circle(cell,(50,50,50),(cell.get_width()//4*3,cell.get_height()//4),grid_size//8)
            pygame.draw.circle(cell,(50,50,50),(cell.get_width()//4*3,cell.get_height()//4*3),grid_size//8)
            screen.blit(cell,(local_x, local_y))
            screen.blit(cell, (local_x, local_y))
        else:
            cell = pygame.Surface((grid_size,grid_size))
            cell.fill((255,255,255))
            font = pygame.font.SysFont('Arial', grid_size//2)
            cell.blit((font.render(('None','AND','OR','NAND','NOR','XOR','XNOR','NOT')[gate_type], True, (0,0,0))),(grid_size//4,grid_size//4))
            screen.blit(cell,(local_x, local_y))
            screen.blit(cell, (local_x, local_y))

def slot_coord(x,y,slot_code):#only used in calc the path of an interconnect
    #x and y use grid pos
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
    # data type- int
    def __init__(self):
        self.__array = array.array('L',[])#signed long long
    
    def render_column(self, x):
        """
        # Use starmap to maintain order
        global process_pool
        if process_pool is None:
            raise RuntimeError("multiprocessing Pool not initialized! Create it in main.py under if __name__ == '__main__':")
        results = process_pool.starmap(object_load, [(x, y,True) for y in range(min_y, max_y)])
        self.__array.extend(results)"""
        for y in range(min_y, max_y):
            self.__array.append(object_load(x,y))

    def __setitem__(self,y,gate_type):
        self.__array[y] = gate_type

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
    
    def __len__(self):
        return len(self.__array)
    
class interconnect_y_cloumn:
    def __init__(self):
        #format outx,outy,outslot
        #access path interconnect_cache -> interconnect_column -> slot -> index
        #assignment path interconnect_cache -> interconnect_column -> index, slot
        """
        self.__slot0 = array.array('L',[])
        self.__slot1 = array.array('L',[])
        self.__slot2 = array.array('L',[])
        self.__slot3 = array.array('L',[])
        """
        #temp use
        self.__slot0 = []
        self.__slot1 = []
        self.__slot2 = []
        self.__slot3 = []
    
    def __append__(self,inslot,outx,outy,outslot):#slot: 0-top left, 1-top right, 2-bottom left, 3-bottom right
        if inslot == None:
            self.__slot0.append(None)
            self.__slot1.append(None)
            self.__slot2.append(None)
            self.__slot3.append(None)
        else:
            if isinstance(inslot,int) == False: raise Warning('inslot is not int type')
            elif isinstance(outx,int) == False: raise Warning('outx is not int type')
            elif isinstance(outy,int) == False: raise Warning('outy is not int type')
            elif isinstance(outslot,int) == False: raise Warning('outslot is not int type')
            elif inslot == 0:
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
    
    def load_path(self,x,y):
        if object_search_connected(x,y) is not None:
                inx,iny,outx,outy,inslot,outslot = object_search_connected(x,y)
                self.__append__(inslot,outx,outy,outslot)
        else: self.__append__(None,None,None,None)

    def remove_path(self,x,y):
        pass

    def load_paths_in_column(self,x):
        """
        # Use starmap to maintain order
        global process_pool
        if process_pool is None:
            raise RuntimeError("multiprocessing Pool not initialized! Create it in main.py under if __name__ == '__main__':")
        process_pool.starmap(self.load_path, [(x, y,True) for y in range(min_y, max_y)])"""
        for y in range(min_y, max_y):
            self.load_path(x,y)
    
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

    def __getitem__(self,slot):
        if 0 <= slot <= 3:
            if slot == 0:
                return self.__slot0
            elif slot == 1:
                return self.__slot1
            elif slot == 2:
                return self.__slot2
            elif slot == 3:
                return self.__slot3
        else: raise TypeError('slot arg is not supported')

    def __setitem__(self, key, value):
    
        if isinstance(key, tuple):
            index, slot = key
            if slot == 0:
                self.__slot0[index] = value
            elif slot == 1:
                self.__slot1[index] = value
            elif slot == 2:
                self.__slot2[index] = value
            elif slot == 3:
                self.__slot3[index] = value
            else:
                raise IndexError(f"Slot must be 0-3, got {slot}")
        else:
            # Set all slots
            self.__slot0[key] = value
            self.__slot1[key] = value
            self.__slot2[key] = value
            self.__slot3[key] = value
    
    def __len__(self):
        return len(self.__slot0),len(self.__slot1),len(self.__slot2),len(self.__slot3)
    
def render():
    global camera_pos, min_x, max_x, min_y, max_y, x_offset, y_offset
    
    for x in range(-x_offset, screen_width + grid_size, grid_size):
        pygame.draw.line(screen, (255,255,255), (x, 0), (x, screen_height))
    for y in range(-y_offset, screen_height + grid_size, grid_size):
        pygame.draw.line(screen, (255,255,255), (0, y), (screen_width, y))

    #dx and dy represent the shift of cells in view
    dx = camera_pos[0] // grid_size - min_x
    dy = camera_pos[1] // grid_size - min_y
    
    min_x = camera_pos[0] // grid_size
    max_x = (camera_pos[0] + screen_width) // grid_size
    min_y = camera_pos[1] // grid_size
    max_y = (camera_pos[1] + screen_height) // grid_size 

    if dx > 0:#right
        for n in range(dx):
            obj_cache.popleft()
            inteconnect_cache.popleft()
            obj_col = obj_y_cloumn()
            obj_col.render_column(max_x+n)
            obj_cache.append(obj_col)
            interconnect_col = interconnect_y_cloumn()
            interconnect_col.load_paths_in_column(max_x+n)
            inteconnect_cache.append(interconnect_col)

    elif dx < 0:
        dx *= -1#change to positive value
        for n in range(dx):
            obj_cache.pop()
            inteconnect_cache.pop()
            obj_col = obj_y_cloumn()
            obj_col.render_column(min_x-n)
            obj_cache.appendleft(obj_col)
            interconnect = interconnect_y_cloumn()
            interconnect.load_paths_in_column(min_x-n)
            inteconnect_cache.appendleft(interconnect)
    if dy > 0:#down
        for n in range(dy):
            x = min_x
            for col in obj_cache:
                col.render_down(x,max_y+n)
                x += 1
    elif dy < 0:
        dy *= -1#change to positive value
        x = min_x
        for n in range(dy):
            for col in obj_cache:
                col.render_up(x,min_y-n)
                x += 1
    
    for x in range(len(obj_cache)):
            for y in range(len(obj_cache[x])):
                if obj_cache[x][y] == 0:pass
                else:
                    draw_cell(min_x+x,min_y+y, obj_cache[x][y])
    
    for interconnect_column in inteconnect_cache:
            x_index = 0
            y_index = 0
            for interconnect in interconnect_column[0]:#access slot 0 in each col
                if interconnect != None:
                    pygame.draw.line(screen,(255,255,255),slot_coord(min_x+x_index,min_y+y_index,0),slot_coord(interconnect[0],interconnect[1],interconnect[3]))
                y_index += 1
            for interconnect in interconnect_column[1]:#access slot 1 in each col
                if interconnect != None:
                    pygame.draw.line(screen,(255,255,255),slot_coord(min_x+x_index,min_y+y_index,1),slot_coord(interconnect[0],interconnect[1],interconnect[3]))
                y_index += 1
            for interconnect in interconnect_column[2]:#access slot 2 in each col
                if interconnect != None:
                    pygame.draw.line(screen,(255,255,255),slot_coord(min_x+x_index,min_y+y_index,2),slot_coord(interconnect[0],interconnect[1],interconnect[3]))
                y_index += 1
            for interconnect in interconnect_column[3]:#access slot 3 in each col
                if interconnect != None:
                    pygame.draw.line(screen,(255,255,255),slot_coord(min_x+x_index,min_y+y_index,3),slot_coord(interconnect[0],interconnect[1],interconnect[3]))
                y_index += 1
            x_index += 1

def setup_render():
    for column_number in range(screen_width//grid_size):
        new_obj_column = obj_y_cloumn()
        new_obj_column.render_column(min_x+column_number)
        new_interconnect_column = interconnect_y_cloumn()
        new_interconnect_column.load_paths_in_column(min_x+column_number)
        obj_cache.append(new_obj_column)
        inteconnect_cache.append(new_interconnect_column)