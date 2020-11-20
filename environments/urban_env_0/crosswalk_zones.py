import sys
import glob
import os
import time

try:
    sys.path.append(glob.glob('/home/niranjan/carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
    
import carla

from shapely.geometry import Point, Polygon



crosswalks = []
corner = carla.Location()

## Junction 1
# crosswalk 1
zone = []
corner = carla.Location(x = 7.6, y = -4.6, z = 0.1)
zone.append(corner)
corner = carla.Location(x = 7.6, y = 5.0, z = 0.1)
zone.append(corner)
corner = carla.Location(x = 3.4, y = 5.0, z = 0.1)
zone.append(corner)
corner = carla.Location(x = 3.4, y = -4.6, z = 0.1)
zone.append(corner)
crosswalks.append(zone)

# crosswalk 2
zone = []
corner = carla.Location(x = 4.6, y = -3.2, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -5.0, y = -3.2, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -5.0, y = -7.4, z = 0.1)
zone.append(corner)
corner = carla.Location(x = 4.6, y = -7.4, z = 0.1)
zone.append(corner)
crosswalks.append(zone)

# crosswalk 3
zone = []
corner = carla.Location(x = -7.8, y = -4.6, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -7.8, y = 5.0, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -3.6, y = 5.0, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -3.6, y = -4.6, z = 0.1)
zone.append(corner)
crosswalks.append(zone)

# crosswalk 4
zone = []
corner = carla.Location(x = 4.6, y = 3.8, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -5.0, y = 3.8, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -5.0, y = 8.0, z = 0.1)
zone.append(corner)
corner = carla.Location(x = 4.6, y = 8.0, z = 0.1)
zone.append(corner)
crosswalks.append(zone)



## Junction 2
# crosswalk 1
zone = []
corner = carla.Location(x = 7.7, y = 45.1, z = 0.1)
zone.append(corner)
corner = carla.Location(x = 7.7, y = 54.7, z = 0.1)
zone.append(corner)
corner = carla.Location(x = 3.5, y = 54.7, z = 0.1)
zone.append(corner)
corner = carla.Location(x = 3.5, y = 45.1, z = 0.1)
zone.append(corner)
crosswalks.append(zone)

# crosswalk 2
zone = []
corner = carla.Location(x = 4.6, y = 46.5, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -5.0, y = 46.5, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -5.0, y = 42.3, z = 0.1)
zone.append(corner)
corner = carla.Location(x = 4.6, y = 42.3, z = 0.1)
zone.append(corner)
crosswalks.append(zone)

# crosswalk 3
zone = []
corner = carla.Location(x = -7.7, y = 45.1, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -7.7, y = 54.7, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -3.5, y = 54.7, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -3.5, y = 45.1, z = 0.1)
zone.append(corner)
crosswalks.append(zone)

# crosswalk 4
zone = []
corner = carla.Location(x = 4.6, y = 53.5, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -5.0, y = 53.5, z = 0.1)
zone.append(corner)
corner = carla.Location(x = -5.0, y = 57.7, z = 0.1)
zone.append(corner)
corner = carla.Location(x = 4.6, y = 57.7, z = 0.1)
zone.append(corner)
crosswalks.append(zone)


def at_crosswalk(x, y):
    within = False
    point = Point(x, y)

    coords = []
    for zones in crosswalks:
        coords = []
        for corner in zones:
            coords.append((corner.x, corner.y))
        
        poly = Polygon(coords)
        
        if point.within(poly):
            within =  True

        coords.clear()

    return within


########## Testing ###########
DEBUG = 0

if DEBUG:
	# Connect to client
	client = carla.Client('127.0.0.1', 2000)
	client.set_timeout(2.0)
	world = client.get_world()

# Display zones
if DEBUG:
    print(len(crosswalks))
    for z in crosswalks:
        for c in z:
            world.debug.draw_string(c, 'O', draw_shadow = False, color = carla.Color(r = 255, g = 0, b = 0), life_time = 10.0, persistent_lines = True)
            #time.sleep(1.0)
        world.debug.draw_line(z[0], z[1], life_time = 100.0)
        world.debug.draw_line(z[1], z[2], life_time = 100.0)
        world.debug.draw_line(z[2], z[3], life_time = 100.0)
        world.debug.draw_line(z[3], z[0], life_time = 100.0)



if DEBUG:
    p = carla.Location(x=-3.5, y=4.3, z = 0.0)
    world.debug.draw_string(p, 'X', draw_shadow = False, color = carla.Color(r = 0, g = 0, b = 255), life_time = 10.0, persistent_lines = True)
    print(within_crosswalk(p.x, p.y))