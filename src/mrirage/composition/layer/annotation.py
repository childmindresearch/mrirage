from abc import ABC
from typing import Optional, Union, Tuple

import matplotlib.pyplot as plt
import numpy as np

from .layer import Layer
from mrirage.composition.layer.style_data import Style
from ...common import rep_tuple
from ...slicer.types import t_spoint, t_spoints


def _get_axlims(plt_ax: plt.Axes):
    xmin, xmax = plt_ax.get_xlim()  # todo min bounds?
    ymin, ymax = plt_ax.get_ylim()
    return xmin, xmax, ymin, ymax


class LayerCrossBase(Layer, ABC):
    def __init__(
            self,
            padding_inner=0.,
            padding_outer=0.,
            style: Style = None,
            legend=False,
            z_index: int = 0
    ):
        super().__init__(legend=legend, z_index=z_index, style=style)
        self.padding_inner = padding_inner
        self.padding_outer = padding_outer
        self._set_default_style(Style(cap_style='round'))

    def _render_cross(self, plt_ax: plt.Axes, view_axis: int, point: np.ndarray):
        var_dims = np.concatenate([np.arange(3) != view_axis, np.full((len(point) - 3,), False)])
        px, py = np.array(point)[var_dims]

        xmin, xmax, ymin, ymax = _get_axlims(plt_ax)

        xmin += self.padding_outer
        xmax -= self.padding_outer
        ymin += self.padding_outer
        ymax -= self.padding_outer

        x = [px - self.padding_inner, xmin, None, px + self.padding_inner, xmax, None, px, px, None, px, px]
        y = [py, py, None, py, py, None, py - self.padding_inner, ymin, None, py + self.padding_inner, ymax]

        self._draw_style.render(
            x, y,
            plt_ax=plt_ax
        )

        return True

    def render_legend(self, ax: plt.Axes, vertical: bool):
        self._draw_style.render(
            [0, 1],
            [0, 0],
            plt_ax=ax
        )
        ax.axis('off')
        self._draw_style.render_set_title('Slices', loc='left', plt_ax=ax)


class LayerCrossOrigin(LayerCrossBase):
    def view_render(
            self,
            plt_ax: plt.Axes,
            view_axis: int,
            bounds: np.ndarray,
            d_origin: Optional[t_spoint] = None,
            d_points: Optional[t_spoints] = None,
            d_axis: Optional[int] = None
    ) -> bool:
        if d_origin is not None:
            return self._render_cross(plt_ax, view_axis, d_origin)
        return False


class LayerCross(LayerCrossBase):
    def view_render(
            self,
            plt_ax: plt.Axes,
            view_axis: int,
            bounds: np.ndarray,
            d_origin: Optional[t_spoint] = None,
            d_points: Optional[t_spoints] = None,
            d_axis: Optional[int] = None
    ) -> bool:
        if d_points is not None:
            # todo avoid loop, only one .plot() call
            for p in d_points:
                self._render_cross(plt_ax, view_axis, p)
            return True
        return False


class LayerLine(Layer):
    def __init__(
            self,
            padding_inner=0.,
            padding_outer=0.,
            style: Style = None,
            legend=False,
            z_index: int = 0
    ):
        super().__init__(legend=legend, z_index=z_index, style=style)
        self.padding_inner = padding_inner
        self.padding_outer = padding_outer

    def view_render(
            self,
            plt_ax: plt.Axes,
            view_axis: int,
            bounds: np.ndarray,
            d_origin: Optional[t_spoint] = None,
            d_points: Optional[t_spoints] = None,
            d_axis: Optional[int] = None
    ) -> bool:
        if d_points is None and d_origin is not None:
            d_points = [d_origin]

        if d_points is None or d_axis is None is None or view_axis == d_axis:
            return False

        dim_map = np.arange(3)
        dim_map = dim_map[dim_map != view_axis]

        x = []
        y = []
        if dim_map[0] == d_axis:
            plt_min, plt_pmax = plt_ax.get_ylim()
            for p in d_points[d_axis]:
                x += [p, p, None]
                y += [plt_min, plt_pmax, None]
        else:
            plt_min, plt_pmax = plt_ax.get_xlim()
            for p in d_points[d_axis]:
                x += [plt_min, plt_pmax, None]
                y += [p, p, None]

        self._draw_style.render(
            x, y, plt_ax=plt_ax
        )

        return True

    def render_legend(self, ax: plt.Axes, vertical: bool):
        self._draw_style.render(
            [0, 1],
            [0, 0],
            plt_ax=ax
        )
        ax.axis('off')
        self._draw_style.render_set_title('Slices', loc='left', plt_ax=ax)


class LayerLR(Layer):
    def __init__(
            self,
            padding: Union[float, Tuple[float, float]] = 0,
            label: Tuple[str, str] = ('L', 'R'),
            style: Style = None,
            z_index: int = 0
    ):
        super().__init__(legend=False, z_index=z_index, style=style)
        self.label_left, self.label_right = label
        self.pad_x, self.pad_y = rep_tuple(2, padding)

    def view_render(
            self,
            plt_ax: plt.Axes,
            view_axis: int,
            bounds: np.ndarray,
            d_origin: Optional[t_spoint] = None,
            d_points: Optional[t_spoints] = None,
            d_axis: Optional[int] = None
    ) -> bool:
        if view_axis == 0:
            return False

        xmin, xmax, ymin, ymax = _get_axlims(plt_ax)

        self._draw_style.render_text(
            xmin + self.pad_x, ymin + self.pad_y,
            self.label_left,
            ha='left', va='bottom',
            plt_ax=plt_ax
        )

        self._draw_style.render_text(
            xmax - self.pad_x, ymin + self.pad_y,
            self.label_right,
            ha='right', va='bottom',
            plt_ax=plt_ax
        )

        return True


class LayerCoordinate(Layer):
    def __init__(self,
                 round_value: Optional[bool] = None,
                 style: Style = None,
                 padding: Union[float, Tuple[float, float]] = 0,
                 label: Tuple[str, str] = ('L', 'R'),
                 z_index: int = 0):
        super().__init__(legend=False, z_index=z_index, style=style)
        self.label_left, self.label_right = label
        self.pad_x, self.pad_y = padding if isinstance(padding, tuple) else (padding, padding)
        self.axis_labels = ('X', 'Y', 'Z')
        self.round_value = round_value

    def view_render(
            self,
            plt_ax: plt.Axes,
            view_axis: int,
            bounds: np.ndarray,
            d_origin: Optional[t_spoint] = None,
            d_points: Optional[t_spoints] = None,
            d_axis: Optional[int] = None
    ) -> bool:
        if d_origin is None:
            return False

        xmin, xmax, ymin, ymax = _get_axlims(plt_ax)

        lab = np.array(self.axis_labels)[view_axis]
        val = np.array(d_origin)[view_axis]

        if self.round_value is None:
            val = round(val) if (abs(val) % 1) < 1e-7 else val
        elif self.round_value:
            val = round(val)

        self._draw_style.render_text(
            xmin + self.pad_x, ymax - self.pad_y,
            f'${lab} = {val}$',
            ha='left', va='top',
            plt_ax=plt_ax
        )

        return True
