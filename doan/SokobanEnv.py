import numpy as np
import random
from move_by_AI import AI

class SokobanEnv:
    def __init__(self, ai: AI):
        self.ai = ai
        self.reset()

    def reset(self):
        # Reset lại bản đồ gốc
        self.map = self.ai.copy_map(self.ai.map)
        self.s_pos = self.ai.player_pos
        self.done = False
        return self._get_state()

    def _get_state(self):
        # Bạn có thể trích xuất thông tin gọn hơn để giảm không gian trạng thái
        # Ở đây ta mã hóa bằng vị trí người + vị trí hộp
        box_positions = [(i, j) for i in range(self.ai.rows) for j in range(self.ai.cols) if self.map[i][j] == 'b']
        return (self.s_pos, tuple(sorted(box_positions)))

    def step(self, action):
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # UP, DOWN, LEFT, RIGHT
        dx, dy = moves[action]

        result = self.ai._try_move(self.map, self.s_pos, dx, dy)
        if result is None:
            # Đụng tường hoặc không hợp lệ → hình phạt
            return self._get_state(), -1, False

        self.map, self.s_pos = result

        # Kiểm tra thắng
        if self.ai.is_finished(self.map):
            self.done = True
            return self._get_state(), 10, True  # Phần thưởng lớn khi hoàn thành

        # Bước hợp lệ nhưng chưa xong
        return self._get_state(), -0.1, False  # Phạt nhẹ để khuyến khích kết thúc nhanh

    def render(self):
        # Hiển thị map (nếu bạn muốn gắn vào pygame hoặc in ra terminal)
        for row in self.map:
            print(''.join(row))
        print()
