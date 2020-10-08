### sumo related ###

sumo_gui = False

# ego vehicle start positon (in sumo)
start_position = 50.0
goal_position = 90.0
ev_type = 'vehicle.audi.etron'



### carla simulation related ### 

display = True
rendering = True
synchronous = True
town = 'Town11'
fps = 10.0

# sensor related
rgb_sensor = True
rgb_size_x = '1920'
rgb_size_y = '1080'
rgb_fov = '110'
rgb_loc_x = -6.5
rgb_loc_y = 0.0
rgb_loc_z = 4.0

# rendering related
render = False
screen_x = 720
screen_y = 720



### spawner related ###

maximum_distance_pedestrian = 40.0
minimum_distance_pedestrian = 0.0
pedestrian_spawn_point_maximum = 30.0
pedestrian_spawn_point_minimum = 8.0
number_of_pedestrians = 1
pedestrian_crossing_legal = 1.0
pedestrian_crossing_illegal = 0.0
