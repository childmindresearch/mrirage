from abc import ABC, abstractmethod
from typing import List, Optional, Union, Tuple

from matplotlib import pyplot as plt

from .layer.layer import Layer
from .layer.style_data import Style
from .view.view import View
from ..common import rep_tuple


class Composition(ABC):
    def __init__(
            self,
            layers: Optional[List[Layer]] = None,
            views: Optional[List[View]] = None,
            style: Optional[Style] = None,
            figure_size: Optional[Union[float, Tuple[float, float]]] = None,
            dpi: int = 200
    ):
        self.layers: List[Layer] = [] if layers is None else layers
        self.views: List[View] = [] if views is None else views
        self.style = Style() if style is None else style
        self.figure_width, self.figure_height = rep_tuple(2, figure_size) if figure_size is not None else (10., 6.)
        self.dpi = dpi

    def render(self) -> Optional[plt.Figure]:
        self.layers = sorted(self.layers)
        for layer in self.layers:
            layer.pre_render(base_style=self.style)
        self._render_figure()
        return self.get_figure()

    @abstractmethod
    def _render_figure(self):
        pass

    @abstractmethod
    def get_figure(self) -> plt.Figure:
        pass

    def append(self, element: Union[Layer, View]):
        if isinstance(element, Layer):
            self.layers.append(element)
        if isinstance(element, View):
            self.views.append(element)

    def render_show(self):
        self.render().show()
        return self.get_figure()

    def render_to_file(self, file_name):
        self.render()
        return self.get_figure().savefig(fname=file_name, dpi=self.dpi)
