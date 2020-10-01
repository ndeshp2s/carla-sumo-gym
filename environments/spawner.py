import sys, os
import glob

import random

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

from agents.tools.misc import is_within_distance_ahead, is_within_distance
from utils.misc import is_within_distance_ahead


class Spawner(object):
    def __init__(self, client = None):

        self.connected_to_server = False

        if client is None:
            self.create_client()

        else:
            self.client = client
            self.world = self.client.get_world()
            self.connected_to_server = True
        
        self.pedestrian_list = []

        self.update_config()


    def create_client(self):
        try:
            self.client = carla.Client('localhost', 2000)
            self.client.set_timeout(10.0)
            self.world = self.client.get_world()
            self.connected_to_server = True

        except (RuntimeError):
            self.client = None
            self.world = None


    def update_config(self, config = None, ped_spawn_points = None, ev_id = None):

        # initialize all variables to none
        self.max_dist_ped = None
        self.min_dist_ped = None
        self.num_of_ped = None
        self.ped_cross = None
        self.ped_cross_illegal = None
        self.ped_sp_max = None
        self.ped_sp_min = None
        self.ped_sp = None
        self.ev_id = None


        if config is not None:
            self.max_dist_ped = config.maximum_distance_pedestrian
            self.min_dist_ped = config.minimum_distance_pedestrian
            self.num_of_ped = config.number_of_pedestrians
            self.ped_cross = config.pedestrian_crossing_legal
            self.ped_cross_illegal = config.pedestrian_crossing_illegal
            self.world.set_pedestrians_cross_factor(self.ped_cross)
            self.world.set_pedestrians_cross_illegal_factor(self.ped_cross_illegal)
            self.ped_sp_max = config.pedestrian_spawn_point_maximum
            self.ped_sp_min = config.pedestrian_spawn_point_minimum

        if ped_spawn_points is not None:
            self.ped_sp = ped_spawn_points

        if ev_id is not None:
            self.ev_id = ev_id


    def run_step(self):

        if self.connected_to_server is False:
            return

        if self.ev_id is None or self.ped_sp is None:
            return

        # Get ego vehicle details
        actor_list = self.world.get_actors()
        actor = actor_list.find(self.ev_id)
        ev_trans = actor.get_transform()

        # delete farther pedestrians
        self.delete_pedestrians(ev_trans)

        # initialize controller of each pedestrian (spawned in previous step) and set target to walk to  
        self.spawn_controllers()

        # spawn the pedestrians
        self.spawn_pedestrians(ev_trans)


    def spawn_pedestrians(self, ev_trans):

        if len(self.pedestrian_list) >= 10:
            return

        # Find nearby spawn points
        spawn_points = []
        for i in range(self.num_of_ped):
            spawn_point = carla.Transform()
            spawn_point.location = self.world.get_random_location_from_navigation()
            if (spawn_point.location != None and is_within_distance_ahead(target_transform = spawn_point, current_transform = ev_trans, max_distance = (self.max_dist_ped - 10), min_distance = self.min_dist_ped)):
                spawn_points.append(spawn_point)


        # Spawn the pedestrians
        for i in range(len(spawn_points)):
            sp = random.choice(spawn_points)
            pedestrian_bp = random.choice(self.world.get_blueprint_library().filter("walker.pedestrian.*"))

            ped = self.world.try_spawn_actor(pedestrian_bp, sp)
            if ped is not None:
                self.pedestrian_list.append({"id": ped.id, "controller": None, "start": sp})

                spawn_points.remove(sp)

            if len(self.pedestrian_list) >= 10:
                break 


    def spawn_controllers(self):
        controller_bp = self.world.get_blueprint_library().find('controller.ai.walker')

        for p in self.pedestrian_list:
            if p["controller"] is None:
                ped = self.world.get_actor(p["id"])
                controller = self.world.spawn_actor(controller_bp, carla.Transform(), attach_to = ped)
                controller.start()
                controller.go_to_location(self.world.get_random_location_from_navigation())
                controller.set_max_speed(1 + random.random())

                i = self.pedestrian_list.index(p)
                self.pedestrian_list[i]["controller"] = controller.id


    def delete_pedestrians(self, ev_trans):

        for p in self.pedestrian_list:
            ped = self.world.get_actor(p['id'])
            if ped is None:
                continue

            ped_trans = ped.get_transform()

            if not is_within_distance(target_location = ped_trans.location, current_location = ev_trans.location, orientation = ev_trans.rotation.yaw, max_distance = self.max_dist_ped, d_angle_th_up = 90, d_angle_th_low = 0):
                if p["controller"] is not None:
                    controller = self.world.get_actor(p["controller"])
                    if controller is not None:
                        controller.stop()
                        controller.destroy()

                ped.destroy()
                self.pedestrian_list.remove(p)




# Testing the library class
import time
from environments.urban_env_0.walker_spawn_points import walker_spawn_points
from environments.urban_env_0 import config

DEBUG = 1

def main():

    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)
    world = client.get_world()


    world.apply_settings(carla.WorldSettings(synchronous_mode = True, fixed_delta_seconds = 0.1))

    # Spawn a dummy ego vehicle
    sp = carla.Transform(carla.Location(x = 34.4, y = -1.7, z = 0.1), carla.Rotation(yaw = 180))
    bp = random.choice(world.get_blueprint_library().filter('vehicle.audi.etron'))
    bp.set_attribute('role_name', 'hero')

    ego_vehicle = world.spawn_actor(bp, sp)

    world.tick()

    spawner = Spawner(client, walker_spawn_points, ego_vehicle.id)
    spawner.update_config(max_dist_ped = config.maximum_distance_pedestrian, min_dist_ped = config.minimum_distance_pedestrian, num_of_ped = config.number_of_pedestrians, ped_crossing = config.pedestrian_crossing_legal, ped_crossing_illegal = config.pedestrian_crossing_illegal)


    try:
        while True:
            spawner.run_step()
            world.tick()
            time.sleep(0.1)


    except KeyboardInterrupt:
        
        # Destroy any previous actors
        actor_list = world.get_actors()
        print(actor_list)
        for a in actor_list.filter("walker.pedestrian.*"):
            a.destroy()
        for a in actor_list.filter("vehicle.*"):
            a.destroy()

        print('Done.')




if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\nTesting Spawner library done.')