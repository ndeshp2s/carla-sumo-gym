import sys, os
import time
import gym
import environments

# Test for env-0
env0 = gym.make('Urban-v0')


try:
	for i in range(10):
		env0.reset()
		for j in range(1000):
			action = input('Enter action: ')
			action = int(action)
			env0.step(action = action)
			time.sleep(0.1)

			#print('ev id: ', env0.get_ego_vehicle_id())

except KeyboardInterrupt:
	print('Closing')

finally:
	env0.close()
