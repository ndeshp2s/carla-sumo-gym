point_spacing = 10

walker_spawn_points = []

for i in range(15, 90, point_spacing):
    spawn_point = carla.Transform(carla.Location(x=i,y=-5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
    walker_spawn_points.append(spawn_point)

    spawn_point = carla.Transform(carla.Location(x=i,y=5.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
    walker_spawn_points.append(spawn_point)

spawn_point = carla.Transform(carla.Location(x=11,y=-5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=9,y=-5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)

spawn_point = carla.Transform(carla.Location(x=11,y=5.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=9,y=5.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)


spawn_point = carla.Transform(carla.Location(x=12,y=44.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=9,y=44.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)

spawn_point = carla.Transform(carla.Location(x=12,y=55.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=9,y=55.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)



for i in range(-185, -15, point_spacing):
    spawn_point = carla.Transform(carla.Location(x=i,y=44.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
    walker_spawn_points.append(spawn_point)  

    spawn_point = carla.Transform(carla.Location(x=i,y=55.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
    walker_spawn_points.append(spawn_point)  


spawn_point = carla.Transform(carla.Location(x=-11,y=-5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-8,y=-5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)

spawn_point = carla.Transform(carla.Location(x=-11,y=5.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-8,y=5.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)


spawn_point = carla.Transform(carla.Location(x=-12,y=44.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-9,y=44.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)


spawn_point = carla.Transform(carla.Location(x=-12,y=55.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-9,y=55.5,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)



spawn_point = carla.Transform(carla.Location(x=5.5,y=61,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-5.5,y=61,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)


for i in range(20, 43, point_spacing):

  spawn_point = carla.Transform(carla.Location(x=5.5,y=i,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
  walker_spawn_points.append(spawn_point)  
  spawn_point = carla.Transform(carla.Location(x=-5.5,y=i,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
  walker_spawn_points.append(spawn_point)  

spawn_point = carla.Transform(carla.Location(x=5.5,y=9,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point) 
spawn_point = carla.Transform(carla.Location(x=5.5,y=11,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=5.5,y=13,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point) 


spawn_point = carla.Transform(carla.Location(x=5.5,y=38,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=5.5,y=37,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point) 


spawn_point = carla.Transform(carla.Location(x=-5.5,y=9,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-5.5,y=11,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-5.5,y=13,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point) 


spawn_point = carla.Transform(carla.Location(x=-5.5,y=40,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-5.5,y=38,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point) 
spawn_point = carla.Transform(carla.Location(x=-5.5,y=37,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)     


spawn_point = carla.Transform(carla.Location(x=5.5,y=-10,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=5.5,y=-12,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point) 

spawn_point = carla.Transform(carla.Location(x=-5.5,y=-10,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point)
spawn_point = carla.Transform(carla.Location(x=-5.5,y=-12,z=0.5), carla.Rotation(yaw=0, pitch=0, roll=0))
walker_spawn_points.append(spawn_point) 