from abc import ABC
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from mrirage.slicer.spoint import t_spoint, t_spoints

from .style_data import Style


class Layer(ABC):
    """
    Layer base class. Layer components should (in most cases) overload
    ``Layer.view_render()`` and ``Layer.render_legend()``.
    """

    def __init__(self, style: Style = None, legend: bool = False, z_index: int = 0):
        self.style = style
        self._default_style = None
        self._draw_style = None
        self.legend = legend
        self.z_index = z_index

    def _set_default_style(self, default_style: Style):
        self._default_style = default_style

    def pre_render(self, base_style: Style) -> None:
        """
        Called once for each layer in composition before rendering views.
        """

        if self.style is None:
            if self._default_style is None:
                self._draw_style = base_style
            else:
                self._draw_style = self._default_style
        else:
            if self._default_style is None:
                self._draw_style = self.style.override(base_style)
            else:
                self._draw_style = self.style.override(self._default_style).override(base_style)

    def render_legend(self, ax: plt.Axes, vertical: bool):
        pass

    def has_legend(self) -> bool:
        return self.legend

    def get_z_index(self) -> int:
        return self.z_index

    def __eq__(self, other):
        return self.get_z_index() == other.get_z_index()

    def __ne__(self, other):
        return self.get_z_index() != other.get_z_index()

    def __lt__(self, other):
        return self.get_z_index() < other.get_z_index()

    def __le__(self, other):
        return self.get_z_index() <= other.get_z_index()

    def __gt__(self, other):
        return self.get_z_index() > other.get_z_index()

    def __ge__(self, other):
        return self.get_z_index() >= other.get_z_index()

    def view_render(  # pylint: disable=no-self-use,unused-argument
            self,
            plt_ax: plt.Axes,
            view_axis: int,
            bounds: np.ndarray,
            d_origin: Optional[t_spoint] = None,
            d_points: Optional[t_spoints] = None,
            d_axis: Optional[int] = None
    ) -> bool:
        return False
