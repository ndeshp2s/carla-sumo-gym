import os
import pygame
from pygame.locals import *
import numpy as np 


class Renderer(object):
    def __init__(self):
        self.size = (1, 1)
        self.screen = None
        self.clock = pygame.time.Clock()
        self.display = pygame.display
        self.fps = 20
        self.pressed_keys = []
        self.is_open = False

        self.rend_img = False
        self.rent_q_val = False
        self.rend_grid = False
        self.img_win_size = (0, 0)
        self.q_values_win_size = (0, 0)
        self.grid_window_size = (0, 0)
        self.grid_size = (0, 0)
        self.grid_resolution = 0.0

        self.GREEN = (0, 153, 76)
        self.ORANGE = (204, 102, 0)
        self.RED = (204, 0, 0)
        self.YELLOW = (204, 204, 0)
        self.BLACK = (0, 0, 0)
        self.OFF_WHITE = (200, 200, 200)
        self.WHITE = (255, 255, 255)

        pygame.font.init()




    def create_screen(self, width = 720, height = 720, render_image = True, render_q_values = True, render_grid = True, grid_x = 0, grid_y = 0, grid_resolution = 0.5):
        """
        Creates a pygame window
        :param width: the width of the window
        :param height: the height of the window
        :return: None
        """
        if render_image:
            self.img_win_size = (720, 720)
            self.rend_img = True
        if render_q_values:
            self.q_values_win_size = (720, 100)
            self.rent_q_val = True
        if render_grid: 
            self.grid_window_size = (640, 940) 
            self.rend_grid = True
            self.grid_size = (grid_x, grid_y)
            self.grid_resolution = grid_resolution
        
        self.border_margin = 20 
        x = self.border_margin + self.img_win_size[0] + self.border_margin + self.grid_window_size[0] + self.border_margin
        y = self.border_margin + self.grid_window_size[1] + self.border_margin

        self.size = (x, y)
        self.screen = self.display.set_mode(self.size, HWSURFACE | DOUBLEBUF)
        self.display.set_caption("Renderer")
        self.is_open = True


    def render(self, image, q_values = None, grid = None, speed = 0):
        """
        Render the given image to the pygame window
        :param image: a grayscale or color image in an arbitrary size. assumes that the channels are the last axis
        :return: None
        """
        if self.is_open:
            self.screen.fill(self.OFF_WHITE)

            if self.render_image:
                self.render_image(image = image)
            if self.render_q_values:
                self.render_q_values(q_values = q_values, speed = speed)
            if self.rend_grid:
                self.render_grid(grid = grid)

            self.display.flip()
            self.clock.tick()
            self.get_events()

            #self.save_image(image = self.screen, frame = image_frame)


    def render_image(self, image):
        """
        Render the given image to the pygame window
        :param image: a grayscale or color image in an arbitrary size. assumes that the channels are the last axis
        :return: None
        """
        if len(image.shape) == 2:
            image = np.stack([image] * 3)
        if len(image.shape) == 3:
            if image.shape[0] == 3 or image.shape[0] == 1:
                image = np.transpose(image, (1, 2, 0))
        surface = pygame.surfarray.make_surface(image.swapaxes(0, 1))
        surface = pygame.transform.scale(surface, (720, 720))
        
        self.screen.blit(surface, (self.border_margin, (self.size[1] - self.img_win_size[1] - self.border_margin)))


    def save_image(self, image, frame):
        image_dir = '/home/niranjan/carla-sumo-gym/experiments/cnn_dqn/test2/images'
        image_name = image_dir + ('/image-%05d.png' % frame)
        pygame.image.save(self.screen, image_name)


    def get_events(self):
        """
        Get all the window events in the last tick and reponse accordingly
        :return: None
        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.pressed_keys.append(event.key)
                # esc pressed
                if event.key == pygame.K_ESCAPE:
                    self.close()
            elif event.type == pygame.KEYUP:
                if event.key in self.pressed_keys:
                    self.pressed_keys.remove(event.key)
            elif event.type == pygame.QUIT:
                self.close()


    def render_q_values(self, q_values, speed = 0):

        base_dir = os.path.dirname(os.path.realpath(__file__))
        font_file = os.path.join(base_dir, 'Roboto-Light.ttf')
        font = pygame.font.Font(font_file, 18)

        normalized_q_values = self.normalize_array(q_values)
        surface = pygame.Surface((self.q_values_win_size[0],  self.q_values_win_size[1] + self.border_margin))
        surface.fill(self.OFF_WHITE)
        surface.set_alpha(150)

        # print(q_values)
        # print(normalized_q_values)

        # 0th action
        pygame.draw.rect(surface, self.GREEN, (0, 100, 180, -normalized_q_values[0]))
        text = font.render("Accelerate", True, (0, 0, 0))
        surface.blit(text, (1, self.q_values_win_size[1]))

        # 1th action
        pygame.draw.rect(surface, self.ORANGE, (180, 100, 180, -normalized_q_values[1]))
        text = font.render("Decelerate", True, (0, 0, 0))
        surface.blit(text, (181, self.q_values_win_size[1]))

        # 2th action
        pygame.draw.rect(surface, self.YELLOW, (360, 100, 180, -normalized_q_values[2]))
        text = font.render("Steer", True, (0, 0, 0))
        surface.blit(text, (361, self.q_values_win_size[1]))

        # 3th action
        pygame.draw.rect(surface, self.RED, (540, 100, 180, -normalized_q_values[3]))
        text = font.render("Brake", True, (0, 0, 0))
        surface.blit(text, (541, self.q_values_win_size[1]))

        pygame.draw.rect(surface, self.BLACK, pygame.Rect(0, 0, self.q_values_win_size[0], self.q_values_win_size[1] + 20), 1)

        self.screen.blit(surface, (self.border_margin, (self.size[1] - self.img_win_size[1] - 2*self.border_margin - self.q_values_win_size[1] - self.border_margin)))


        # Speed
        font_file = os.path.join(base_dir, 'Roboto-LightItalic.ttf')
        font_unit = pygame.font.Font(font_file, 20)
        unit = font_unit.render("km/hr", 1, (0, 0, 0))
        speed_string = font.render(str(speed), 1, (0, 0, 0))

        self.screen.blit(speed_string, (580, 50))
        self.screen.blit(unit, (630, 50))


    def show(self, q, speed = 0):
        pygame.font.init()

        self.screen.fill(self.OFF_WHITE)

        base_dir = os.path.dirname(os.path.realpath(__file__))
        font_file = os.path.join(base_dir, 'Roboto-Light.ttf')

        font = pygame.font.Font(font_file, 20)

        normalized_q_values = self.normalize_array(q)


        # 0th action
        surface = pygame.Surface((120, 100))
        surface.set_colorkey((0,0,0))
        surface.set_alpha(150)
        pygame.draw.rect(surface, self.GREEN, (0, 100, 150, -normalized_q_values[0]))
        text = font.render("accelerate", True, (0, 0, 0))
        
        self.screen.blit(surface, (2.5, 10))
        self.screen.blit(text, (13, 120))

        # 1st action
        surface = pygame.Surface((120, 100))
        surface.set_colorkey((0,0,0))
        surface.set_alpha(150)
        pygame.draw.rect(surface, self.ORANGE, (0, 100, 150, -normalized_q_values[1]))
        text = font.render("decelerate", True, (0, 0, 0))

        self.screen.blit(surface, (127.5, 10))
        self.screen.blit(text, (143, 120))


        # 2th action
        surface = pygame.Surface((120, 100))
        surface.set_colorkey((0,0,0))
        surface.set_alpha(150)
        pygame.draw.rect(surface, self.YELLOW, (0, 100, 150, -normalized_q_values[2]))
        text = font.render("steer", True, (0, 0, 0))

        self.screen.blit(surface, (252.5, 10))
        self.screen.blit(text, (290, 120))

        # 3nd action
        surface = pygame.Surface((120, 100))
        surface.set_colorkey((0,0,0))
        surface.set_alpha(150)
        pygame.draw.rect(surface, self.RED, (0, 100, 150, -normalized_q_values[3]))
        text = font.render("brake", True, (0, 0, 0))


        self.screen.blit(surface, (377.5, 10))
        self.screen.blit(text, (413, 120))

        # Speed
        font_file = os.path.join(base_dir, 'Roboto-LightItalic.ttf')
        font_unit = pygame.font.Font(font_file, 20)
        unit = font_unit.render("km/hr", 1, (0, 0, 0))
        speed_string = font.render(str(speed), 1, (0, 0, 0))

        self.screen.blit(speed_string, (580, 50))
        self.screen.blit(unit, (630, 50))


        self.display.flip()


    def normalize_array(self, array): 
        old_min = min(array)
        old_max = max(array)

        new_min = 0
        new_max = 100

        old_range = (old_max - old_min)
        new_range = (new_max - new_min)

        norm_array = []
        for i in array:
            new_value = (((i - old_min) * new_range) / old_range) + new_min
            norm_array.append(new_value)

        return norm_array



    def get_key_names(self, key_ids):
        """
        Get the key name for each key index in the list
        :param key_ids: a list of key id's
        :return: a list of key names corresponding to the key id's
        """
        return [pygame.key.name(key_id) for key_id in key_ids]
        

    def close(self):
        """
        Close the pygame window
        :return: None
        """
        self.is_open = False
        pygame.quit()


    def render_grid(self, grid):
        WIDTH = 20/4
        HEIGHT = 20/4
        MARGIN = 5
        
        font = pygame.font.SysFont('arial', 12, False)
        surface = pygame.Surface((self.grid_window_size[0], self.grid_window_size[1]))
        surface.fill(self.WHITE)
        BLACK = (0, 0, 0)
        for row in range(30*4):
            row_cord = MARGIN + row * HEIGHT

            if row < 10:
                indent = '   '
            else:
                indent = '  '
            text = font.render(indent + str(row - 4), 1, (0, 0, 0))
            surface.blit(pygame.transform.flip(text, False, True), (5 + 20 * WIDTH, row_cord))

            for column in range(20*4):
                col_cord = MARGIN + column * WIDTH

                if column < 10:
                    indent = '  '
                else:
                    indent = ' '
                text = font.render(indent + str(column - 10), 1, (0, 0, 0))
                surface.blit(pygame.transform.flip(text, False, True), (col_cord, 5 + 30 * HEIGHT))

                color = self.BLACK

                if grid[row][column] == 0.5:
                    #color = (0, 255, 0)
                    pygame.draw.rect(surface, self.RED, [(WIDTH) * (column) + MARGIN, (HEIGHT) * row + MARGIN, (WIDTH), (HEIGHT)])

                elif grid[row][column] == 1.0:
                    #color = (0, 255, 0)
                    pygame.draw.rect(surface, self.GREEN, [(WIDTH) * (column) + MARGIN, (HEIGHT) * row + MARGIN, (WIDTH), (HEIGHT)])

                # if grid[row][column] == 0.33:
                #     #color = (0, 255, 0)
                #     pygame.draw.rect(surface, self.RED, [(WIDTH) * (column) + MARGIN, (HEIGHT) * row + MARGIN, (WIDTH), (HEIGHT)])

                # elif grid[row][column] == 0.67:
                #     #color = (0, 255, 0)
                #     pygame.draw.rect(surface, self.GREEN, [(WIDTH) * (column) + MARGIN, (HEIGHT) * row + MARGIN, (WIDTH), (HEIGHT)])

                # elif grid[row][column] == 1.0:
                #     #color = (0, 255, 0)
                #     pygame.draw.rect(surface, self.ORANGE, [(WIDTH) * (column) + MARGIN, (HEIGHT) * row + MARGIN, (WIDTH), (HEIGHT)])

                pygame.draw.rect(surface, color, pygame.Rect(col_cord, row_cord, HEIGHT, WIDTH), 1)

               
        #self.screen.blit(pygame.transform.rotate(surface, 180), (740, 0))
        self.screen.blit(pygame.transform.flip(surface, False, True), ((self.border_margin + self.img_win_size[0] + self.border_margin), (self.size[1] -  self.grid_window_size[1] - self.border_margin)))

        # WIDTH = 20
        # HEIGHT = 20
 
        # # This sets the margin between each cell
        # MARGIN = 5
        # surface = pygame.Surface((640, 940))
        # surface.fill((255, 255, 255))
        # for row in range(45):
        #     for column in range(30):
        #         color = (0, 0, 0)
        #         # if grid[row][column] == 1:
        #         #     color = GREEN
        #         pygame.draw.rect(surface,
        #                          color,
        #                          [(MARGIN + WIDTH) * (column) + MARGIN,
        #                           (MARGIN + HEIGHT) * row + MARGIN,
        #                           WIDTH,
        #                           HEIGHT])
        # #         # font = pygame.font.SysFont('1,2', 5)
        # #         # screen.blit(font.render('Hello!', True, (255,0,0)), (200, 100))

        # self.screen.blit(surface, (0, 0))
