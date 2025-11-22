import start,GUI,db, render, pygame
from sys import exit

main_menu = True
project = False
while True:
    while main_menu:
        start.screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start.save(None,None,None)
                # Close database and quit
                db.close_database()
                exit()#clode program

        keys = pygame.key.get_pressed()
        GUI.mpos = mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
        #close setting menu
        if keys[pygame.K_ESCAPE]:
            main = True
            settings_menu_open = False
            break

        GUI.
    while project:
        pass