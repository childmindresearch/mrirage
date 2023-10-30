from abc import ABC
from typing import Optional

import fineslice as fine
import matplotlib.pyplot as plt
import numpy as np

from .style_data import Style


class Layer(ABC):
    """
    Layer base class. Layer components should (in most cases) overload
    ``Layer.view_render()`` and ``Layer.render_legend()``.
    """

    def __init__(
        self, style: Optional[Style] = None, legend: bool = False, z_index: int = 0
    ) -> None:
        self.style: Optional[Style] = style
        self._default_style: Optional[Style] = None
        self._draw_style: Optional[Style] = None
        self.legend = legend
        self.z_index = z_index

    def _set_default_style(self, default_style: Style) -> None:
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
                self._draw_style = self.style.override(self._default_style).override(
                    base_style
                )

    def render_legend(self, ax: plt.Axes, vertical: bool) -> None:
        pass

    def has_legend(self) -> bool:
        return self.legend

    def get_z_index(self) -> int:
        return self.z_index

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, Layer)
        return self.get_z_index() == other.get_z_index()

    def __ne__(self, other: object) -> bool:
        assert isinstance(other, Layer)
        return self.get_z_index() != other.get_z_index()

    def __lt__(self, other: object) -> bool:
        assert isinstance(other, Layer)
        return self.get_z_index() < other.get_z_index()

    def __le__(self, other: object) -> bool:
        assert isinstance(other, Layer)
        return self.get_z_index() <= other.get_z_index()

    def __gt__(self, other: object) -> bool:
        assert isinstance(other, Layer)
        return self.get_z_index() > other.get_z_index()

    def __ge__(self, other: object) -> bool:
        assert isinstance(other, Layer)
        return self.get_z_index() >= other.get_z_index()

    def view_render(  # pylint: disable=unused-argument
        self,
        plt_ax: plt.Axes,
        view_axis: int,
        bounds: Optional[np.ndarray] = None,
        d_origin: Optional[fine.types.SamplerPoint] = None,
        d_points: Optional[fine.types.SamplerPoints] = None,
        d_axis: Optional[int] = None,
    ) -> bool:
        return False
