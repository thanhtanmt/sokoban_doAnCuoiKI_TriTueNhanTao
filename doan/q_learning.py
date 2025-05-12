import numpy as np
import random

def q_learning(env, episodes=100, alpha=0.1, gamma=0.9, epsilon=1.0):
    q_table = {}  # {(state_tuple): [Q_up, Q_down, Q_left, Q_right]}

    for ep in range(episodes):
        state = env.reset() 
        done = False

        while not done:
            state_key = tuple(state)  

            if state_key not in q_table:
                q_table[state_key] = [0, 0, 0, 0]  

            if random.uniform(0, 1) < epsilon:
                action = random.randint(0, 3) 
            else:
                action = np.argmax(q_table[state_key]) 

            next_state, reward, done = env.step(action)
            next_key = tuple(next_state)

            if next_key not in q_table:
                q_table[next_key] = [0, 0, 0, 0]

            # Q-learning update rule
            best_next_q = max(q_table[next_key])
            q_table[state_key][action] += alpha * (reward + gamma * best_next_q - q_table[state_key][action])

            state = next_state

        # Giảm epsilon dần theo số episodes
        epsilon = max(0.1, 1.0 - ep / episodes)

        if (ep + 1) % 100 == 0:
            print(f"Episode {ep + 1} done")

    return q_table
