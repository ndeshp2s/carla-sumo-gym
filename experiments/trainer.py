import os
import shutil
from torch.utils.tensorboard import SummaryWriter

from utils.epsilon_decay import EpsilonDecay

DEBUG = 0
class Trainer:
    def __init__(self, env, agent, spawner, params, exp_dir):
        self.env = env
        self.agent = agent
        self.spawner = spawner
        self.params = params

        self.epsilon_decay = EpsilonDecay(epsilon_start = self.params.hyperparameters['epsilon_start'], epsilon_end = self.params.hyperparameters['epsilon_end'], \
                                          epsilon_decay = self.params.hyperparameters['epsilon_decay'], total_steps = self.params.hyperparameters['epsilon_steps'])

        log_dir = os.path.join(exp_dir, 'logs')
        if os.path.exists(log_dir):
            shutil.rmtree(log_dir)
            os.makedirs(log_dir)

        self.writer = SummaryWriter(log_dir = log_dir)



    def train(self, pre_eps = -1):
        epsilon = self.params.hyperparameters['epsilon_start']
        total_steps = 0

        for ep in range(pre_eps + 1, self.params.training_episodes):
    
            state = self.env.reset()
            #self.spawner.reset(config = self.env.config, spawn_points = self.env.walker_spawn_points, ev_id = self.env.get_ego_vehicle_id())

            episode_reward = 0 
            episode_steps = 0           

            for step in range(self.params.training_steps_per_episode):                

                # Select action
                if DEBUG:
                    action = input('Enter action: ')
                    action = int(action)
                else:
                    action = self.agent.pick_action(state, epsilon)

                # Execute action for n times
                #self.spawner.run_step(step) # running spawner step

                for i in range(0, self.params.action_repeat):
                    next_state, reward, done = self.env.step(action)

                # Add experience to memory of local network
                self.agent.add(state = state, action = action, reward = reward, next_state = next_state, done = done)

                # Update parameters
                state = next_state
                episode_reward += reward
                episode_steps += 1
                total_steps += 1

                # compute the loss
                if self.agent.memory.__len__() > self.params.hyperparameters['batch_size']:
                    loss = 0
                    loss = self.agent.learn(batch_size = self.params.hyperparameters['batch_size'])
                    # save the loss
                    self.writer.add_scalar('Loss per step', loss, total_steps)

                    if total_steps % self.params.hyperparameters['target_network_update_frequency']:
                        self.agent.hard_update_target_network()

                if done:
                    #self.spawner.close()
                    self.env.close()
                    break

            # Print details of the episode
            print("--------------------------------------------------------------------")
            print("Episode: %d, Reward: %5f, Loss: %4f" % (ep, episode_reward, loss))
            print("--------------------------------------------------------------------")


            # Save episode reward, steps and loss
            self.writer.add_scalar('Reward per episode', episode_reward, ep)
            self.writer.add_scalar('Steps per episode', episode_steps, ep)

            # epsilon update
            epsilon = self.epsilon_decay.update_linear(current_eps = epsilon)


    def retrain(self):
        None


    def close(self):
        if self.env.server:
            self.spawner.close()
            self.env.close()


