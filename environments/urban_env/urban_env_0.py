from environments.carla_sumo_gym import CarlaSumoGym
from environments.urban_env import config

class UrbanEnv0(CarlaSumoGym):
    def __init__(self):
        super(UrbanEnv0, self).__init__()

        self.config = config


    def reset(self):
        self.close()

        self.connect_server_client()


    # def close(self):
    #     self.close_sumo()
    #     self.kill_carla_server()
