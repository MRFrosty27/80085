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

        #text box
        if mouse_buttons[0]:
            GUI.tb1.click()
            GUI.tb2.click()
            GUI.tb3.click()
            GUI.tb4.click()

        for event in pygame.event.get():  # Process events for text input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        GUI.tb1.input_remove()
                        GUI.tb2.input_remove()
                        GUI.tb3.input_remove()
                        GUI.tb4.input_remove()
                    elif event.key == pygame.K_RETURN and len() > 0:
                        pass
                    elif event.unicode.isalnum() and len() <= 16:
                        GUI.tb1.input_add(event.unicode)
                        GUI.tb2.input_add(event.unicode)
                        GUI.tb3.input_add(event.unicode)
                        GUI.tb4.input_add(event.unicode)
        GUI.tb1.render()
        GUI.tb2.render()
        GUI.tb3.render()
        GUI.tb4.render()
        #project list


    while project:
        #gate and interconnect placement

        #gate option menu

        #interconnect option menu

        #render

        pass
    