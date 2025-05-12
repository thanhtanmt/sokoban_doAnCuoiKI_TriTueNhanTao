import csv
import os

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
save_algorithm_result('result.csv', 'BFS', 0.045, 210, 25)
