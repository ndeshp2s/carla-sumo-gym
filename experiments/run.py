import argparse
import os
import sys

import gym

from experiments.trainer import Trainer
from experiments.tester import Tester
from utils.load_parameters import load_parameters
from experiments.parameters import Parameters
from rl_agents.q_learning.ddqn import DDQNAgent

import environments
from environments.spawner import Spawner

def main(args):
    if args.dir is None:
        print(' ---------- Please mention current experiment directory ----------')
        return

    # Directory of current experiment
    base_dir = os.path.dirname(os.path.realpath(__file__))
    experiment_dir = os.path.join(base_dir, args.agent_type, args.dir)

    # load traing/testing parameters
    params = load_parameters(file = os.path.join(experiment_dir, 'params.dat'))

    # Initialize the environment
    env = gym.make(params.environment)
    state_size = env.observation_space.shape
    action_size = env.action_space.n

    # Initialize the agent
    agent = DDQNAgent(state_size = state_size, action_size = action_size, hyperparameters = params.hyperparameters)

    # Initialize spawner
    spawner = Spawner()

    if args.train:
        trainer = Trainer(env = env, agent = agent, spawner = spawner, params = params, exp_dir = experiment_dir)

        try:
            trainer.train()

        except KeyboardInterrupt:
            trainer.close()
            sys.exit(0)

        finally:
            print('\ndone.')

    if args.test:
        tester = Tester(env = env, agent = None, spawner = spawner, params = params)
      

        try:
            tester.test()


        except KeyboardInterrupt:
            try:
                tester.close()
                sys.exit(0)
            except SystemExit:
                tester.close()
                os._exit(0)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--train', dest='train', action='store_true', help='train model')
    parser.add_argument('--retrain', dest='retrain', action='store_true', help='re-train model')
    parser.add_argument('--test', dest='test', action='store_true', help='test model')
    parser.add_argument('--parameters', dest='parameters', action='store_true', help='file for training/testing parameters')
    parser.add_argument('--dir', default = None, type=str, help='directory for the experiment')
    parser.add_argument('--env', default='Urban-v0', type=str, help='gym environment')
    parser.add_argument('--agent_type', default='fc_dqn', type=str, help='type of RL agent used')
    args = parser.parse_args()

    main(parser.parse_args())
