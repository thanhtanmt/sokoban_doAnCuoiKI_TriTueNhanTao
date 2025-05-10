import pygame
from collections import deque
# import copy
import heapq
import random
import math

class AI:
    def __init__(self, raw_map, s_pos_raw, box_pos_raw):
        self.rows = len(raw_map)
        self.cols = len(raw_map[0])
        self.map = [['0' for _ in range(self.cols)] for _ in range(self.rows)] 
        self.known_map = [['?' for _ in range(self.cols)] for _ in range(self.rows)]


        # Vị trí các đối tượng
        self.goals = []
        self.walls = []
        self.boxes = []
        self.player_pos = None

        # Duyệt map gốc để lấy goals và walls
        for i in range(self.rows):
            for j in range(self.cols):
                cell = raw_map[i][j]
                if cell == 'g':
                    self.goals.append((i, j))
                elif cell == 'w':
                    self.walls.append((i, j))

        # Cập nhật vào map
        for (i, j) in self.walls:
            self.map[i][j] = 'w'

        for (j, i) in box_pos_raw:  # input là [x, y]
            self.map[i][j] = 'b'
            self.boxes.append((i, j))

        x, y = s_pos_raw  # [x, y]
        self.map[y][x] = 's'
        self.player_pos = (y, x)

    def is_finished(self, map_data=None):
        map_data = map_data or self.map
        return all(map_data[i][j] == 'b' for (i, j) in self.goals)

    def _hash_state(self, map_data, s_pos):
        return (tuple(tuple(row) for row in map_data), s_pos)

    def _try_move(self, map_data, s_pos, dx, dy):
        new_map = self.copy_map(map_data)
        x, y = s_pos
        nx, ny = x + dx, y + dy

        if new_map[nx][ny] == 'w':
            return None

        if new_map[nx][ny] == 'b':
            bx, by = nx + dx, ny + dy
            if new_map[bx][by] in ('w', 'b'):
                return None
            new_map[bx][by] = 'b'
            new_map[nx][ny] = '0'

        new_map[x][y] = '0'
        new_map[nx][ny] = 's'
        return new_map, (nx, ny)

    def copy_map(self, m):
            return [row[:] for row in m]  # sao chép nông từng hàng (hiệu quả hơn deepcopy)
    
    # nhóm thuật toán thứ nhất chọn bfs
    def bfs(self):
        start_map = self.copy_map(self.map)
        start_pos = self.player_pos
        queue = deque([(start_map, [], start_pos)])
        visited = set()

        visited.add(self._hash_state(start_map, start_pos))

        while queue:
            current_map, path, s_pos = queue.popleft()

            if self.is_finished(current_map):
                return path

            for dx, dy, move in [(-1, 0, 'UP'), (1, 0, 'DOWN'), (0, -1, 'LEFT'), (0, 1, 'RIGHT')]:
                result = self._try_move(current_map, s_pos, dx, dy)
                if result is None:
                    continue

                new_map, new_pos = result
                state_hash = self._hash_state(new_map, new_pos)
                if state_hash not in visited:
                    visited.add(state_hash)
                    queue.append((self.copy_map(new_map), path + [move], new_pos))  # đảm bảo mỗi map là bản riêng

        return None
    # nhóm thuật toán thứ 2 chọn A*
    def A_star(self):
        start_map = self.copy_map(self.map)
        start_pos = self.player_pos
        start_h = self.heuristic(start_map)
        queue = [(start_h, 0, start_map, [], start_pos)]  # (f = g + h, g, map, path, pos)
        visited = set()

        visited.add(self._hash_state(start_map, start_pos))

        while queue:
            f, g, current_map, path, s_pos = heapq.heappop(queue)

            if self.is_finished(current_map):
                return path

            for dx, dy, move in [(-1, 0, 'UP'), (1, 0, 'DOWN'), (0, -1, 'LEFT'), (0, 1, 'RIGHT')]:
                result = self._try_move(current_map, s_pos, dx, dy)
                if result is None:
                    continue

                new_map, new_pos = result
                # if self.is_deadlock(new_map):
                #     continue

                state_hash = self._hash_state(new_map, new_pos)
                if state_hash not in visited:
                    visited.add(state_hash)
                    h = self.heuristic(new_map)
                    heapq.heappush(queue, (g + 1 + h, g + 1, self.copy_map(new_map), path + [move], new_pos))

        return None
    
    def heuristic(self, map_data):
        boxes = [(i, j) for i in range(self.rows) for j in range(self.cols) if map_data[i][j] == 'b']
        
        h = 0
        for (bi, bj) in boxes:
            min_dist = min(abs(bi - gi) + abs(bj - gj) for (gi, gj) in self.goals)
            h += min_dist
        return h
    
    #nhóm thuật toán thứ 3 local search chọn Simulated Annealing
    def evaluate(self, path):
        # Đếm số bước là đơn giản nhất
        return len(path)
    
    def mutate_path(self, path):
        if len(path) < 2:
            return path[:]
        
        new_path = path[:]
        i = random.randint(0, len(path) - 2)
        j = random.randint(i + 1, len(path) - 1)
        new_path[i], new_path[j] = new_path[j], new_path[i]
        return new_path

    def simulated_annealing(self, initial_path, max_iter=1000, T=100.0, alpha=0.99):
        current_path = initial_path
        current_score = self.evaluate(current_path)

        for _ in range(max_iter):
            new_path = self.mutate_path(current_path)
            new_score = self.evaluate(new_path)

            delta = new_score - current_score
            if delta < 0 or random.random() < math.exp(-delta / T):
                current_path = new_path
                current_score = new_score

            T *= alpha  # Giảm nhiệt độ

        return current_path
    #nhóm thuật toán thứ 4 omplex Environment chọn Partial Observation + A*
    def update_visibility(self, real_map, s_pos, vision_range=1):
        x, y = s_pos
        for dx in range(-vision_range, vision_range + 1):
            for dy in range(-vision_range, vision_range + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    self.known_map[nx][ny] = real_map[nx][ny]

    def A_star_partial(self):
        start_map = self.known_map
        start_pos = self.player_pos
        start_h = self.heuristic(start_map)
        queue = [(start_h, 0, start_map, [], start_pos)]
        visited = set()

        visited.add(self._hash_state(start_map, start_pos))

        while queue:
            f, g, current_map, path, s_pos = heapq.heappop(queue)

            if self.is_finished(current_map):
                return path

            self.update_visibility(self.map, s_pos)  # Cập nhật tầm nhìn

            for dx, dy, move in [(-1, 0, 'UP'), (1, 0, 'DOWN'), (0, -1, 'LEFT'), (0, 1, 'RIGHT')]:
                nx, ny = s_pos[0] + dx, s_pos[1] + dy

                if not (0 <= nx < self.rows and 0 <= ny < self.cols):
                    continue

                if self.known_map[nx][ny] in ('w', '?'):
                    continue

                result = self._try_move(current_map, s_pos, dx, dy)
                if result is None:
                    continue

                new_map, new_pos = result
                state_hash = self._hash_state(new_map, new_pos)
                if state_hash not in visited:
                    visited.add(state_hash)
                    h = self.heuristic(new_map)
                    heapq.heappush(queue, (g + 1 + h, g + 1, self.copy_map(new_map), path + [move], new_pos))

        return []  # Không tìm thấy đường đi
    
    # nhóm thuật toán thứ 5CSPs (Constraint Satisfaction Problems) chọn Backtracking
    def backtracking(self, current_map=None, path=None, visited=None, s_pos=None):
        if current_map is None:
            current_map = self.copy_map(self.map)
            path = []
            visited = set()
            s_pos = self.player_pos

        if self._hash_state(current_map, s_pos) in visited:
            return None

        if self.is_finished(current_map):
            return path

        visited.add(self._hash_state(current_map, s_pos))

        for dx, dy, move in [(-1, 0, 'UP'), (1, 0, 'DOWN'), (0, -1, 'LEFT'), (0, 1, 'RIGHT')]:
            result = self._try_move(current_map, s_pos, dx, dy)
            if result is None:
                continue
            new_map, new_pos = result
            
            res_path = self.backtracking(self.copy_map(new_map), path + [move], visited, new_pos)
            if res_path is not None:
                return res_path

        return None








