"""
TODO change all position arrays to just X and Y variable to eliminate the overhead of arrays
TODO improve GUI text_box class by adding inheritance, and spliting typable and static text boxes into child clases
All exec() must be run in main.py
all returns of a function must only be of one data type
word refers to the entire project grid space
local refers to only the gridspace with the users window/screen
"""

def calc_slot_number():
    if mouse_grid_world_pos[0] - int(mouse_grid_world_pos[0]) < 0.5:
        if mouse_grid_world_pos[1] - int(mouse_grid_world_pos[1]) < 0.5: 
            return 0
        else:
            return 1
    else:
        if mouse_grid_world_pos[1] - int(mouse_grid_world_pos[1]) < 0.5: 
            return 2
        else:
            return 3

if __name__ == '__main__':
    #import non-multiprocessing libraries here
    #this ensures that only one window is created
    import start,GUI,db, render, pygame, multiprocessing
    from sys import exit
    from datetime import datetime
    from multiprocessing import freeze_support
    freeze_support()  # is safe for Windoes,MacOS and others

    #component menu
    component_menu_top = start.screen_height - (2*render.grid_size)#y cord for the top of the menu
    component_icon_top_y_point = component_menu_top+(render.grid_size//2)#y cord for the top of the component 
    component_selected_index = None#stores which component is selected for placement
    component_surfaces = (None,GUI.AND_surface,GUI.OR_surface,GUI.NAND_surface,GUI.NOR_surface,GUI.XOR_surface,GUI.XNOR_surface,GUI.NOT_surface,GUI.interconnect_surface)
    component_icon_gap = render.grid_size * 1.5
    main_menu = True
    project = False

    while True:
        while main_menu:
            start.screen.fill((0, 0, 0))
            
            keys = pygame.key.get_pressed()
            GUI.mouse_pos = mouse_pos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
            #close setting menu or swap to project
            if keys[pygame.K_ESCAPE] and db.db_name != None:
                main_menu = False
                project = True
                break
            
            #text box
            if mouse_buttons[0]:
                GUI.new_project_name_button.click()
                exec(GUI.exit_button.click())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if render.process_pool is not None:
                        render.process_pool.close()
                        render.process_pool.join()
                    pygame.quit()
                    exit()
                #tb3 text input interaction
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        GUI.new_project_name_button.input_remove()
                    elif event.key == pygame.K_RETURN:
                        if GUI.new_project_name_button.selected_get() == True and len(GUI.new_project_name_button.input_get())> 0:
                            time = datetime.now().strftime("%Y-%m-%d ")
                            db.project_create(GUI.new_project_name_button.input_get(),1*10^9,f"{time}",f"{time}",f"{time}")
                            db.db_name = db.access_database(GUI.new_project_name_button.input_get())
                            db.table_object_create()
                            db.table_interconnect_create()
                            GUI.new_project_name_button.input_reset()
                    elif event.unicode.isalnum():
                        GUI.new_project_name_button.input_add(event.unicode)
            GUI.new_project_name_button.render()
            GUI.exit_button.render()
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
                            if project_data[0] == db.db_name:
                                db.db_name = None
                            db.project_delete(project_data[0])
                    start.screen.blit(GUI.font_project_list.render(f"{"DEL"}",True,GUI.plat),(GUI.del_x_pos,GUI.project_list_dim[1]))
                n+=1 

            pygame.display.flip()
            start.clock.tick(60)

        while project:
            start.screen.fill((0, 0, 0))
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if render.process_pool is not None:
                        render.process_pool.close()
                        render.process_pool.join()
                    pygame.quit()
                    exit()
                elif keys[pygame.K_ESCAPE]:
                    main_menu = True
                    project = False
                    break
            
            mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
            GUI.mouse_pos = mouse_pos = pygame.mouse.get_pos()
            mouse_grid_world_pos = ((mouse_pos[0] + render.camera_pos[0])/render.grid_size,(mouse_pos[1] + render.camera_pos[1])/render.grid_size)#must be float for calc_slot_num()
            mouse_grid_world_pos_int = (int(mouse_grid_world_pos[0]),int(mouse_grid_world_pos[1]))
            mouse_grid_local_pos = int(mouse_grid_world_pos[0]-render.min_x),int(mouse_grid_world_pos[1]-render.min_y)
            #interconnect points format- x,y,slot num
            interconnect_from_point = None,None, None
            interconnect_to_point = None,None, None
            try:
                mouse_cell_contains = render.obj_cache[mouse_grid_local_pos[0]][mouse_grid_local_pos[1]]
            except:
                print('there was an issue with accessing obj_cache')
                print(f'obj_cache col len: {render.obj_cache[mouse_grid_local_pos[0]]}')
                print(f'tried accesses index {mouse_grid_local_pos[1]}')
                mouse_cell_contains = None

            # Camera Movement
            # new x and y = cam pos to ensure that it is in sync
            if keys[pygame.K_w]: render.camera_pos[1] -= render.cam_speed
            elif keys[pygame.K_s]: render.camera_pos[1] += render.cam_speed
            if keys[pygame.K_a]: render.camera_pos[0] -= render.cam_speed
            elif keys[pygame.K_d]: render.camera_pos[0] += render.cam_speed
            render.x_offset = render.camera_pos[0] % render.grid_size
            render.y_offset = render.camera_pos[1] % render.grid_size
            render.render()
            
            #component menu
            #gate and interconnect placement
            pygame.draw.rect(start.screen,(255,255,255),(0,component_menu_top,start.screen_width,start.screen_height))
            pygame.draw.line(start.screen,(200,250,250),(0,component_menu_top),(start.screen_width,component_menu_top))

            # Draw component icons (always drawn when not placing)
            for n in range(1, len(component_surfaces)):
                component_icon_x_pos = n * component_icon_gap
                start.screen.blit(component_surfaces[n], (component_icon_x_pos, component_icon_top_y_point))

                # Check for click only when mouse is in the component menu
                if mouse_buttons[0] and mouse_pos[1] > component_menu_top and component_icon_x_pos <= mouse_pos[0] <= component_icon_x_pos + render.grid_size and component_icon_top_y_point <= mouse_pos[1] <= component_icon_top_y_point + render.grid_size:
                    component_selected_index = n

            # Handle placing the selected component
            if component_selected_index is not None:
                if 1 <= component_selected_index <= 7:  # Valid placeable component
                    render.display_slots = False
                    start.screen.blit(component_surfaces[component_selected_index], mouse_pos)
                    
                    if mouse_buttons[0] and mouse_pos[1] < component_menu_top: 
                        # Place the component
                        db.object_add(
                            mouse_grid_world_pos_int[0],
                            mouse_grid_world_pos_int[1],
                            component_selected_index + 1)
                        render.obj_cache[mouse_grid_local_pos[0]][mouse_grid_local_pos[1]] = component_selected_index + 1
                        component_selected_index = None
                
                elif component_selected_index == 8:
                    start.screen.blit(component_surfaces[n], (component_icon_x_pos, component_icon_top_y_point))
                    render.display_slots = True
                    if mouse_cell_contains and mouse_buttons[0]:
                        if interconnect_from_point == None:
                            interconnect_from_point = mouse_grid_world_pos_int[0], mouse_grid_world_pos_int[1], calc_slot_number()
                        elif interconnect_to_point == None and mouse_grid_world_pos_int[0] != interconnect_from_point[0] and mouse_grid_world_pos_int[1] != interconnect_from_point[1]:
                            #pygame.draw.line(start.screen,(255,55,55),(interconnect_from_point[0],interconnect_from_point[1]),)
                            interconnect_to_point = mouse_grid_world_pos_int[0], mouse_grid_world_pos_int[1], calc_slot_number()
                        else: db.interconnect_add(interconnect_from_point[0],interconnect_from_point[1],interconnect_from_point[2],interconnect_to_point[0],interconnect_to_point[1],interconnect_to_point[2])

            else: render.display_slots = False

            #gate option menu
            if mouse_buttons[2]:
                if mouse_cell_contains == 0: 
                    GUI.obj_option_menu.set_open_to(False)
                elif 1 <= mouse_cell_contains <= 7: 
                    GUI.obj_option_menu.set_open_to(True)
                    GUI.selected_component_grid_x_pos, GUI.selected_component_grid_y_pos = mouse_grid_local_pos[0],mouse_grid_local_pos[1]
            elif mouse_buttons[0]:
                try:
                    exec(GUI.obj_option_menu.click())
                except:
                    pass
            elif keys[pygame.K_w] or keys[pygame.K_2] or keys[pygame.K_a] or keys[pygame.K_d]:
                GUI.obj_option_menu.set_open_to(False)
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

            pygame.display.flip()
            start.clock.tick(60)
        