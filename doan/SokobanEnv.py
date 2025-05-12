import numpy as np
import random
from move_by_AI import AI

class SokobanEnv:
    def __init__(self, ai: AI):
        self.ai = ai
        self.reset()

    def reset(self):
        self.map = self.ai.copy_map(self.ai.map)
        self.s_pos = self.ai.player_pos
        self.done = False
        return self._get_state()

    def _get_state(self):
        box_positions = [(i, j) for i in range(self.ai.rows) for j in range(self.ai.cols) if self.map[i][j] == 'b']
        return (self.s_pos, tuple(sorted(box_positions))) 
    def step(self, action):
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = moves[action]

        old_boxes_on_goal = sum(1 for b in self.ai.goals if self.map[b[0]][b[1]] == 'b')

        result = self.ai._try_move(self.map, self.s_pos, dx, dy)
        if result is None:
            return self._get_state(), -1, False

        self.map, self.s_pos = result

        new_boxes_on_goal = sum(1 for b in self.ai.goals if self.map[b[0]][b[1]] == 'b')

        reward = (new_boxes_on_goal - old_boxes_on_goal) * 1.0

        if self.ai.is_finished(self.map):
            return self._get_state(), reward + 10, True

        return self._get_state(), reward - 0.1, False

    def render(self):
        for row in self.map:
            print(''.join(row))
        print()
