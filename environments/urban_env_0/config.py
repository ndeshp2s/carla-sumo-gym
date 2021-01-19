### sumo related ###

sumo_gui = False

# ego vehicle related
#  start positon (in sumo)
start_position = 60.0
goal_position = 90.0
ev_type = 'vehicle.audi.etron'
# goal position (in carla)
goal_x = -140.0
goal_y = 48.25

max_speed = 12 # in mps
target_speed = 8 # in mps



### carla simulation related ### 

display = True
rendering = True
synchronous = True
town = 'Town11'
fps = 10.0
rendering_screen_x = 720
rendering_screen_y = 720

# sensor related
rgb_sensor = True
rgb_size_x = '1920'
rgb_size_y = '1080'
rgb_fov = '110'
rgb_loc_x = -8.0
rgb_loc_y = 0.0
rgb_loc_z = 4.5

# observation space related
grid_height = 30
grid_width = 20
features = 4

grid_height_min = -4
grid_height_max = 25

grid_width_min = -10
grid_width_max = 9

# action space related
N_DISCRETE_ACTIONS = 4


### spawner related ###
spawner_frequency = 10
number_of_walkers = 20
walker_spawn_distance_maximum = 50.0
walker_spawn_distance_minimum = 5.0
walker_allowed_distance_maximum = 55.0
walker_allowed_distance_minimum = 0.0
walker_pedestrians_crossing = 0.7
walker_pedestrians_crossing_illegal = 0.1

maximum_distance_pedestrian = 40.0
minimum_distance_pedestrian = 0.0
pedestrian_spawn_point_maximum = 30.0
pedestrian_spawn_point_minimum = 8.0
number_of_pedestrians = 1
pedestrian_crossing_legal = 1.0
pedestrian_crossing_illegal = 0.0

# reward related
nc_distance_threshold = 20.0


# Spawner related
num_of_ped = 15
num_of_veh = 0
percentage_pedestrians_crossing = 0.7
percentage_pedestrians_crossing_illegal = 0.1
ped_spawn_min_dist = 8.0
ped_spawn_max_dist = 30.0
ped_max_dist = 35.0
ped_min_dist = 0.0
