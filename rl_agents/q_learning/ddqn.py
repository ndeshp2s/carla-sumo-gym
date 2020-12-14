from rl_agents.q_learning.dqn import DQNAgent
from neural_networks.cnn_2 import NeuralNetwork

class DDQNAgent(DQNAgent):
    def __init__(self, state_size = 0, action_size = 0, hyperparameters = None):
        DQNAgent.__init__(self, state_size = state_size, action_size = action_size, hyperparameters = hyperparameters)
        # Initialise Q-Network
        self.target_network = NeuralNetwork(self.state_dim, self.action_dim).to(self.device)
        self.hard_update_target_network()

    def compute_predicted_q_next(self, ego_vehicle_next_states, environment_next_states):
        # Find q value for next state
        q_next_predicted_for_all_actions = self.target_network(x1 = ego_vehicle_next_states, x2 = environment_next_states)
        # Find the index of action (from local network) with maximum q value 
        max_action_index = q_next_predicted_for_all_actions.max(1)[1].unsqueeze(1)
        # Get the q value (from local network) corrsponding to best action in next state
        q_next_predicted = q_next_predicted_for_all_actions.gather(1, max_action_index).squeeze(1)  
        
        return q_next_predicted

    def hard_update_target_network(self):
        self.target_network.load_state_dict(self.local_network.state_dict())