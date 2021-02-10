import numpy as np
import random
import torch
import torch.optim as optim
from neural_networks.lstm import NeuralNetwork
from rl_agents.replay_buffer import ReplayBuffer

class DQNAgent:
    def __init__(self, state_size = 0, action_size = 0, hyperparameters = None):

        self.state_dim = state_size
        self.action_dim  = action_size
        self.hyperparameters = hyperparameters

        # if self.hyperparameters["use_cuda"]:
        #     self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # else:
        self.device = "cpu"

        # Initialise Q-Network
        self.local_network = NeuralNetwork(self.state_dim, self.action_dim).to(self.device)
        self.target_network = NeuralNetwork(self.state_dim, self.action_dim).to(self.device)
        self.hard_update_target_network()
        self.optimizer = optim.Adam(self.local_network.parameters(), lr = self.hyperparameters["learning_rate"], eps = 1e-4)
        self.criterion = torch.nn.MSELoss()

        # Initialise replay memory
        self.buffer = ReplayBuffer(buffer_size = self.hyperparameters["buffer_size"], batch_size = self.hyperparameters["batch_size"])


    def add(self, episode):
        self.buffer.add_experience(episode)


    def learn(self, batch_size = 32, experiences = None, step = 0):
        if experiences is None:
            experiences  = self.buffer.sample(batch_size)

        ego_vehicle_states, environment_states, actions, rewards, ego_vehicle_next_states, environment_next_states, dones = [], [], [], [], [], [], []

        for batch in experiences:
            ev_s, env_s, a, r, ev_ns, env_ns, d = [], [], [], [], [], []
            for episode in batch:
                ev_s.append(episode.state[0])
                env_s.append(episode.state[1])

                a.append(episode.action)
                r.append(episode.reward)

                ev_ns.append(episode.next_state[0])
                env_ns.append(episode.next_state[1])

                d.append(episode.done)

            ego_vehicle_states.append(ev_s)
            environment_states.append(env_s)
            actions.append(a)
            rewards.append(r)
            ego_vehicle_next_states.append(ev_ns)
            environment_next_states.append(env_ns)
            dones.append(d)


        ego_vehicle_states = torch.from_numpy(np.array(ego_vehicle_states)).float().to(self.device)
        environment_states = torch.from_numpy(np.array(environment_states)).float().to(self.device)
        actions = torch.from_numpy(np.array(actions)).long().to(self.device)
        rewards = torch.from_numpy(np.array(rewards)).float().to(self.device)
        ego_vehicle_next_states = torch.from_numpy(np.array(ego_vehicle_next_states)).float().to(self.device)
        environment_next_states = torch.from_numpy(np.array(environment_next_states)).float().to(self.device)
        dones = torch.from_numpy(np.array(dones)).float().to(self.device)

        hidden_ev_s, cell_ev_s = self.local_network.init_hidden_states(batch_size = batch_size, lstm_memory = 32)
        hidden_env_s, cell_env_s = self.local_network.init_hidden_states(batch_size = batch_size, lstm_memory = 256)



        # ego_vehicle_states = torch.from_numpy(np.vstack([e.state[0] for e in experiences if e is not None])).float().to(self.device)
        # environment_states = torch.from_numpy(np.vstack([e.state[1] for e in experiences if e is not None])).float().to(self.device)
        # actions = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).long().to(self.device)
        # rewards = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float().to(self.device)
        # ego_vehicle_next_states = torch.from_numpy(np.vstack([e.next_state[0] for e in experiences if e is not None])).float().to(self.device)
        # environment_next_states = torch.from_numpy(np.vstack([e.next_state[1] for e in experiences if e is not None])).float().to(self.device)
        # dones = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None])).float().to(self.device)

        ## COMPUTE THE LOSS
        #q_predicted = self.compute_predicted_q(ego_vehicle_states = ego_vehicle_states, environment_states = environment_states, actions = actions)

        #q_target = self.compute_target_q(ego_vehicle_next_states = ego_vehicle_next_states, environment_next_states  = environment_next_states , rewards = rewards, dones = dones)

        # Get the q values for all actions from local network
        q_predicted_all = self.local_network.forward(x1 = ego_vehicle_states, x2 = environment_states)
        #Get the q value corresponding to the action executed
        q_predicted = q_predicted_all.gather(dim = 1, index = actions.unsqueeze(dim = 1)).squeeze(dim = 1)
        # Get q values for all the actions of next state
        q_next_predicted_all = self.target_network.forward(x1 = ego_vehicle_next_states, x2 = environment_next_states)
        
        # get q values for the actions of next state from target netwrok
        q_next_target_all = self.target_network.forward(x1 = ego_vehicle_next_states, x2 = environment_next_states)
        # get q value of action with same index as that of the action with maximum q values (from local network)
        q_next_target = q_next_target_all.gather(1, q_next_predicted_all.max(1)[1].unsqueeze(1)).squeeze(1)
        # Find target q value using Bellmann's equation
        q_target = rewards + (self.hyperparameters["discount_rate"] * q_next_target *(1 - dones))




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
        q_target = rewards + (self.hyperparameters["discount_rate"] * q_next_predicted)
        return q_target


    def compute_predicted_q_next(self, ego_vehicle_next_states, environment_next_states):
        # Find q value for next state
        q_next_predicted_for_all_actions = self.local_network(x1 = ego_vehicle_next_states, x2 = environment_next_states)
        # Find the index of action (from local network) with maximum q value 
        max_action_index = q_next_predicted_for_all_actions.max(1)[1].unsqueeze(1)
        # Get the q value (from local network) corrsponding to best action in next state
        q_next_predicted = q_next_predicted_for_all_actions.gather(1, max_action_index).squeeze(1) 
        return q_next_predicted


    def pick_action(self, state, epsilon, hs1, cs1, hs2, cs2):

        ego_vehicle_state_tensor = torch.from_numpy(state[0]).float().unsqueeze(0).to(self.device)
        environment_state_tensor = torch.from_numpy(state[1]).float().unsqueeze(0).to(self.device)

        # Query the network
        model_output = self.local_network.forward(x1 = ego_vehicle_state_tensor, x2 = environment_state_tensor, batch_size = 1, time_step = 1, hs1 = hs1, cs1 = cs1, hs2 = hs2, cs2 = cs2)
        hs_new1 = model_output[1][0]
        cs_new1 = model_output[1][1]
        hs_new2 = model_output[2][0]
        cs_new2 = model_output[2][1]

        if np.random.uniform() > epsilon:
            action = action_values.max(1)[1].item()

        else:
            action = np.random.randint(0, 4)

        return action, hs_new1, cs_new1, hs_new2, cs_new2, model_output[0].squeeze(0)


    def hard_update_target_network(self):
        self.target_network.load_state_dict(self.local_network.state_dict())

