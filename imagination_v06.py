import pygame
import sys
import os
import json
import GUI
import SQLite3_database as db
from datetime import datetime

#create folder where database files are stored
os.makedirs(os.path.join(os.path.dirname(__file__),"projects"),exist_ok=True ) 

# Load settings from JSON (cross-platform)
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
DEFAULT_SETTINGS = {
    "screen_width": 1920,
    "screen_height": 1080,
    "fullscreen": True,
    "fps": 60
}

try:
    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)
except FileNotFoundError:
    with open(SETTINGS_FILE, "w") as f:
        json.dump(DEFAULT_SETTINGS, f, indent=4)
    settings = DEFAULT_SETTINGS

# Set up display
pygame.init()
flags = pygame.FULLSCREEN if settings["fullscreen"] else 0
GUI.display = screen = pygame.display.set_mode((settings["screen_width"], settings["screen_height"]), flags)
clock = pygame.time.Clock()

# Initialize game state
GUI.screen_width = screen_width = settings["screen_width"]
GUI.screen_height = screen_height = settings["screen_height"]
GUI.box_dim = int(GUI.screen_width * 0.1),int(GUI.screen_height * 0.1)
grid_size=100
cam_speed=5
pygame.key.set_repeat(100, 100)  # 500ms delay before repeating, 50ms interval between repeats
animation_clock = 0#used for animation that change over time

#load screen
def loading_screen(perc,text):
    if type(perc) != int:
        raise TypeError("perc is not int type")
    elif 0 > perc > 100:
        raise ValueError("perc is not between 0 and 100")
    if type(text) != str:
        raise TypeError("perc is not str type")
    screen.fill((255,255,255))
    screen.blit((pygame.font.SysFont("Arial", 100)).render(f"{text}",True,(0,0,0)),(0,0))
    pygame.draw.rect(screen,(0,255,255),(screen_width*0.1,screen_height*0.6,int(screen_width*0.008*perc),screen_height*0.1))
    pygame.draw.rect(screen,(255,215,0),(screen_width*0.1,screen_height*0.6,screen_width*0.8,screen_height*0.1),10)
    pygame.display.flip()

# Pygame coordinate note: +x = right, +y = down
def save(width,height,fullscreen):
    if width is None:
        pass#no changes made
    elif isinstance(width,int) == False:
        raise TypeError("width is not int type")
    else:
        GUI.screen_width = screen_width = settings["screen_width"] = width
    
    if height is None:
        pass#no changes made
    elif isinstance(height,int) == False:
        raise TypeError("height is not int type")
    else:
        GUI.screen_height = screen_height = settings["screen_height"] = height

    if fullscreen is None:
        pass#no changes made
    elif isinstance(fullscreen,int) == False:
        raise TypeError("fullscreen is not bool")
    else:
        GUI.screen_height = screen_height = settings["screen_height"] = height

    try:
        GUI.display = screen = pygame.display.set_mode((settings["screen_width"], settings["screen_height"]), flags)
    except:
        pass
    # Save settings
    with open(SETTINGS_FILE, "w") as f:
        json.dump({
            "screen_width": settings["screen_width"],
            "screen_height": settings["screen_height"],
            "fullscreen": settings["fullscreen"],
            "fps": settings["fps"]
        }, f, indent=4)

def draw_cell(x, y, gate_type, screen, camera_pos, font):
    world_x = x * grid_size - camera_pos[0]
    world_y = y * grid_size - camera_pos[1]
    if 0 <= world_x < screen.get_width() and 0 <= world_y < screen.get_height():#only render cell if in view
        cell = pygame.Surface((grid_size,grid_size))
        cell.fill((255,255,255))
        cell.blit((gate_img[gate_type]),(0,0))
        screen.blit(cell,(world_x, world_y))
        text = font.render(f"{x}:{y}", True, (0,0,0))
        screen.blit(text, (world_x, world_y))

def draw_sp(x, y, colour, screen, camera_pos, grid_size, font):
    world_x = x * grid_size - camera_pos[0]
    world_y = y * grid_size - camera_pos[1]
    if (0 <= world_x < screen.get_width() and 0 <= world_y < screen.get_height()):
        rect = pygame.Rect(world_x, world_y, grid_size, grid_size)
        pygame.draw.rect(screen, colour, rect)
        text = font.render(f"{x}:{y}", True, (255 - colour[0], 255 - colour[1], 255 - colour[2]))
        screen.blit(text, (world_x, world_y))
        screen.blit(font.render(f"{db.search_SP(x,y)[2]}", True, (255 - colour[0], 255 - colour[1], 255 - colour[2])),(world_x+(grid_size/2)-10, world_y+(grid_size/2)-10))

def within_gate_option_menu_bool(mouse_pos, gate_option_menu_pos):
    if (mouse_pos[0] < gate_option_menu_pos[0] or 
        mouse_pos[0] > gate_option_menu_pos[0] + 150 or 
        mouse_pos[1] < gate_option_menu_pos[1] or 
        mouse_pos[1] > gate_option_menu_pos[1] + 150):
        return False
    return True

