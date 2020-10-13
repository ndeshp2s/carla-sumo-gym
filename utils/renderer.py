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


    def create_screen(self, width, height):
        """
        Creates a pygame window
        :param width: the width of the window
        :param height: the height of the window
        :return: None
        """
        self.size = (width, height + 140)
        self.screen = self.display.set_mode(self.size, HWSURFACE | DOUBLEBUF)
        self.display.set_caption("Renderer")
        self.is_open = True


    def render_image(self, image, image_frame = 0, model_output = None, speed = 0):
        """
        Render the given image to the pygame window
        :param image: a grayscale or color image in an arbitrary size. assumes that the channels are the last axis
        :return: None
        """
        if self.is_open:
            if len(image.shape) == 2:
                image = np.stack([image] * 3)
            if len(image.shape) == 3:
                if image.shape[0] == 3 or image.shape[0] == 1:
                    image = np.transpose(image, (1, 2, 0))
            surface = pygame.surfarray.make_surface(image.swapaxes(0, 1))
            surface = pygame.transform.scale(surface, (720, 720))

            if model_output is not None:
                self.show(q = model_output, speed = speed)
            bright = pygame.Surface((surface.get_width(), surface.get_height()), flags=pygame.SRCALPHA)
            bright.fill((40, 40, 40, 0))
            surface.blit(bright, (0, 140), special_flags=pygame.BLEND_RGBA_ADD)

            

            self.screen.blit(surface, (0, 140))
            self.display.flip()
            self.clock.tick()
            self.get_events()

            self.save_image(image = self.screen, frame = image_frame)


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

    def show(self, q, speed = 0):
        pygame.font.init()
        self.GREEN = (0, 153, 76)
        self.ORANGE = (204, 102, 0)
        self.RED = (204, 0, 0)
        self.YELLOW = (204, 204, 0)
        self.screen.fill((200, 200, 200))

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