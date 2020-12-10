import numpy as np
import torch
import torch.nn as nn


class NeuralNetwork(nn.Module):

    """
    #################################################
    Initialize neural network model 
    Initialize parameters and build model.
    """
    def __init__(self, input_size, output_size):
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
      
        self.conv1 = nn.Conv2d(in_channels = self.input_size[2], out_channels = 32, kernel_size = (3, 3), stride = 1)
        self.conv2 = nn.Conv2d(in_channels = 32, out_channels = 64, kernel_size = (3, 3), stride = 1)
        self.conv3 = nn.Conv2d(in_channels = 64, out_channels = 64, kernel_size = (3, 3), stride = 1)

        self.avg_pool = nn.AvgPool2d(kernel_size = (5, 5), stride = (3, 3))

        self.fc1 = nn.Linear(513, 256)
        self.fc2 = nn.Linear(256, 64)
        self.fc3 = nn.Linear(64, self.output_size)

        self.relu = nn.ReLU()



    """
    ###################################################
    Build a network that maps state -> action values.
    """
    def forward(self, x1, x2):
        x2 = x2.view(-1, self.input_size[2], self.input_size[0], self.input_size[1])

        conv_out = self.conv1(x2)
        conv_out = self.relu(conv_out)
        #conv_out = self.avg_pool(conv_out)
        #print(conv_out.size())

        conv_out = self.conv2(conv_out)
        conv_out = self.relu(conv_out)
        conv_out = self.avg_pool(conv_out)

        conv_out = self.conv3(conv_out)
        conv_out = self.relu(conv_out)
        conv_out = self.avg_pool(conv_out)

        n_features = np.prod(conv_out.size()[1:])

        output = conv_out.view(-1, n_features)
        output = torch.cat((x1, output), dim = 1)

        output = self.fc1(output)
        output = self.relu(output)

        output = self.fc2(output)
        output = self.relu(output)

        output = self.fc3(output)

        return output



DEBUG = 0

if DEBUG:
    state_1 = np.zeros([1])
    state_2 = np.zeros([60, 40, 4])



    batch_size = 32
    state_1_batch = []
    state_2_batch = []

    for i in range(batch_size):
        state_1_batch.append(state_1)
        state_2_batch.append(state_2)

    state_1_batch = torch.from_numpy(np.array(state_1_batch)).float()
    state_2_batch = torch.from_numpy(np.array(state_2_batch)).float()

    model = NeuralNetwork(input_size = state_2.shape, output_size = 4)
    model.forward(x1 = state_1_batch, x2 = state_2_batch)