import warnings
from dataclasses import dataclass
from typing import Any, Optional, Union, Callable

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors as pltcol

from mrirage.datacube import Datacube
from mrirage.loader.nifti import get_nifti_cube

from .layer import Layer, Style
from ... import slicer


class LayerVoxel(Layer):
    def __init__(  # pylint: disable=too-many-arguments
            self,
            data: Union[Datacube, Any],
            alpha_map: Optional[Union[Datacube, Callable[[Datacube], Datacube], Any]] = None,
            alpha: float = None,
            color_scale: 'ColorScale' = None,
            interp_data='nearest',
            interp_screen='nearest',
            style: Style = None,
            legend: bool = False,
            legend_label: Optional[str] = None,
            z_index: int = 0
    ):
        super().__init__(legend=legend, z_index=z_index, style=style)
        self.data: Datacube = get_nifti_cube(data)
        self.alpha_map: Optional[Datacube] = get_nifti_cube(alpha_map)
        self.alpha: float = 1. if alpha is None else alpha
        self.color_scale: ColorScale = ColorScale() if color_scale is None else color_scale
        self.interp_data = interp_data  # todo
        self.interp_screen = interp_screen
        self.legend_label = legend_label

    def pre_render(self, base_style: Style) -> None:
        super().pre_render(base_style)
        self.color_scale.attach_image(self)
        if callable(self.alpha_map):
            self.alpha_map = self.alpha_map(self.data)

    def view_render(
            self,
            plt_ax: plt.Axes,
            view_axis: int,
            bounds: np.ndarray,
            d_origin: Optional[slicer.t_spoint] = None,
            d_points: Optional[slicer.t_spoints] = None,
            d_axis: Optional[int] = None
    ) -> bool:
        if d_origin is None:
            return False

        axis_offset = d_origin[view_axis]

        raster, axis_lims, _ = slicer.slice_image(
            data=self.data,
            axis=view_axis,
            axis_offset=axis_offset,
            bounds=bounds
        )

        raster_alpha = None
        if self.alpha_map is not None:
            raster_alpha, _, _ = slicer.slice_image(
                data=self.alpha_map,
                axis=view_axis,
                axis_offset=axis_offset,
                bounds=bounds,
                sampling_dims=raster.shape
            )

            if self.alpha < 1:
                raster_alpha *= self.alpha

        plt_ax.imshow(
            raster.T,
            norm=None,
            vmin=self.color_scale.vmin,
            vmax=self.color_scale.vmax,
            cmap=self.color_scale.cmap,
            origin='lower',
            alpha=self.alpha if raster_alpha is None else raster_alpha.T,
            interpolation=self.interp_screen,
            extent=axis_lims.flatten()
        )
        return True

    def render_legend(self, ax, vertical: bool):
        self.color_scale.render_legend(ax, vertical, self.legend_label, alpha=self.alpha, style=self._draw_style)

    def has_legend(self) -> bool:
        return self.legend


@dataclass
class ColorScale:
    cmap = None
    vmin: Optional[float] = None
    vmax: Optional[float] = None

    def attach_image(self, image: LayerVoxel):
        if self.vmin is None:
            self.vmin = np.nanmin(image.data.image)
        if self.vmax is None:
            self.vmax = np.nanmax(image.data.image)

    def render_legend(self, ax, vertical: bool, label: Optional[str], alpha: float, style: Style):
        image_scale = plt.cm.ScalarMappable(
            norm=pltcol.Normalize(vmin=self.vmin, vmax=self.vmax),
            cmap=self.cmap
        )
        plt.colorbar(image_scale, cax=ax, orientation='vertical' if vertical else 'horizontal', alpha=alpha)
        if label is not None:
            style.render_set_title(label, loc='left', plt_ax=ax)
        style.render_set_ticklabels(plt_ax=ax)


class ColorScaleFromName(ColorScale):
    def __init__(self, name: str, vmin: Optional[float] = None, vmax: Optional[float] = None):
        super().__init__(vmin=vmin, vmax=vmax)
        self.cmap = plt.get_cmap(name)


class ColorScaleSolid(ColorScale):
    def __init__(self, color: str, vmin: Optional[float] = None, vmax: Optional[float] = None):
        super().__init__(vmin=vmin, vmax=vmax)
        self.cmap = pltcol.ListedColormap([color])

    def render_legend(self, ax, vertical: bool, label: Optional[str], alpha: float, style: Style):
        ax.imshow(
            np.array([[0]]),
            vmin=0,
            vmax=0,
            cmap=self.cmap,
            aspect='auto',
            interpolation='nearest',
            alpha=alpha
        )
        ax.axis('off')
        if label is not None:
            style.render_set_title(label, loc='left', plt_ax=ax)


class LayerVoxelGlass(LayerVoxel):
    def view_render(
            self,
            plt_ax: plt.Axes,
            view_axis: int,
            bounds: np.ndarray,
            d_origin: Optional[slicer.t_spoint] = None,
            d_points: Optional[slicer.t_spoints] = None,
            d_axis: Optional[int] = None
    ) -> bool:

        raster_3d, axis_lims_3d, _ = slicer.slice_3d(
            data=self.data,
            bounds=bounds
        )
        axis_lims_2d = axis_lims_3d[slicer.eye_1d(n=3, i=view_axis, v=False, f=True)]

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', r'All-NaN slice encountered')
            raster_2d = np.nansum(raster_3d, axis=view_axis)

        raster_alpha_2d = None
        if self.alpha_map is not None:
            raster_alpha_3d, _, _ = slicer.slice_3d(
                data=self.alpha_map,
                bounds=bounds,
                sampling_dims=raster_3d.shape
            )

            raster_alpha_2d = np.nanmax(raster_alpha_3d, axis=view_axis)

            if self.alpha < 1:
                raster_alpha_2d *= self.alpha

        plt_ax.imshow(
            raster_2d.T,
            norm=None,
            vmin=self.color_scale.vmin,
            vmax=self.color_scale.vmax,
            cmap=self.color_scale.cmap,
            origin='lower',
            alpha=self.alpha if raster_alpha_2d is None else raster_alpha_2d.T,
            interpolation=self.interp_screen,
            extent=axis_lims_2d.flatten()
        )
        return True

