import warnings
from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

import fineslice as fine
import matplotlib.colors
import numpy as np
from matplotlib import colors as pltcol
from matplotlib import pyplot as plt

from ...datacube.datacube import Datacube
from ...loader.nifti import get_nifti_cube
from .layer import Layer, Style


class LayerVoxel(Layer):
    """
    A layer that renders a 3D voxel image slice (optionally with an alpha mask).
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        data: Union[Datacube, Any],
        alpha_map: Optional[
            Union[Datacube, Callable[[Datacube], Datacube], Any]
        ] = None,
        alpha: Optional[float] = None,
        color_scale: Optional["ColorScale"] = None,
        interp_data: str = "nearest",
        interp_screen: str = "nearest",
        style: Optional[Style] = None,
        legend: bool = False,
        legend_label: Optional[str] = None,
        z_index: int = 0,
    ) -> None:
        super().__init__(legend=legend, z_index=z_index, style=style)
        self.data: Datacube = get_nifti_cube(data)
        self.alpha_map: Optional[
            Union[Datacube, Callable[[Datacube], Datacube]]
        ] = get_nifti_cube(alpha_map)
        self.alpha: float = 1.0 if alpha is None else alpha
        self.color_scale: ColorScale = (
            ColorScale() if color_scale is None else color_scale
        )
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
        bounds: Optional[np.ndarray] = None,
        d_origin: Optional[fine.types.SamplerPoint] = None,
        d_points: Optional[fine.types.SamplerPoints] = None,
        d_axis: Optional[int] = None,
    ) -> bool:
        if d_origin is None:
            return False

        sample = fine.sample_2d(
            texture=self.data.image,
            affine=self.data.affine,
            out_position=d_origin,
            out_axis=view_axis,
            out_bounds=bounds,
        )

        if sample is None:
            pass  # todo

        sample_alpha = None
        if self.alpha_map is not None:
            assert isinstance(self.alpha_map, Datacube)
            sample_alpha = fine.sample_2d(
                texture=self.alpha_map.image,  # type: ignore
                affine=self.alpha_map.affine,
                out_position=d_origin,
                out_axis=view_axis,
                out_bounds=bounds,
                out_resolution=sample.texture.shape,  # type: ignore
            )

            if sample_alpha is None:
                pass  # todo
            else:
                if self.alpha < 1:
                    sample_alpha.texture *= self.alpha

        plt_ax.imshow(
            sample.texture.T,
            norm=None,
            vmin=self.color_scale.vmin,
            vmax=self.color_scale.vmax,
            cmap=self.color_scale.cmap,
            origin="lower",
            alpha=self.alpha if sample_alpha is None else sample_alpha.texture.T,
            interpolation=self.interp_screen,
            extent=sample.coordinates.flatten(),  # type: ignore
        )
        return True

    def render_legend(self, ax: plt.Axes, vertical: bool) -> None:
        assert self._draw_style is not None
        self.color_scale.render_legend(
            ax, vertical, self.legend_label, alpha=self.alpha, style=self._draw_style
        )

    def has_legend(self) -> bool:
        return self.legend


@dataclass
class ColorScale:
    cmap: Optional[matplotlib.colors.Colormap] = None
    vmin: Optional[float] = None
    vmax: Optional[float] = None

    def attach_image(self, image: LayerVoxel) -> None:
        if self.vmin is None:
            self.vmin = np.nanmin(image.data.image)
        if self.vmax is None:
            self.vmax = np.nanmax(image.data.image)

    def render_legend(
        self,
        ax: plt.Axes,
        vertical: bool,
        label: Optional[str],
        alpha: float,
        style: Style,
    ) -> None:
        image_scale = plt.cm.ScalarMappable(
            norm=pltcol.Normalize(vmin=self.vmin, vmax=self.vmax), cmap=self.cmap
        )
        plt.colorbar(
            image_scale,
            cax=ax,
            orientation="vertical" if vertical else "horizontal",
            alpha=alpha,
        )
        if label is not None:
            style.render_set_title(label, loc="left", plt_ax=ax)
        style.render_set_ticklabels(plt_ax=ax)


class ColorScaleFromName(ColorScale):
    def __init__(
        self, name: str, vmin: Optional[float] = None, vmax: Optional[float] = None
    ) -> None:
        super().__init__(vmin=vmin, vmax=vmax)
        self.cmap = plt.get_cmap(name)


class ColorScaleSolid(ColorScale):
    def __init__(
        self, color: str, vmin: Optional[float] = None, vmax: Optional[float] = None
    ) -> None:
        super().__init__(vmin=vmin, vmax=vmax)
        self.cmap = pltcol.ListedColormap([color])

    def render_legend(
        self,
        ax: plt.Axes,
        vertical: bool,
        label: Optional[str],
        alpha: float,
        style: Style,
    ) -> None:
        ax.imshow(
            np.array([[0]]),
            vmin=0,
            vmax=0,
            cmap=self.cmap,
            aspect="auto",
            interpolation="nearest",
            alpha=alpha,
        )
        ax.axis("off")
        if label is not None:
            style.render_set_title(label, loc="left", plt_ax=ax)


class LayerVoxelGlass(LayerVoxel):
    def view_render(
        self,
        plt_ax: plt.Axes,
        view_axis: int,
        bounds: Optional[np.ndarray] = None,
        d_origin: Optional[fine.types.SamplerPoint] = None,
        d_points: Optional[fine.types.SamplerPoints] = None,
        d_axis: Optional[int] = None,
    ) -> bool:
        sample = fine.sample_3d(
            texture=self.data.image, affine=self.data.affine, out_bounds=bounds
        )

        if sample is None:
            pass  # todo

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", r"All-NaN slice encountered")
            raster_2d = np.nansum(sample.texture, axis=view_axis)

        raster_alpha_2d = None
        if self.alpha_map is not None:
            assert isinstance(self.alpha_map, Datacube)
            sample_alpha = fine.sample_3d(
                texture=self.alpha_map.image,
                affine=self.alpha_map.affine,
                out_bounds=bounds,
            )

            if sample_alpha is None:
                pass  # todo

            raster_alpha_2d = np.nanmax(sample_alpha.texture, axis=view_axis)

            if self.alpha < 1:
                raster_alpha_2d *= self.alpha

        plt_ax.imshow(
            raster_2d.T,
            norm=None,
            vmin=self.color_scale.vmin,
            vmax=self.color_scale.vmax,
            cmap=self.color_scale.cmap,
            origin="lower",
            alpha=self.alpha if raster_alpha_2d is None else raster_alpha_2d.T,
            interpolation=self.interp_screen,
            extent=np.delete(sample.coordinates, view_axis, axis=0).flatten(),  # type: ignore
        )
        return True
