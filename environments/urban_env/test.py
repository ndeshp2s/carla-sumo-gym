import sys, os
import gym
import environments

# Test for env-0
env0 = gym.make('Urban-v0')


try:
	for i in range(10):
		env0.reset()
		for j in range(10):
			env0.tick()

except KeyboardInterrupt:
	print('Closing')
	# try:
	# 	env0.close()
	# 	sys.exit(0)
	# except SystemExit:
	# 	env0.close()
	# 	ss.exit(0)
finally:
	env0.close()
