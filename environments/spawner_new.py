import sys, os
import glob
import random
import time

# carla library
try:
    sys.path.append(glob.glob('/home/niranjan/Desktop/carla/Dist/CARLA_Shipping_0.9.11/LinuxNoEditor/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

from utils.misc import is_within_distance, is_within_distance_ahead, euclidean_distance, walker_relative_position


class Spawner(object):
    def __init__(self, client = None, config = None, spawn_points = None, ev_id = None):

        self.config = None

        self.walker_spawn_points = None

        self.connected_to_server = False

        # get ego vehicle 
        self.ego_vehicle_id = None
        
        # initialize walker list
        self.walker_list = []

        # client related
        self.client = None
        self.world = None
        self.map = None

    def run_spawner_step(self, ev_trans):

        if self.ego_vehicle_id is None or self.walker_spawn_points is None:
            return

        # delete farther pedestrians
        self.delete_pedestrians(ev_trans)

        # initialize controller of each pedestrian (spawned in previous step) and set target to walk to  
        self.spawn_controllers()

        # spawn the pedestrians
        self.spawn_pedestrians(ev_trans)


       
    def spawn_pedestrians(self, ev_trans):

        if len(self.walker_list) >= self.config.number_of_walkers:
            return

        # Find nearby spawn points
        spawn_points = []
        for sp in self.walker_spawn_points:
            if is_within_distance(tar_loc = sp.location, cur_loc = ev_trans.location, rot = ev_trans.rotation.yaw, max_dist = self.config.walker_spawn_distance_maximum, min_dist = self.config.walker_spawn_distance_minimum):
                spawn_points.append(sp)

        # Spawn the walkers
        for i in range(self.config.number_of_walkers):
            if len(spawn_points) == 0 or len(self.walker_list) >= self.config.number_of_walkers:
                return

            # add walker
            walker = None

            walker_bp = random.choice(self.world.get_blueprint_library().filter("walker.pedestrian.*"))
            
            walker_sp = carla.Transform()
            walker_sp = random.choice(spawn_points)            
            walker_sp.location.x += random.uniform(-0.2, 0.2)
            walker_sp.location.y += random.uniform(-0.2, 0.2)

            walker = self.world.try_spawn_actor(walker_bp, walker_sp)

            if walker is not None:
                self.walker_list.append({"id": walker.id, "controller": None, "start": walker_sp})
                spawn_points.remove(walker_sp)


    def spawn_controllers(self):
        controller_bp = self.world.get_blueprint_library().find('controller.ai.walker')

        for w in self.walker_list:
            if w["controller"] is None:
                walker = self.world.get_actor(w["id"])
                controller = self.world.spawn_actor(controller_bp, carla.Transform(), attach_to = walker)
                goal = self.get_walker_goal(goal_points = self.walker_spawn_points, start = w["start"])
                goal.location.z = 0.2

                controller.start()
                controller.go_to_location(goal.location)
                controller.set_max_speed(1 + random.random())

                i = self.walker_list.index(w)
                self.walker_list[i]["controller"] = controller.id


    def delete_pedestrians(self, ev_trans):
        for w in self.walker_list:
            walker = self.world.get_actor(w['id'])
            if walker is None:
                continue

            walker_trans = walker.get_transform()

            walker_loc = walker_relative_position(walker_trans = walker_trans, ev_trans = ev_trans)

            if walker_loc[0] > self.config.walker_allowed_distance_maximum or walker_loc[0] < self.config.walker_allowed_distance_minimum or abs(walker_loc[1]) > 20:                
                if w["controller"] is not None:
                    controller = self.world.get_actor(w["controller"])
                    if controller is not None:
                        controller.stop()
                        controller.destroy()

                walker.destroy()
                self.walker_list.remove(w)


    def get_walker_goal(self, goal_points, start, crossing = True):
        for goal in goal_points:
            goal_wp = self.map.get_waypoint(goal.location, project_to_road = True, lane_type = carla.LaneType.Any)
            start_wp = self.map.get_waypoint(start.location, project_to_road = True, lane_type = carla.LaneType.Any)
             

            if goal_wp is not None and start_wp is not None:

                if crossing is True:
                    if (goal_wp.lane_id ^ start_wp.lane_id) < 0 and goal_wp.road_id == start_wp.road_id and euclidean_distance(goal, start) < 20.0:
                        return goal_wp.transform
                else:
                    if goal_wp.lane_id == start_wp.lane_id and goal_wp.road_id == start_wp.road_id:
                        return goal_wp.transform
            
        goal = random.choice(goal_points)
        goal_wp = self.map.get_waypoint(goal.location, project_to_road = True, lane_type = carla.LaneType.Any)

        return goal_wp.transform

