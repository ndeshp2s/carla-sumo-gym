import sys
import glob
import os
import random
import numpy as np
from math import sqrt
import math
try:
    sys.path.append(glob.glob('/home/niranjan/carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

from environments.urban_env_0 import carla_config
from environments.urban_env_0.walker_spawn_points import *
from utils.misc import walker_relative_position


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




class Spawner(object):
    def __init__(self):

        self.client = None
        self.world = None
        self.map = None
        self.connected_to_server = False


        self.num_of_ped = carla_config.num_of_ped
        self.num_of_veh = carla_config.num_of_veh

        self.pedestrian_list = []

        self.pedestrian_ids = [0 for i in range(carla_config.num_of_ped + 1)]
        self.pedestrian_ids[0] = 1

        self.counter = 0


    def reset(self):
        self.connect_to_server()
        self.pedestrian_list = []
        self.pedestrian_ids = [0 for i in range(carla_config.num_of_ped + 1)]
        self.pedestrian_ids[0] = 1


    def connect_to_server(self):
        try:
            self.client = carla.Client('localhost', 2000)
            self.client.set_timeout(10.0)
            self.world = self.client.get_world()
            self.map = self.world.get_map()
            self.connected_to_server = True

            self.world.set_pedestrians_cross_factor(carla_config.percentage_pedestrians_crossing)
            self.world.set_pedestrians_cross_illegal_factor(carla_config.percentage_pedestrians_crossing_illegal)

        except (RuntimeError):
            self.client = None
            self.world = None
            self.ev_id = None
            pass


    def set_factors(self, crossing, illegal_crossing):
        self.world.set_pedestrians_cross_factor(crossing)
        self.world.set_pedestrians_cross_illegal_factor(illegal_crossing)



    def run_step(self, ev_trans = None, step_num = 0, crossing = True):

        print('No. Of peds: ', len(self.pedestrian_list))
        
        if crossing is True:
            self.set_factors(crossing = carla_config.percentage_pedestrians_crossing, illegal_crossing = carla_config.percentage_pedestrians_crossing_illegal)

        else:
            self.set_factors(crossing = 0.0, illegal_crossing = 0.0)


        #ev_trans = self.get_ev_trans()



        spawn_points = self.get_spawn_points(ev_trans)
        
        self.controller_turnon(spawn_points, crossing = crossing)
        

        self.spawn_pedestrian(spawn_points, ev_trans)

        self.check_pedestrian_distance(ev_trans)

        


            
        
    def spawn_pedestrian(self, spawn_points, ev_trans = None):

        if self.connected_to_server is False:
            return

        if ev_trans is None:
            return

        if len(self.pedestrian_list) >=  self.num_of_ped:
            return


        #print('spawner')
        counter = 0
        while len(self.pedestrian_list) <  self.num_of_ped:
            if len(spawn_points) == 0 or counter >= self.num_of_ped:
                return

            # Add pedestrian
            ped_bp = random.choice(self.world.get_blueprint_library().filter("walker.pedestrian.*"))
            ped_id = 0#next((index for index, value in enumerate(self.pedestrian_ids) if value == 0), None)

            if ped_id is None:
                ped_id = 0

            ped_bp.set_attribute('role_name', str(ped_id))

            ped = None
            sp = carla.Transform()

            sp = random.choice(spawn_points)
            sp.location.x += random.uniform(-0.5, 0.5)
            sp.location.y += random.uniform(-0.5, 0.5)

            ped = self.world.try_spawn_actor(ped_bp, sp)

            if ped is not None:
                #print('spawned')
                self.counter += 1
                self.pedestrian_ids[ped_id] = 1
                self.pedestrian_list.append({"id": ped.id, "controller": None, "start": sp})
                sp.location.z = 0.0
                self.world.debug.draw_string(sp.location, str(self.counter), draw_shadow=False,  color=carla.Color(r=255, g=0, b=0), life_time=10.0,persistent_lines=True)
                spawn_points.remove(sp)

            counter = counter + 1


    def controller_turnon(self, goal_points, crossing = True):
        #print('controller_turnon')
        controller_bp = self.world.get_blueprint_library().find('controller.ai.walker')

        for p in self.pedestrian_list:
            if p["controller"] is None:
                ped = self.world.get_actor(p["id"])
                controller = self.world.spawn_actor(controller_bp, carla.Transform(), attach_to = ped)
                controller.start()
                goal = self.get_goal(goal_points, p["start"], crossing = crossing)

                goal.location.z = 0.2
                controller.go_to_location(goal.location)
                #controller.go_to_location(self.world.get_random_location_from_navigation())

                controller.set_max_speed(round(random.uniform(0.75, 1.7), 2))

                #print('controller_turnedon')

                index = self.pedestrian_list.index(p)
                self.pedestrian_list[index]["controller"] = controller.id
                goal.location.z = 0.0
                self.world.debug.draw_string(goal.location, str(self.counter), draw_shadow=False,  color=carla.Color(r=0, g=255, b=0), life_time=10.0,persistent_lines=True)



    def check_pedestrian_distance(self, ev_trans = None):
        if ev_trans is None:
            return

        #print('check_pedestrian_distance')
        for p in self.pedestrian_list:

            ped = self.world.get_actor(p["id"])
            if ped is None:
                continue

            ped_trans = ped.get_transform()

            ped_loc = pedestrian_relative_position(ped_trans = ped_trans, ev_trans = ev_trans)


            #if not self.is_within_distance(ped_trans.location, ev_trans.location, ev_trans.rotation.yaw, carla_config.ped_max_dist, carla_config.ped_min_dist, spawn = False): 
            if ped_loc[0] > carla_config.ped_max_dist or ped_loc[0] < carla_config.ped_min_dist or abs(ped_loc[1]) > 10:
                if p["controller"] is not None:
                    controller = self.world.get_actor(p["controller"])
                    if controller is not None:
                        controller.stop()
                        controller.destroy()

                ped_id = int(ped.attributes['role_name'])
                self.pedestrian_ids[ped_id] = 0

                ped.destroy()
                #print('pedestrian_destroyed')


                self.pedestrian_list.remove(p)
                
                
    def get_ev_trans(self):
        #print('get_ev_trans')
        ev = self.get_ev()

        if ev is not None:
            return ev.get_transform()

        return None


    def get_ev(self):
        #print('get_ev')
        actors = self.world.get_actors().filter(carla_config.ev_bp)

        if actors is not None:
            for a in actors:
                if a.attributes.get('role_name') == carla_config.ev_name: 
                    return a
        else:
            return None


    def destroy_all(self):
        #print('destroy_all')

        world = self.client.get_world()
        if world is not None:
            actor_list = world.get_actors()

            for a in actor_list.filter("walker.pedestrian.*"):
                a.destroy()


    def is_within_distance(self, tar_loc, cur_loc, rot, max_dist, min_dist, spawn = True):
        #print('is_within_distance')

        if not spawn:
            if abs(tar_loc.x - cur_loc.x) > carla_config.ped_max_dist or abs(tar_loc.y - cur_loc.y) > carla_config.ped_max_dist:
                return False

        tar_vec = np.array([tar_loc.x - cur_loc.x, tar_loc.y - cur_loc.y])
        norm = np.linalg.norm(tar_vec)

        for_vec = np.array([math.cos(math.radians(rot)), math.sin(math.radians(rot))])
        d_ang = math.degrees(math.acos(np.dot(for_vec, tar_vec) / norm))

        if norm < 0.001:
            return True

        if (norm > max_dist or norm < min_dist):
            return False

        return d_ang < 90.0


    def get_spawn_points(self, ev_trans = None):
        #print('get_spawn_points')
        if ev_trans is None:
            return
        spawn_points = []

        for sp in walker_spawn_points:
            if self.is_within_distance(sp.location, ev_trans.location, ev_trans.rotation.yaw, carla_config.ped_spawn_max_dist, carla_config.ped_spawn_min_dist):
                spawn_points.append(sp)

        return spawn_points


    def get_goal(self, goal_points, start, crossing = True):
        #print('get_goal')
        for goal in goal_points:
            goal_wp = self.map.get_waypoint(goal.location, project_to_road = True, lane_type = carla.LaneType.Any)
            start_wp = self.map.get_waypoint(start.location, project_to_road = True, lane_type = carla.LaneType.Any)
             

            if goal_wp is not None and start_wp is not None:
                if crossing is True:
                    if (goal_wp.lane_id ^ start_wp.lane_id) < 0 and goal_wp.road_id == start_wp.road_id and self.distance(goal, start) < 40.0:
                        return goal_wp.transform
                else:
                    if goal_wp.lane_id == start_wp.lane_id and goal_wp.road_id == start_wp.road_id:
                        return goal_wp.transform
            
        goal = random.choice(walker_goal_points)
        goal_wp = self.world.get_map().get_waypoint(goal.location, project_to_road = True, lane_type = carla.LaneType.Any)

        return goal_wp.transform


    def distance(self, source_transform, destination_transform):
        #print('distance')
        dx = source_transform.location.x - destination_transform.location.x
        dy = source_transform.location.y - destination_transform.location.y

        return math.sqrt(dx * dx + dy * dy)



# Only for testing
import sys, os
import glob

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


def destroy(world):
    actor_list = world.get_actors()
    for a in actor_list.filter("walker.pedestrian.*"):
        a.destroy()
    for a in actor_list.filter("vehicle.*"):
                a.destroy()



import time
def main():

    carla_sim = CarlaSimulation('localhost', 2000, 0.1) # host, port, step_length
    client = carla_sim.client

    print(client.show_recorder_file_info(str = "~/tutorial/recorder/recording03.log"))

    client.replay_file("/home/niranjan/recording01.log",0,1000,1)


    # client = carla.Client('localhost', 2000)
    # client.set_timeout(2.0)

    # world = client.get_world()


    # destroy(world)

    # settings = world.get_settings()
    # world.apply_settings(carla.WorldSettings(no_rendering_mode = False, synchronous_mode = True, fixed_delta_seconds = 0.1))

    # world.set_pedestrians_cross_factor(0.70)
    # world.set_pedestrians_cross_illegal_factor(0.0)

    # # Spawn ego vehicle
    # # sp = carla.Transform(carla.Location(x = 34.4, y = -1.7, z = 0.1), carla.Rotation(yaw = 180))
    # # bp = random.choice(world.get_blueprint_library().filter('vehicle.audi.etron'))
    # # bp.set_attribute('role_name', 'hero')

    # # veh = world.spawn_actor(bp, sp)

    # current_map = world.get_map()
    # basedir = os.path.dirname(os.path.realpath(__file__))
    # net_file = os.path.join(basedir, 'sumo_config/net', current_map.name + '.net.xml')
    # cfg_file = os.path.join(basedir, 'sumo_config', current_map.name + '.sumocfg')

    # sumo_net =  sumolib.net.readNet(net_file)
    # sumo_sim =  SumoSimulation(cfg_file=cfg_file, step_length=0.1, host=None, port=None, sumo_gui=False, client_order=1)
    # synchronization = SimulationSynchronization(sumo_sim, carla_sim, 'none', True, False)

    # traci.vehicle.addFull(vehID = 'ev', routeID = 'routeEgo', depart=None, departPos=str(70.0), departSpeed='0', typeID='vehicle.audi.etron')
    # traci.vehicle.setSpeedMode(vehID = 'ev', sm = int('00000',0))
    # traci.vehicle.setSpeed(vehID = 'ev', speed = 0.0)
    # # traci.vehicle.setMaxSpeed(vehID = 'ev', speed = 10.0)
    # # max_speed = 10.0
    # # synchronization.sumo.subscribe(actor_id = 'ev')

    # #synchronization.tick()

    # # ego_vehicle = world.get_actors().filter('vehicle.audi.etron')
    # # print(ego_vehicle)
    # # veh = ego_vehicle[0]

    # spawner = Spawner()
    # spawner.reset()


    try:
        while True:

            input('Enter: ')

            synchronization.tick()

            #find_ttc(veh.get_transform())
            #print(veh.get_transform())

            veh_trans = carla.Transform(carla.Location(x=23.436005, y=-1.545837, z=0.000000), carla.Rotation(pitch=0.000000, yaw=179.937103, roll=0.000000)) #veh.get_transform()

            spawner.run_step(ev_trans = veh_trans)

            for p in spawner.pedestrian_list:
                ped = world.get_actor(p["id"])
                if ped is None:
                    continue

                ped_trans = ped.get_transform()

                ped_loc = pedestrian_relative_position(ped_trans = ped_trans, ev_trans = veh_trans)
            #     print(ped_loc)

                if abs(ped_loc[0]) < 3.5 and abs(ped_loc[1]) < 1.4:
                    print('collision')

            #time.sleep(0.5)


    except KeyboardInterrupt:
        world.apply_settings(carla.WorldSettings(no_rendering_mode = False, synchronous_mode = False, fixed_delta_seconds = 0.1))
        spawner.destroy_all()
        veh.destroy()



if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
