import numpy as np
import torch
import torch.nn as nn

DEBUG = 0
class NeuralNetwork(nn.Module):

    """
    #################################################
    Initialize neural network model 
    Initialize parameters and build model.
    """
    def __init__(self, input_size, output_size, device = "cpu"):
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

        self.avg_pool = nn.AvgPool2d(kernel_size = (5, 5), stride = (5, 5))
        self.softmax = nn.Softmax(dim=1)

        self.lstm_layer1 = nn.LSTM(input_size = 1, hidden_size = 32, num_layers = 1, batch_first = True)
        self.lstm_layer2 = nn.LSTM(input_size = 512, hidden_size = 512, num_layers = 1, batch_first = True)

        self.fc1 = nn.Linear(544, 128)
        self.fc2 = nn.Linear(128, 32)
        self.fc3 = nn.Linear(32, self.output_size)

        self.relu = nn.ReLU()

        self.device = device



    """
    ###################################################
    Build a network that maps state -> action values.
    """
    def forward(self, batch_size, time_step, x1, x2, hs1, cs1, hs2, cs2):
        x1 = x1.view(batch_size, time_step, 1)
        x2 = x2.view(batch_size*time_step, self.input_size[2], self.input_size[0], self.input_size[1])
        # if DEBUG: print(x2.size())

        lstm_output_1 = self.lstm_layer1(x1, (hs1, cs1))
        output_1 = lstm_output_1[0][:, time_step - 1, :]       
        if DEBUG: print('LSTM 1 Output: ', output_1.size())
        hs_new1 = lstm_output_1[1][0]
        cs_new1 = lstm_output_1[1][1]


        x2 = self.conv1(x2)
        x2 = self.relu(x2)
        if DEBUG: print(x2.size())

        x2 = self.conv2(x2)
        x2 = self.relu(x2)
        x2 = self.avg_pool(x2)
        if DEBUG: print(x2.size())

        x2 = self.conv3(x2)
        x2 = self.relu(x2)
        x2 = self.avg_pool(x2)
        if DEBUG: print(x2.size())

        n_features = np.prod(x2.size()[1:])
        if DEBUG: print(n_features)

        x2 = x2.view(batch_size, time_step, n_features)
        if DEBUG: print(x2.size())

        lstm_output_2 = self.lstm_layer2(x2, (hs2, cs2))
        output_2 = lstm_output_2[0][:, time_step - 1, :]
        if DEBUG: print('LSTM 2 Output: ', output_2.size())
        hs_new2 = lstm_output_2[1][0]
        cs_new2 = lstm_output_2[1][1]

        output = torch.cat((output_1, output_2), dim = 1)
        if DEBUG: print(output.size())

        output = self.fc1(output)
        output = self.relu(output)
        if DEBUG: print(output.size())

        output = self.fc2(output)
        output = self.relu(output)
        if DEBUG: print(output.size())

        output = self.fc3(output)
        if DEBUG: print(output.size())
        output = self.softmax(output)
        if DEBUG: print(output.size())


        return output, (hs_new1, cs_new1), (hs_new2, cs_new2)

    def init_hidden_states(self, batch_size, lstm_memory):
        h = torch.zeros(1, batch_size, lstm_memory).float().to(self.device)
        c = torch.zeros(1, batch_size, lstm_memory).float().to(self.device)
        
        return h, c


if DEBUG:

    BATCH_SIZE = 2
    TIME_STEP = 4
    OUT_SIZE = 4

    # Dummy data
    x = []
    x.append(np.zeros([1]))
    x.append(np.zeros([120,80,3]))
    

    batch = []
    for i in range(BATCH_SIZE):
        episode = []
        for j in range(TIME_STEP):
            episode.append(x)
        #print(len(episode))
        batch.append(episode)

    #print(len(batch))
    states1 = []
    states2 = []
    actions = []
    rewards = []
    next_states1 = []
    next_states2 = []

    for b in batch:
        #print(len(b))
        s1, s2, a, r, ns1, ns2 = [], [], [], [], [], []
        for e in b:
            s1.append(e[0])
            s2.append(e[1])

        states1.append(s1)
        states2.append(s2)


    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    states1 = torch.from_numpy(np.array(states1)).float().to(device)
    states2 = torch.from_numpy(np.array(states2)).float().to(device)


    model = NeuralNetwork(input_size=[120,80,3], output_size=OUT_SIZE)
    hidden_state1, cell_state1 = model.init_hidden_states(batch_size=BATCH_SIZE, lstm_memory=32)
    hidden_state2, cell_state2 = model.init_hidden_states(batch_size=BATCH_SIZE, lstm_memory=512)

    if torch.cuda.is_available():
        model.cuda()

    q_predicted_all = model.forward(x1 = states1, x2 = states2, batch_size = BATCH_SIZE, time_step = TIME_STEP, hs1 = hidden_state1, cs1 = cell_state1, hs2 = hidden_state2, cs2 = cell_state2)
