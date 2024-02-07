from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import QPoint, Qt
import numpy as np
import traceback
from collections import deque
from heapq import heapify, heappop, heappush

class AlgorithmSimulator(QWidget):
    def __init__(self):
        super().__init__()
        
        self.window_x = 100
        self.window_y = 100
        self.window_width = 300
        self.window_height
        self.setWindowTitle("Path-planning algorithm Simulator")
        self.setGeometry(100, 100, 300, 400)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create and add a label for selecting algorithms
        algorithm_label = QLabel("Select Algorithm to run:")
        layout.addWidget(algorithm_label)

        # Create and add a dropdown menu for selecting algorithms
        self.algorithm_combobox = QComboBox()
        algorithms = ["Dijkstra's", "A*", "D*"]  # Add your algorithms here
        self.algorithm_combobox.addItems(algorithms)
        layout.addWidget(self.algorithm_combobox)

        # Create a paint interface to draw the map
        self.map_width, self.map_height = 400, 400
        self.map_label = QLabel("Map Canvas")
        self.map_canvas = QPixmap(self.map_width, self.map_height)
        self.map_canvas.fill(Qt.GlobalColor.white)
        self.map_label.setPixmap(self.map_canvas)
        layout.addWidget(self.map_label)
        self.add_mapelements()

        # Create and add a button to simulate the selected algorithm
        simulate_button = QPushButton("Simulate")
        simulate_button.clicked.connect(self.simulate_algorithm)
        layout.addWidget(simulate_button)

        randomize_button = QPushButton("Randomize map")
        randomize_button.clicked.connect(self.add_mapelements)
        layout.addWidget(randomize_button)

        self.setLayout(layout)

    def add_mapelements(self):
        self.map_canvas = self.map_label.pixmap()
        self.painter = QPainter(self.map_canvas)
        self.start_point = QPoint(np.random.randint(10, self.map_width - 10), 
                                  np.random.randint(10, self.map_height - 10))
        self.goal_point = QPoint(np.random.randint(10, self.map_width - 10), 
                                 np.random.randint(10, self.map_width - 10))
        how_many_obs_points = np.random.randint(15)
        self.obstacle_points = [QPoint(np.random.randint(10, self.map_width - 10), 
                                       np.random.randint(10, self.map_width - 10)) for point in range(how_many_obs_points)]

        self.map_canvas.fill(Qt.GlobalColor.white)

        pen = QPen()
        pen.setWidth(6)
        pen.setColor(QColor('green'))
        self.painter.setPen(pen)
        self.painter.drawPoint(self.start_point)
        
        pen.setColor(QColor('red'))
        self.painter.setPen(pen)
        self.painter.drawPoint(self.goal_point)
    
        pen.setColor(QColor('black'))
        self.painter.setPen(pen)
        self.painter.drawLines(self.obstacle_points)
        self.map_label.setPixmap(self.map_canvas)
        self.painter.end()

    def simulate_algorithm(self):
        selected_algorithm = self.algorithm_combobox.currentText()
        try:
            self.grid_matrix = self.map_canvas.toImage()
            image = []
            width, height = self.grid_matrix.width(), self.grid_matrix.height()
            for y in range(height):
                row = []
                for x in range(width):
                    pixel = self.grid_matrix.pixelColor(x, y).lightness()
                    row.append(pixel)
                image.append(row)

            image = np.array(image)
            image[image == 0] = 1
            image[image == 255] = 0

            if selected_algorithm == "Dijkstra's":
                print(f"Simulating {selected_algorithm} algorithm.")
                self.grid = image
                self.start = int(self.start_point.x()), int(self.start_point.y())
                self.goal  = int(self.goal_point.x()), int(self.goal_point.y())
                self.heuristic = False
                self.a_star(self.grid, self.start, self.goal, self.heuristic)
            
            elif selected_algorithm == "A*":
                print(f"Simulating {selected_algorithm} algorithm.")
                self.grid = image
                self.start = int(self.start_point.x()), int(self.start_point.y())
                self.goal  = int(self.goal_point.x()), int(self.goal_point.y())
                self.heuristic = True
                self.a_star(self.grid, self.start, self.goal, self.heuristic)

            elif selected_algorithm == "D*":
                print(f"Simulating {selected_algorithm} algorithm.")
        except Exception as e:
            print(f"An exception occurred: {e}")
            traceback.print_exec()

    # A* algo. If heuristic=False, use Dijkstra's
    def a_star(self, grid, start, goal, heuristic=True):
        start = np.array(start)
        goal  = np.array(goal)
        goal_found = False

        # Obtain pixmap and add transparent layer for painting the final path
        self.map_canvas = self.map_label.pixmap()
        self.painter = QPainter(self.map_canvas)
        self.map_canvas.fill(Qt.GlobalColor.transparent)

        # Initialize all g-scores to infinity and start node's g to 0
        # Same for f-scores, and start node's f is h
        # g-score for all cells
        gScore = [[float('infinity') for row in range(len(grid[0]))] for col in range(len(grid))]
        gScore[start[0]][start[1]] = 0

        # f-score for all cells -- f = g + h
        fScore = [[float('infinity') for row in range(len(grid[0]))] for col in range(len(grid))]
        fScore[start[0]][start[1]] = np.linalg.norm(start - goal)

        # open_set = to be evaluated
        # closed_set = already evaluated
        # open_set = [(start[0], start[1], fScore[start[0]][start[1]], gScore[start[0]][start[1]])]
        open_set = [(fScore[start[0]][start[1]], start[0], start[1], gScore[start[0]][start[1]])]
        closed_set = []
        node_tree = {}

        # All 8 neigbours of the cell
        neighbor_check = [[0, -1],
                          [-1,-1],
                          [-1, 0],
                          [-1, 1],
                          [0, 1],
                          [1, 1],
                          [1, 0],
                          [1, -1]]

        # While open set isn't empty
        while len(open_set) != 0:
            heapify(open_set)
            current_node = heappop(open_set)
            closed_set.append(current_node)
            _, current_x, current_y, _= current_node

            # If you're on the goal
            if current_x == goal[0] and current_y == goal[1]:
                goal_found = True
                break

            for i in neighbor_check:
                neighbor_x = current_x + i[0]
                neighbor_y = current_y + i[1]
                neighbor = np.array([neighbor_x, neighbor_y])
                current = np.array([current_x, current_y])
                temp_g = np.linalg.norm(current - start) + np.linalg.norm(current - neighbor)
                if heuristic:
                    temp_f = temp_g + np.linalg.norm(neighbor - goal)
                else:
                    temp_f = temp_g
                neighbor_node = (temp_f, neighbor_x, neighbor_y, temp_g)
                try:
                    # if cell is not an obstacle
                    if grid[neighbor_y][neighbor_x] != 1:
                        # if new g-score is better than neighbour's g-score
                        if temp_g < gScore[neighbor_x][neighbor_y]:
                            gScore[neighbor_x][neighbor_y] = temp_g
                            fScore[neighbor_x][neighbor_y] = temp_f
                            node_tree[neighbor_node] = current_node
                            
                            pen = QPen()
                            pen.setWidth(3)
                            pen.setColor(QColor('yellow'))
                            self.painter.setPen(pen)
                            self.painter.drawPoint(QPoint(neighbor_node[1], neighbor_node[2]))
                            self.map_label.setPixmap(self.map_canvas)
                            QApplication.processEvents()

                            if neighbor_node not in open_set:
                                heappush(open_set, neighbor_node)
                except IndexError as idx_error:
                    # print(f"List index out of range -- out of bounds ({neighbor_x}, {neighbor_y})")
                    pass

        if goal_found == True:
            route = deque()
            route.appendleft(current_node)
            while current_node in node_tree:
                current_node = node_tree[current_node]

                route.appendleft(current_node)
                pen = QPen()
                pen.setWidth(2)
                pen.setColor(QColor('blue'))
                self.painter.setPen(pen)
                self.painter.drawPoint(QPoint(current_node[1], current_node[2]))
                self.map_label.setPixmap(self.map_canvas)
                QApplication.processEvents()

        else:
            print("There is no path from start to goal :(")

        self.painter.end()  


if __name__ == "__main__":
    app = QApplication([])
    window = AlgorithmSimulator()
    window.show()
    app.exec()
