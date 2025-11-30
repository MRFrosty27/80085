import os, json,pygame
from db import create_table_of_database_names

#create folder where database files are stored 
os.makedirs(os.path.join(os.path.dirname(__file__),"projects"),exist_ok=True )
create_table_of_database_names()

# Load settings from JSON (cross-platform)
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
DEFAULT_SETTINGS = {
    "screen_width": 1920,
    "screen_height": 1080
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
screen = pygame.display.set_mode((settings["screen_width"], settings["screen_height"]))
clock = pygame.time.Clock()

# Initialize game state
screen_width = settings["screen_width"]
screen_height = settings["screen_height"]
pygame.key.set_repeat(100, 100)  # 100ms delay before repeating, 100ms interval between repeats

def save(width,height):
    if width is None:
        pass#no changes made
    elif isinstance(width,int) == False:
        raise TypeError("width is not int type")
    else:
        screen_width = settings["screen_width"] = width
    
    if height is None:
        pass#no changes made
    elif isinstance(height,int) == False:
        raise TypeError("height is not int type")
    else:
        screen_height = settings["screen_height"] = height

    try:
        screen = pygame.display.set_mode((settings["screen_width"], settings["screen_height"]))
    except:
        pass
    # Save settings
    with open(SETTINGS_FILE, "w") as f:
        json.dump({
            "screen_width": settings["screen_width"],
            "screen_height": settings["screen_height"]
        }, f, indent=4)
