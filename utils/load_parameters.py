from experiments.parameters import Parameters

def load_parameters(file, )
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
    params.training_episodes = int(params_dict['training_episodes'])
    params.steps_per_episode = int(params_dict['steps_per_episode'])
    params.testing_episodes = int(params_dict['testing_episodes'])


    return params


