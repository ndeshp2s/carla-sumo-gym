import os
import torch
from torch.utils.tensorboard import SummaryWriter

from utils.epsilon_decay import EpsilonDecay
from utils.misc import create_directory

DEBUG = 0
class Trainer:
    def __init__(self, env, agent, spawner, params, exp_dir, retrain = False):
        self.env = env
        self.agent = agent
        self.spawner = spawner
        self.params = params

        self.epsilon_decay = EpsilonDecay(epsilon_start = self.params.hyperparameters['epsilon_start'], epsilon_end = self.params.hyperparameters['epsilon_end'], \
                                          epsilon_decay = self.params.hyperparameters['epsilon_decay'], total_steps = self.params.hyperparameters['epsilon_steps'])

        self.epsilon = self.params.hyperparameters['epsilon_start']

        log_dir = os.path.join(exp_dir, 'logs')
        if not retrain: create_directory(dir = log_dir)
        self.writer = SummaryWriter(log_dir = log_dir)

        # # checkpoint directory
        self.checkpoint_dir = os.path.join(exp_dir, 'checkpoints')
        if not retrain: create_directory(dir = self.checkpoint_dir)


    def train(self, pre_eps = -1, total_steps = 0):
        
        total_steps = total_steps

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
                    action = 3#self.agent.pick_action(state, self.epsilon)

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
                loss = 0
                if self.agent.memory.__len__() > self.params.hyperparameters['batch_size']:
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
            print("Episode: %d, Reward: %5f, Loss: %4f, Epsilon: %4f" % (ep, episode_reward, loss, self.epsilon))
            print("--------------------------------------------------------------------")


            # Save episode reward, steps and loss
            self.writer.add_scalar('Reward per episode', episode_reward, ep)
            self.writer.add_scalar('Steps per episode', episode_steps, ep)

            # update training parameters
            checkpoint = {'state_dict': self.agent.local_network.state_dict(),
                            'optimizer': self.agent.optimizer.state_dict(),
                            'episode': ep,
                            'epsilon': self.epsilon,
                            'total_steps': total_steps}
            torch.save(checkpoint, self.checkpoint_dir + '/model_and_parameters.pth')

            # epsilon update
            self.epsilon = self.epsilon_decay.update_linear(current_eps = self.epsilon)
            self.writer.add_scalar('Epsilon decay', self.epsilon, ep)


    def retrain(self):
        # load training parameters
        checkpoint = torch.load(self.checkpoint_dir + '/model_and_parameters.pth')
        self.agent.local_network.load_state_dict(checkpoint['state_dict'])
        self.agent.target_network.load_state_dict(checkpoint['state_dict'])
        self.agent.optimizer.load_state_dict(checkpoint['optimizer'])
        previous_episode = checkpoint['episode']
        total_steps = checkpoint['total_steps']
        self.epsilon = checkpoint['epsilon']

        self.agent.local_network.train()
        self.agent.target_network.train()

        self.train(pre_eps = previous_episode, total_steps = total_steps)


    def close(self):
        if self.env.server:
            self.spawner.close()
            self.env.close()


