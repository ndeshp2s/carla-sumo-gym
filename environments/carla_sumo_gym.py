import os 
import sys
import subprocess
import glob
import time
from os import path, environ
import psutil
import tempfile
import gym


# carla library
try:
    sys.path.append(glob.glob('../../PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

# sumo library
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


# imports
import sumolib  
import traci  

from sumo_integration.carla_simulation import CarlaSimulation
from sumo_integration.sumo_simulation import SumoSimulation

from util.netconvert_carla import netconvert_carla


class CarlaSumoGym(gym.Env):
    def __init__(self):
        super(CarlaSumoGym, self).__init__()
        self.carla = CarlaSimulation('localhost', 2000, 0.1) # host, port, step_length
        #self.sumo =  SumoSimulation(cfg_file, args.step_length, host=args.sumo_host, port=args.sumo_port, sumo_gui=args.sumo_gui, client_order=args.client_order)






        
        # xodr_file = os.path.join(tmpdir + '/carla', current_map.name + '.xodr')
        # # print(xodr_file)
        # current_map.save_to_disk(xodr_file)

        # net_file = os.path.join(tmpdir + '/sumo', current_map.name + '.net.xml')
        # print(net_file)
        # netconvert_carla(xodr_file, net_file, guess_tls=True)

        # basedir = os.path.dirname(os.path.realpath(__file__))
        # print(basedir)
        # vtypes_file = os.path.join(basedir, 'examples', 'carlavtypes.rou.xml')



def main():

    test_carla_sumo_gym = CarlaSumoGym()
    test_carla_sumo_gym.sumo_config_files()



if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')