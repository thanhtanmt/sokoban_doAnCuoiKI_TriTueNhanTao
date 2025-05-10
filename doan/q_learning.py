import numpy as np
import random

def q_learning(env, episodes=1000, alpha=0.1, gamma=0.9, epsilon=0.1):
    """
    env: môi trường Sokoban (bạn phải tự định nghĩa theo chuẩn Gym)
    alpha: learning rate
    gamma: discount factor
    epsilon: xác suất chọn hành động ngẫu nhiên (exploration)
    """
    # Q-table: lưu giá trị Q cho mỗi (state, action)
    q_table = {}  # {(state_tuple): [Q_up, Q_down, Q_left, Q_right]}

    for ep in range(episodes):
        state = env.reset()  # bạn phải trả về 1 tuple đại diện cho trạng thái
        done = False

        while not done:
            state_key = tuple(state)  # giả sử state là 1 vector

            if state_key not in q_table:
                q_table[state_key] = [0, 0, 0, 0]  # 4 hành động

            # Chọn hành động theo epsilon-greedy
            if random.uniform(0, 1) < epsilon:
                action = random.randint(0, 3)  # khám phá
            else:
                action = np.argmax(q_table[state_key])  # khai thác

            next_state, reward, done = env.step(action)
            next_key = tuple(next_state)

            if next_key not in q_table:
                q_table[next_key] = [0, 0, 0, 0]

            # Q-learning update rule
            best_next_q = max(q_table[next_key])
            q_table[state_key][action] += alpha * (reward + gamma * best_next_q - q_table[state_key][action])

            state = next_state

        if (ep + 1) % 100 == 0:
            print(f"Episode {ep + 1} done")

    return q_table
