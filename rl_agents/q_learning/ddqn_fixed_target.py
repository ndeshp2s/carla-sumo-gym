from rl_agents.q_learning.ddqn import DDQNAgent
from neural_networks.cnn import NeuralNetwork

class DDQNFixedTargetAgent(DDQNAgent):
    def __init__(self, state_size = 0, action_size = 0, hyperparameters = None):
        DDQNAgent.__init__(self, state_size = state_size, action_size = action_size, hyperparameters = hyperparameters)
        # Initialise Q-Network
        self.target_network = NeuralNetwork(self.state_dim, self.action_dim).to(self.device)
        self.hard_update_target_network()

    # def compute_predicted_q_next(self, ego_vehicle_next_states, environment_next_states):
    #     # Find q value for next state
    #     q_next_predicted_for_all_actions = self.target_network(x1 = ego_vehicle_next_states, x2 = environment_next_states)
    #     # Find the index of action (from local network) with maximum q value 
    #     max_action_index = q_next_predicted_for_all_actions.max(1)[1].unsqueeze(1)
    #     # Get the q value (from local network) corrsponding to best action in next state
    #     q_next_predicted = q_next_predicted_for_all_actions.gather(1, max_action_index).squeeze(1)  
        
    #     return q_next_predicted

    def compute_predicted_q_next(self, ego_vehicle_next_states, environment_next_states):
        # Find the index of action (from local network) with maximum q value 
        max_action_index = self.target_network(x1 = ego_vehicle_next_states, x2 = environment_next_states).detach().argmax(1)
        # Get the q value (from target network) corrsponding to best action in next state
        q_next_predicted = self.target_network(x1 = ego_vehicle_next_states, x2 = environment_next_states).gather(1, max_action_index.unsqueeze(1)).squeeze(1)

        return q_next_predicted
