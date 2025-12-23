import os,pygame
from db import create_table_of_database_names

#create folder where database files are stored 
os.makedirs(os.path.join(os.path.dirname(__file__),"projects"),exist_ok=True )
create_table_of_database_names()

# Set up display
pygame.init()
pygame.display.set_caption('Imagination')
screen_width,screen_height = dim = pygame.display.get_desktop_sizes()[0]
screen = pygame.display.set_mode((screen_width,screen_height),pygame.NOFRAME)
pygame.display.set_caption("Imagination")
clock = pygame.time.Clock()
pygame.key.set_repeat(100, 100)  # 100ms delay before repeating, 100ms interval between repeats
