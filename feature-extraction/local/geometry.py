from typing import Literal

import numpy as np
import pandas as pd
import pyrr
from numpy.typing import ArrayLike

from local import face


def normalized(array: ArrayLike) -> np.ndarray:
    """Returns `array` divided by its norm, as an `ndarray`."""
    array = np.asarray(array)
    return array / np.linalg.norm(array)


def make_plane(normal: ArrayLike, distance: float) -> np.ndarray:
    """
    Returns a plane in `pyrr` format, given the provided plane `normal` and `distance` to the origin.

    * The `normal` must be a length-3 vector in any `ArrayLike` format. It is transformed to a unit-vector `ndarray` prior to `pyrr` encoding.
    * The `distance` is taken from the origin along the `normal`. A negative distance means the normal vector placed in the plane points towards the origin.
    """
    normal = normalized(normal)
    return pyrr.plane.create(normal, distance, dtype=float)


SCREEN_PLANES = {
    "frontal-cam" : make_plane(normal=[ 0, 0, -1], distance=250),
    "left-cam"    : make_plane(normal=[-1, 1, -1], distance=250),
    "right-cam"   : make_plane(normal=[ 1, 1, -1], distance=250),
}


def get_face_ray(data: pd.DataFrame, frame: int, face_id: int, eye: Literal["left", "right"]) -> np.ndarray:
    """Returns a ray in `pyrr` format, emanating in the given `frame` for the given `face_id`, from the requested `eye` (in the appropriate eye-specific direction)."""
    eye_id : int
    eye_numbers : list[int]

    if eye == "left": # `eye` given from individual's perspective (as you'd do in medicine). OpenFace does from camera persepective, which is the opposite.
        eye_id = 1
        eye_numbers = face.LEFT_EYE_LANDMARKS
    else: # "right"
        eye_id = 0
        eye_numbers = face.RIGHT_EYE_LANDMARKS

    origin = face.get_keypoint_average(data, frame, face_id, eye_numbers)
    direction = data.loc[(frame, face_id), [f"gaze_{eye_id}_x", f"gaze_{eye_id}_y", f"gaze_{eye_id}_z"]].to_numpy()

    return pyrr.ray.create(origin, direction)


def get_face_sphere(data: pd.DataFrame, frame: int, face_id: int) -> np.ndarray:
    """Returns a sphere in `pyrr` format, tightly containing all facial landmarks in the given `frame` for the given `face_id`."""
    center = face.get_keypoint_average(data, frame, face_id) # Average overal ALL facial landmarks.

    radius = 0
    for keypoint_id in range(face.FACE_KEYPOINT_COUNT):
        position = face.get_3d_keypoint(data, frame, face_id, keypoint_id)
        r = np.linalg.norm(position - center)
        radius = max(r, radius)

    return pyrr.sphere.create(center, radius)


def looks_at_face(left_eye_ray: np.ndarray, right_eye_ray: np.ndarray, face_sphere: np.ndarray) -> bool:
    """Returns `True` if either eye ray intersects the `face_sphere`; returns `False` otherwise."""

    # ray_intersect_sphere() returns a list of intersection points. If the list is empty, there is no intersection.
    left_intersection  = pyrr.geometric_tests.ray_intersect_sphere(left_eye_ray , face_sphere)
    right_intersection = pyrr.geometric_tests.ray_intersect_sphere(right_eye_ray, face_sphere)

    return (len(left_intersection) > 0) or (len(right_intersection) > 0)


def ray_intersects_plane_reasonable(ray: np.ndarray, plane: np.ndarray, max_magnitude: float) -> bool:
    """Returns `True` if `ray` intersects `plane` at a point with smaller L2 norm than `max_magnitude`; returns `False` otherwise."""

    # ray_intersect_plane() returns None if no intersection, or the intersection location if yes intersection.
    intersection = pyrr.geometric_tests.ray_intersect_plane(ray, plane)

    if intersection is None:
        return False

    magnitude = np.linalg.norm(intersection)
    if magnitude > max_magnitude:
        return False

    return True


def looks_at_screen(left_eye_ray: np.ndarray, right_eye_ray: np.ndarray, screen_plane: np.ndarray, max_magnitude: float) -> bool:
    """Returns `True if either eye ray intersects the `screen_plane` at a reasonable location; returns `False` otherwise."""
    return ray_intersects_plane_reasonable(left_eye_ray, screen_plane, max_magnitude) or ray_intersects_plane_reasonable(right_eye_ray, screen_plane, max_magnitude)
