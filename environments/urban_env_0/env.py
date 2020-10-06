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

class UrbanEnv(CarlaSumoGym):
    def __init__(self):
        super(UrbanEnv, self).__init__()

        self.config = config

        self.rgb_sensor = None
        self.rgb_image = None
        self.renderer = None

        if config.rendering:
            self.renderer = Renderer()
            self.renderer.create_screen(config.screen_x, config.screen_y)


    def step(self, action = None):

        print('before: ', self.get_ego_vehicle_speed(kmph = False))

        # select action to be taken
        self.take_action(action)

        # render the image
        self.render()

        # perform action in the simulation environment
        self.tick()

        # get next state and reward
        self.get_observations()


    def reset(self):

        self.connect_server_client(display = config.display, rendering = config.rendering, town = config.town, fps = config.fps, sumo_gui = config.sumo_gui)
        
        self.spawn_ego_vehicle(position = config.start_position, type_id = config.ev_type)

        self.tick()

        self.add_sensors()

        self.tick()


    def get_observations(self):
        # get ego vehicle current speed and convert to km/hr
        # ego_vehicle_speed = (self.get_ego_vehicle_speed())
        # ego_vehicle_speed *= 3.6
        # ego_vehicle_speed = round( ego_vehicle_speed, 2)
        print('after: ', self.get_ego_vehicle_speed(kmph = False))


    def add_sensors(self):

        # add rgb sensor to ego vehicle
        if config.add_rgb_sensor:
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


    def render(self):
        if self.renderer is not None and self.rgb_image is not None: 
            self.renderer.render_image(self.rgb_image)


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


    # def render(self):
    #     if self.renderer is None:
    #         return

    #     img =  self.get_rendered_image()
    #     self.renderer.render_image(img)


    def get_rendered_image(self):
        temp = []
        if config.rgb_sensor: temp.append(self.rgb_image)
        if config.sem_sensor: temp.append(self.semantic_image)

        return np.vstack(img for img in temp)






