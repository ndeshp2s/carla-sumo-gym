town = "Town11"
sp_x = 40.0
sp_y = -1.7
sp_z = 0.2
sp_yaw = 180.0
sp_pitch = 0.0
sp_roll = 0.0

ev_bp = 'vehicle.audi.etron'
ev_name = 'hero'
ev_goal_x = -140.0
ev_goal_y = 40.25
ev_goal_z = 0.2
ev_goal_yaw = 180.0

# Sensors
rgb_sensor = False
rgb_size_x = '1920'
rgb_size_y = '1080'
rgb_fov = '110'
rgb_loc_x = -6.5#2.5
rgb_loc_y = 0.0
rgb_loc_z = 4.0#2.0

sem_sensor = False

# Display True
display = False

# Rendering related
render = False
screen_x = 720
screen_y = 720


#ACTIONS = ['forward', 'brake', 'no_action'] #['forward', 'forward_left', 'forward_right', 'brake', 'brake_left', 'brake_right']
ACTIONS = ['accelerate', 'cont', 'decelerate', 'brake']
N_DISCRETE_ACTIONS = 4

# Observation space
num_of_ped = 3
HEIGHT = 1
WIDTH = 4*num_of_ped
N_CHANNELS = 0
grid_height = 45#32#45
grid_width = 30#32#30
features = 4
lane_types = 3# Driving(road)-1, sidewalk(shoulder)-2, crosswalk-3 

x_min = 0
x_max = 45#32#45
x_size = 45#32#45
y_min = -15#-16#15
y_max = 15#16#15
y_size = 30#32#30

# Pedestrian behavior probalities
# Four types of behaviors:
## normal walking
## normal crossing at intersection
## Jaw-walking
## standing on road (group of people standing on road side)
## pedestrian walking on road
ped_beh_prob = [1.0, 0.0, 0.0, 0.0,0.0] # 
ped_max_speed = 3.0

# Spawner related
num_of_ped = 10
num_of_veh = 0
percentage_pedestrians_crossing = 0.7
percentage_pedestrians_crossing_illegal = 0.2
ped_spawn_min_dist = 8.0
ped_spawn_max_dist = 25.0
ped_max_dist = 35.0
ped_min_dist = 0.0