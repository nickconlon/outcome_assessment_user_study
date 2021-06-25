import numpy as np


def get_coordinates(index, width):
    x = int(index % width)
    y = int(index / width)
    return x, y


def get_free_spaces(fname):
    free = []
    height = 0
    width = 0
    index = 0
    with open(fname, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            height += 1
            width = len(line)
            for l in line:
                if l == '-':
                    free.append(index)
                index += 1

    return free, width, height

def recreate_map(holes, glass, obstacles, width, height, base_fname, new_fname):
    map = []
    with open(base_fname, 'r') as f:
        for line in f.readlines():
            newLine = []
            for l in line.strip():
                newLine.append(l)
            map.append(newLine)

    for i in holes:
        x, y = get_coordinates(i, width)
        map[y][x] = 'd'
    for i in glass:
        x, y = get_coordinates(i, width)
        map[y][x] = 'g'
    for i in obstacles:
        x, y = get_coordinates(i, width)
        map[y][x] = 'o'

    write_map(new_fname, map)


def write_map(fname, map):
    with open(fname, 'w') as f:
        for line in map:
            for l in line:
                f.write(l)
            f.write('\n')


def run(num_holes, num_glass, num_obstacles, fname):
    free, width, height = get_free_spaces(fname)
    holes = np.random.choice(free, size=num_holes, replace=False)
    for i in holes:
        free.remove(i)
    glass = np.random.choice(free, size=num_glass, replace=False)
    for i in glass:
        free.remove(i)
    obstacles = np.random.choice(free, size=num_obstacles, replace=False)
    for i in obstacles:
        free.remove(i)

    return holes, glass, obstacles


def test1():
    num_obstacles = 50
    num_glass = 25
    num_holes = 25
    goal = 1
    start = 1
    width = 30
    height = 7

    obstacles = np.random.randint(2, width*height-2, num_obstacles)
    glass = np.zeros(num_glass)
    holes = np.zeros(num_holes)

    i = 0
    while True:
        g = np.random.randint(1, width*height-2, 1)[0]
        if g not in obstacles:
            glass[i] = g
            i+=1
            if i == len(glass):
                break
    i = 0
    while True:
        h = np.random.randint(1, width*height-2, 1)[0]
        if h not in obstacles and h not in glass:
            holes[i] = h
            i+=1
            if i == len(holes):
                break
    print(obstacles)
    print(glass)
    print(holes)

    board = [[] for i in range(height)]
    for i in range(height):
        for j in range(width):
            board[i].append('-')
    """
    x = index % width
    y = index / width 
    """

    for o in obstacles:
        x = int(o % width)
        y = int(o / width)
        board[y][x] = 'o'
    for o in glass:
        x = int(o % width)
        y = int(o / width)
        board[y][x] = 'g'
    for o in holes:
        x = int(o % width)
        y = int(o / width)
        board[y][x] = 'h'

    board[0][0]='S'
    board[height-1][width-1]='G'

    with open('map1.txt', 'w') as f:
        for l in board:
            for c in l:
                f.write(c)
            f.write('\n')

if __name__ == "__main__":
    base_filename = "flaskr/maps/created_maps/base_map.txt"

    for i in range(20):
        new_filename = base_filename.replace("base_map.txt", "map"+str(i)+".txt")
        free, width, height = get_free_spaces(base_filename)
        holes, glass, obstacles = run(10, 10, 5, base_filename)
        recreate_map(holes, glass, obstacles, width, height, base_filename, new_filename)
