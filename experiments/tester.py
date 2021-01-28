import os
import torch
import time

DEBUG = 0

class Tester:
    def __init__(self, env, agent, spawner, params, exp_dir):
        self.env = env
        self.agent = agent
        self.spawner = spawner
        self.params = params
        self.epsilon = 0

        # checkpoint directory
        self.checkpoint_dir = os.path.join(exp_dir, 'checkpoints')
        self.load_checkpoint()


    def test(self):

        collision_free = 0

        for ep in range(self.params.testing_episodes):
            state = self.env.reset(type = 'soft')
            #self.spawner.reset(config = self.env.config, spawn_points = self.env.walker_spawn_points, ev_id = self.env.get_ego_vehicle_id())
            episode_steps = 0

            for step in range(self.params.testing_steps_per_episode): 
                # Select action
                if DEBUG:
                    action = input('Enter action: ')
                    action = int(action)
                else:
                    #input('Enter: ')
                    action, action_values = self.agent.pick_action(state, 0)
                    #print(action_values)
                time.sleep(0.1)

                # Execute action for n times
                #self.spawner.run_step(step) # running spawner step

                for i in range(0, self.params.action_repeat):
                    next_state, reward, done, info = self.env.step(action = action, action_values = action_values)
                    #print('state: ', next_state[0])
                    #print('speed: ', self.env.get_ego_vehicle_speed(kmph = False))
                    #print('action: ', action)
                    #print('reward: ', reward)

                state = next_state
                episode_steps += 1

                if done:
                    if info != 'NormalCollision':
                        collision_free += 1 

                    break


            # Print details of the episode
            print("-----------------------------------------------------------------------------------")
            print("Episode: %d, Episode_Steps: %d, Info: %s" % (ep, episode_steps, info))
            print("-----------------------------------------------------------------------------------")

            #self.spawner.close()
            #self.env.close()


    def load_checkpoint(self):
        # load training parameters
        checkpoint = torch.load(self.checkpoint_dir + '/model_and_parameters.pth')

        # Load network weights and biases
        self.agent.local_network.load_state_dict(checkpoint['state_dict'])
        self.agent.target_network.load_state_dict(checkpoint['state_dict'])
        self.agent.optimizer.load_state_dict(checkpoint['optimizer'])

        self.agent.local_network.eval()
        self.agent.target_network.eval()


    def close(self):
        self.env.close()



