import pygame
from a_star import *

# Generate the window
class gen_env(object):
    # width - width of the grid
    # height - height of the grid
    # cell_size - size of each individual cell
    # surface_color - colour of the grid surface
    # algo_type - type of algorithm (A* or Dijkstra)
    def __init__(self, width, height, cell_size, surface_color, algo_type=None):
        self.algorithm = algo_type
        self.run = True

        self.draw_mode = False
        self.left_click = False
        self.right_click = False
        self.color = None
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.surface_color = surface_color

        self.white = (255, 255, 255)
        self.red   = (255,   0,   0)
        self.green = (  0, 255,   0)
        self.grey  = (128, 128, 128)
        self.black = (  0,   0,   0)
        self.yellow= (255, 255,   0)
        self.blue  = (  0,   0, 255)
        self.orange= (255, 165,   0)

        self.obstacle_rect = pygame.Rect(4, 4, 30, 10) 
        self.start_rect    = pygame.Rect(4, 16, 30, 10)
        self.goal_rect     = pygame.Rect(4, 28, 30, 10)
        self.astar_rect    = pygame.Rect(180, 4, 30, 10)
        self.dijkstra_rect = pygame.Rect(180, 16, 30, 10)
        self.grid = [[0 for x in range(self.width//self.cell_size)] for y in range((self.height//self.cell_size)-5)]
        self.start = None
        self.goal  = None

        self.mouse_pos = None
    def display(self):
        pygame.init()
        self.surface = pygame.display.set_mode((self.width, self.height))
        interface_font = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.surface.fill(self.white)

        pygame.draw.rect(self.surface, self.grey, self.obstacle_rect)
        text_obstacle = interface_font.render("Place Obstacles", True, (0, 0, 0))
        text_start    = interface_font.render("Place start point", True, (0, 0, 0))
        text_goal     = interface_font.render("Place goal point", True, (0, 0, 0))
        text_astar    = interface_font.render("A*", True, (0, 0, 0))
        text_dijkstra = interface_font.render("Dijkstra's", True, (0, 0, 0))

        pygame.draw.rect(self.surface, self.green, self.start_rect)
        pygame.draw.rect(self.surface, self.red, self.goal_rect)
        pygame.draw.rect(self.surface, self.grey, self.astar_rect)
        pygame.draw.rect(self.surface, self.grey, self.dijkstra_rect)

        self.surface.blit(text_obstacle, dest=(40, 4))
        self.surface.blit(text_start, dest=(40, 16))
        self.surface.blit(text_goal, dest=(40, 28))
        self.surface.blit(text_astar, dest=(214, 4))
        self.surface.blit(text_dijkstra, dest=(214, 16))

        self.draw_grid()

        while self.run == True:
            self.pick_celltype()

            for event in pygame.event.get():
                self.mouse_pos = pygame.mouse.get_pos()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.add_cell(event, self.mouse_pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.draw_mode = False
                    self.left_click = False
                    self.right_click = False

                elif event.type == pygame.MOUSEMOTION:
                    self.draw(self.mouse_pos)

                elif event.type == pygame.KEYDOWN:
                    self.start_planning(event)

            pygame.display.update()

    
    def draw_grid(self):
        cells = []
        for x in range(self.width):
            for y in range(5, self.height):
                cell = pygame.Rect(
                    x*self.cell_size, 
                    y*self.cell_size, 
                    self.cell_size, 
                    self.cell_size)

                cells.append(cell)
                pygame.draw.rect(self.surface, self.black, cell, 1)

        return cells

    def pick_celltype(self):
        if self.obstacle_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.color = self.grey

        elif self.start_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.color = self.green

        elif self.goal_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.color = self.red

        if self.astar_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.algorithm = "a*"
        
        elif self.dijkstra_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.algorithm = "dijkstra"

    def add_cell(self, event, mouse_pos):
        self.draw_mode = True
        mouse_x, mouse_y = mouse_pos[0], mouse_pos[1]
        if mouse_y > 50:
            if event.button == 1:
                self.left_click = True
                pygame.draw.rect(self.surface, self.color, (mouse_x - (mouse_x % 10), mouse_y - (mouse_y % 10), 10, 10))
                pygame.draw.rect(self.surface, self.black, (mouse_x - (mouse_x % 10), mouse_y - (mouse_y % 10), 10, 10), 1)
                if self.color == self.grey:
                    self.grid[((mouse_pos[1] - (mouse_pos[1] % 10)) - 50) // 10][(mouse_pos[0] - (mouse_pos[0]%10)) // 10] = 1

                elif self.color == self.green:
                    self.grid[((mouse_pos[1] - (mouse_pos[1] % 10)) - 50) // 10][(mouse_pos[0] - (mouse_pos[0]%10)) // 10] = 5
                    self.start = ((mouse_pos[0] - (mouse_pos[0] % 10)) // 10, ((mouse_pos[1] - (mouse_pos[1] % 10)) - 50) // 10)

                elif self.color == self.red:
                    self.grid[((mouse_pos[1] - (mouse_pos[1] % 10)) - 50) // 10][(mouse_pos[0] - (mouse_pos[0]%10)) // 10] = 6
                    self.goal = ((mouse_pos[0] - (mouse_pos[0] % 10)) // 10, ((mouse_pos[1] - (mouse_pos[1] % 10)) - 50) // 10)

            else:
                self.right_click = True
                pygame.draw.rect(self.surface, self.white, (mouse_pos[0] - (mouse_pos[0] % 10), mouse_pos[1] - (mouse_pos[1] % 10), 10, 10))
                pygame.draw.rect(self.surface, self.black, (mouse_pos[0] - (mouse_pos[0] % 10), mouse_pos[1] - (mouse_pos[1] % 10), 10, 10), 1)
                self.grid[((mouse_pos[1] - (mouse_pos[1] % 10)) - 50) // 10][(mouse_pos[0] - (mouse_pos[0] % 10)) // 10] = 0

    def draw(self, mouse_pos):
        if self.draw_mode == True:
            if mouse_pos[1] > 50:
                if self.left_click:
                    pygame.draw.rect(self.surface, self.color, (mouse_pos[0] - (mouse_pos[0] % 10), mouse_pos[1] - (mouse_pos[1] % 10), 10, 10))
                    pygame.draw.rect(self.surface, self.black, (mouse_pos[0] - (mouse_pos[0] % 10), mouse_pos[1] - (mouse_pos[1] % 10), 10, 10), 1)
                    if self.color == self.grey:
                        self.grid[((mouse_pos[1] - (mouse_pos[1] % 10)) - 50) // 10][(mouse_pos[0] - (mouse_pos[0] % 10)) // 10] = 1
                    elif self.color == self.green:
                        self.grid[((mouse_pos[1] - (mouse_pos[1] % 10)) - 50) // 10][(mouse_pos[0] - (mouse_pos[0] % 10)) // 10] = 5
                    elif self.color == self.red:
                        self.grid[((mouse_pos[1] - (mouse_pos[1] % 10)) - 50) // 10][(mouse_pos[0] - (mouse_pos[0] % 10)) // 10] = 6

                elif self.right_click:
                    pygame.draw.rect(self.surface, self.white, (mouse_pos[0] - (mouse_pos[0] % 10), mouse_pos[1] - (mouse_pos[1] % 10), 10, 10))
                    pygame.draw.rect(self.surface, self.black, (mouse_pos[0] - (mouse_pos[0] % 10), mouse_pos[1] - (mouse_pos[1] % 10), 10, 10), 1)
                    self.grid[((mouse_pos[1] - (mouse_pos[1] % 10)) - 50) // 10][(mouse_pos[0] - (mouse_pos[0] % 10)) // 10] = 0

    def start_planning(self, event):
        if event.key == pygame.K_RETURN:
            if self.algorithm == "a*":
                palette = (self.blue, self.black, self.yellow)
                a_star(self.grid, self.start, self.goal, self.surface, palette)
                self.run = False
            elif self.algorithm == "dijkstra":
                palette = (self.blue, self.black, self.yellow)
                a_star(self.grid, self.start, self.goal, self.surface, palette, heuristic=False)
                self.run = False

if __name__ == "__main__":
    env = gen_env(300, 350, 10, (255, 255, 255))
    env.display()