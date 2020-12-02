from rl_agents.q_learning.dqn import DQNAgent
from neural_networks.cnn import NeuralNetwork

class DDQNAgent(DQNAgent):
    def __init__(self, state_size = 0, action_size = 0, hyperparameters = None):
        DQNAgent.__init__(self, state_size = state_size, action_size = action_size, hyperparameters = hyperparameters)
        # Initialise Q-Network
        self.target_network = NeuralNetwork(self.state_dim, self.action_dim).to(self.device)
        self.hard_update_target_network()

    def compute_predicted_q_next(self, next_states):
        # Find the index of action (from local network) with maximum q value 
        max_action_index = self.local_network(next_states).detach().argmax(1)
        # Get the q value (from local network) corrsponding to best action in next state
        q_next_predicted = self.target_network(next_states).gather(1, max_action_index.unsqueeze(1)) 
        return q_next_predicted

    def hard_update_target_network(self):
        self.target_network.load_state_dict(self.local_network.state_dict())