from experiments.parameters import Parameters

def load_parameters(file):
    p_file = file
    p_obj = open(p_file)
    params_dict = {}
    for line in p_obj:
        line = line.strip()
        if not line.startswith('#'):
            key_value = line.split('=')
            if len(key_value) == 2:
                params_dict[key_value[0].strip()] = key_value[1].strip()

    # save the values in parameter class instance
    params = Parameters()
    params.environment = str(params_dict['env'])
    params.agent = str(params_dict['agent'])
    params.action_repeat = int(params_dict['action_repeat'])
    params.training_episodes = int(params_dict['training_episodes'])
    params.training_steps_per_episode = int(params_dict['training_steps_per_episode'])
    params.training_total_steps = int(params_dict['training_total_steps'])
    params.testing_episodes = int(params_dict['testing_episodes'])
    params.testing_steps_per_episode = int(params_dict['testing_steps_per_episode'])

    params.hyperparameters['epsilon_start'] = float(params_dict['epsilon_start'])
    params.hyperparameters['epsilon_end'] = float(params_dict['epsilon_end'])
    params.hyperparameters['epsilon_decay'] = float(params_dict['epsilon_decay'])
    params.hyperparameters['epsilon_steps'] = int(params_dict['epsilon_steps'])
    params.hyperparameters['use_cuda'] = bool(params_dict['use_cuda'])
    params.hyperparameters['learning_rate'] = float(params_dict['learning_rate'])
    params.hyperparameters['buffer_size'] = int(params_dict['buffer_size'])
    params.hyperparameters['batch_size'] = int(params_dict['batch_size'])
    params.hyperparameters['discount_rate'] = float(params_dict['discount_rate'])
    params.hyperparameters['target_network_update_frequency'] = int(params_dict['target_network_update_frequency'])
    params.hyperparameters['update_buffer_memory_frequency'] = int(params_dict['update_buffer_memory_frequency'])
    params.hyperparameters['reward_summation'] = bool(params_dict['reward_summation'])

    return params

