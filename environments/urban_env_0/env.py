import os 
import sys
import glob

import numpy as np
import gym
from gym import spaces
from random import randrange

# carla library
try:
    sys.path.append(glob.glob('/home/niranjan/carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
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
from environments.urban_env_0.crosswalk_zones import at_crosswalk
from utils.misc import euclidean_distance, compute_relative_position, compute_relative_heading, normalize_data, get_speed, get_index, ray_intersection
from agents.tools.misc import is_within_distance_ahead, is_within_distance, compute_distance

DEBUG = 0

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

        # state and action space
        self.observation_space = spaces.Box(low = 0, high = 255, shape = (config.grid_height, config.grid_width, config.features), dtype = np.uint8)
        self.action_space = spaces.Discrete(config.N_DISCRETE_ACTIONS)


    def step(self, action = None, action_values = None):

        q_values = action_values#self.compute_q_values(action = action)

        # select action to be taken
        self.take_action(max_speed = self.config.max_speed, action = action)

        # perform action in the simulation environment
        self.tick()

        # get next state and reward
        state = None
        reward = 0
        done = 0
        state = self.get_observation()
        reward, done, info = self.get_reward()

        environment_state = state[1]
        self.render(model_output = q_values, speed = self.get_ego_vehicle_speed(kmph = False), grid = environment_state[:,:,3])

        return state, reward, done, info


    def reset(self):

        self.close()

        self.connect_server_client(display = config.display, rendering = config.rendering, town = config.town, fps = config.fps, sumo_gui = config.sumo_gui)
        
        start_pos = config.start_position + randrange(0, 15)
        self.spawn_ego_vehicle(position = config.start_position, type_id = config.ev_type)

        self.add_sensors()

        self.tick()

        self.init_system()

        if config.rendering:
            self.renderer = Renderer()
            self.renderer.create_screen(config.rendering_screen_x, config.rendering_screen_y)

        state = self.get_observation()

        print('Server and client Connected')

        return state


    def get_observation(self):
        environment_state = np.zeros([self.config.grid_height, self.config.grid_width, self.config.features])
        ego_vehicle_state = np.zeros([1])

        # Get ego vehicle information
        ego_vehicle_trans = self.get_ego_vehicle_transform()
        ego_vehicle_speed = self.get_ego_vehicle_speed(kmph = False)
        ego_vehicle_speed_norm = normalize_data(data = ego_vehicle_speed, min_val = 0, max_val = self.config.max_speed)
        ego_vehicle_speed_norm = round(ego_vehicle_speed_norm, 2)
        ego_vehicle_state[0] = ego_vehicle_speed_norm


        # # Fill grid with ego vehicle position
        # for i in range(0, 1):
        #     for j in range(0, 1):
        #         x_discrete, status = get_index(val = i, start = self.config.grid_height_min, stop = self.config.grid_height_max, num = self.config.grid_height)
        #         y_discrete, status = get_index(val = j, start = self.config.grid_width_min, stop = self.config.grid_width_max, num = self.config.grid_width)

        #         x_discrete = np.argmax(x_discrete)
        #         y_discrete = np.argmax(y_discrete)

        #         # lane type
        #         waypoint = self.map.get_waypoint(ego_vehicle_trans.location, project_to_road=True, lane_type=(carla.LaneType.Driving))
        #         ev_lane = self.find_lane_type(wp = waypoint, trans = ego_vehicle_trans)
        #         ev_lane_norm = normalize_data(data = ev_lane, min_val = 0, max_val = 3)
        #         ev_lane_norm = round(ev_lane_norm, 2)
                
        #         # state update for ego vehicle -> occupancy, heading, speed, lane type
        #         environment_state[x_discrete, y_discrete, :] = [0.5, 0.0, ego_vehicle_speed_norm, ev_lane_norm]


        # Fill walkers information
        walker_list = self.world.get_actors().filter('walker.pedestrian.*')
        for w in walker_list:
            w_trans = w.get_transform()
            walker_relative_position = compute_relative_position(source_transform = ego_vehicle_trans, destination_transform = w_trans)

            x_discrete, status_x = get_index(val = walker_relative_position[0], start = self.config.grid_height_min, stop = self.config.grid_height_max, num = self.config.grid_height)
            y_discrete, status_y = get_index(val = walker_relative_position[1], start = self.config.grid_width_min, stop = self.config.grid_width_max, num = self.config.grid_width)
            

            if status_x and status_y:

                # occupancy/position
                x_discrete = np.argmax(x_discrete)
                y_discrete = np.argmax(y_discrete)

                # heading
                w_relative_heading = compute_relative_heading(source_transform = ego_vehicle_trans, destination_transform = w_trans)

                # walker speed
                w_speed = round(get_speed(w), 2)

                # walker lane type
                waypoint = self.map.get_waypoint(w_trans.location, project_to_road=True, lane_type=(carla.LaneType.Driving | carla.LaneType.Sidewalk))

                if waypoint.lane_type == carla.LaneType.Driving:
                    w_lane = 1
                elif waypoint.lane_type == carla.LaneType.Sidewalk or waypoint.lane_type == carla.LaneType.Shoulder:
                    w_lane = 2
                if at_crosswalk(w_trans.location.x, w_trans.location.y):
                    w_lane = 3


                # data normalization
                w_relative_heading_norm = normalize_data(data = w_relative_heading, min_val = 0, max_val = 360.0)
                w_relative_heading_norm = round(w_relative_heading_norm, 2)
                w_speed_norm = normalize_data(data = w_speed, min_val = 0, max_val = self.config.max_speed)
                w_speed_norm = round(w_speed_norm, 2)
                w_lane_norm = normalize_data(data = w_lane, min_val = 0, max_val = 3)
                w_lane_norm = round(w_lane_norm, 2)
                w_lane_norm = round(w_lane_norm, 2)

                # state update for walker w-> occupancy, heading, speed
                environment_state[x_discrete, y_discrete,:] = [1.0, w_relative_heading_norm, w_speed_norm, w_lane_norm] 


        state_tensor = []
        state_tensor.append(ego_vehicle_state)
        state_tensor.append(environment_state)
        return state_tensor


    def get_reward(self):
        done = 0
        info = 'None'
        total_reward = d_reward = nc_reward = c_reward = 0.0

        # reward for speed
        ego_vehicle_speed = self.get_ego_vehicle_speed(kmph = False)
        ego_vehicle_speed = round(ego_vehicle_speed, 2)

        target_speed = self.config.target_speed
        if ego_vehicle_speed > 0.0 and ego_vehicle_speed <= target_speed:
            d_reward = (target_speed - abs(target_speed - ego_vehicle_speed))/target_speed
        elif ego_vehicle_speed <= 0.0:
            d_reward = -1.0
        elif ego_vehicle_speed > target_speed:
            d_reward = -1.0

        # reward for collision
        walker_list = self.world.get_actors().filter('walker.pedestrian.*')
        nc_dist_max = (ego_vehicle_speed*ego_vehicle_speed)/(2*2.5) + 2.5
        nc_dist_min = (ego_vehicle_speed*ego_vehicle_speed)/(2*7.5) + 2.5
        nc_dist_max = round(nc_dist_max, 2)
        nc_dist_min = round(nc_dist_min, 2)
        collision, near_collision, walker, distance = self.find_collision(walker_list = walker_list, range = nc_dist_max)
        if near_collision:
            nc_reward = normalize_data(data = distance, min_val = nc_dist_max, max_val = 0)

            if distance >= nc_dist_min:
                nc_reward = -2 * nc_reward
            elif distance < nc_dist_min:
                nc_reward = -4 * nc_reward

            nc_reward = round(nc_reward, 4)

        elif collision:
            if ego_vehicle_speed > 0.0:
                c_reward = -10
                done = 1
                info = 'Normal Collision'
            else:
                done = 1
                info = 'Pedestrian Collision'
           

        # check goal reached
        ego_vehicle_trans = self.get_ego_vehicle_transform()
        goal_trans = carla.Transform(carla.Location(x = self.config.goal_x, y = self.config.goal_y, z = ego_vehicle_trans.location.z))
        self.world.debug.draw_string(goal_trans.location, 'O', draw_shadow=False, color=carla.Color(r=255, g=0, b=0), life_time=10.0,persistent_lines=True)
        dist = compute_distance(location_1 = ego_vehicle_trans.location, location_2 = goal_trans.location)

        if dist <= 10:
            done = 1
            info = 'Goal Reached'

        # total_reward = d_reward + c_reward + nc_reward
        # total_reward = round(total_reward, 4)

        if collision:
            total_reward = c_reward
        elif near_collision:
            total_reward = nc_reward
        else:
            total_reward = d_reward

        total_reward = round(total_reward, 4)


        return total_reward, done, info


    def orientation(self, p, q, r):
        val = ((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1]))
        if val == 0 : return 0
        return 1 if val > 0 else -1


    def compute_bounding_box_distance(self, entity_one, entity_two):
        dist = compute_distance(entity_one.get_location(), entity_two.get_location())
        final_dist = dist - max(entity_one.bounding_box.extent.y, entity_one.bounding_box.extent.x) - max(entity_two.bounding_box.extent.y, entity_two.bounding_box.extent.x)
        return final_dist


    def find_collision(self, walker_list, range):
        collision = near_collision = False
        walker = None
        distance = 100.0

        ego_vehicle = self.get_ego_vehicle()

        if DEBUG: self.world.debug.draw_box(carla.BoundingBox(ego_vehicle.get_transform().location, ego_vehicle.bounding_box.extent), ego_vehicle.get_transform().rotation, 0.1, carla.Color(255,255,0,0), 0.10) 

        walker_list = [w for w in walker_list if self.compute_bounding_box_distance(entity_one = w, entity_two = ego_vehicle) <= range]

        # iterate over the list
        for target_walker in walker_list:
            if DEBUG: self.world.debug.draw_box(carla.BoundingBox(target_walker.get_transform().location, target_walker.bounding_box.extent), target_walker.get_transform().rotation, 0.1, carla.Color(0,0,0,255), 0.1)

            # check if walker is on driving lane
            target_wp = self.map.get_waypoint(target_walker.get_transform().location, project_to_road = True, lane_type = (carla.LaneType.Driving | carla.LaneType.Sidewalk))
            if target_wp.lane_type != carla.LaneType.Driving:
                continue

            if DEBUG: self.world.debug.draw_box(carla.BoundingBox(target_walker.get_transform().location, target_walker.bounding_box.extent), target_walker.get_transform().rotation, 0.1, carla.Color(255,0,0,255), 0.1)
    
            walker_dist = self.compute_bounding_box_distance(entity_one = target_walker, entity_two = ego_vehicle)
            walker_dist = round(walker_dist, 4)

            # check for collision
            if walker_dist <= 0.1:
                if DEBUG: self.world.debug.draw_box(carla.BoundingBox(target_walker.get_transform().location, target_walker.bounding_box.extent), target_walker.get_transform().rotation, 0.1, carla.Color(0,0,255,255), 0.1)
                collision = True
                walker = target_walker
                return (collision, near_collision, walker, distance)

            # check for near collision

            # same or next lane
            target_walker_relative_position = compute_relative_position(source_transform = ego_vehicle.get_transform(), destination_transform = target_walker.get_transform())
            if (target_walker_relative_position[1] >= -2.0 and target_walker_relative_position[1] <= 2.0):
                if DEBUG: self.world.debug.draw_box(carla.BoundingBox(target_walker.get_transform().location, target_walker.bounding_box.extent), target_walker.get_transform().rotation, 0.1, carla.Color(0,255,0,255), 0.1)
                if distance > walker_dist:
                    near_collision = True
                    distance = walker_dist
                    walker = target_walker

            elif (target_walker_relative_position[1] >= -8.0 and target_walker_relative_position[1] <= 2.0) and \
                ray_intersection(p1 = target_walker.get_transform().location, p2 = ego_vehicle.get_transform().location, n1 = target_walker.get_transform().get_forward_vector(), n2 = ego_vehicle.get_transform().get_forward_vector()):
                if DEBUG: self.world.debug.draw_box(carla.BoundingBox(target_walker.get_transform().location, target_walker.bounding_box.extent), target_walker.get_transform().rotation, 0.1, carla.Color(0,255,0,255), 0.1)
                if distance > walker_dist:
                    near_collision = True
                    distance = walker_dist
                    walker = target_walker

                        # ego_veh_forward_vector = ego_vehicle_trans.get_forward_vector()
            # walker_forward_vector = target_walker_trans.get_forward_vector()
            # ego_veh_loc = ego_vehicle_trans.location
            # p1_x = ego_veh_loc.x
            # p1_y = ego_veh_loc.y
            # p2_x = target_walker_loc.x
            # p2_y = target_walker_loc.y
            # n1_x = ego_veh_forward_vector.x
            # n1_y = ego_veh_forward_vector.y
            # n2_x = walker_forward_vector.x
            # n2_y = walker_forward_vector.y
            # u = (p1_y * n2_x + n2_y * p2_x - p2_y * n2_x - n2_y * p1_x) / (n1_x * n2_y - n1_y * n2_x)
            # v = (p1_x + n1_x * u - p2_x) / n2_x
            # #print(u, v)





        # ego_vehicle_trans = self.get_ego_vehicle_transform()
        # ego_vehicle_wp = self.map.get_waypoint(ego_vehicle_trans.location)
        # ego_vehicle_bb = self.get_ego_vehicle_bounding_box()

        # self.world.debug.draw_box(carla.BoundingBox(ego_vehicle_trans.location, ego_vehicle_bb.extent), ego_vehicle_trans.rotation, 0.1,  carla.Color(255,255,0,0), 0.10)
        # self.world.debug.draw_arrow(ego_vehicle_trans.location, ego_vehicle_trans.location + ego_vehicle_trans.get_forward_vector()*20,thickness=0.05, arrow_size=0.1, color=carla.Color(255,255,255,255), life_time=0.1)


        # def dist(w): 
        #     #return w.get_location().distance(ego_vehicle_trans.location)
        #     return compute_distance(w.get_location(), ego_vehicle_trans.location)
        # walker_list = [w for w in walker_list if dist(w) <= 10.0] 
        # print(len(walker_list))     

        # for target_walker in walker_list:
        #     target_walker_trans = target_walker.get_transform()
        #     target_wp = self.map.get_waypoint(target_walker_trans.location, project_to_road = True, lane_type = (carla.LaneType.Driving | carla.LaneType.Sidewalk))
        #     self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(0,0,0,255), 0.1)
        # #     self.world.debug.draw_arrow(target_walker_trans.location, target_walker_trans.location + target_walker_trans.get_forward_vector()*10,thickness=0.05, arrow_size=0.1, color=carla.Color(255,255,255,255), life_time=0.1)

        # #     #print(target_wp.lane_type)

        #     if target_wp.lane_type != carla.LaneType.Driving:
        #         continue

        #     self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(255,0,0,255), 0.1)

        #     #walker_dist = target_walker.get_location().distance(ego_vehicle_trans.location)
        #     walker_dist = compute_distance(target_walker_trans.location, ego_vehicle_trans.location)

        #     # check for collision
        #     if (walker_dist - max(target_walker.bounding_box.extent.y, target_walker.bounding_box.extent.x) - max(ego_vehicle_bb.extent.y, ego_vehicle_bb.extent.x)) <= 0.1:
        #         self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(255,0,0,255), 0.10)
        #         collision = True
        #         distance = walker_dist
        #         walker = target_walker
        #         return (collision, near_collision, walker, distance)


        #     #     final_dist = distance - max(target_walker.bounding_box.extent.y, target_walker.bounding_box.extent.x) - max(ego_vehicle_bb.extent.y, ego_vehicle_bb.extent.x)
        #     #     self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(0,0,0,255), 0.10)

        #     target_walker_relative_position = compute_relative_position(source_transform = ego_vehicle_trans, destination_transform = target_walker_trans)
        #     # #print(target_walker_relative_position)

        #     # check if within x,y range
        #     # for same lane
        #     if target_walker_relative_position[0] <= range and target_walker_relative_position[1] >= -3.0 and target_walker_relative_position[1] <= 3.0 or \
        #        (target_walker_relative_position[0] <= config.nc_distance_threshold and target_walker_relative_position[1] >= -8.0 and target_walker_relative_position[1] <= 3.0 and \
        #         ray_intersection(p1 = ego_vehicle_trans.location, p2 = target_walker_trans.location, n1 = ego_vehicle_trans.get_forward_vector(), n2 = target_walker_trans.get_forward_vector())):
        #             self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(255,255,255,255), 0.10)
                
        #             if walker_dist < distance:

        #                 near_collision = True
        #                 distance = walker_dist
        #                 walker = target_walker   

        
        if DEBUG and walker is not None: self.world.debug.draw_box(carla.BoundingBox(walker.get_transform().location, walker.bounding_box.extent), walker.get_transform().rotation, 0.1,  carla.Color(0,255,255,255), 0.1)    
        
        return (collision, near_collision, walker, distance)


            # # check for heading direction
            # self.world.debug.draw_arrow(target_walker_trans.location, target_walker_trans.location + target_walker_trans.get_forward_vector()*10,thickness=0.05, arrow_size=0.1, color=carla.Color(255,255,255,255), life_time=0.1)

            # if not ray_intersection(p1 = ego_vehicle_trans.location, p2 = target_walker_trans.location, n1 = ego_vehicle_trans.get_forward_vector(), n2 = target_walker_trans.get_forward_vector()):
            #     continue
            
            # self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(255,255,255,255), 0.10)

            # #check if possible collision
            


            # if target_wp.lane_type != carla.LaneType.Driving:
            #     continue

            # if is_within_distance_ahead(target_transform = target_walker_trans, current_transform = ego_vehicle_trans, max_distance = 10.0):
            #     self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(255,255,255,255), 0.10)



            #self.world.debug.draw_string(target_wp.transform.location, 'O', draw_shadow=False, color=carla.Color(r=255, g=0, b=0), life_time=0.1,persistent_lines=True)
            #next_wp = self.planner.local_planner.get_incoming_waypoint_and_direction(steps=5)[0]
            #self.world.debug.draw_string(next_wp.transform.location, 'O', draw_shadow=False, color=carla.Color(r=255, g=0, b=0), life_time=0.1,persistent_lines=True)
            # print(ego_vehicle_wp.lane_id, target_wp.lane_id)
            # print(ego_vehicle_wp.road_id, target_wp.road_id)
            # print('---------------------------------------')

            # If same lane
            #if target_wp.lane_type == carla.LaneType.Driving and target_wp.lane_id != ego_vehicle_wp.lane_id:


            # target_walker_loc = target_walker.get_location()
            # target_walker_trans = target_walker.get_transform()
            # #print(target_walker_trans.get_forward_vector())
            # # If the object is not in our next or current lane it's not an obstacle

            # self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(255,255,255,255), 0.10)
            # self.world.debug.draw_arrow(target_walker_trans.location, target_walker_trans.location + target_walker_trans.get_forward_vector()*10,thickness=0.05, arrow_size=0.1, color=carla.Color(255,255,255,255), life_time=0.1)

            # ego_veh_forward_vector = ego_vehicle_trans.get_forward_vector()
            # walker_forward_vector = target_walker_trans.get_forward_vector()
            # ego_veh_loc = ego_vehicle_trans.location
            # p1_x = ego_veh_loc.x
            # p1_y = ego_veh_loc.y
            # p2_x = target_walker_loc.x
            # p2_y = target_walker_loc.y
            # n1_x = ego_veh_forward_vector.x
            # n1_y = ego_veh_forward_vector.y
            # n2_x = walker_forward_vector.x
            # n2_y = walker_forward_vector.y
            # u = (p1_y * n2_x + n2_y * p2_x - p2_y * n2_x - n2_y * p1_x) / (n1_x * n2_y - n1_y * n2_x)
            # v = (p1_x + n1_x * u - p2_x) / n2_x
            # #print(u, v)
            # print(ego_veh_forward_vector, walker_forward_vector)
            # target_vector = np.array([target_walker_trans.location.x - ego_vehicle_trans.location.x, target_walker_trans.location.y - ego_vehicle_trans.location.y])
            # norm_target = np.linalg.norm(target_vector)
            # vec_2 = np.array([ego_vehicle_trans.get_forward_vector().x, ego_vehicle_trans.get_forward_vector().y])
            # vec_1 = np.array([target_walker_trans.get_forward_vector().x, target_walker_trans.get_forward_vector().y])
            # print(math.degrees(math.acos(np.clip(np.dot(vec_2, target_vector) / norm_target, -1., 1.))))
            #if np.cross(vec_1, vec_2) < 0.0:
            #    self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(0,0,0,255), 0.10)


            # target_wpt = self.map.get_waypoint(target_walker_loc, project_to_road = True, lane_type = (carla.LaneType.Driving | carla.LaneType.Sidewalk | carla.LaneType.Shoulder))
            # if target_wpt is None:
            #     self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(0,0,0,255), 0.10)

            # if target_wpt.lane_type != carla.LaneType.Driving or \
            #         target_wpt.lane_id != ego_vehicle_wp.lane_id:
            #     continue

            # if is_within_distance(target_walker_loc, ego_vehicle_trans.location,
            #                       ego_vehicle_trans.rotation.yaw,
            #                       20.0, 90.0, 0.0):
            #     distance = compute_distance(target_walker_loc, ego_vehicle_trans.location)

            #     final_dist = distance - max(target_walker.bounding_box.extent.y, target_walker.bounding_box.extent.x) - max(ego_vehicle_bb.extent.y, ego_vehicle_bb.extent.x)
            #     self.world.debug.draw_box(carla.BoundingBox(target_walker_trans.location, target_walker.bounding_box.extent), target_walker_trans.rotation, 0.1,  carla.Color(0,0,0,255), 0.10)

        # for e in entity_list:
        #     e_trans = e.get_transform()
        #     e_relative_position = compute_relative_position(source_transform = ego_vehicle_trans, destination_transform = e_trans)

        #     self.world.debug.draw_box(carla.BoundingBox(e_trans.location, e.bounding_box.extent), e_trans.rotation, 0.1,  carla.Color(255,0,0,0), 0.10)

        #return collision, near_collision


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


    def render(self, model_output = None, speed = 0, grid = None):
        if self.renderer is not None and self.rgb_image is not None: 
            #self.renderer.render_image(image = self.rgb_image, image_frame = self.rgb_image_frame, model_output = model_output, speed = speed, grid = grid)
            self.renderer.render(image = self.rgb_image, q_values = model_output, grid = grid, speed = speed)


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
        for i in range(5):
            self.take_action(action = 3)


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


    def find_lane_type(self, wp, trans):
        lane = 1
        if wp.lane_type == carla.LaneType.Driving:
            lane = 1
        elif wp.lane_type == carla.LaneType.Sidewalk or wp.lane_type == carla.LaneType.Shoulder:
            lane = 2
        if at_crosswalk(trans.location.x, trans.location.y):
            lane = 3

        return lane






