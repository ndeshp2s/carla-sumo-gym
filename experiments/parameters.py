class Parameters:
    environment = None
    action_repeat = 0
    agent = None
    training_episodes = 0
    training_steps_per_episode = 0
    training_total_steps = 0
    testing_episodes = 0
    testing_steps_per_episode = 0

    # hyperparameters
    hyperparameters = {}
    hyperparameters['epsilon_start'] = 0.0
    hyperparameters['epsilon_end'] = 0.0
    hyperparameters['epsilon_decay'] = 0.0
    hyperparameters['epsilon_steps'] = 0.0
    hyperparameters['use_cuda'] = False
    hyperparameters['learning_rate'] = 0.0
    hyperparameters['buffer_size'] = 0
    hyperparameters['batch_size'] = 0
    hyperparameters['discount_rate'] = 0.0
    hyperparameters['target_network_update_frequency'] = 0
    hyperparameters['update_buffer_memory_frequency'] = 0
    hyperparameters['reward_summation'] = False
