from typing import Optional, List, Union, Tuple

import numpy as np

from ..slicer.spoint import t_spoint_like
from ..composition import Composition, CompositionGrid, Layer, View, Style


def quick_add_xyz(composition: Composition, origin: Optional[t_spoint_like], bounds: Optional[np.ndarray] = None):
    for i in range(3):
        composition.views.append(View(view_axis=i, origin=origin if origin is not None else (0, 0, 0), bounds=bounds))


def quick_xyz(
        layers: Optional[List[Layer]],
        origin: Optional[t_spoint_like] = None,
        bounds: Optional[np.ndarray] = None,
        figure_size: Union[float, Tuple[float, float]] = None,
        dpi=200,
        color_bg=None,
        nbreak=3,
        legend_scale: float = 0.6,
        style: Style = None
) -> CompositionGrid:
    composition = CompositionGrid(
        layers=layers,
        figure_size=figure_size,
        dpi=dpi,
        color_bg=color_bg,
        nbreak=nbreak,
        legend_scale=legend_scale,
        style=style
    )
    quick_add_xyz(composition, origin, bounds)
    return composition
