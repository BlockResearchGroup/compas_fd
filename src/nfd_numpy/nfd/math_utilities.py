from math import sin, cos, asin, acos, hypot

from numpy import asarray


__all__ = [
    'euclidean_distance',
    'arc_sin',
    'arc_cos',
    'planar_rotation',
    'is_isotropic',
    'transform_stress',
    'transform_stress_angle',
    'stress_vec_to_tensor',
    'stress_tensor_to_vec'
]


s, c = sin, cos
def s2(x): return s(x) * s(x)  # noqa E704
def c2(x): return c(x) * c(x)  # noqa E704


def euclidean_distance(u, v):
    """Calculate distance between two 3D points using the hypotenuse."""
    return hypot(u[0] - v[0], u[1] - v[1], u[2] - v[2])


def arc_sin(a):
    """Calculate inverse sine. Input values are bounded
    between -.9999 and .9999 for numerical stability."""
    return asin(max(min(a, .9999), -.9999))


def arc_cos(a):
    """Calculate inverse cosine. Input values are bounded
    between -.9999 and .9999 for numerical stability."""
    return acos(max(min(a, .9999), -.9999))


def planar_rotation(angle):
    """Return a planar rotation matrix from an angle in radians."""
    return asarray([[c(angle),  -s(angle)],
                    [s(angle),   c(angle)]])


def is_isotropic(vec):
    """Check whether an input stress pseudo-vector is isotropic."""
    return (vec[0] == vec[1]) and (vec[2] == 0)


def transform_stress(stress, rotation, invert=False):
    """Transform planar stress vector by 2x2 rotation matrix."""
    s, R = stress_vec_to_tensor(stress), rotation
    r = (R.dot(s).dot(R.T) if invert
         else R.T.dot(s).dot(R))
    return stress_tensor_to_vec(r)


def transform_stress_angle(stress, angle, invert=False):
    """Transform a planar stress vector by angle in radians."""
    a = -angle if invert else angle
    s2a = s2(a)
    c2a = c2(a)
    sca = s(a) * c(a)
    T = [[c2a,    s2a,     2 * sca],
         [s2a,    c2a,    -2 * sca],
         [-sca,   sca,   c2a - s2a]]
    return asarray(T).dot(stress)


def stress_vec_to_tensor(vec):
    """Convert planar stresses from pseudo-vector to tensor form."""
    return asarray([[vec[0], vec[2]],
                    [vec[2], vec[1]]])


def stress_tensor_to_vec(tens):
    """Convert planar stresses from tensor to pseudo-vector form."""
    return asarray([tens[0, 0], tens[1, 1], tens[0, 1]])
