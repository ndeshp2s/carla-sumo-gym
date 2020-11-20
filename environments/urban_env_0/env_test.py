import sys, os
import time
import gym
import environments
from environments.spawner import Spawner



# Test for env-0
def test_one():
	env0 = gym.make('Urban-v0')


	try:
		for i in range(10):
			env0.reset()
			for j in range(1000):
				action = input('Enter action: ')
				action = int(action)
				env0.step(action = action)
				time.sleep(0.2)

				#print('ev id: ', env0.get_ego_vehicle_id())

	except KeyboardInterrupt:
		print('Closing')

	finally:
		env0.close()




# Test for env-0 with spawner
def test_two():
	from environments.urban_env_0 import config

	env0 = gym.make('Urban-v0')
	spawner = Spawner()


	try:
		for i in range(10):
			env0.reset()
			time.sleep(2.0)
			spawner.reset(config = env0.config, spawn_points = env0.walker_spawn_points, ev_id = env0.get_ego_vehicle_id())
			
			for j in range(1000):
				action = input('Enter action: ')
				action = int(action)
				print(action)
				env0.step(action = action)
				spawner.run_step()
				time.sleep(0.2)

				#print('ev id: ', env0.get_ego_vehicle_id())

	except KeyboardInterrupt:
		print('Closing')

	finally:
		env0.close()





if __name__ == "__main__":
    #test_one()
    test_two()
    print("Test 1 passed")
