import random
import numpy as np
import torch
from collections import deque, namedtuple
import pickle

class ReplayBuffer():
    def __init__(self, buffer_size, batch_size):

        self.memory = deque(maxlen = buffer_size)
        self.batch_size = batch_size
        self.experience = namedtuple("experience", field_names = ["state", "action", "reward", "next_state", "done"])
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def add_experience(self, state, action, reward, next_state, done):
        experience = self.experience(state = state, action = action, reward = reward, next_state = next_state, done = done)
        self.memory.append(experience)

    # def sample(self, batch_size = None):
    #     if batch_size is None:
    #         batch_size = self.batch_size

    #     experiences = random.sample(self.memory, k = batch_size)

    #     states = torch.from_numpy(np.vstack([e.state for e in experiences if e is not None])).float().to(self.device)
    #     actions = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).long().to(self.device)
    #     rewards = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float().to(self.device)
    #     next_states = torch.from_numpy(np.vstack([e.next_state for e in experiences if e is not None])).float().to(self.device)
    #     dones = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None]).astype(np.uint8)).float().to(self.device)

    #     return (states, actions, rewards, next_states, dones)

    def sample(self, batch_size = None):
        if batch_size is None:
            batch_size = self.batch_size

        experiences = random.sample(self.memory, k = batch_size)

        return experiences

    def __len__(self):
        return len(self.memory)

    def save_buffer(self, file):
        # data = []
        # for e in self.agent.buffer.memory:
        #     print(e)
        #     data.append(e)
        # print(len(data))

        # file = self.buffer_dir + '/replay_memory_buffer.txt'
        
        self.experience = namedtuple("Experience", field_names = ["state", "action", "reward", "next_state", "done"])
        with open(file, 'wb') as fp:
            pickle.dump(self.memory, fp)