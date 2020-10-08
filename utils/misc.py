import math
import numpy as np

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