def message(text, font,font_size, screen):
    len(text)
    font = pygame.font.SysFont(f"{font}", font_size)
    screen.blit((font.render(f"{text}", True, (255, 255, 255))),(screen_width - (len(text)*font_size), screen_height * 0.7))

def slot_coord(x,y,slot_code):#only used to render interconnect path
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

loading_screen(0,"Starting")
#load gate img
#scale(load(dir_path))
#gate number- and:0 , or:1, nand:2, nor:3, xor:4, xnor:5, not:6
gate_img = (
    pygame.transform.scale(pygame.image.load(f"{os.path.join(os.path.dirname(__file__), "AND_gate.svg.png")}"),(grid_size, grid_size)),
    pygame.transform.scale(pygame.image.load(f"{os.path.join(os.path.dirname(__file__), "OR_gate.svg.png")}" ),(grid_size, grid_size)),
    pygame.transform.scale(pygame.image.load(f"{os.path.join(os.path.dirname(__file__), "NAND_gate.svg.png")}" ),(grid_size, grid_size)),
    pygame.transform.scale(pygame.image.load(f"{os.path.join(os.path.dirname(__file__), "NOR_gate.svg.png")}" ),(grid_size, grid_size)),
    pygame.transform.scale(pygame.image.load(f"{os.path.join(os.path.dirname(__file__), "XOR_gate.svg.png")}" ),(grid_size, grid_size)),
    pygame.transform.scale(pygame.image.load(f"{os.path.join(os.path.dirname(__file__), "XNOR_gate.svg.png")}" ),(grid_size, grid_size)),
    pygame.transform.scale(pygame.image.load(f"{os.path.join(os.path.dirname(__file__), "NOT_gate.svg.png")}" ),(grid_size, grid_size))
)
#draw circles on gates
pygame.draw.circle(gate_img[0],(0,0,0),(grid_size/4,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[0],(0,0,0),(grid_size/4*3,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[0],(0,0,0),(grid_size/4,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[0],(0,0,0),(grid_size/4*3,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[1],(0,0,0),(grid_size/4,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[1],(0,0,0),(grid_size/4*3,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[1],(0,0,0),(grid_size/4,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[1],(0,0,0),(grid_size/4*3,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[2],(0,0,0),(grid_size/4,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[2],(0,0,0),(grid_size/4*3,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[2],(0,0,0),(grid_size/4,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[2],(0,0,0),(grid_size/4*3,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[3],(0,0,0),(grid_size/4,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[3],(0,0,0),(grid_size/4*3,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[3],(0,0,0),(grid_size/4,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[3],(0,0,0),(grid_size/4*3,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[4],(0,0,0),(grid_size/4,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[4],(0,0,0),(grid_size/4*3,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[4],(0,0,0),(grid_size/4,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[4],(0,0,0),(grid_size/4*3,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[5],(0,0,0),(grid_size/4,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[5],(0,0,0),(grid_size/4*3,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[5],(0,0,0),(grid_size/4,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[5],(0,0,0),(grid_size/4*3,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[6],(0,0,0),(grid_size/4,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[6],(0,0,0),(grid_size/4*3,grid_size/4),grid_size/10)
pygame.draw.circle(gate_img[6],(0,0,0),(grid_size/4,grid_size/4*3),grid_size/10)
pygame.draw.circle(gate_img[6],(0,0,0),(grid_size/4*3,grid_size/4*3),grid_size/10)

loading_screen(20,"Loaded logic gate images")

#setting menu state data
settings_menu_open = False
settings_new_project = ""
settings_active_field = False
tb2_selected = False
tb3_selected = False

loading_screen(30,"Loaded setting menu state data")

#gate menu state
selected_gate = None
selected_interconnect = False
first_click = False
second_click = False
selected_sp = False

loading_screen(40,"Loaded gate menu state variables")

# Gate Option Menu
gate_option_menu_bool = False
open_gate_option_menu_bool =True#signals whether the menu has been opened 
gate_option_menu_pos = (0, 0)
selected_grid = None
in_cell = None

loading_screen(50,"Loaded gate option menu variables")

# Project and Database Setup
db.create_table_of_database_names()#if one does not exist
project_name=""
selected_table = ""

loading_screen(60,"Setup Project and Database")

# Colors
GREEN = (125, 255, 125)  # AND gate
BLUE = (125, 125, 255)   # OR gate
RED = (255, 0, 0)        # NAND gate
PURPLE = (255, 0, 255)   # NOR gate
ORANGE = (255, 155, 0)   # interconnects
WHITE = (255, 255, 255)
navy = (0,50,255)
gold = (255,215,0)
"cyan"

loading_screen(70,"loaded colours")

# Grid and Camera Settings
GRID_SIZE = 100
camera_pos = [0, 0]
CAM_SPEED = 5

loading_screen(80,"loaded Grid and Camera Settings")

# Render UI
font_size = int(screen_height * 0.02)
font = pygame.font.SysFont("Arial", font_size)
UI_bar = pygame.Surface((screen_width,screen_height*0.3))
UI_bar.fill(WHITE)
pygame.draw.line(UI_bar, gold, (0, 0), (screen_width, 0))
interconnect_img = pygame.Surface((grid_size,grid_size))
interconnect_img.fill(WHITE)
pygame.draw.line(interconnect_img,(0,0,0),(grid_size//4,grid_size//2),(grid_size//4*3,grid_size//2),grid_size//10)
pygame.draw.circle(interconnect_img,(0,0,0),(grid_size//4,grid_size//2),grid_size//10)
pygame.draw.circle(interconnect_img,(0,0,0),(grid_size//4*3,grid_size//2),grid_size//10)
SP_img = pygame.Surface((grid_size,grid_size))
SP_img.fill(WHITE)
pygame.draw.circle(SP_img,(0,0,0),(grid_size//4,grid_size//4),grid_size//10)
pygame.draw.circle(SP_img,(0,0,0),(grid_size//4*3,grid_size//4),grid_size//10)
pygame.draw.circle(SP_img,(0,0,0),(grid_size//4,grid_size//4*3),grid_size//10)
pygame.draw.circle(SP_img,(0,0,0),(grid_size//4*3,grid_size//4*3),grid_size//10)
pygame.draw.circle(SP_img,(0,0,0),(grid_size//2,grid_size//2),grid_size//5)
gate_positions = [
    (screen_width * 0.1,gate_img[0]), (screen_width * 0.2,gate_img[1]),
    (screen_width * 0.3,gate_img[2]), (screen_width * 0.4,gate_img[3]),
    (screen_width * 0.5,gate_img[4]), (screen_width * 0.6,gate_img[5]),
    (screen_width * 0.7,gate_img[6]),(screen_width * 0.8,interconnect_img),
    (screen_width * 0.9,SP_img)
]
for x,img in gate_positions:
    UI_bar.blit(img,(x,screen_height * 0.1))
padding = 10#px
bouder = 10#px
del_button_width = 100

loading_screen(90,"loaded UI")

main = False
settings_menu_open = True
while True:
    while settings_menu_open == True:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save(None,None,None)
                # Close database and quit
                db.close_database()
                sys.exit()
        
        keys = pygame.key.get_pressed()
        GUI.mpos = mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
        #close setting menu
        if keys[pygame.K_ESCAPE]:
            main = True
            settings_menu_open = False
            break

        if settings["fullscreen"] == True:
            tb1 = GUI.text_box(padding,padding,"Fullscreen: ON")
        else:
            tb1 = GUI.text_box(padding,padding,"Fullscreen: OFF")
        
        #dropdown for resolution. has to be last so that the dropdown menu is rendered above other buttons
        if tb2_selected == True:
            tb2 = GUI.text_box(padding,int(screen_height * 0.1) + 20,f"Resolution: {screen_width}x{screen_height}")
            resolutions = (3620,2036),(2560,1440),(1920,1080),(1280,720),(800,600)
            pygame.draw.rect(screen,WHITE,(tb2.x,tb2.y + (screen_height * 0.1),tb2.width,len(resolutions) * font_size ))
            n = 0
            while n < len(resolutions):
                dim = tb2.x,tb2.y + (screen_height * 0.1) + (font_size * n),tb2.x + tb2.width,tb2.y + (screen_height * 0.1) + (font_size * (n+1))
                if dim[0] <= mouse_pos[0] <= dim[2] and dim[1] <= mouse_pos[1] <= dim[3]:
                    if mouse_buttons[0]:
                        settings["screen_width"] = screen_width = resolutions[n][0]
                        settings["screen_height"] = screen_height = resolutions[n][1]
                        save(settings["screen_width"],settings["screen_height"],None)
                        break
                    pygame.draw.rect(screen,navy,(dim[0],dim[1],tb2.width,(font_size)))
                    pygame.draw.rect(screen,gold,(dim[0],dim[1],tb2.width,(font_size)),bouder)

                screen.blit(font.render(f"{resolutions[n][0]}x{resolutions[n][1]}", True, (0, 0, 0)), (dim[0],dim[1]))
                n+=1
            tb3 = GUI.text_box(padding,int(screen_height * 0.2) + 30 + int(screen_height * len(resolutions) * 0.02 ),f"New project name: {settings_new_project}")
            tb4 = GUI.text_box(padding,int(screen_height * 0.3) + 40 + int(screen_height * len(resolutions) * 0.02 ),"Quit")
        #if the user clicks on the text box they can type the new project name
        elif tb3_selected == True:
            tb2 = GUI.text_box(padding,int(screen_height * 0.1) + 20,f"Resolution: {screen_width}x{screen_height}")
            tb3 = GUI.text_box(padding,int(screen_height * 0.2) + 30,f"New project name: {settings_new_project}")
            tb4 = GUI.text_box(padding,int(screen_height * 0.3) + 40,"Quit")
            for event in pygame.event.get():  # Process events for text input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        settings_new_project = settings_new_project[:-1]  # Remove last character
                    elif event.key == pygame.K_RETURN and len(settings_new_project) > 0:
                        project_name = settings_new_project
                        db.db_name = db.access_database(settings_new_project)
                        db.add_database_name(settings_new_project,1*10^9,f"{datetime.now()}",f"{datetime.now()}",f"{datetime.now()}")
                        db.create_table()
                        db.create_inteconnect_table()
                        db.create_start_table()
                        db.create_volitile_memory_table()
                        settings_new_project = ""  # Clear after creating project
                        tb3_selected = False
                    elif event.unicode.isalnum() and len(settings_new_project) <= 20:  # Allow letters and numbers
                        settings_new_project += event.unicode
        else:
            tb2 = GUI.text_box(10,int(screen_height * 0.1) + 20,f"Resolution: {screen_width}x{screen_height}")
            tb3 = GUI.text_box(10,int(screen_height * 0.2) + 30,f"New project name: {settings_new_project}")
            tb4 = GUI.text_box(10,int(screen_height * 0.3) + 40,"Quit")


        #user can select existing projects
        pygame.draw.rect(screen,WHITE,(screen_width * 0.5, padding, screen_width * 0.5 - padding, screen_height - 20))
        pygame.draw.rect(screen,gold,(screen_width * 0.5, padding, screen_width * 0.5 - padding, screen_height - 20),bouder)
        screen.blit(font.render(f"{"Name|Speed(GHz)|Created|Last accessed|Last modified"}",True,(0,0,0)),(screen_width * 0.5 + bouder, bouder + padding))
        n=0
        for project in db.get_all_database_names():
            project_name_dim = (screen_width * 0.5 + bouder,font_size*(n+1) + bouder + padding,screen_width - padding - bouder, font_size*(n+2)  + bouder + padding)
            screen.blit(font.render(f"{project[0]}|{project[1]}|{project[2]}|{project[3]}|{project[4]}",True,(0,0,0)),(project_name_dim[0],project_name_dim[1]))
            if n == int((screen_height - (bouder+padding)*2)/font_size):#stops projects names from being rendered off the list
                break
            if project_name_dim[1] <= mouse_pos[1]<= project_name_dim[3] and project_name_dim[0] <= mouse_pos[0]:
                if mouse_pos[0] < project_name_dim[2]-del_button_width:
                    if mouse_buttons[0]:
                        main = True
                        settings_menu_open = False
                        db.db_name = db.access_database(project[0])
                        break
                    else:
                        screen.blit(font.render(f"{"DEL"}",True,(0,0,0)),(project_name_dim[2]-del_button_width,project_name_dim[1]))
                elif mouse_pos[0] >= project_name_dim[2]-del_button_width:
                    if mouse_buttons[0]:
                        db.del_project(project[0])
                    else:
                        screen.blit(font.render(f"{"DEL"}",True,gold),(project_name_dim[2]-del_button_width,project_name_dim[1]))
            n+=1 

        # Settings Menu Interaction
        if mouse_buttons[0]:
            # Handle fullscreen toggle
            if tb1.hover:
                settings["fullscreen"] = not settings["fullscreen"]  # Toggle fullscreen
                save(None, None, settings["fullscreen"])
            # Handle text box selection
            elif tb2.hover:
                tb2_selected = True
                tb3_selected = False  # Deselect tb3 when tb2 is selected
            elif tb3.hover:
                tb3_selected = True
                tb2_selected = False  # Deselect tb2 when tb3 is selected
            elif tb4.hover:
                save(None, None, None)
                db.close_database()
                sys.exit()
            else:
                # Deselect both text boxes if clicking outside
                tb2_selected = False
                tb3_selected = False
                settings_new_project = ""  # Clear project name when deselecting tb3
                
        pygame.display.flip()
        clock.tick(settings["fps"])
    # prerender objects in view on startup
    obj_in_view = []  # Store obj that are in view to improve performance
    SP_in_view = [] #stores starting points in view to improve performance
    action_queue = []#used to store user action for undo functionality
    min_x = camera_pos[0] // GRID_SIZE
    max_x = (camera_pos[0] + screen_width) // GRID_SIZE + 1
    min_y = camera_pos[1] // GRID_SIZE
    max_y = (camera_pos[1] + screen_height) // GRID_SIZE + 1
    for x in range(min_x, max_x):
        temp_list = []  # List that contains all obj with the same x coord
        for y in range(min_y, max_y):
            obj = db.load_object(x, y)
            if obj:
                temp_list.append(obj[2])
            if db.search_SP(x, y):
                SP_in_view.append((x,y))
            else:
                temp_list.append((None))#empty tuple is added so that later a value can be added without the delay of adding a new value especially at lower index values e.g 0
        obj_in_view.append(temp_list)
    x_column = min_x
    xx_column = min_x#used to render interconnect path
    array_interconnect = []#stores interconnect path to improfamce by not having to recalculate every frame
    # prerender interconnects in view on startup
    for x in range(min_x, max_x):#create 2D array for interconnects
        temp_list = []  # List that contains all interconnects with the same x coord
        for y in range(min_y, max_y):
            temp_list.append(())#empty tuple is added so that later a value can be added without the delay of adding a new value especially at lower index values e.g 0
        array_interconnect.append(temp_list)
    for x in range(min_x, max_x):#represents the nested list that hold the x value for the in coloumb
        for y in range(min_y, max_y):
            for xx in range(min_x, max_x):#represents the nested list that hold the x value for the out coloumb
                for yy in range(min_y, max_y):
                    if db.search_if_connected(x,y,xx,yy) == True:
                        inslot_code,outslot_code = db.get_interconnect_slot(x,y,xx,yy)#coordinate is calculate by the slot number(0-3)
                        inslot = slot_coord(x,y,inslot_code)
                        outslot = slot_coord(x,yy,outslot_code)
                        array_interconnect[x][y] = inslot,outslot
                    else:array_interconnect[x][y] = None
    while main == True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if selected_gate == True or selected_interconnect == True or selected_sp == True:
                    selected_gate = selected_interconnect = selected_sp = False
                else:
                    sys.exit()
            
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)

        #open setting menu
        if keys[pygame.K_ESCAPE]:
            main = False
            settings_menu_open = True
            break
        
        # Camera Movement
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= CAM_SPEED
        if keys[pygame.K_s]: dy += CAM_SPEED
        if keys[pygame.K_a]: dx -= CAM_SPEED
        if keys[pygame.K_d]: dx += CAM_SPEED
        camera_pos[0] += dx
        camera_pos[1] += dy 

        # Calculate mouse grid position
        world_x = mouse_pos[0] + camera_pos[0]
        world_y = mouse_pos[1] + camera_pos[1]
        grid_x = world_x // GRID_SIZE
        grid_y = world_y // GRID_SIZE

        #store what a cell contains when cursor is hovered over it
        if db.load_object(int(grid_x), int(grid_y)):
            in_cell = "obj"
        elif db.search_SP(int(grid_x), int(grid_y)):
            in_cell = "sp" 
        else:
            in_cell = None

        # Mouse Interaction (Left Click)
        if mouse_buttons[0]:  # select
            if screen_height * 0.8 <= mouse_pos[1] <= screen_height * 0.8 + GRID_SIZE:
                if screen_width * 0.1 <= mouse_pos[0] <= screen_width * 0.1 + GRID_SIZE:
                    selected_gate = 0
                    selected_sp = second_click = first_click = selected_interconnect = False
                elif screen_width * 0.2 <= mouse_pos[0] <= screen_width * 0.2 + GRID_SIZE:
                    selected_gate = 1
                    selected_sp = second_click = first_click = selected_interconnect = False
                elif screen_width * 0.3 <= mouse_pos[0] <= screen_width * 0.3 + GRID_SIZE:
                    selected_gate = 2
                    selected_sp = second_click = first_click = selected_interconnect = False
                elif screen_width * 0.4 <= mouse_pos[0] <= screen_width * 0.4 + GRID_SIZE:
                    selected_gate = 3
                    selected_sp = second_click = first_click = selected_interconnect = False
                elif screen_width * 0.5 <= mouse_pos[0] <= screen_width * 0.5 + GRID_SIZE:
                    selected_gate = 4
                    selected_sp = second_click = first_click = selected_interconnect = False
                    message("Picked up interconnect", font,font_size, screen)
                elif screen_width * 0.6 <= mouse_pos[0] <= screen_width * 0.6 + GRID_SIZE:
                    selected_gate = 5
                    selected_sp = second_click = first_click = selected_interconnect = False
                elif screen_width * 0.7 <= mouse_pos[0] <= screen_width * 0.7 + GRID_SIZE:
                    selected_gate = 6
                    selected_sp = second_click = first_click = selected_interconnect = False
                elif screen_width * 0.8 <= mouse_pos[0] <= screen_width * 0.8 + GRID_SIZE:
                    selected_sp = second_click = first_click = False
                    selected_gate = None
                    selected_interconnect = True
                elif screen_width * 0.9 <= mouse_pos[0] <= screen_width * 0.9 + GRID_SIZE:
                    second_click = first_click = selected_interconnect = False
                    selected_gate = None
                    selected_sp = True
                    message("Picked up starting point", font,font_size, screen)
            elif mouse_pos[1] < screen_height * 0.7:# place
                if selected_gate != None and 0 <= selected_gate <= 7 and selected_interconnect == False and selected_sp == False:
                    if in_cell == None:
                        db.user_add_object( int(grid_x), int(grid_y), selected_gate)
                        message(f"Placed gate {['AND', 'OR', 'NAND', 'NOR','XOR','XNOR','NOT'][selected_gate]} at ({grid_x}, {grid_y})", font,font_size, screen)
                        selected_gate = None
                        # Update obj_in_view
                        for n, col in enumerate(obj_in_view):
                            if min_x + n == grid_x:
                                col.append(((grid_x, grid_y, selected_gate), grid_y))
                                break
                    else:
                        message(f"Spot ({grid_x}, {grid_y}) already occupied", font,font_size, screen)
                # place interconnect
                elif selected_interconnect == True and selected_gate == False and  selected_sp == False :
                    if in_cell == None:
                        message("No gate at this position", font,font_size, screen)
                    else:
                        if not first_click:
                            first_click = True
                            in_gate_cord = grid_x, grid_y
                            message("Selected input gate", font,font_size, screen)
                        elif grid_x == in_gate_cord[0] and grid_y == in_gate_cord[1]:
                            message("Cannot connect gate to itself", font,font_size, screen)
                        elif not second_click:
                            second_click = True
                            out_gate_cord = grid_x, grid_y
                            if db.search_if_connected(in_gate_cord[0], in_gate_cord[1], out_gate_cord[0], out_gate_cord[1]):
                                message("Gates already connected", font,font_size, screen)
                            elif out_gate_cord[0] != in_gate_cord[0] and out_gate_cord[1] != in_gate_cord[1]:  # Fix: Straight line check
                                message("Can only connect an interconnect in a straight line", font,font_size, screen)
                            else:
                                db.add_interconnect(in_gate_cord[0], in_gate_cord[1], out_gate_cord[0], out_gate_cord[1])
                                message("Interconnect placed", font,font_size, screen)
                            first_click = False
                            second_click = False
                            selected_interconnect = False
                # place a starting point
                elif selected_sp and not selected_interconnect and selected_gate is None:
                    if in_cell is None:
                        db.add_starting_point( int(grid_x), int(grid_y))
                        message(f"Placed starting point at ({grid_x}, {grid_y})", font,font_size, screen)
                        SP_in_view.append((grid_x,grid_y))
                        selected_sp = False
                    else:
                        message(f"Spot ({grid_x}, {grid_y}) already occupied", font,font_size, screen)

        # Right Click (Gate Option Menu)
        #issue: when removing a logic gate the application crashes
        if mouse_buttons[2]:
            if selected_gate is None and in_cell is not None and mouse_pos[1] < screen_height * 0.7:
                gate_option_menu_bool = True
                if open_gate_option_menu_bool:
                    gate_option_menu_pos = mouse_pos
                    selected_grid = (grid_x, grid_y)
                    open_gate_option_menu_bool = False
                    in_cell = in_cell
        elif mouse_buttons[2] and gate_option_menu_bool and not within_gate_option_menu_bool(mouse_pos, gate_option_menu_pos):#if user right clicks on another gate while gate option menu is true, then move gate option menu
            gate_option_menu_pos = mouse_pos
            selected_grid = (grid_x, grid_y)
            open_gate_option_menu_bool = False
            in_cell = in_cell
        elif mouse_buttons[0] and gate_option_menu_bool and not within_gate_option_menu_bool(mouse_pos, gate_option_menu_pos):#close gate option menu
            open_gate_option_menu_bool = False
            gate_option_menu_pos = (0, 0)
            selected_grid = None
            in_cell = None
            open_gate_option_menu_bool = True
        elif (dx != 0 or dy != 0) and gate_option_menu_bool:
            open_gate_option_menu_bool = False
            gate_option_menu_pos = (0, 0)
            selected_grid = None
            in_cell = None
            open_gate_option_menu_bool = True
            

        # Load new obj in view and remove obj out of view
        #range of cells in the x and y axis
        new_min_x = camera_pos[0] // GRID_SIZE 
        new_max_x = (camera_pos[0] + screen_width) // GRID_SIZE + 1
        new_min_y = camera_pos[1] // GRID_SIZE
        new_max_y = (camera_pos[1] + screen_height) // GRID_SIZE + 1

        if new_min_x < min_x:  # Render 1 grid left
            #gates
            temp_list_obj = []
            for y in range(min_y, max_y):
                obj = db.load_object(new_min_x, y)
                if obj:
                    temp_list_obj.append(obj[2])
                else:
                    temp_list_obj.append((None))
            obj_in_view.insert(0, temp_list_obj)
            obj_in_view.pop(-1)
            #interconnects
            temp_list_interconnect = []
            for y in range(min_y, max_y):
                for x in range(min_x,max_x):
                    for yy in range(min_y, max_y):
                        if db.search_if_connected(new_min_x,y,x,yy):
                            inslot_code,outslot_code = db.get_interconnect_slot(new_min_x,y,x,yy)
                            temp_list_interconnect.append((inslot_code,outslot_code))
                        else:
                            temp_list_interconnect.append((None))
            array_interconnect.insert(0, temp_list_interconnect) 
            array_interconnect.pop(-1)#remove last index
            min_x = new_min_x
            max_x = new_max_x
        elif new_max_x > max_x:  # Render 1 grid right
            #gates
            temp_list_obj = []
            for y in range(min_y, max_y):
                    obj = db.load_object(new_max_x - 1, y)
                    if obj:
                        temp_list_obj.append(obj[2])
                    else:
                        temp_list_obj.append((None))
            obj_in_view.append(temp_list)
            obj_in_view.pop(0)
            #interconnects
            temp_list_interconnect = []
            for y in range(min_y, max_y):
                    for x in range(min_x, max_x):
                        for yy in range(min_y, max_y):
                            if db.search_if_connected(new_max_x,y,x,yy):
                                inslot_code,outslot_code = db.get_interconnect_slot(new_min_x,y,x,yy)
                                temp_list_interconnect.append((inslot_code,outslot_code))
                            else:
                                temp_list_interconnect.append((None))
            array_interconnect.insert(0, temp_list_interconnect)
            array_interconnect.pop(-1)#remove last index
            min_x = new_min_x
            max_x = new_max_x
        if new_min_y < min_y:  # Render 1 grid up
            #gate
            for n in range(len(obj_in_view)):
                obj = db.load_object(min_x + n, new_min_y)
                if obj:
                    obj_in_view[n].insert(0, obj[2])
                else:obj_in_view[n].insert(0, (None))
                obj_in_view[n].pop(-1)
            #interconnect
            for n in range(len(array_interconnect)):
                for x in range(min_x, max_x):
                        for y in range(min_y, max_y):
                            if db.search_if_connected(new_min_x+n,new_min_y,x,y):
                                inslot_code,outslot_code = db.get_interconnect_slot(new_min_x,y,x,yy)
                                array_interconnect[n].insert(0, (inslot_code,outslot_code))
                            else:
                                array_interconnect[n].insert(0, (None))
                array_interconnect[n].pop(-1)
            min_y = new_min_y
            max_y = new_max_y
        elif new_max_y > max_y:  # Render 1 grid down
            #gates
            for n in range(len(obj_in_view)):
                obj = db.load_object(min_x + n, new_max_y - 1)
                if obj:
                    obj_in_view[n].append(obj[2])
                else:obj_in_view[n].append(None)
                obj_in_view[n].pop(0)
            #interconnect
            for n in range(len(array_interconnect)):
                for x in range(min_x, max_x):
                        for y in range(min_y, max_y):
                            if db.search_if_connected(new_min_x+n,new_max_y,x,y):
                                inslot_code,outslot_code = db.get_interconnect_slot(new_min_x+n,new_max_y,x,y)
                                array_interconnect[n].insert(0, (inslot_code,outslot_code))
                            else:
                                array_interconnect[n].insert(0, (None))
                array_interconnect[n].pop(-1)
            min_y = new_min_y
            max_y = new_max_y

        #starting points
        if new_min_x < min_x or new_max_x > max_x or new_min_y < min_y or new_max_y > max_y:
            for x,y in SP_in_view:
                #remove starting point out of render range
                if new_max_x < x:
                    SP_in_view.remove((x,y))
                elif new_min_x > x:
                    SP_in_view.remove((x,y))
                if new_max_y > y:
                    SP_in_view.remove((x,y))
                elif new_min_y < y:
                    SP_in_view.remove((x,y))
            #add starting point in render range
            if new_min_x < min_x:
                for y in range(new_max_y-new_min_y):
                    if db.search_SP(new_min_x,y) != None:
                        SP = db.search_SP(new_min_x,y)
                        SP_in_view.append((SP[0],SP[1]))
            elif new_max_x > max_x:
                for y in range(new_max_y-new_min_y):
                    if db.search_SP(new_max_x,y) != None:
                        SP = db.search_SP(new_max_x,y)
                        SP_in_view.append((SP[0],SP[1]))
            if new_min_y < min_y:
                for x in range(new_max_x-new_min_x):
                    if db.search_if_starting_point(project_name,x,new_min_y) != None:
                        SP = db.search_SP(x,new_min_y)
                        SP_in_view.append((SP[0],SP[1]))
            elif new_max_y > max_y:
                for x in range(new_max_x-new_min_x):
                    if db.search_SP(x,new_max_y) != None:
                        SP = db.search_if_starting_point(project_name,x,new_max_y)
                        SP_in_view.append((SP[0],SP[1]))

        # Gate Option Menu Interaction
        if mouse_buttons[0] and gate_option_menu_bool and within_gate_option_menu_bool(mouse_pos, gate_option_menu_pos):
            if in_cell == "obj":
                if gate_option_menu_pos[1] <= mouse_pos[1] < gate_option_menu_pos[1] + 30:
                    db.update_operation(selected_grid[0], selected_grid[1], 1)
                    message("Changed to AND gate", font,font_size, screen)
                    gate_option_menu_bool = False
                    open_gate_option_menu_bool = True
                elif gate_option_menu_pos[1] + 30 <= mouse_pos[1] < gate_option_menu_pos[1] + 60:
                    db.update_operation(selected_grid[0], selected_grid[1], 2)
                    message("Changed to OR gate", font,font_size, screen)
                    gate_option_menu_bool = False
                    open_gate_option_menu_bool = True
                elif gate_option_menu_pos[1] + 60 <= mouse_pos[1] < gate_option_menu_pos[1] + 90:
                    db.update_operation(selected_grid[0], selected_grid[1], 3)
                    message("Changed to NAND gate", font,font_size, screen)
                    gate_option_menu_bool = False
                    open_gate_option_menu_bool = True
                elif gate_option_menu_pos[1] + 90 <= mouse_pos[1] < gate_option_menu_pos[1] + 120:
                    db.update_operation(selected_grid[0], selected_grid[1], 4)
                    message("Changed to NOR gate", font,font_size, screen)
                    gate_option_menu_bool = False
                    open_gate_option_menu_bool = True
                elif gate_option_menu_pos[1] + 120 <= mouse_pos[1] < gate_option_menu_pos[1] + 150:
                        db.remove_object(selected_grid[0], selected_grid[1])
                        db.remove_interconnect(selected_grid[0], selected_grid[1])
                        message("Gate removed", font,font_size, screen)
                        gate_option_menu_bool = False
                        open_gate_option_menu_bool = True
                        # Update obj_in_view
                        for n, col in enumerate(obj_in_view):
                            if min_x + n == selected_grid[0]:
                                for i, (obj, y) in enumerate(col):
                                    if y == selected_grid[1]:
                                        col.pop(i)
                                        break
                                break
            elif in_cell == "sp":
                if gate_option_menu_pos[1] <= mouse_pos[1] < gate_option_menu_pos[1] + 30:
                    db.remove_SP(selected_grid[0], selected_grid[1])
                    db.remove_interconnect(selected_grid[0], selected_grid[1])
                    gate_option_menu_bool = False
                    open_gate_option_menu_bool = True
                    SP_in_view.remove((selected_grid))
                elif gate_option_menu_pos[1] + 30 <= mouse_pos[1] < gate_option_menu_pos[1] + 60:
                    db.change_starting_point_bit(selected_grid[0], selected_grid[1])
                    gate_option_menu_bool = False
                    open_gate_option_menu_bool = True

        #undo
        if keys[pygame.KMOD_CTRL] and keys[pygame.K_z]:
            # use a queue(FIFO) to store actions, when the user press ctrl + z the inverse action is performed to undo
            action_queue[-1]

        # Rendering
        # Grid
        x_offset = camera_pos[0] % GRID_SIZE
        y_offset = camera_pos[1] % GRID_SIZE
        for x in range(-x_offset, screen_width + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(screen, WHITE, (x, 0), (x, screen_height))
        for y in range(-y_offset, screen_height + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(screen, WHITE, (0, y), (screen_width, y))

        # Render gates
        x_column = min_x
        for col in obj_in_view:
            for obj in col:
                if obj != None:
                    #when placeing a gate 
                    draw_cell(x_column, y, obj, screen, camera_pos, font)
            x_column += 1

        # starting points
        for x,y in SP_in_view:
            draw_sp(x,y,(255,255,0),screen,camera_pos, GRID_SIZE, pygame.font.SysFont('Arial', 20))

        # Render interconnects
        for col in array_interconnect:
            for path in col:
                if path == None: pass
                elif len(path) == 2:
                    pygame.draw.line(screen,WHITE,path[0],path[1])
                else: message("could not render interconnect",font,font_size,screen)

        # Render the picked up gate relative to cursor
        if selected_gate:
            screen.blit(gate_img[selected_gate], (mouse_pos[0], mouse_pos[1]))
        elif selected_sp:
            screen.blit(gate_img[-1], (mouse_pos[0], mouse_pos[1]))

        # Render mini menu
        if gate_option_menu_bool:
            if in_cell == "obj":
                pygame.draw.rect(screen, WHITE, (gate_option_menu_pos[0], gate_option_menu_pos[1], 150, 150))
                screen.blit(font.render("Change to AND", True, (0, 0, 0)), (gate_option_menu_pos[0], gate_option_menu_pos[1]))
                screen.blit(font.render("Change to OR", True, (0, 0, 0)), (gate_option_menu_pos[0], gate_option_menu_pos[1] + 30))
                screen.blit(font.render("Change to NAND", True, (0, 0, 0)), (gate_option_menu_pos[0], gate_option_menu_pos[1] + 60))
                screen.blit(font.render("Change to NOR", True, (0, 0, 0)), (gate_option_menu_pos[0], gate_option_menu_pos[1] + 90))
                screen.blit(font.render("Remove", True, RED), (gate_option_menu_pos[0], gate_option_menu_pos[1] + 120))
            elif in_cell == "sp":
                pygame.draw.rect(screen, WHITE, (gate_option_menu_pos[0], gate_option_menu_pos[1], 150, 150))
                screen.blit(font.render("Remove starting point", True, (0, 0, 0)), (gate_option_menu_pos[0], gate_option_menu_pos[1]))
                screen.blit(font.render("Change state", True, (0, 0, 0)), (gate_option_menu_pos[0], gate_option_menu_pos[1] + 30))

        screen.blit(UI_bar,(0,screen_height*0.7))
        pygame.display.flip()
        clock.tick(settings["fps"])