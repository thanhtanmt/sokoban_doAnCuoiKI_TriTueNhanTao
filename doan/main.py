import pygame
import time
from map import Map1
from move_by_AI import AI
from SokobanEnv import SokobanEnv
from q_learning import q_learning
import numpy as np
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
pygame.init()

width, height = 339, 600

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Trò chơi Sokoban")

clock = pygame.time.Clock()
flag= True
def plot_data(map_file):
    data = pd.read_csv(f'data/{map_file}.csv')
    data_avg = data.groupby('Algorithm').agg({'Time': 'mean', 'Steps': 'mean', 'Path Length': 'mean'}).reset_index()

    plt.figure(figsize=(8, 6))
    plt.bar(data_avg['Algorithm'], data_avg['Time'], color='skyblue', edgecolor='black')
    plt.title(f'Average Time for {map_file}', fontsize=16)
    plt.xlabel('Algorithm', fontsize=12)
    plt.ylabel('Time (s)', fontsize=12)
    plt.xticks(rotation=45)  
    plt.tight_layout() 

def plot_all_maps():
    plt.figure(figsize=(10, 6))
    
    for i in range(1, 13):
        map_file = f"map{i}"
        data = pd.read_csv(f'data/{map_file}.csv')

        data_avg = data.groupby('Algorithm').agg({'Time': 'mean', 'Steps': 'mean', 'Path Length': 'mean'}).reset_index()

        plt.plot(data_avg['Algorithm'], data_avg['Time'], marker='o', label=f'Map {i}')  # Vẽ đường với marker
    
    plt.xlabel('Algorithm', fontsize=12)
    plt.ylabel('Time (s)', fontsize=12)
    plt.title('Average Time for All Maps', fontsize=16)
    plt.legend(title='Maps', fontsize=10)
    plt.xticks(rotation=45)
    plt.tight_layout()  
    plt.show()

def save_algorithm_result(file_name, algorithm, time_elapsed, steps, path_length):

    folder = 'data'
    os.makedirs(folder, exist_ok=True) 
    file_path = os.path.join(folder, file_name)
    
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Algorithm', 'Time', 'Steps', 'Path Length'])
        writer.writerow([algorithm, time_elapsed, steps, path_length])

def extract_path_from_pair_qtable(q_raw, start_state):
    path = []
    current = start_state
    visited = set()

    direction_map = {
        0: "UP",
        1: "DOWN",
        2: "LEFT",
        3: "RIGHT"
    }

    while True:
        if current in visited:
            break
        visited.add(current)
        candidates = [(next_state[0], q_values) 
                      for (state, next_state), q_values in q_raw.items() 
                      if state == current]

        if not candidates:
            break  

        best_action = -1
        best_q = -float('inf')
        next_pos = None

        for ns, q_values in candidates:
            for i, q in enumerate(q_values):
                if q > best_q:
                    best_q = q
                    best_action = i
                    next_pos = ns

        if best_action == -1 or next_pos is None:
            break

        path.append(direction_map[best_action])
        current = next_pos

        if best_q == 0:  
            break

    return path

def next_level(map_index, path_length, time):
    print (path_length)

    popup=pygame.transform.smoothscale(pygame.image.load(r'assets\images\popup-sheet0.png').convert_alpha(),(279,181))
    btn_nextlevel=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnnextlevel-sheet0.png').convert_alpha(),(51,51))
    btn_restart=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnrestart-sheet0.png').convert_alpha(),(51,51))
    btn_menu=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnmenu-sheet0.png').convert_alpha(),(51,51))
    btn_nextlevel_rect=btn_nextlevel.get_rect(topleft=(258,340))
    btn_menu_rect=btn_nextlevel.get_rect(topleft=(30,340))
    btn_restart_rect=btn_nextlevel.get_rect(topleft=(207,340))

    # viết level lên header
    font = pygame.font.SysFont("Arial", 38,  bold=True)
    font2 = pygame.font.SysFont("Arial", 19,  bold=True)
    text_surface = font.render(f"level {map_index}", True, (0, 0, 0))
    text_surface2 = font2.render(f"step: {path_length} time: {round(time, 4)}", True, (0, 0, 0))
    transparent_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA) 
    transparent_surface.blit(text_surface, (0, 0))
    transparent_surface2 = pygame.Surface(text_surface2.get_size(), pygame.SRCALPHA) 
    transparent_surface2.blit(text_surface2, (0, 0))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_restart_rect.collidepoint(event.pos):
                    AI_Algorithms(map_index)
                    running=False
                elif btn_menu_rect.collidepoint(event.pos):
                    menu()
                    running=False
                elif btn_nextlevel_rect.collidepoint(event.pos) and map_index!=12:
                    AI_Algorithms(map_index+1)
                    running=False
        screen.blit(popup,(30,210))
        screen.blit(btn_nextlevel,btn_nextlevel_rect.topleft)
        screen.blit(btn_menu,btn_menu_rect.topleft)
        screen.blit(btn_restart,btn_restart_rect.topleft)
        screen.blit(transparent_surface, (130, 260)) 
        screen.blit(transparent_surface2, (90, 310)) 
        
        pygame.display.flip()

