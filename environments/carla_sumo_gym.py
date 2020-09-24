import os 
import sys
import subprocess
import glob
import time
import json
import re
import random

from os import path, environ
import psutil
import tempfile
import gym


# carla library
try:
    sys.path.append(glob.glob('../carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
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
from run_synchronization import SimulationSynchronization

from util.netconvert_carla import netconvert_carla


class CarlaSumoGym(gym.Env):
    def __init__(self):
        super(CarlaSumoGym, self).__init__()
        self.client = None
        self.world = None
        self.synchronization = None
        # # carla simulation
        # self.carla_simulation = CarlaSimulation('localhost', 2000, 0.1) # host, port, step_length
        # self.client = self.carla_simulation.client
        # self.world = self.carla_simulation.client.get_world()
        # current_map = self.world.get_map()

        # # sumo simulation
        # basedir = os.path.dirname(os.path.realpath(__file__))
        # net_file = os.path.join(basedir, 'sumo_config', current_map.name + '.net.xml')
        # cfg_file = os.path.join(basedir, 'sumo_config', current_map.name + '.sumocfg')

        # self.sumo_net = sumolib.net.readNet(net_file)
        # self.sumo_simulation =  SumoSimulation(cfg_file=cfg_file, step_length=0.1, host=None, port=None, sumo_gui=True, client_order=1)

        # # synchronization
        # self.synchronization = SimulationSynchronization(self.sumo_simulation, self.carla_simulation, 'none',
        #                                         True, False)

        # # Spawn the ego vehicle
        # self.spawn_ego_vehicle()

    def connect_server_client(self, display = True, rendering = True, synchronous = True, town = 'Town11', fps = 10.0):

        self.kill_carla_server()

        # open the server
        p = None
        cmd = [path.join(environ.get('CARLA_SERVER'), 'CarlaUE4.sh')]

        if not display:
            env_ =  {**os.environ, 'DISPLAY': ''}
            cmd.append(" -opengl")
            p = subprocess.Popen(cmd, env=env_)

        else:
            cmd.append(" -opengl")
            p = subprocess.Popen(cmd)

        
        # connect to client
        while True:
            try:
                carla_sim = CarlaSimulation('localhost', 2000, 10.0) # host, port, step_length
                self.client = carla_sim.client
                self.world = self.client.get_world()

                if self.world.get_map().name != town:
                    carla.Client('localhost', 2000, 10).load_world(town)
                    while True:
                        try:
                            while carla.Client('localhost', 2000, 10).get_world().get_map().name != town:
                                time.sleep(0.1)
                            break
                        except:
                            pass
                break
            except Exception as e:
                time.sleep(0.1)

        # apply settings
        delta_sec = 1.0 / fps
        settings = self.world.get_settings()
        self.world.apply_settings(carla.WorldSettings(no_rendering_mode = not rendering, synchronous_mode = synchronous, fixed_delta_seconds = delta_sec))


        # open sumo simulator
        current_map = self.world.get_map()
        basedir = os.path.dirname(os.path.realpath(__file__))
        net_file = os.path.join(basedir, 'sumo_config/net', current_map.name + '.net.xml')
        cfg_file = os.path.join(basedir, 'sumo_config', current_map.name + '.sumocfg')

        sumo_net =  sumolib.net.readNet(net_file)
        sumo_sim =  SumoSimulation(cfg_file=cfg_file, step_length=0.1, host=None, port=None, sumo_gui=True, client_order=1)
        self.synchronization = SimulationSynchronization(sumo_sim, carla_sim, 'none', True, False)


    def tick(self):
        self.synchronization.tick()


    def spawn_ego_vehicle(self):
        traci.vehicle.addFull('ego_vehicle', 'routeEgo', depart=None, departPos=str(20.0), departSpeed='0', typeID='vehicle.audi.etron')
        traci.vehicle.setSpeedMode('ego_vehicle', int('00000',0))
        traci.vehicle.setSpeed('ego_vehicle', 0.0)


    def kill_carla_server(self):
        binary = 'CarlaUE4.sh'
        for process in psutil.process_iter():


            if process.name().lower().startswith(binary.split('.')[0].lower()):
                try:
                    process.terminate()
                except:
                    pass

        # Check if any are still alive, create a list
        still_alive = []
        for process in psutil.process_iter():
            if process.name().lower().startswith(binary.split('.')[0].lower()):
                still_alive.append(process)

        # Kill process and wait until it's being killed
        if len(still_alive):
            for process in still_alive:
                try:
                    process.kill()
                except:
                    pass
            psutil.wait_procs(still_alive)


    def close(self):
        if self.synchronization is not None:
            self.synchronization.close()

        self.kill_carla_server()
