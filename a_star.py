import pygame
import time
import math
from collections import deque

# h - Euclidean distance from current to goal
def h(current_x, current_y, goal_x, goal_y):
    return math.sqrt(((current_x - goal_x)**2) + ((current_y - goal_y)**2))

# g - Euclidean distance from start to current
def g(current_x, current_y, start_x, start_y):
    return math.sqrt(((current_x - start_x)**2) + ((current_y - start_y)**2))

# A* algo. If heuristic=False, use Dijkstra's
def a_star(grid, start, goal, surface, palette, heuristic=True):
    goal_found = False
    visual = True
    blue, black, yellow = palette

    # g-score for all cells
    gScore = [[float('infinity') for row in range(len(grid[0]))] for col in range(len(grid))]
    print(len(gScore[0]), len(gScore))
    gScore[start[0]][start[1]] = 0

    # f-score for all cells -- f = g + h
    fScore = [[float('infinity') for row in range(len(grid[0]))] for col in range(len(grid))]
    fScore[start[0]][start[1]] = h(start[0], start[1], goal[0], goal[1])

    # open_set = to be evaluated
    # closed_set = already evaluated
    open_set = [(start[0], start[1], fScore[start[0]][start[1]], gScore[start[0]][start[1]])]
    closed_set = []
    node_tree = {}

    # All 8 neigbours of the cell
    neighbor_check = [[0, -1],
                    #[-1, -1],
                    [-1, 0],
                    #[-1, 1],
                    [0, 1],
                    #[1, 1],
                    [1, 0]]
                    #[1, -1]]

    while len(open_set) != 0:
        open_set.sort(key = lambda tup: tup[2], reverse = True)
        current_node = open_set.pop()
        closed_set.append(current_node)
        current_x, current_y, _, _ = current_node

        # If you're on the goal
        if current_x == goal[0] and current_y == goal[1]:
            goal_found = True
            break

        for i in neighbor_check:
            neighbor_x = current_x + i[0]
            neighbor_y = current_y + i[1]
            temp_g = g(neighbor_x, neighbor_y, start[0], start[1])
            if heuristic:
                temp_f = temp_g + h(neighbor_x, neighbor_y, goal[0], goal[1])
            else:
                temp_f = temp_g
            neighbor_node = (neighbor_x, neighbor_y, temp_f, temp_g)
            try:
                # if cell is not an obstacle
                if grid[neighbor_y][neighbor_x] != 1:
                    # if cell is not evaluated already
                    if neighbor_node not in closed_set:
                        # if new g-score is better than neighbour's g-score
                        if temp_g < gScore[neighbor_x][neighbor_y]:
                            gScore[neighbor_x][neighbor_y] = temp_g
                            fScore[neighbor_x][neighbor_y] = temp_f
                            node_tree[neighbor_node] = current_node
                            if visual == True:
                                pygame.draw.rect(surface, yellow, (neighbor_x * 10, (neighbor_y * 10) + 50, 10, 10))
                                pygame.draw.rect(surface, black, (neighbor_x * 10, (neighbor_y * 10) + 50, 10, 10), 1)
                                time.sleep(0.001)
                                pygame.display.update()
                            if neighbor_node not in open_set:
                                open_set.append(neighbor_node)
            except IndexError as idx_error:
                # print(f"List index out of range -- out of bounds ({neighbor_x}, {neighbor_y})")
                pass

    if goal_found == True:
        route = deque()
        route.appendleft(current_node)
        while current_node in node_tree:
            current_node = node_tree[current_node]
            route.appendleft(current_node)
            pygame.draw.rect(surface, blue, (current_node[0] * 10, (current_node[1] * 10) + 50, 10, 10))
            pygame.draw.rect(surface, black, (current_node[0] * 10, (current_node[1] * 10) + 50, 10, 10), 1)
            time.sleep(0.001)
            pygame.display.update()

        time.sleep(5)

    else:
        print("There is no path from start to goal :(")