def game_play(map_index, label):
    back_groud=pygame.transform.smoothscale(pygame.image.load(r'assets/images/tiledbackground2.png').convert_alpha(),(339,600))
    header=pygame.transform.smoothscale(pygame.image.load(r'assets\images\header-sheet0.png').convert_alpha(),(339,60))
    btn_restart=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnrestart-sheet0.png').convert_alpha(),(60,60))
    btn_exit=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnback-sheet0.png').convert_alpha(),(60,60))
    wall_image=pygame.transform.smoothscale(pygame.image.load(r'assets/images/block-sheet0.png').convert_alpha(),(40,40))
    box_image= pygame.transform.smoothscale(pygame.image.load(r'assets\images\crate-sheet0.png').convert_alpha(),(40,40))
    box_at_goal_image=pygame.transform.smoothscale(pygame.image.load(r'assets\images\crate-sheet1.png').convert_alpha(),(40,40))
    floor_image=pygame.transform.smoothscale(pygame.image.load(r'assets\images\tiledbackground.png').convert_alpha(),(40,40))
    sokoban_down=pygame.transform.smoothscale(pygame.image.load(r'assets\images\player-sheet0.png').convert_alpha(),(40,40))
    sokoban_left=pygame.transform.smoothscale(pygame.image.load(r'assets\images\sokoban_left.png').convert_alpha(),(40,40))
    sokoban_right=pygame.transform.smoothscale(pygame.image.load(r'assets\images\sokoban_right.png').convert_alpha(),(40,40))
    sokoban_up=pygame.transform.smoothscale(pygame.image.load(r'assets\images\sokoban_up.png').convert_alpha(),(40,40))
    btn_mute=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnsound-sheet0.png').convert_alpha(),(60,60))
    btn_not_mute=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnsound-sheet1.png').convert_alpha(),(60,60))
    goal_image=pygame.transform.smoothscale(pygame.image.load(r'assets\images\environment-sheet0.png'),(25,25))
    btn_exit_rect=btn_exit.get_rect(topleft=(0,0))
    btn_restart_rect=btn_restart.get_rect(topleft=(279,0))
    btn_mute_rect=btn_mute.get_rect(topleft=(219,0))
    running=True
    check_var=True
    global flag
    toplefts_of_map=[[70,120],[30,150],[50,190],[50,200],[50,200],[30,190],[10,200],[10,190],[30,190],[30,180],[30,180],[10,200]]
    bando=Map1(floor_image,wall_image,sokoban_down,sokoban_up,sokoban_right,sokoban_left,box_image,goal_image,box_at_goal_image,map_index,toplefts_of_map[map_index-1][0],toplefts_of_map[map_index-1][1])
    pygame.mixer.music.load("assets\soud\mattoglseby - 4.ogv")
    pygame.mixer.music.play(-1)
    bando_ai=AI(bando.map1,bando.s_side_map1,bando.list_box_map1)
    step=0
    time_elapsed=0
    path=None

    if label=="Autoplay":
        check_var=False
    elif label=="BFS":
        path, time_elapsed, step=bando_ai.bfs()
        print(path)
        if path is not None:
            save_algorithm_result(f'map{map_index}.csv', 'BFS', time_elapsed, step, len(path))
        else:
            save_algorithm_result(f'map{map_index}.csv', 'BFS', time_elapsed, step, -1)
    elif label== "A*":
        path, time_elapsed, step=bando_ai.A_star()
        print(path)
        if path is not None:
            save_algorithm_result(f'map{map_index}.csv', 'A*', time_elapsed, step, len(path))
        else:
            save_algorithm_result(f'map{map_index}.csv', 'A*', time_elapsed, step, -1)
    elif label== "Simulated Annealing":
        a_star_solution = bando_ai.A_star()[0]
        path, time_elapsed, step = bando_ai.simulated_annealing(a_star_solution)
        # path=bando_ai.simulated_annealing(a_star_solution)
        print(path)
        if path is not None:
            save_algorithm_result(f'map{map_index}.csv', 'Simulated Annealing', time_elapsed, step, len(path))
        else:
            save_algorithm_result(f'map{map_index}.csv', 'Simulated Annealing', time_elapsed, step, -1)
    elif label== "Partial Observation + A*":
        bando_ai.known_map = [['?' for _ in range(bando_ai.cols)] for _ in range(bando_ai.rows)]
        bando_ai.update_visibility(bando_ai.map, bando_ai.player_pos)
        path, time_elapsed, step = bando_ai.A_star_partial()
        print(path)
        if path is not None:
            save_algorithm_result(f'map{map_index}.csv', 'Partial Observation + A*', time_elapsed, step, len(path))
        else:
            save_algorithm_result(f'map{map_index}.csv', 'Partial Observation + A*', time_elapsed, step, -1)
    elif label== "Backtracking":
        path,step, time_elapsed= bando_ai.backtracking()
        # path=bando_ai.backtracking()
        print(path)
        if path is not None:
            save_algorithm_result(f'map{map_index}.csv', 'Backtracking', time_elapsed, step, len(path))
        else:
            save_algorithm_result(f'map{map_index}.csv', 'Backtracking', time_elapsed, step, -1)
    elif label== "Q-Learning":
        env = SokobanEnv(bando_ai)
        q_table = q_learning(env)
        path = extract_path_from_pair_qtable(q_table, start_state=(1, 2))
        print(path)
    count=0
    path_index=0
    # viết level lên header
    font = pygame.font.SysFont("Arial", 38)
    text_surface = font.render(f"level {map_index}", True, (255, 255, 255))
    transparent_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA) 
    transparent_surface.blit(text_surface, (0, 0))

    while running:
        count+=1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_restart_rect.collidepoint(event.pos):
                    bando=Map1(floor_image,wall_image,sokoban_down,sokoban_up,sokoban_right,sokoban_left,box_image,goal_image,box_at_goal_image,map_index,toplefts_of_map[map_index-1][0],toplefts_of_map[map_index-1][1])
                elif btn_exit_rect.collidepoint(event.pos):
                    menu()
                    running=False
                elif btn_mute_rect.collidepoint(event.pos):
                    flag= not(flag)
                
        
        keys=pygame.key.get_pressed()
        if(keys[pygame.K_RIGHT]):
            bando.move_right(pygame.time.get_ticks())
        if (keys[pygame.K_LEFT]):
           bando.move_left(pygame.time.get_ticks())
        if(keys[pygame.K_DOWN]):
            bando.move_down(pygame.time.get_ticks())
        if (keys[pygame.K_UP]) :
            bando.move_up(pygame.time.get_ticks())
        if check_var and count>70 and path!= None and path_index < len(path):
            if path[path_index]=='LEFT':
                bando.move_left(pygame.time.get_ticks())
                path_index+=1
                time.sleep(0.3)
            elif path[path_index]=='RIGHT':
                bando.move_right(pygame.time.get_ticks())
                path_index+=1
                time.sleep(0.3)
            elif  path[path_index]=='UP':
                bando.move_up(pygame.time.get_ticks())
                path_index+=1
                time.sleep(0.3)
            elif  path[path_index]=='DOWN':
                bando.move_down(pygame.time.get_ticks())
                path_index+=1
                time.sleep(0.3)

        if flag:
            pygame.mixer.music.set_volume(0.3)
            btn_mute1=btn_mute
        else:
            pygame.mixer.music.set_volume(0)
            btn_mute1=btn_not_mute
        screen.blit(back_groud,(0,0)) 
        screen.blit(header,(0,0))
        screen.blit(btn_exit,(0,0))
        screen.blit(btn_restart,(279,0))
        screen.blit(btn_mute1,(219,0))
        screen.blit(transparent_surface, (80, 5))       
        bando.draw_map(screen)
        
        pygame.display.flip()
        if bando.is_finished():
            next_level(map_index, 0 if path==None else len(path), time_elapsed)
            running= False
            break
        clock.tick(60)

