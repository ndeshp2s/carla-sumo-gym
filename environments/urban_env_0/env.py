import os 
import sys
import glob

import numpy as np

# carla library
try:
    sys.path.append(glob.glob('../carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

from environments.carla_sumo_gym import CarlaSumoGym
from environments.urban_env_0 import config
from utils.renderer import Renderer
from environments.spawner import Spawner
from environments.urban_env_0.walker_spawn_points import walker_spawn_points

class UrbanEnv(CarlaSumoGym):
    def __init__(self):
        super(UrbanEnv, self).__init__()

        self.config = config

        self.rgb_sensor = None
        self.rgb_image = None
        self.rgb_image_frame = 0
        self.renderer = None

        if config.rendering:
            self.renderer = Renderer()
            self.renderer.create_screen(config.rendering_screen_x, config.rendering_screen_y)

        self.walker_spawn_points = walker_spawn_points


    def step(self, action = None):

        q_values = self.compute_q_values(action = action)

        self.render(model_output = q_values, speed = self.get_ego_vehicle_speed(kmph = True))

        # select action to be taken
        self.take_action(action)


        # perform action in the simulation environment
        self.tick()

        # get next state and reward
        state = self.get_observations()

        return state


    def reset(self):

        self.connect_server_client(display = config.display, rendering = config.rendering, town = config.town, fps = config.fps, sumo_gui = config.sumo_gui)
        
        self.spawn_ego_vehicle(position = config.start_position, type_id = config.ev_type)

        self.add_sensors()

        self.tick()

        #self.init_system()

        state = self.get_observations()

        self.client.start_recorder("/home/niranjan/recording01.log")

        return state


    def get_observations(self):
        # get ego vehicle current speed and convert to km/hr
        # ego_vehicle_speed = (self.get_ego_vehicle_speed())
        # ego_vehicle_speed *= 3.6
        # ego_vehicle_speed = round( ego_vehicle_speed, 2)
        print('ev speed: ', self.get_ego_vehicle_speed(kmph = False), self.get_ego_vehicle_speed(kmph = True))
        return None


    def add_sensors(self):

        # add rgb sensor to ego vehicle
        if config.rgb_sensor:
            rgb_bp = rgb_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
            rgb_bp.set_attribute('image_size_x', config.rgb_size_x)
            rgb_bp.set_attribute('image_size_y', config.rgb_size_y)
            rgb_bp.set_attribute('fov', config.rgb_fov)
            transform = carla.Transform(carla.Location(x = config.rgb_loc_x, z = config.rgb_loc_z))
            ego_vehicle = self.world.get_actor(self.get_ego_vehicle_id())

            self.rgb_sensor = self.world.spawn_actor(rgb_bp, transform, attach_to = ego_vehicle)
            self.rgb_sensor.listen(self.rgb_sensor_callback)


    def rgb_sensor_callback(self, image):
        #image.convert(cc.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        self.rgb_image = array
        self.rgb_image_frame = image.frame


    def render(self, model_output = None, speed = 0):
        if self.renderer is not None and self.rgb_image is not None: 
            self.renderer.render_image(image = self.rgb_image, image_frame = self.rgb_image_frame, model_output = model_output, speed = speed)


    def close(self):
        if self.rgb_sensor is not None:
            self.rgb_sensor.destroy()

        if self.renderer is not None:
            self.renderer.close()

        super(UrbanEnv, self).close()


    def init_renderer(self):
        self.no_of_cam = 0
        if config.rgb_sensor: self.no_of_cam += 1
        if config.sem_sensor: self.no_of_cam += 1

        self.renderer.create_screen(config.screen_x, config.screen_y * self.no_of_cam)


    def get_rendered_image(self):
        temp = []
        if config.rgb_sensor: temp.append(self.rgb_image)
        if config.sem_sensor: temp.append(self.semantic_image)

        return np.vstack(img for img in temp)


    def init_system(self):
        for i in range(10):
            self.step(action = 3)


    def compute_q_values(self, action = 0):
        import random

        q_values = [1,0.2,0.3,0.5] 

        if action == 0:
            q_values[0] = round(random.uniform(0.9, 1.0), 2) # accelerate 
            q_values[1] = round(random.uniform(0.4, 0.6), 2) # decelerate 
            q_values[2] = round(random.uniform(0.6, 0.8), 2) # steer
            q_values[3] = round(random.uniform(0.3, 0.5), 2) # brake

        elif action == 1:
            q_values[0] = round(random.uniform(0.4, 0.7), 2)
            q_values[1] = round(random.uniform(0.9, 1.0), 2)
            q_values[2] = round(random.uniform(0.4, 0.6), 2)
            q_values[3] = round(random.uniform(0.6, 0.8), 2)
 
        elif action == 2:
            q_values[0] = round(random.uniform(0.6, 0.8), 2)
            q_values[1] = round(random.uniform(0.4, 0.6), 2)
            q_values[2] = round(random.uniform(0.9, 1.0), 2)
            q_values[3] = round(random.uniform(0.4, 0.5), 2)

        elif action == 3: 
            q_values[0] = round(random.uniform(0.5, 0.6), 2)
            q_values[1] = round(random.uniform(0.5, 0.6), 2)
            q_values[2] = round(random.uniform(0.4, 0.6), 2)
            q_values[3] = round(random.uniform(0.9, 0.9), 2)

        return q_values





