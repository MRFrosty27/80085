import os, json,GUI,pygame

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
GUI.display = screen = pygame.display.set_mode((settings["screen_width"], settings["screen_height"]))
clock = pygame.time.Clock()

# Initialize game state
GUI.screen_width = screen_width = settings["screen_width"]
GUI.screen_height = screen_height = settings["screen_height"]
GUI.box_dim = int(GUI.screen_width * 0.1),int(GUI.screen_height * 0.1)
pygame.key.set_repeat(100, 100)  # 500ms delay before repeating, 50ms interval between repeats

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

    try:
        GUI.display = screen = pygame.display.set_mode((settings["screen_width"], settings["screen_height"]))
    except:
        pass
    # Save settings
    with open(SETTINGS_FILE, "w") as f:
        json.dump({
            "screen_width": settings["screen_width"],
            "screen_height": settings["screen_height"],
            "fps": settings["fps"]
        }, f, indent=4)

#check if file structure is correct 