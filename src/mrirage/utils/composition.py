from typing import List, Optional, Tuple, Union

import fineslice as fine
import numpy as np

from ..composition import Composition, CompositionGrid, Layer, View
from ..composition.layer import Style


def quick_add_xyz(
    composition: Composition,
    origin: Optional[fine.types.SamplerPointLike],
    bounds: Optional[np.ndarray] = None,
) -> None:
    """
    Add three views to a composition, one for each axis.

    Args:
        composition: Composition to add views to.
        origin: Origin of the views.
        bounds: Bounds of the views.

    Returns:
        None

    """
    for i in range(3):
        composition.views.append(
            View(
                view_axis=i,
                origin=origin if origin is not None else (0, 0, 0),
                bounds=bounds,
            )
        )


def quick_xyz(
    layers: Optional[List[Layer]],
    origin: Optional[fine.types.SamplerPointLike] = None,
    bounds: Optional[np.ndarray] = None,
    figure_size: Optional[Union[float, Tuple[float, float]]] = None,
    dpi=200,
    color_bg=None,
    nbreak=3,
    legend_scale: float = 0.6,
    style: Optional[Style] = None,
) -> CompositionGrid:
    """
    Create a composition with three views, one for each axis.

    Args:
        layers: Layers to add to the composition.
        origin: Origin of the views.
        bounds: Bounds of the views.
        figure_size: Size of the figure.
        dpi: DPI of the figure.
        color_bg: Background color of the figure.
        nbreak: Number of elements in a row.
        legend_scale: Scale of the legend.
        style: Style of the composition.

    Returns:
        CompositionGrid
    """
    composition = CompositionGrid(
        layers=layers,
        figure_size=figure_size,
        dpi=dpi,
        color_bg=color_bg,
        nbreak=nbreak,
        legend_scale=legend_scale,
        style=style,
    )
    quick_add_xyz(composition, origin, bounds)
    return composition
