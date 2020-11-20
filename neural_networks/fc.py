import numpy as np
import torch
import torch.nn as nn
from torch.nn import functional as F

class NeuralNetwork(nn.Module):

    """
    #################################################
    Initialize neural network model 
    Initialize parameters and build model.
    """
    def __init__(self, input_size, output_size, fc1_units = 1024, fc2_units = 512, fc3_units = 512, fc4_units = 256):
        """
        Params
        ======
            state_size (int): Dimension of each state
            action_size (int): Dimension of each action
            seed (int): Random seed
            fc1_units (int): Number of nodes in first hidden layer
            fc2_units (int): Number of nodes in second hidden layer
        """
        super(NeuralNetwork, self).__init__()
        self.input_size = input_size
        self.output_size = output_size

        self.input_size = np.prod(self.input_size)
       
        self.fc1 = nn.Linear(self.input_size, fc1_units)
        self.fc2 = nn.Linear(fc1_units, fc2_units)
        self.fc3 = nn.Linear(fc2_units, fc3_units)
        self.fc4 = nn.Linear(fc3_units, fc4_units)
        self.output = nn.Linear(fc4_units, self.output_size)


    """
    ###################################################
    Build a network that maps state -> action values.
    """
    def forward(self, x):
        x = x.view(-1, self.input_size)
        
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = self.output(x)

        return x



DEBUG = 0

if DEBUG:
    state = np.zeros([30, 20, 4])

    batch_size = 32
    state_batch = []

    for i in range(batch_size):
        state_batch.append(state)

    state_batch = torch.from_numpy(np.array(state_batch)).float()

    model = NeuralNetwork(input_size = state.shape, output_size = 4)
    model.forward(x = state_batch)