def AI_Algorithms(map_index):
    global flag
    WIDTH, HEIGHT = 340, 600
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    btn_mute=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnsound-sheet0.png').convert_alpha(),(60,60))
    btn_not_mute=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnsound-sheet1.png').convert_alpha(),(60,60))
    header=pygame.transform.smoothscale(pygame.image.load(r'assets\images\header-sheet0.png').convert_alpha(),(339,60))
    btn_exit=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnback-sheet0.png').convert_alpha(),(60,60))
    btn_exit_rect=btn_exit.get_rect(topleft=(0,0))
    btn_mute_rect=btn_mute.get_rect(topleft=(279,0))
    
    # Colors
    WHITE = (245, 247, 250)
    DARK_BLUE = (30, 144, 255)
    HOVER_BLUE = (70, 160, 255)
    # CLICK_BLUE = (20, 120, 200)
    CLICK_GREEN = (0, 150, 0)  # Màu khi nhấn giữ
    BLACK = (33, 33, 33)
    SHADOW = (200, 200, 200)

    # Fonts
    TITLE_FONT = pygame.font.SysFont("arial", 28, bold=True)
    BUTTON_FONT = pygame.font.SysFont("arial", 20)

    # Button labels
    buttons = [
        "Autoplay",
        "BFS",
        "A*",
        "Simulated Annealing",
        "Partial Observation + A*",
        "Backtracking",
        "Q-Learning"
    ]

    # Create button rectangles
    button_rects = []
    button_width, button_height = 280, 50
    gap = 15
    start_y = 130

    for i, label in enumerate(buttons):
        x = (WIDTH - button_width) // 2
        y = start_y + i * (button_height + gap)
        rect = pygame.Rect(x, y, button_width, button_height)
        button_rects.append((label, rect))

    def draw_buttons(mouse_pos, mouse_pressed):
        SCREEN.fill(WHITE)
        
        title = TITLE_FONT.render("Select Algorithm", True, BLACK)
        SCREEN.blit(title, ((WIDTH - title.get_width()) // 2, 60))
        
        for label, rect in button_rects:
            color = DARK_BLUE
            if rect.collidepoint(mouse_pos):
                color = CLICK_GREEN if mouse_pressed[0] else CLICK_GREEN

            shadow_rect = rect.copy()
            shadow_rect.move_ip(3, 3)
            pygame.draw.rect(SCREEN, SHADOW, shadow_rect, border_radius=12)

            pygame.draw.rect(SCREEN, color, rect, border_radius=12)
            text = BUTTON_FONT.render(label, True, WHITE)
            SCREEN.blit(text, (rect.x + (rect.width - text.get_width()) // 2,
                            rect.y + (rect.height - text.get_height()) // 2))
    running = True
    # viết level lên header
    font = pygame.font.SysFont("Arial", 38)
    text_surface = font.render(f"level {map_index}", True, (255, 255, 255))
    transparent_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA) 
    transparent_surface.blit(text_surface, (0, 0))

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        draw_buttons(mouse_pos, mouse_pressed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_mute_rect.collidepoint(event.pos):
                    flag= not(flag)
                elif btn_exit_rect.collidepoint(event.pos):
                    menu()
                    running=False
                for label, rect in button_rects:
                    if rect.collidepoint(event.pos):
                        game_play(map_index, label)
                        running=False
        if flag:
            pygame.mixer.music.set_volume(0.3)
            btn_mute1=btn_mute
        else:
            pygame.mixer.music.set_volume(0)
            btn_mute1=btn_not_mute
        screen.blit(header,(0,0))
        screen.blit(btn_exit,(0,0))
        screen.blit(btn_mute1,(279,0))
        screen.blit(transparent_surface, (80, 5))
        pygame.display.flip()
                    
def menu():
    global flag
    back_groud=pygame.transform.smoothscale(pygame.image.load(r'assets\images\bglevel-sheet0.png').convert_alpha(),(339,600))
    font_img = pygame.transform.smoothscale(pygame.image.load(r'assets\images\spritefont.png').convert_alpha(),(160,160))
    btn_level1= pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnlevel-sheet1.png').convert_alpha(),(90,90))
    btn_level2= pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnlevel-sheet0.png').convert_alpha(),(95,95))
    btn_exit=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnback-sheet0.png').convert_alpha(),(60,60))
    btn_mute=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnsound-sheet0.png').convert_alpha(),(60,60))
    btn_not_mute=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnsound-sheet1.png').convert_alpha(),(60,60))
    header=pygame.transform.smoothscale(pygame.image.load(r'assets\images\header-sheet0.png').convert_alpha(),(339,60))
    lvl_1_rect=btn_level1.get_rect(topleft=(25,150))
    lvl_2_rect=btn_level1.get_rect(topleft=(125,150))
    lvl_3_rect=btn_level1.get_rect(topleft=(225,150))
    lvl_4_rect=btn_level1.get_rect(topleft=(25,250))
    lvl_5_rect=btn_level1.get_rect(topleft=(125,250))
    lvl_6_rect=btn_level1.get_rect(topleft=(225,250))
    lvl_7_rect=btn_level1.get_rect(topleft=(25,350))
    lvl_8_rect=btn_level1.get_rect(topleft=(125,350))
    lvl_9_rect=btn_level1.get_rect(topleft=(225,350))
    lvl_10_rect=btn_level1.get_rect(topleft=(25,450))
    lvl_11_rect=btn_level1.get_rect(topleft=(125,450))
    lvl_12_rect=btn_level1.get_rect(topleft=(225,450))
    btn_exit_rect=btn_exit.get_rect(topleft=(0,0))
    btn_mute_rect=btn_mute.get_rect(topleft=(279,0))

    chars = "01234" + "56789" + "/"
    char_width = 29  
    char_height = 45 

    font_sprites = {}
    for index, char in enumerate(chars):
        x = (index % 5) * char_width
        y = (index // 5) * char_height
        rect = pygame.Rect(x, y, char_width, char_height)
        font_sprites[char] = font_img.subsurface(rect)

    def draw_text(text, pos):
        x, y = pos
        for char in text:
            if char in font_sprites:
                screen.blit(font_sprites[char], (x, y))
                x += char_width + 2 
    running=True
    pygame.mixer.music.load("assets\soud\mattoglseby - 2.ogv")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)
    # Màu sắc
    WHITE = (255, 255, 255)
    BUTTON_COLOR = (70, 130, 180)       # Xanh dương nhạt
    SHADOW_COLOR = (50, 100, 150)       # Bóng đậm hơn
    TEXT_COLOR = (255, 255, 255)

    # Font
    font = pygame.font.SysFont("Arial", 32, bold=True)

    # Nút (tọa độ, kích thước)
    button_rect = pygame.Rect(76, 80, 200, 60)
    shadow_offset = 4

    while running:
        level_rects = [
            lvl_1_rect, lvl_2_rect, lvl_3_rect, lvl_4_rect,
            lvl_5_rect, lvl_6_rect, lvl_7_rect, lvl_8_rect,
            lvl_9_rect, lvl_10_rect, lvl_11_rect, lvl_12_rect
        ]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_mute_rect.collidepoint(event.pos):
                    flag= not(flag)
                elif btn_exit_rect.collidepoint(event.pos):
                    waiting_hall()
                    running=False
                else:
                    for i, rect in enumerate(level_rects):
                        if rect.collidepoint(event.pos):
                            AI_Algorithms(i+1)
                            running=False

        if flag:
            pygame.mixer.music.set_volume(0.3)
            btn_mute1=btn_mute
        else:
            pygame.mixer.music.set_volume(0)
            btn_mute1=btn_not_mute
        screen.blit(back_groud,(0,0))
        screen.blit(header,(0,0))
        screen.blit(btn_exit,(0,0))
        screen.blit(btn_mute1,(279,0))
        mouse_pos = pygame.mouse.get_pos()
        for rect in level_rects:
            if rect.collidepoint(mouse_pos):
                screen.blit(btn_level2, rect.topleft)
            else:
                screen.blit(btn_level1, rect.topleft)

        draw_text("1",(55,172))
        draw_text("2",(155,172))
        draw_text("3",(255,172))
        draw_text("4",(55,272))
        draw_text("5",(155,272))
        draw_text("6",(255,272))
        draw_text("7",(55,372))
        draw_text("8",(155,372))
        draw_text("9",(255,372))
        draw_text("10",(45,472))
        draw_text("11",(145,472))
        draw_text("12",(245,472))

        # Vẽ bóng nút
        shadow_rect = button_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=12)

        # Vẽ nút chính
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect, border_radius=12)

        # Vẽ chữ
        text_surf = font.render("LEVEL SELECT", True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)

        pygame.display.flip()
        # clock.tick(60)

def data():
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    LIGHT_BLUE = (100, 100, 255)
    LIGHT_GREEN = (100, 255, 100)

    # Kích thước nút
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 30

    def draw_buttons(mouse_pos, mouse_pressed):
        font = pygame.font.Font(None, 20)
        
        for i in range(12):
            # Kiểm tra vị trí chuột để thay đổi màu khi rê chuột hoặc nhấn
            if 50 <= mouse_pos[0] <= 50 + BUTTON_WIDTH and 50 + i * (BUTTON_HEIGHT + 10) <= mouse_pos[1] <= 50 + i * (BUTTON_HEIGHT + 10) + BUTTON_HEIGHT:
                button_color = LIGHT_BLUE if not mouse_pressed else BLUE  # Màu khi rê chuột hoặc nhấn
            else:
                button_color = BLUE
            
            # Vẽ nút với bo góc và hiệu ứng gradient
            pygame.draw.rect(screen, button_color, (50, 50 + i * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT), border_radius=15)
            text = font.render(f"Level {i + 1}", True, WHITE)
            screen.blit(text, (50 + 30, 50 + i * (BUTTON_HEIGHT + 10) + 10))
        
        # Vẽ nút tổng hợp (Level 13)
        if 50 <= mouse_pos[0] <= 50 + BUTTON_WIDTH and 50 + 12 * (BUTTON_HEIGHT + 10) <= mouse_pos[1] <= 50 + 12 * (BUTTON_HEIGHT + 10) + BUTTON_HEIGHT:
            button_color = LIGHT_GREEN if not mouse_pressed else GREEN  # Màu khi rê chuột hoặc nhấn
        else:
            button_color = GREEN
        
        # Vẽ nút tổng hợp
        pygame.draw.rect(screen, button_color, (50, 50 + 12 * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT), border_radius=15)
        text = font.render("All in", True, WHITE)
        screen.blit(text, (50 + 30, 50 + 12 * (BUTTON_HEIGHT + 10) + 10))

    running = True
    mouse_pressed = False  # Biến theo dõi việc nhấn chuột
    while running:
        screen.fill(WHITE)  # Màu nền cửa sổ
        mouse_pos = pygame.mouse.get_pos()  # Lấy vị trí chuột
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pressed = True  # Khi nhấn chuột
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_pressed = False  # Khi thả chuột
            
        draw_buttons(mouse_pos, mouse_pressed)  # Vẽ các nút
        
        # Kiểm tra các sự kiện nhấn chuột để thực thi hành động
        if mouse_pressed:
            for i in range(12):
                if 50 <= mouse_pos[0] <= 50 + BUTTON_WIDTH and 50 + i * (BUTTON_HEIGHT + 10) <= mouse_pos[1] <= 50 + i * (BUTTON_HEIGHT + 10) + BUTTON_HEIGHT:
                    map_file = f"map{i + 1}"
                    plot_data(map_file)
            
            # Kiểm tra nút tổng hợp (Level 13)
            if 50 <= mouse_pos[0] <= 50 + BUTTON_WIDTH and 50 + 12 * (BUTTON_HEIGHT + 10) <= mouse_pos[1] <= 50 + 12 * (BUTTON_HEIGHT + 10) + BUTTON_HEIGHT:
                plot_all_maps()

        pygame.display.flip()  # Cập nhật cửa sổ

def waiting_hall():
    login1=pygame.transform.smoothscale(pygame.image.load(r'assets\images\bgm-sheet0.png').convert_alpha(),(339,600))
    login2=pygame.transform.smoothscale(pygame.image.load(r'assets\images\gametitle-sheet0.png').convert_alpha(),(339,200))
    btn_play=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnplay-sheet0.png').convert_alpha(),(174,58))
    btn_data=pygame.transform.smoothscale(pygame.image.load(r'assets\images\btnundo-sheet0.png').convert_alpha(),(50,50))
    btn_data_rect=btn_data.get_rect(topleft=(0,0))
    btn_play_rect = btn_play.get_rect(topleft=(83, 271))
    running=True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_play_rect.collidepoint(event.pos):
                    menu()
                    running=False
                if btn_data_rect.collidepoint(event.pos):
                    data()

        screen.blit(login1,(0,0))
        screen.blit(login2,(0,0))
        screen.blit(btn_play,(83,271))
        screen.blit(btn_data, btn_data_rect.topleft)
        
        pygame.display.flip()

waiting_hall()


    

