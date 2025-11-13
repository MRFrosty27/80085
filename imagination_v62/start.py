import os, json
import GUI

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
pygame.key.set_repeat(100, 100)  # 500ms delay before repeating, 50ms interval between repeats

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