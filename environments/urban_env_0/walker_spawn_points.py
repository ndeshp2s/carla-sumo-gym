import sys, glob, os

# carla library
try:
    sys.path.append(glob.glob('../carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla


point_spacing = 4

walker_spawn_points = []
walker_goal_points = []

for i in range(15, 90, point_spacing):
    spawn_point = carla.Transform(carla.Location(x=i,y=-5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
    walker_spawn_points.append(spawn_point)

    spawn_point = carla.Transform(carla.Location(x=i,y=5.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
    walker_spawn_points.append(spawn_point)

spawn_point = carla.Transform(carla.Location(x=11,y=-5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=8,y=-5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)

spawn_point = carla.Transform(carla.Location(x=11,y=5.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=8,y=5.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)



for i in range(9, 25, point_spacing):
  spawn_point = carla.Transform(carla.Location(x=i,y=44.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
  walker_spawn_points.append(spawn_point)
  spawn_point = carla.Transform(carla.Location(x=i,y=55.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
  walker_spawn_points.append(spawn_point)


for i in range(-185, -15, point_spacing):
    spawn_point = carla.Transform(carla.Location(x=i,y=44.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
    walker_spawn_points.append(spawn_point)  

    spawn_point = carla.Transform(carla.Location(x=i,y=55.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
    walker_spawn_points.append(spawn_point)  


spawn_point = carla.Transform(carla.Location(x=-12,y=-5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-9,y=-5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)

spawn_point = carla.Transform(carla.Location(x=-12,y=5.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-9,y=5.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)


spawn_point = carla.Transform(carla.Location(x=-12,y=44.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)



spawn_point = carla.Transform(carla.Location(x=-12,y=55.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)

for i in range(61, 80, point_spacing):
  spawn_point = carla.Transform(carla.Location(x=5.1,y=i,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
  walker_spawn_points.append(spawn_point)
  spawn_point = carla.Transform(carla.Location(x=-5.5,y=i,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
  walker_spawn_points.append(spawn_point)


spawn_point = carla.Transform(carla.Location(x=5.1,y=65,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=5.1,y=69,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=5.1,y=73,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)

spawn_point = carla.Transform(carla.Location(x=-5.5,y=61,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)


for i in range(20, 43, point_spacing):

  spawn_point = carla.Transform(carla.Location(x=5.5,y=i,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
  walker_spawn_points.append(spawn_point)  
  spawn_point = carla.Transform(carla.Location(x=-5.5,y=i,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
  walker_spawn_points.append(spawn_point)  

spawn_point = carla.Transform(carla.Location(x=-5.5,y=13,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point) 
spawn_point = carla.Transform(carla.Location(x=5.5,y=11,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=5.5,y=15,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point) 


spawn_point = carla.Transform(carla.Location(x=-5.5,y=9,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-5.5,y=11,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-5.5,y=13,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point) 



walker_goal_points = walker_spawn_points

DEBUG = 0
#if DEBUG:
    # # Connect to client
    # client = carla.Client('127.0.0.1', 2000)
    # client.set_timeout(2.0)
    # world = client.get_world()

    # location = carla.Location(x=15,y=65, z=0.1)
    # world.debug.draw_string(location, 'O', draw_shadow=False, color=carla.Color(r=255, g=0, b=0), life_time=10.0, persistent_lines=True)
    # location = carla.Location(x=15,y=35,z=0.1)
    # world.debug.draw_string(location, 'O', draw_shadow=False, color=carla.Color(r=255, g=0, b=0), life_time=10.0, persistent_lines=True)
    # location = carla.Location(x=-15,y=65,z=0.1)
    # world.debug.draw_string(location, 'O', draw_shadow=False, color=carla.Color(r=255, g=0, b=0), life_time=10.0, persistent_lines=True)
    # location = carla.Location(x=-15,y=35,z=0.1)
    # world.debug.draw_string(location, 'O', draw_shadow=False, color=carla.Color(r=255, g=0, b=0), life_time=10.0, persistent_lines=True)

if DEBUG:
    # Connect to client
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)
    world = client.get_world()

    for w in walker_spawn_points:
        world.debug.draw_string(w.location, 'O', draw_shadow=False, 
            color=carla.Color(r=255, g=0, b=0), life_time=10.0,
            persistent_lines=True)
