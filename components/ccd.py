import itertools
import numpy as np


def factorial_points(k):
    """
    Full factorial points at (-1, +1)^k
    """
    return np.array(
        list(itertools.product([-1.0, 1.0], repeat=k)),
        dtype=float
    )


def center_points(k, n_center):
    """
    Repeated center points at (0, ..., 0)
    """
    return np.zeros((n_center, k), dtype=float)


def axial_points(k, alpha):
    """
    Axial (star) points at ±alpha along each axis
    """
    points = []

    for i in range(k):
        p = np.zeros(k)
        p[i] = alpha
        points.append(p.copy())

        p[i] = -alpha
        points.append(p.copy())

    return np.array(points, dtype=float)


def central_composite(
    k: int,
    ccd_type: str="face-centered",
    n_center: int=1
):
    """
    Generate a Central Composite Design (CCD).

    Parameters
    ----------
    k : int
        Number of factors
    ccd_type : str
        'face-centered' or 'spherical'
    n_center : int
        Number of center points

    Returns
    -------
    ndarray
        Shape (N, k) array of normalized DOE points
    """

    if k < 1:
        raise ValueError("k must be >= 1")

    if n_center < 1:
        raise ValueError("n_center must be >= 1")

    ccd_type = ccd_type.lower()

    if ccd_type == "spherical":
        alpha = (2 ** k) ** 0.25
    elif ccd_type in ("face-centered", "face"):
        alpha = 1.0
    else:
        raise ValueError(
            "ccd_type must be 'face-centered' or 'spherical'"
        )

    F = factorial_points(k)
    A = axial_points(k, alpha)
    C = center_points(k, n_center)

    return np.vstack([F, A, C])

def scale_to_bounds(points, mins, maxs):
    mins = np.asarray(mins)
    maxs = np.asarray(maxs)
    return mins + (points + 1) * (maxs - mins) / 2
