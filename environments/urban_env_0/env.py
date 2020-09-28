from environments.carla_sumo_gym import CarlaSumoGym
from environments.urban_env_0 import config

class UrbanEnv(CarlaSumoGym):
    def __init__(self):
        super(UrbanEnv, self).__init__()

        self.config = config


    def step(self, action = None):

    	# select action to be taken
    	self.take_action(action)

    	# perform action in the simulation environment
    	self.tick()

    	# get next state and reward
    	self.get_observations()


    def reset(self):

        self.connect_server_client(display = config.display, rendering = config.rendering, town = config.town, fps = config.fps)
        
        self.spawn_ego_vehicle(position = config.start_position, type_id = config.ev_type)


    def get_observations(self):
    	# get ego vehicle current speed and convert to km/hr
    	ego_vehicle_speed = (self.get_ego_vehicle_speed())
    	ego_vehicle_speed *= 3.6
    	ego_vehicle_speed = round( ego_vehicle_speed, 2)
    	print('ego vehicle speed: ', ego_vehicle_speed)


