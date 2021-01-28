import os
import shutil
import math
import numpy as np
import transforms3d

def get_index(val, start, stop, num):

    grids = np.linspace(start, stop, num)
    features = np.zeros(num)

    #Check extremes
    if val <= grids[0] or val > grids[-1]:
        return features, False

    for i in range(len(grids) - 1):
        if val >= grids[i] and val < grids[i + 1]:
            features[i] = 1

    return features, True


def get_speed(vehicle):
    """
    Compute speed of a vehicle in Km/h.
        :param vehicle: the vehicle for which speed is calculated
        :return: speed as a float in Km/h
    """
    vel = vehicle.get_velocity()

    return 3.6 * math.sqrt(vel.x ** 2 + vel.y ** 2 + vel.z ** 2)

def get_speed(vehicle):
    """
    Compute speed of a vehicle in Km/h.
        :param vehicle: the vehicle for which speed is calculated
        :return: speed as a float in Km/h
    """
    vel = vehicle.get_velocity()

    return 3.6 * math.sqrt(vel.x ** 2 + vel.y ** 2 + vel.z ** 2)

def compute_relative_heading(source_transform, destination_transform):
    d_heading = (destination_transform.rotation.yaw + 360) % 360
    s_heading = (source_transform.rotation.yaw + 360) % 360
    head_rel = d_heading - s_heading
    head_rel = (head_rel + 360) % 360
    head_rel = round(head_rel, 2)

    return head_rel


def compute_relative_position(source_transform, destination_transform):
    d_xyz = np.array([destination_transform.location.x, destination_transform.location.y, destination_transform.location.z])
    s_xyz = np.array([source_transform.location.x, source_transform.location.y, source_transform.location.z])
    pos = d_xyz - s_xyz

    pitch = math.radians(source_transform.rotation.pitch)
    roll = math.radians(source_transform.rotation.roll)
    yaw = math.radians(source_transform.rotation.yaw)

    R = transforms3d.euler.euler2mat(roll, pitch, yaw).T
    pos_rel = np.dot(R, pos)

    return pos_rel


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


def normalize_data(data, min_val, max_val):
    return (data - min_val) / (max_val - min_val)

# def ray_intersection(pos_one, pos_two, vec_one, vec_two):
#     p1_x = pos_one.x
#     p1_y = pos_one.y
#     p2_x = pos_two.x
#     p2_y = pos_two.y
#     n1_x = ego_veh_forward_vector.x
#     n1_y = ego_veh_forward_vector.y
#             # n2_x = walker_forward_vector.x
#             # n2_y = walker_forward_vector.y
#             # u = (p1_y * n2_x + n2_y * p2_x - p2_y * n2_x - n2_y * p1_x) / (n1_x * n2_y - n1_y * n2_x)
#             # v = (p1_x + n1_x * u - p2_x) / n2_x

def ray_intersection(p1, p2, n1, n2, dist):
    if (n1.y * n2.x - n1.x * n2.y) == 0.0 or n2.x == 0.0:
        return False

    u = (p1.x * n2.y + p2.y * n2.x - p2.x * n2.y - p1.y * n2.x) / (n1.y * n2.x - n1.x * n2.y)
    v = (p1.x + n1.x * u - p2.x) / n2.x

    if u > 0 and v > 0:
        # print('intersection: ', get_intersection(p1, p2, n1, n2), dist)
        # if get_intersection(p1, p2, n1, n2) <= dist:
        return True

    return False

def get_intersection(p1, p2, n1, n2):
    A = p1
    B = p1 + n1
    C = p2
    D = p2 + n2

    # a1x + b1y = c1
    a1 = B.y - A.y
    b1 = A.x - B.x
    c1 = a1 * (A.x) + b1 * (A.y)

    # a2x + b2y = c2
    a2 = D.y - C.y
    b2 = C.x - D.x
    c2 = a2 * (C.x) + b2 * (C.y)

    # determinant
    det = a1 * b2 - a2 * b1

    # parallel line
    if det == 0:
        return 10000.0

    # intersect point(x,y)
    x = ((b2 * c1) - (b1 * c2)) / det
    y = ((a1 * c2) - (a2 * c1)) / det

    dx = p2.x - x
    dy = p2.y - y

    return math.sqrt(dx * dx + dy * dy)
    #return (x, y)






    # p1_end = p1 + n1
    # p2_end = p2 + n2

    # m1 = (p1_end.y - p1.y)/(p1_end.x - p1.x)
    # m2 = (p2_end.y - p2.y)/(p2_end.x - p2.x)

    # b1 = p1.y - m1 * p1.x
    # b2 = p2.y - m2 * p2.x

    # px = (b2 - b1) / (m1 - m2)
    # py = m1 * px + b1

    # # find distance
    # dx = p1.x - destination_transform.location.x
    # dy = p1.y - destination_transform.location.y

    # return math.sqrt(dx * dx + dy * dy)


def create_directory(dir, recreate = True):
    if recreate:
        if os.path.exists(dir):
            shutil.rmtree(dir)
    os.makedirs(dir)