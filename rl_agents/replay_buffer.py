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
        self.device = "cpu"


    def add_experience(self, episode):
        self.memory.append(episode)


    def sample(self, batch_size = 32, time_step = 8):
        episodes = random.sample(self.memory, batch_size)

        batch = []
        for e in episodes:
            point = np.random.randint(0, len(e) + 1 - time_step)
            batch.append(e[point:point + time_step])
        return batch


    def __len__(self):
        return len(self.memory)
