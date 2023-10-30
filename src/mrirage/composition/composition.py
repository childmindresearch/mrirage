import os
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

from matplotlib import pyplot as plt

from ..common import rep_tuple
from .layer.layer import Layer
from .layer.style_data import Style
from .view.view import View


class Composition(ABC):
    """
    Abstract composition base class.

    A composition is a collection of layers and views. It is responsible for
    rendering the layers and views into a figure.

    Composition components should (in most cases) overload
    ``Composition._render_figure()`` and ``Composition.get_figure()``.
    """

    def __init__(
        self,
        layers: Optional[List[Layer]] = None,
        views: Optional[List[View]] = None,
        style: Optional[Style] = None,
        figure_size: Optional[Union[float, Tuple[float, float]]] = None,
        dpi: int = 200,
    ) -> None:
        self.layers: List[Layer] = [] if layers is None else layers
        self.views: List[View] = [] if views is None else views
        self.style = Style() if style is None else style
        self.figure_width, self.figure_height = (
            rep_tuple(2, figure_size) if figure_size is not None else (10.0, 6.0)
        )
        self.dpi = dpi

    def render(self) -> Optional[plt.Figure]:
        self.layers = sorted(self.layers)
        for layer in self.layers:
            layer.pre_render(base_style=self.style)
        self._render_figure()
        return self.get_figure()

    @abstractmethod
    def _render_figure(self) -> bool:
        return False

    @abstractmethod
    def get_figure(self) -> Optional[plt.Figure]:
        pass

    def append(self, element: Union[Layer, View]) -> None:
        if isinstance(element, Layer):
            self.layers.append(element)
        if isinstance(element, View):
            self.views.append(element)

    def render_show(self) -> None:
        fig = self.render()
        assert fig is not None, "Figure is None"
        fig.show()

    def render_to_file(self, file_name: Union[str, os.PathLike]) -> None:
        fig = self.render()
        assert fig is not None, "Figure is None"
        fig.savefig(fname=file_name, dpi=self.dpi)
