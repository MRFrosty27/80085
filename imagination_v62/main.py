import multiprocessing
from multiprocessing import freeze_support

def calc_slot_number():
    if mouse_grid_world_pos[0] - int(mouse_grid_world_pos[0]) < 0.5:
        if mouse_grid_world_pos[1] - int(mouse_grid_world_pos[1]) < 0.5: 
            pass
        else:
            pass
    else:
        if mouse_grid_world_pos[1] - int(mouse_grid_world_pos[1]) < 0.5: 
            pass
        else:
            pass

if __name__ == '__main__':
    #import non-multiprocessing libraries here
    #this ensures that only one window is created
    import start,GUI,db, render, pygame
    from sys import exit
    from datetime import datetime
    freeze_support()  # is safe for Windoes,MacOS and others

    #component menu
    component_menu_top = start.screen_height - (2*render.grid_size)#y cord for the top of the menu
    component_icon_top_y_point = component_menu_top+(render.grid_size//2)#y cord for the top of the component 
    component_selected_index = None#stores which component is selected for placement
    component_surfaces = (GUI.AND_surface,GUI.OR_surface,GUI.NAND_surface,GUI.NOR_surface,GUI.XOR_surface,GUI.XNOR_surface,GUI.NOT_surface,GUI.interconnect_surface)
    component_icon_gap = render.grid_size + render.grid_size//2
    first_interconnect_point_selected = False
    second_interconnect_point_selected = False
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
                GUI.tb3.click()
                GUI.tb4.click()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if render.process_pool is not None:
                        render.process_pool.close()
                        render.process_pool.join()
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        GUI.tb3.input_remove()
                    elif event.key == pygame.K_RETURN:
                        if GUI.tb3.selected_get() == True and len(GUI.tb3.input_get())> 0:
                            time = datetime.now().strftime("%Y-%m-%d ")
                            db.project_create(GUI.tb3.input_get(),1*10^9,f"{time}",f"{time}",f"{time}")
                            db.db_name = db.access_database(GUI.tb3.input_get())
                            db.table_object_create()
                            db.table_interconnect_create()
                            GUI.tb3.input_reset()
                    elif event.unicode.isalnum():
                        GUI.tb3.input_add(event.unicode)
            GUI.tb3.render()
            GUI.tb4.render()
            #project list

            pygame.draw.rect(start.screen,GUI.white,(start.screen_width * 0.5, GUI.screen_height_20th, start.screen_width * 0.5 - GUI.screen_width_20th, start.screen_height - 2*GUI.screen_height_20th))
            pygame.draw.rect(start.screen,GUI.plat,(start.screen_width * 0.5, GUI.screen_height_20th, start.screen_width * 0.5 - GUI.screen_width_20th, start.screen_height - 2*GUI.screen_height_20th),GUI.border)
            start.screen.blit(GUI.font_project_list.render(f"{"Name|Speed(GHz)|Created|Last accessed|Last modified"}",True,(0,0,0)),(start.screen_width * 0.5, GUI.screen_height_20th))
            n=0
            for project_data in db.database_get_all_project_names():
                GUI.project_list_dim[1] = GUI.font_size_project_list*(n+1) + GUI.screen_height_20th
                GUI.project_list_dim[3] = GUI.project_list_dim[1]+ GUI.font_size_project_list
                start.screen.blit(GUI.font_project_list.render(f"{project_data[0]}|{project_data[1]}|{project_data[2]}|{project_data[3]}|{project_data[4]}",True,(0,0,0)),(GUI.project_list_dim[0],GUI.project_list_dim[1]))
                if n == int((start.screen_height - GUI.screen_height_20th*2)/GUI.font_size_project_list):#stops projects names from being rendered off the list
                    break
                if GUI.project_list_dim[1] <= mouse_pos[1]<= GUI.project_list_dim[3] and GUI.project_list_dim[0] <= mouse_pos[0]:
                    if mouse_buttons[0]:
                        if mouse_pos[0] < GUI.del_x_pos:
                                db.db_connection,db.db_cursor = db.access_database(project_data[0])
                                db.db_name = project_data[0]
                                render.process_pool = multiprocessing.Pool(processes=multiprocessing.cpu_count(),initializer=db.init_process_connection(db.db_name))
                                render.setup_render()
                                project = True
                                main_menu = False
                                break
                        else:
                            db.project_delete(project_data[0])
                    start.screen.blit(GUI.font_project_list.render(f"{"DEL"}",True,GUI.plat),(GUI.del_x_pos,GUI.project_list_dim[1]))
                n+=1 

            pygame.display.flip()
            start.clock.tick(60)

        while project:
            start.screen.fill((0, 0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if render.process_pool is not None:
                        render.process_pool.close()
                        render.process_pool.join()
                    pygame.quit()
                    exit()

            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
            mouse_pos = pygame.mouse.get_pos()
            mouse_grid_world_pos = ((mouse_pos[0] + render.camera_pos[0])/render.grid_size,(mouse_pos[1] + render.camera_pos[1])/render.grid_size)
            mouse_grid_local_pos = (mouse_pos[0]//render.grid_size, mouse_pos[1]//render.grid_size)

            # Camera Movement
            # new x and y = cam pos to ensure that it is in sync
            if keys[pygame.K_w]: render.camera_pos[1] -= render.cam_speed
            elif keys[pygame.K_s]: render.camera_pos[1] += render.cam_speed
            if keys[pygame.K_a]: render.camera_pos[0] -= render.cam_speed
            elif keys[pygame.K_d]: render.camera_pos[0] += render.cam_speed
            render.render()
            
            #component menu
            #gate and interconnect placement
            pygame.draw.rect(start.screen,(255,255,255),(0,component_menu_top,start.screen_width,start.screen_height))
            pygame.draw.line(start.screen,(200,250,250),(0,component_menu_top),(start.screen_width,component_menu_top))
            padding = start.screen_width*0.05

            if mouse_pos[1] > component_menu_top:#mouse within component menu
                for n in range(len(component_surfaces)):
                    component_icon_top_x_point = n*component_icon_gap
                    start.screen.blit(component_surfaces[n],(padding + component_icon_top_x_point,component_icon_top_y_point))
                    if mouse_buttons[0] and component_icon_top_x_point <= mouse_pos[0] <= component_icon_top_x_point + render.grid_size and component_icon_top_y_point <= mouse_pos[1] <= component_icon_top_y_point + render.grid_size:
                        component_selected_index = n-1
            elif component_selected_index != None:
                for n in range(len(component_surfaces)):
                    component_icon_top_x_point = n*component_icon_gap
                    start.screen.blit(component_surfaces[n],(padding + component_icon_top_x_point,component_icon_top_y_point))
                if 0 <= component_selected_index <= 6:#place selected component
                    start.screen.blit(component_surfaces[component_selected_index],(mouse_pos[0],mouse_pos[1]))
                    if mouse_buttons[0]:
                        db.object_add(int(mouse_grid_world_pos[0]),int(mouse_grid_world_pos[1]),component_selected_index+1)
                        render.obj_cache[mouse_grid_local_pos[0]].change_cell(mouse_grid_local_pos[1],component_selected_index+1)
                        component_selected_index = None
                elif component_selected_index == 7:
                    pass
            else:
                for n in range(len(component_surfaces)):
                    component_icon_top_x_point = n*component_icon_gap
                    start.screen.blit(component_surfaces[n],(padding + component_icon_top_x_point,component_icon_top_y_point))

            #gate option menu
            mouse_cell_contains = db.object_load(mouse_pos[0],mouse_pos[1])
            if mouse_cell_contains != 0 and mouse_buttons[2]:
                GUI.obj_option_menu.click()
            elif GUI.obj_option_menu.open_get() == True:
                GUI.obj_option_menu.render()

            #interconnect option menu
            #render.process_pool.map(db.object_search_connected,[() for ])
            for x in range(render.min_x,render.max_x):
                for y in range(render.min_y,render.max_y):
                    interconnect = db.object_search_connected(x,y)
                    if interconnect is None: continue
                    else:
                        inx,iny,outx,outy,inslot,outslot = interconnect
                        point_one = render.slot_coord(inx,iny,inslot)
                        point_two = render.slot_coord(outx,outy,outslot)

            if mouse_pos[1] < component_menu_top:
                if mouse_buttons[0]:
                    pass

            pygame.display.flip()
            start.clock.tick(60)
        