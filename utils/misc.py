import math
import numpy as np
import transforms3d

def is_within_distance(tar_loc, cur_loc, rot, max_dist, min_dist, spawn = True):
    if not spawn:
        if abs(tar_loc.x - cur_loc.x) > carla_config.ped_max_dist or abs(tar_loc.y - cur_loc.y) > carla_config.ped_max_dist:
            return False

    tar_vec = np.array([tar_loc.x - cur_loc.x, tar_loc.y - cur_loc.y])
    norm = np.linalg.norm(tar_vec)

    for_vec = np.array([math.cos(math.radians(rot)), math.sin(math.radians(rot))])
    d_ang = math.degrees(math.acos(np.dot(for_vec, tar_vec) / norm))

    if norm < 0.001:
        return True

    if (norm > max_dist or norm < min_dist):
        return False

    return d_ang < 90.0


def is_within_distance_ahead(target_transform, current_transform, max_distance, min_distance = 0.0):
    """
    Check if a target object is within a certain distance in front of a reference object.
    :param target_transform: location of the target object
    :param current_transform: location of the reference object
    :param orientation: orientation of the reference object
    :param max_distance: maximum allowed distance
    :return: True if target object is within max_distance ahead of the reference object
    """
    target_vector = np.array([target_transform.location.x - current_transform.location.x, target_transform.location.y - current_transform.location.y])
    norm_target = np.linalg.norm(target_vector)

    # If the vector is too short, we can simply stop here
    if norm_target < 0.001:
        return True

    if (norm_target > max_distance) or (norm_target < min_distance):
        return False

    fwd = current_transform.get_forward_vector()
    forward_vector = np.array([fwd.x, fwd.y])
    d_angle = math.degrees(math.acos(np.clip(np.dot(forward_vector, target_vector) / norm_target, -1., 1.)))

    return d_angle < 90.0


def euclidean_distance(source_transform, destination_transform):
    dx = source_transform.location.x - destination_transform.location.x
    dy = source_transform.location.y - destination_transform.location.y

    return math.sqrt(dx * dx + dy * dy)


def walker_relative_position(walker_trans, ev_trans):
    p_xyz = np.array([walker_trans.location.x, walker_trans.location.y, walker_trans.location.z])
    ev_xyz =  np.array([ev_trans.location.x, ev_trans.location.y, ev_trans.location.z])
    ped_loc = p_xyz - ev_xyz

    pitch = math.radians(ev_trans.rotation.pitch)
    roll = math.radians(ev_trans.rotation.roll)
    yaw = math.radians(ev_trans.rotation.yaw)
    R = transforms3d.euler.euler2mat(roll, pitch, yaw).T
    walker_loc_relative = np.dot(R, ped_loc)

    return walker_loc_relative


def load_parameters(file, params):
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
    params.training_episodes = int(params_dict['training_episodes'])
    params.training_steps_per_episode = int(params_dict['training_steps_per_episode'])
    params.testing_episodes = int(params_dict['testing_episodes'])
    params.testing_steps_per_episode = int(params_dict['testing_steps_per_episode'])

    return params