from typing import List, Optional

import numpy as np
from matplotlib import pyplot as plt

from ..layer.layer import Layer
from ...slicer.types import t_spoint_like, t_spoints_like, as_slicer_points, as_slicer_point


class View:  # pylint: disable=too-few-public-methods
    def __init__(
            self,
            view_axis: int = 0,
            bounds: Optional[np.ndarray] = None,
            origin: Optional[t_spoint_like] = None,
            points: Optional[t_spoints_like] = None,
            axis: Optional[int] = None
    ):
        self.view_axis = view_axis
        self.bounds = bounds
        self.origin = None if origin is None else as_slicer_point(origin)
        self.points = None if points is None else as_slicer_points(points)
        self.axis = axis

    def render(self, layers: List[Layer], plt_ax: plt.Axes) -> None:
        for layer in layers:
            layer.view_render(
                plt_ax=plt_ax,
                view_axis=self.view_axis,
                bounds=self.bounds,
                d_origin=self.origin,
                d_points=self.points,
                d_axis=self.axis
            )
