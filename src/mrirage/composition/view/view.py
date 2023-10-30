from typing import List, Optional

import fineslice as fine
import numpy as np
from matplotlib import pyplot as plt

from ..layer.layer import Layer


class View:  # pylint: disable=too-few-public-methods
    """
    Views represent the individual subplots in the composition.
    They contain individual projection information which is
    passed to each layer while rendering.
    """

    def __init__(
        self,
        view_axis: int = 0,
        bounds: Optional[np.ndarray] = None,
        origin: Optional[fine.types.SamplerPointLike] = None,
        points: Optional[fine.types.SamplerPointsLike] = None,
        axis: Optional[int] = None,
    ) -> None:
        self.view_axis = view_axis
        self.bounds = bounds
        self.origin = None if origin is None else fine.types.sampler_point_3d(origin)
        self.points = None if points is None else fine.types.as_sampler_points(points)
        self.axis = axis

    def render(self, layers: List[Layer], plt_ax: plt.Axes) -> None:
        assert self.bounds is not None
        for layer in layers:
            layer.view_render(
                plt_ax=plt_ax,
                view_axis=self.view_axis,
                bounds=self.bounds,
                d_origin=self.origin,
                d_points=self.points,
                d_axis=self.axis,
            )
