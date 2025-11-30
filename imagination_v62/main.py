import start,GUI,db, render, pygame
from sys import exit
from datetime import datetime

#component menu
component_menu_top = start.screen_height - (2*render.grid_size)#y cord for the top of the menu
pointy = component_menu_top+(render.grid_size//2)#y cord for the top of the component 
selected_array = (False*8)#stores which component is selected for placement
component_surfaces = (GUI.AND_surface,GUI.OR_surface,GUI.NAND_surface,GUI.NOR_surface,GUI.XOR_surface,GUI.XNOR_surface,GUI.NOT_surface,GUI.interconnect_surface)

main_menu = True
project = False
while True:
    while main_menu:
        start.screen.fill((0, 0, 0))
        
        keys = pygame.key.get_pressed()
        GUI.mpos = mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
        #close setting menu
        if keys[pygame.K_ESCAPE]:
            main_menu = False
            project = True
            break
        
        #text box
        if mouse_buttons[0]:
            GUI.tb1.click()
            GUI.tb2.click()
            GUI.tb3.click()
            GUI.tb4.click()

        for event in pygame.event.get():  # Process events for text input
            if event.type == pygame.QUIT:
                start.save(None,None)
                # Close database and quit
                exit()#clode program
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    GUI.tb1.input_remove()
                    GUI.tb2.input_remove()
                    GUI.tb3.input_remove()
                elif event.key == pygame.K_RETURN:
                    if GUI.tb1.selected_get() == True and len(GUI.tb1.input_get())> 0:
                        start.save(GUI.tb1.input_get(),None)
                        GUI.tb1.input_reset()
                    elif GUI.tb2.selected_get() == True and len(GUI.tb2.input_get())> 0:
                        start.save(None,GUI.tb2.input_get())
                        GUI.tb2.input_reset()
                    elif GUI.tb3.selected_get() == True and len(GUI.tb3.input_get())> 0:
                        time = datetime.now().strftime("%Y-%m-%d ")
                        db.project_create(GUI.tb3.input_get(),1*10^9,f"{time}",f"{time}",f"{time}")
                        GUI.tb3.input_reset()
                elif event.unicode.isalnum():
                    GUI.tb1.input_add(event.unicode)
                    GUI.tb2.input_add(event.unicode)
                    GUI.tb3.input_add(event.unicode)
        GUI.tb1.render()
        GUI.tb2.render()
        GUI.tb3.render()
        GUI.tb4.render()
        #project list

        pygame.draw.rect(start.screen,GUI.white,(start.screen_width * 0.5, GUI.screen_height_20th, start.screen_width * 0.5 - GUI.screen_width_20th, start.screen_height - 2*GUI.screen_height_20th))
        pygame.draw.rect(start.screen,GUI.plat,(start.screen_width * 0.5, GUI.screen_height_20th, start.screen_width * 0.5 - GUI.screen_width_20th, start.screen_height - 2*GUI.screen_height_20th),GUI.border)
        start.screen.blit(GUI.font_project_list.render(f"{"Name|Speed(GHz)|Created|Last accessed|Last modified"}",True,(0,0,0)),(start.screen_width * 0.5, GUI.screen_height_20th))
        n=0
        for project in db.database_get_all_project_names():
            GUI.project_list_dim[1] = GUI.font_size_project_list*(n+1) + GUI.screen_height_20th
            GUI.project_list_dim[3] = GUI.project_list_dim[1]+ GUI.font_size_project_list
            start.screen.blit(GUI.font_project_list.render(f"{project[0]}|{project[1]}|{project[2]}|{project[3]}|{project[4]}",True,(0,0,0)),(GUI.project_list_dim[0],GUI.project_list_dim[1]))
            if n == int((start.screen_height - GUI.screen_height_20th*2)/GUI.font_size_project_list):#stops projects names from being rendered off the list
                break
            if GUI.project_list_dim[1] <= mouse_pos[1]<= GUI.project_list_dim[3] and GUI.project_list_dim[0] <= mouse_pos[0]:
                if mouse_buttons[0]:
                    if mouse_pos[0] < GUI.del_x_pos:
                            db.db_name = db.access_database(project[0])
                            project = True
                            main_menu = False
                            break
                    else:
                        db.project_delete(project[0])
                start.screen.blit(GUI.font_project_list.render(f"{"DEL"}",True,GUI.plat),(GUI.del_x_pos,GUI.project_list_dim[1]))
            n+=1 

        pygame.display.flip()
        start.clock.tick(60)
    while project:
        
        mouse_pos = pygame.mouse.get_pos()
        # Camera Movement
        # new x and y = cam pos to ensure that it is in sync
        new_x = render.camera_pos[0]
        new_y = render.camera_pos[1]
        if keys[pygame.K_w]: new_y -= render.cam_speed
        if keys[pygame.K_s]: new_y += render.cam_speed
        if keys[pygame.K_a]: new_x -= render.cam_speed
        if keys[pygame.K_d]: new_x += render.cam_speed
        render.render(new_x,new_y)
        mouse_cell_contains = db.object_load(render.camera_pos[0],render.camera_pos[1])
        #component menu
        #gate and interconnect placement
        pygame.draw.rect(start.screen,(255,255,255),(0,component_menu_top,start.screen_width,start.screen_height))
        pygame.draw.line(start.screen,(200,250,250),(0,component_menu_top,start.screen_width,component_menu_top))
        padding = start.screen_width*0.05
        for n in range(8):
            pointx = (n*render.grid_size) + render.grid_size//2
            
            start.screen.blit(component_surfaces[n],(padding + pointx,pointy))
            if pointx <= mouse_pos[0] <= pointx + render.grid_size and pointy <= mouse_pos[1] <= pointy + render.grid_size:
                selected_array[n]=True
        #gate option menu
        if mouse_cell_contains:
            pass
        #interconnect option menu
        
        for n in range(len(selected_array)):
            if selected_array[n] == True:
                start.screen.blit(component_surfaces[n],mouse_pos[0],mouse_pos[1])
        pygame.display.flip()
        start.clock.tick(60)
    