import numpy as np
import random
import torch
import torch.optim as optim
from neural_networks.cnn_2 import NeuralNetwork
from rl_agents.replay_buffer import ReplayBuffer

class DQNAgent:
    def __init__(self, state_size = 0, action_size = 0, hyperparameters = None):

        self.state_dim = state_size
        self.action_dim  = action_size
        self.hyperparameters = hyperparameters

        if self.hyperparameters["use_cuda"]:
            self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        else:
            self.device = "cpu"

        # Initialise Q-Network
        self.local_network = NeuralNetwork(self.state_dim, self.action_dim).to(self.device)
        self.optimizer = optim.Adam(self.local_network.parameters(), lr = self.hyperparameters["learning_rate"])
        self.criterion = torch.nn.MSELoss()

        # Initialise replay memory
        self.buffer = ReplayBuffer(buffer_size = self.hyperparameters["buffer_size"], batch_size = self.hyperparameters["batch_size"])


    def add(self, state, action, reward, next_state, done):
        self.buffer.add_experience(state = state, action = action, reward = reward, next_state = next_state, done = done)


    def learn(self, batch_size = 32, experiences = None, step = 0):
        if experiences is None:
            experiences  = self.buffer.sample(batch_size)

        ego_vehicle_states, environment_states, actions, rewards, ego_vehicle_next_states, environment_next_states, dones = [], [], [], [], [], [], []
        for e in experiences:
            ego_vehicle_states.append(e.state[0])
            environment_states.append(e.state[1])

            actions.append(e.action)
            rewards.append(e.reward)

            ego_vehicle_next_states.append(e.next_state[0])
            environment_next_states.append(e.next_state[1])

            dones.append(e.done)


        ego_vehicle_states = torch.from_numpy(np.array(ego_vehicle_states)).float().to(self.device)
        environment_states = torch.from_numpy(np.array(environment_states)).float().to(self.device)
        actions = torch.from_numpy(np.array(actions)).long().to(self.device)
        rewards = torch.from_numpy(np.array(rewards)).float().to(self.device)
        ego_vehicle_next_states = torch.from_numpy(np.array(ego_vehicle_next_states)).float().to(self.device)
        environment_next_states = torch.from_numpy(np.array(environment_next_states)).float().to(self.device)
        dones = torch.from_numpy(np.array(dones)).float().to(self.device)



        # ego_vehicle_states = torch.from_numpy(np.vstack([e.state[0] for e in experiences if e is not None])).float().to(self.device)
        # environment_states = torch.from_numpy(np.vstack([e.state[1] for e in experiences if e is not None])).float().to(self.device)
        # actions = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).long().to(self.device)
        # rewards = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float().to(self.device)
        # ego_vehicle_next_states = torch.from_numpy(np.vstack([e.next_state[0] for e in experiences if e is not None])).float().to(self.device)
        # environment_next_states = torch.from_numpy(np.vstack([e.next_state[1] for e in experiences if e is not None])).float().to(self.device)
        # dones = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None])).float().to(self.device)

        ## COMPUTE THE LOSS
        q_predicted = self.compute_predicted_q(ego_vehicle_states = ego_vehicle_states, environment_states = environment_states, actions = actions)

        q_target = self.compute_target_q(ego_vehicle_next_states = ego_vehicle_next_states, environment_next_states  = environment_next_states , rewards = rewards, dones = dones)

        # Compute the loss
        loss = self.criterion(q_predicted, q_target)

        # make previous grad zero
        self.optimizer.zero_grad()

        # backward
        loss.backward()

        # Gradient clipping
        for param in self.local_network.parameters():
            param.grad.data.clamp_(-1, 1)

        # update params
        self.optimizer.step()

        return loss.item()


    def compute_predicted_q(self, ego_vehicle_states, environment_states, actions):
        # Get the q value (from local network) corresponding to the action executed
        q_predicted = self.local_network(x1 = ego_vehicle_states, x2 = environment_states).gather(1, actions.unsqueeze(1)).squeeze(1)
        return q_predicted


    def compute_target_q(self, ego_vehicle_next_states, environment_next_states, rewards, dones):
        # Get the q value corrsponding to best action in next state
        q_next_predicted = self.compute_predicted_q_next(ego_vehicle_next_states = ego_vehicle_next_states, environment_next_states  = environment_next_states)
        # Find target q value using Bellmann's equation
        q_target = rewards + (self.hyperparameters["discount_rate"] * q_next_predicted * (1 - dones))
        return q_target


    def compute_predicted_q_next(self, ego_vehicle_next_states, environment_next_states):
        # Find q value for next state
        q_next_predicted_for_all_actions = self.local_network(x1 = ego_vehicle_next_states, x2 = environment_next_states)
        # Find the index of action (from local network) with maximum q value 
        max_action_index = q_next_predicted_for_all_actions.max(1)[1].unsqueeze(1)
        # Get the q value (from local network) corrsponding to best action in next state
        q_next_predicted = q_next_predicted_for_all_actions.gather(1, max_action_index).squeeze(1) 
        return q_next_predicted


    def pick_action(self, state, epsilon):
        ego_vehicle_state_tensor = torch.from_numpy(state[0]).float().unsqueeze(0).to(self.device)
        environment_state_tensor = torch.from_numpy(state[1]).float().unsqueeze(0).to(self.device)

        # Query the network
        action_values = self.local_network.forward(x1 = ego_vehicle_state_tensor, x2 = environment_state_tensor)

        if random.random() > epsilon:
            action = action_values.max(1)[1].item()

        else:
            action = np.random.randint(0, action_values.shape[1])

        return action, action_values[0].squeeze(0)

