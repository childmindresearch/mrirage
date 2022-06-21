from typing import Union

import numpy as np
from matplotlib import pyplot as plt


def norm_vec(v: np.ndarray) -> np.ndarray:
    """
    Normalize vector
    :param v: vector
    :return:
    """
    return np.linalg.norm(v)


def eye_1d(
        n: int,
        i: int,
        v: Union[int, float, complex, np.ndarray] = 1,
        f: Union[int, float, complex, np.ndarray] = 0,
        dtype=None
):
    """
    Similar to ``np.full`` but a single index is changed.

    :param n: vector length
    :param i: index
    :param v: index value
    :param f: fill value
    :param dtype: The desired data-type for the array The default, None, means ``np.array(f).dtype``.
    :return:
    """
    a = np.full((n,), fill_value=f, dtype=dtype)
    a[i] = v
    return a


def plot_poly(vertices, edges=None, inters=None, labels=None):
    """
    Plot polygon
    :param vertices:
    :param edges:
    :param inters:
    :param labels:
    :return:
    """
    labs = ('X', 'Y', 'Z') if labels is None else labels
    ax = plt.axes(projection='3d', xlabel=labs[0], ylabel=labs[1], zlabel=labs[2])
    ax.scatter3D(vertices[0], vertices[1], vertices[2], c=np.arange(vertices.shape[1]), cmap='Set1')

    if edges is not None:
        for e in edges:
            ax.plot3D(vertices[0, e], vertices[1, e], vertices[2, e])

    if inters is not None:
        ax.scatter3D(inters[0], inters[1], inters[2], c="red")

    return ax
