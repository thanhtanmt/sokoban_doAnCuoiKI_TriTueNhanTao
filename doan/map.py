import pygame
from read_file_map import read_file as rd

class Map1:
    def __init__(self, floor_image, wall_image, sokuban_down, sokoban_up, sokoban_right, sokoban_left, box_image, goal_image,box_at_goal_image, map_select,a,b):
        path_file=f'map\map{map_select}.txt'
        lists=rd(path_file)
        self.map1= lists[0]
        self.list_box_map1 = lists[1]
        self.list_box_map1_rect=lists[2]
        self.s_side_map1 =lists[3]
        self.s_side_map1_rect = lists[4]      
        self.last_move_time = pygame.time.get_ticks()
        self.floor_image = floor_image
        self.wall_image = wall_image
        self.sokuban_image = sokuban_down
        self.sokoban_down=sokuban_down
        self.sokoban_up=sokoban_up
        self.sokoban_right=sokoban_right
        self.sokoban_left=sokoban_left
        self.box_image = box_image
        self.box_at_goal_image=box_at_goal_image
        self.goal_image = goal_image
        self.a=a
        self.b=b

    def draw_map(self, screen):
        side_y=self.b
        for row in self.map1:
            side_x = self.a
            for cell in row:
                if cell == 'w':
                    screen.blit(self.wall_image, (side_x, side_y))
                elif cell == 'g':
                    screen.blit(self.floor_image, (side_x, side_y))
                    screen.blit(self.goal_image, (side_x+6, side_y+6))
                elif cell == 'f':
                    screen.blit(self.floor_image, (side_x, side_y))
                side_x += 40
            side_y += 40
            index=0
        for box_rect in self.list_box_map1_rect:
            if (self.map1[self.list_box_map1[index][1]][self.list_box_map1[index][0]]=="g"):
                screen.blit(self.box_at_goal_image, (box_rect[0] + self.a, box_rect[1] + self.b))
            else:
                screen.blit(self.box_image, (box_rect[0] + self.a, box_rect[1] + self.b))
            index+=1

        screen.blit(self.sokuban_image, (self.s_side_map1_rect[0]+self.a, self.s_side_map1_rect[1]+self.b))

    def can_move_to(self, x, y):
        if 0 <= y < len(self.map1) and 0 <= x < len(self.map1[0]):
            # return self.map1[x][y] != 'w'
            return self.map1[y][x] != 'w'
        return False

    def is_box_at(self, x, y): 
        return [x, y] in self.list_box_map1
    
    def is_finished(self):
        self.list_box_map1
        for i in range(len(self.map1)):
            for j in range(len(self.map1[i])):
                if self.map1[i][j]=='g':
                    if [j,i] not in self.list_box_map1:
                        return False
                        
        return True

    def move_up(self, current_time):
        if current_time - self.last_move_time < 200:
            return
        
        self.sokuban_image=self.sokoban_up
        x, y = self.s_side_map1
        new_x, new_y = x, y - 1

        if not self.can_move_to(new_x, new_y):
            return

        if self.is_box_at(new_x, new_y):
            box_new_x, box_new_y = new_x, new_y - 1
            if self.can_move_to(box_new_x, box_new_y) and not self.is_box_at(box_new_x, box_new_y):
                idx = self.list_box_map1.index([new_x, new_y])
                self.list_box_map1[idx] = [box_new_x, box_new_y]
                self.list_box_map1_rect[idx][1] -= 40
            else:
                return 
        self.s_side_map1 = [new_x, new_y]
        self.s_side_map1_rect[1] -= 40
        self.last_move_time = current_time

    def move_down(self, current_time):
        if current_time - self.last_move_time < 200:
            return

        self.sokuban_image=self.sokoban_down
        x, y = self.s_side_map1
        new_x, new_y = x, y + 1

        if not self.can_move_to(new_x, new_y):
            return

        if self.is_box_at(new_x, new_y):
            box_new_x, box_new_y = new_x, new_y + 1
            if self.can_move_to(box_new_x, box_new_y) and not self.is_box_at(box_new_x, box_new_y):
                idx = self.list_box_map1.index([new_x, new_y])
                self.list_box_map1[idx] = [box_new_x, box_new_y]
                self.list_box_map1_rect[idx][1] += 40
            else:
                return
        self.s_side_map1 = [new_x, new_y]
        self.s_side_map1_rect[1] += 40
        self.last_move_time = current_time

    def move_left(self, current_time):
        if current_time - self.last_move_time < 200:
            return

        self.sokuban_image=self.sokoban_left
        x, y = self.s_side_map1
        new_x, new_y = x - 1, y

        if not self.can_move_to(new_x, new_y):
            return

        if self.is_box_at(new_x, new_y):
            box_new_x, box_new_y = new_x - 1, new_y
            if self.can_move_to(box_new_x, box_new_y) and not self.is_box_at(box_new_x, box_new_y):
                idx = self.list_box_map1.index([new_x, new_y])
                self.list_box_map1[idx] = [box_new_x, box_new_y]
                self.list_box_map1_rect[idx][0] -= 40
            else:
                return
        
        self.s_side_map1 = [new_x, new_y]
        self.s_side_map1_rect[0] -= 40
        self.last_move_time = current_time

    def move_right(self, current_time):
        if current_time - self.last_move_time < 200:
            return
        
        self.sokuban_image=self.sokoban_right

        x, y = self.s_side_map1
        new_x, new_y = x + 1, y

        if not self.can_move_to(new_x, new_y):
            return

        if self.is_box_at(new_x, new_y):
            box_new_x, box_new_y = new_x + 1, new_y
            if self.can_move_to(box_new_x, box_new_y) and not self.is_box_at(box_new_x, box_new_y):
                idx = self.list_box_map1.index([new_x, new_y])
                self.list_box_map1[idx] = [box_new_x, box_new_y]
                self.list_box_map1_rect[idx][0] += 40
            else:
                return
        self.s_side_map1 = [new_x, new_y]
        self.s_side_map1_rect[0] += 40
        self.last_move_time = current_time