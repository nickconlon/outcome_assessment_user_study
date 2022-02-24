import numpy as np
import matplotlib.pyplot as plt

def display_map(map_path):
    map = np.zeros([7,30,3])+5
    with open(map_path) as file:
        for y, line in enumerate(file.readlines()):
            for x, c in enumerate(line):
                if c == 'o':
                    map[y,x] =[0.5,0.5,0.5]#obstacle
                if c == 'g':
                    map[y,x] =[0,0,1]#randomizers.append([x, y])
                if c == 'd':
                    map[y,x] =[0,0,0]#dangers.append([x, y])
                if c == 'r':
                    map[y,x] =[0,0,1]#subgoal = [x, y]
                if c == 'G':
                    map[y,x] =[0,1,0]
                if c == 'a':
                    map[y,x] =[1,1,0]
    return map

if __name__ == "__main__":

    m = display_map('../flaskr/maps/level_3/map0.txt')
    print(m)
    plt.axes().set_aspect('equal')
    plt.imshow(m)
    plt.show()