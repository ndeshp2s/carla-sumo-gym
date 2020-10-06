from environments.carla_sumo_gym import CarlaSumoGym
from environments.urban_env_0 import config
from utils.renderer import Renderer

class UrbanEnv(CarlaSumoGym):
    def __init__(self):
        super(UrbanEnv, self).__init__()

        self.config = config

        if self.config.rendering:
        	self.renderer = Renderer()
        	self.renderer.create_screen(self.config.screen_x, self.config.screen_y)



    def step(self, action = None):

    	# select action to be taken
    	self.take_action(action)

    	# perform action in the simulation environment
    	self.tick()

    	# get next state and reward
    	self.get_observations()


    def reset(self):

        self.connect_server_client(display = config.display, rendering = config.rendering, town = config.town, fps = config.fps, sumo_gui = config.sumo_gui)
        
        self.spawn_ego_vehicle(position = config.start_position, type_id = config.ev_type)

        self.tick()

        #self.add_sensors(rgb = config.rgb_sensor)


    def get_observations(self):
    	# get ego vehicle current speed and convert to km/hr
    	# ego_vehicle_speed = (self.get_ego_vehicle_speed())
    	# ego_vehicle_speed *= 3.6
    	# ego_vehicle_speed = round( ego_vehicle_speed, 2)
    	print('after: ', self.get_ego_vehicle_speed(kmph = False))


