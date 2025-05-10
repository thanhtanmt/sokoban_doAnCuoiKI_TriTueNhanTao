import ast

def read_file(path_file):
    with open(path_file, "r") as f:
        content = f.read()
    
    blocks = content.split(';')
    lists = [ast.literal_eval(block.strip()) for block in blocks if block.strip()]
    return lists
