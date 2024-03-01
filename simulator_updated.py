from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QCheckBox, QHBoxLayout, QButtonGroup
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PyQt6.QtCore import QPoint, Qt
import numpy as np
from PIL import Image
import traceback
import os
import time
from collections import deque
from heapq import heapify, heappop, heappush

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

class AlgorithmSimulator(QWidget):
    # set window dimensions
    def __init__(self):
        super().__init__()
        
        self.window_x = 100
        self.window_y = 100
        self.window_width = 300
        self.window_height = 400
        self.setWindowTitle("Path-planning algorithm Simulator")
        self.setGeometry(100, 100, 300, 400)

        self.init_ui()

    # populate window with buttons and grid
    def init_ui(self):
        layout = QVBoxLayout()

        # Create and add a label for selecting algorithms
        algorithm_label = QLabel("Select Algorithm to run:")
        layout.addWidget(algorithm_label)

        # Create and add a dropdown menu for selecting algorithms
        self.algorithm_combobox = QComboBox()
        algorithms = ["A*", "Dijkstra's", "D*"] 
        self.algorithm_combobox.addItems(algorithms)
        layout.addWidget(self.algorithm_combobox)

        # Create a paint interface to draw the map
        self.map_width, self.map_height = 40, 40
        self.scale = 10
        self.map_label = QLabel("Map Canvas")
        self.map_canvas = QPixmap(self.map_width, self.map_height)
        size = self.map_canvas.size()
        self.map_canvas_scaled = self.map_canvas.scaled(self.scale * size)
        self.map_label.setPixmap(self.map_canvas_scaled)
        self.map_canvas_scaled.fill(Qt.GlobalColor.white)
        layout.addWidget(self.map_label)
        self.draw_grid()
        self.add_mapelements()

        self.dist_metric = None
        checkbox_layout = QHBoxLayout()
        self.manhattan_checkbox = QCheckBox("Manhattan Distance", self)
        self.euclidean_checbox = QCheckBox("Euclidean Distance", self)
        metric_buttongroup = QButtonGroup(self)
        metric_buttongroup.addButton(self.manhattan_checkbox)
        metric_buttongroup.addButton(self.euclidean_checbox)
        checkbox_layout.addWidget(self.manhattan_checkbox)
        checkbox_layout.addWidget(self.euclidean_checbox)
        layout.addLayout(checkbox_layout)
        self.manhattan_checkbox.toggled.connect(self.set_metric)
        self.euclidean_checbox.toggled.connect(self.set_metric)

        # Create and add a button to simulate the selected algorithm
        simulate_button = QPushButton("Simulate")
        simulate_button.clicked.connect(self.simulate_algorithm)
        layout.addWidget(simulate_button)

        # add button to randomize the gridw
        randomize_button = QPushButton("Randomize map")
        randomize_button.clicked.connect(self.add_mapelements)
        layout.addWidget(randomize_button)

        self.setLayout(layout)        

    def set_metric(self):
        if self.manhattan_checkbox.isChecked():
            self.dist_metric = "manhattan"
        if self.euclidean_checbox.isChecked():
            self.dist_metric = "euclidean"
        print(self.dist_metric)

    def join_pixmaps(self, pixmap_1, pixmap_2, mode=QPainter.CompositionMode.CompositionMode_SourceOver):
        # s = pixmap_1.size().expandedTo(pixmap_2.size())
        result = QPixmap(pixmap_1.size())
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(QPoint(), pixmap_1)
        painter.setCompositionMode(mode)
        painter.drawPixmap(result.rect(), pixmap_2, pixmap_2.rect())
        painter.end()
        return result

    def draw_grid(self):
        self.map_canvas_scaled.fill(Qt.GlobalColor.white)
        painter = QPainter(self.map_canvas_scaled)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen_color = QColor(200, 200, 200)
        painter.setPen(pen_color)

        pixel_size = 10

        for x in range(0, self.map_width * self.scale, pixel_size):
            for y in range(0, self.map_height * self.scale, pixel_size):
                painter.drawRect(x, y, pixel_size, pixel_size)

        self.map_label.setPixmap(self.map_canvas_scaled)

        painter.end()

    def add_mapelements(self):
        self.grid_as_array = np.zeros((self.map_width, self.map_height))
        map_canvas = QPixmap(self.map_width, self.map_height)
        map_canvas.fill(Qt.GlobalColor.transparent)
        self.painter = QPainter(map_canvas)
        self.start_point = (np.random.randint(low=0, high=self.map_width), 
                            np.random.randint(low=0, high=self.map_height))
        self.goal_point = (np.random.randint(low=0, high=self.map_width), 
                           np.random.randint(low=0, high=self.map_height))
        self.grid_as_array[self.start_point[0]][self.start_point[1]] = 2
        self.grid_as_array[self.goal_point[0]][self.goal_point[1]] = 3

        obstacle_frequency = 200

        pen = QPen()
        pen.setWidth(0)
        pen.setColor(QColor('lightgreen'))
        self.painter.setPen(pen)
        self.painter.drawPoint(self.start_point[0], self.start_point[1])
        # self.painter.fillRect(self.start_point[0], self.start_point[1], 10, 10, QColor(0, 255, 0))
        
        pen.setColor(QColor('red'))
        self.painter.setPen(pen)
        # self.painter.fillRect(self.goal_point[0], self.goal_point[1], 10, 10, QColor(255, 0, 0))
        self.painter.drawPoint(self.goal_point[0], self.goal_point[1])
    
        pen.setColor(QColor('black'))
        self.painter.setPen(pen)
        for _ in range(obstacle_frequency):
            self.obstacle_point = (np.random.randint(low=0, high=self.map_width),
                                   np.random.randint(low=0, high=self.map_height))
            if self.obstacle_point != self.start_point and self.obstacle_point !=self.goal_point:
                self.painter.drawPoint(self.obstacle_point[0], self.obstacle_point[1])
                self.grid_as_array[self.obstacle_point[0]][self.obstacle_point[1]] = 1

        self.grid_as_array = self.grid_as_array.transpose()
        scaled_grid = map_canvas.scaled(self.scale * map_canvas.size())
        self.painter.end()
        final_pixmap = self.join_pixmaps(self.map_canvas_scaled, scaled_grid)
        self.map_label.setPixmap(final_pixmap)

    def simulate_algorithm(self, distance_metric):
        selected_algorithm = self.algorithm_combobox.currentText()

        try:
            if selected_algorithm == "Dijkstra's":
                print(f"[ INFO ] Simulating {selected_algorithm} algorithm.")
                self.start = (self.start_point[0], self.start_point[1])
                self.goal  = (self.goal_point[0], self.goal_point[1])
                self.heuristic = False
                self.a_star(self.grid_as_array, self.start, self.goal, self.dist_metric, self.heuristic)
            
            elif selected_algorithm == "A*":
                print(f"[ INFO ] Simulating {selected_algorithm} algorithm.")
                self.start = (self.start_point[0], self.start_point[1])
                self.goal  = (self.goal_point[0], self.goal_point[1])
                self.heuristic = True
                self.a_star(self.grid_as_array, self.start, self.goal, self.dist_metric, self.heuristic)

            elif selected_algorithm == "D*":
                print(f"[ INFO ] Simulating {selected_algorithm} algorithm.")
        except Exception as e:
            print(f"[ ERROR ] An exception occurred: {e}")
            traceback.print_exec()

    # A* algo. If heuristic=False, use Dijkstra's
    def a_star(self, grid, start, goal, dist_metric, heuristic=True):
        print("[ INFO ] Inside a* algorithm function")
        start = np.array(start) 
        goal  = np.array(goal)
        goal_found = False

        # Obtain pixmap and add transparent layer for painting the final path
        grid_path = QPixmap(self.map_width, self.map_height)
        grid_path.fill(Qt.GlobalColor.transparent)
        grid_base = self.map_label.pixmap()
        painter = QPainter(grid_path)

        # Initialize all g-scores to infinity and start node's g to 0
        # Same for f-scores, and start node's f is h
        # g-score for all cells
        gScore = [[float('infinity') for row in range(0, len(grid[0]))] for col in range(0, len(grid[0]))]
        gScore[start[0]][start[1]] = 0

        # f-score for all cells -- f = g + h
        fScore = [[float('infinity') for row in range(0, len(grid[0]))] for col in range(0, len(grid[0]))]
        fScore[start[0]][start[1]] = np.linalg.norm(start - goal)
        print("[ INFO ] g and f scores initialized...")

        # open_set = to be evaluated
        # closed_set = already evaluated
        open_set = [(fScore[start[0]][start[1]], start[0], start[1], gScore[start[0]][start[1]])]
        closed_set = []
        node_tree = {}

        # All 8 neigbours of the cell

        if dist_metric == "euclidean":
            neighbor_check = [[0, -1],
                            [-1,-1],
                            [-1, 0],
                            [-1, 1],
                            [0, 1],
                            [1, 1],
                            [1, 0],
                            [1, -1]]
        elif dist_metric == "manhattan":
            neighbor_check = [[0, -1],
                            [-1, 0],
                            [0, 1],
                            [1, 0]]

        # While open set isn't empty
        while len(open_set) != 0:
            heapify(open_set)
            current_node = heappop(open_set)
            closed_set.append(current_node)
            _, current_x, current_y, _= current_node
            current_x = current_x
            current_y = current_y

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
                # print(f"[ DEBUG ] neighbor node: {neighbor_node}")
                try:
                    # if cell is not an obstacle
                    if grid[neighbor_y][neighbor_x] != 1:
                        # if new g-score is better than neighbour's g-score
                        if temp_g < gScore[neighbor_x][neighbor_y]:
                            gScore[neighbor_x][neighbor_y] = temp_g
                            fScore[neighbor_x][neighbor_y] = temp_f
                            node_tree[neighbor_node] = current_node
                            
                            pen = QPen()
                            pen.setWidth(0)
                            pen.setColor(QColor('yellow'))
                            painter.setPen(pen)
                            painter.drawPoint(QPoint(neighbor_node[1], neighbor_node[2]))
                            grid_path_scaled = grid_path.scaled(self.scale * grid_path.size())
                            grid_pixmap = self.join_pixmaps(grid_base, grid_path_scaled)
                            self.map_label.setPixmap(grid_pixmap)
                            QApplication.processEvents()
                            time.sleep(0.005)

                            if neighbor_node not in open_set:
                                heappush(open_set, neighbor_node)
                except IndexError as idx_error:
                    # print(f"List index out of range -- out of bounds ({neighbor_x}, {neighbor_y})")
                    pass

        if goal_found == True:
            try:
                print("[ INFO ] Goal found")
                route = deque()
                route.appendleft(current_node)
                while current_node in node_tree:
                    current_node = node_tree[current_node]

                    route.appendleft(current_node)
                    pen = QPen()
                    pen.setWidth(0)
                    pen.setColor(QColor('blue'))
                    painter.setPen(pen)
                    painter.drawPoint(QPoint(current_node[1], current_node[2]))
                    grid_path_scaled = grid_path.scaled(self.scale * grid_path.size())
                    grid_pixmap = self.join_pixmaps(self.map_label.pixmap(), grid_path_scaled)
                    self.map_label.setPixmap(grid_pixmap)
                    QApplication.processEvents()
                    time.sleep(0.001)
            except Exception as e:
                print(e)

        else:
            print("There is no path from start to goal :(")
            
        painter.end()  


if __name__ == "__main__":
    app = QApplication([])
    window = AlgorithmSimulator()
    window.show()
    app.exec()
