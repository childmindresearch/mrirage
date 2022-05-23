from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Union

from matplotlib import pyplot as plt

from .composition import Composition
from .layer.layer import Layer
from .view.view import View
from ..common import mpl_dom as mdom
from ..composition.layer.style_data import Style


class CompositionDom(Composition, ABC):
    def __init__(
            self,
            layers: Optional[List[Layer]] = None,
            views: Optional[List[View]] = None,
            figure_size: Optional[Union[float, Tuple[float, float]]] = None,
            dpi: int = 200,
            color_bg: str = None,
            style: Style = None
    ):
        super().__init__(layers=layers, views=views, style=style, figure_size=figure_size, dpi=dpi)
        self.color_bg = color_bg
        self._figure: Optional[plt.Figure] = None

    @abstractmethod
    def _render_document(self, views: List[View], legend_entries: List[Layer]) -> Tuple[mdom.MplDocument,
                                                                                        List[mdom.MplElement],
                                                                                        List[mdom.MplElement]]:
        pass

    def _render_figure(self) -> bool:
        legend_entries = [layer for layer in self.layers if layer.has_legend()]

        doc, view_elements, legend_elements = self._render_document(self.views, legend_entries)

        if not doc.align():
            return False

        self._figure = doc.make_figure()

        # mdom.mpl._debug_document(doc, self._figure, False)

        view_axes = list(zip(self.views, doc.make_axes(self._figure, view_elements)))
        legend_axes = list(zip(legend_entries, doc.make_axes(self._figure, legend_elements)))

        if self.color_bg is not None:
            self._figure.set_facecolor(self.color_bg)

        for view, ax in view_axes:
            ax.axis('off')
            view.render(layers=self.layers, plt_ax=ax)
        for layer, ax in legend_axes:
            layer.render_legend(ax, vertical=False)

        return True

    def get_figure(self):
        return self._figure


class CompositionGrid(CompositionDom):

    def __init__(
            self,
            layers: Optional[List[Layer]] = None,
            views: Optional[List[View]] = None,
            figure_size: Optional[Union[float, Tuple[float, float]]] = None,
            dpi=200,
            color_bg=None,
            nbreak=3,
            legend_scale: float = 0.6,
            style: Style = None
    ):
        super().__init__(layers=layers, views=views, figure_size=figure_size, dpi=dpi, color_bg=color_bg, style=style)

        self.nbreak = nbreak
        self.legend_scale = legend_scale

    def _make_doc_legend(self, legend_entries: List[Layer]):

        view_containers = [
            mdom.MplMargin(
                left=0.1,
                right=0.1,
                bottom=0.1,
                top=0.1,
                fixed=True
            ) for _ in self.views
        ]
        view_elements = [c.child for c in view_containers]

        legend_containers = [
            mdom.MplMargin(
                top=0.3,
                bottom=0.25,
                left=0.1,
                right=0.1,
                fixed=True
            ) for _ in legend_entries
        ]
        legend_elements = [c.child for c in legend_containers]

        legend_margin_h = (1 - self.legend_scale) / 2

        return mdom.MplDocument(
            root=mdom.MplMargin(
                mdom.MplDivider(
                    mdom.MplMargin(
                        mdom.MplGrid(
                            legend_containers,
                            nbreak=999
                        ),
                        left=legend_margin_h,
                        right=legend_margin_h
                    ),
                    mdom.MplGrid(
                        view_containers,
                        nbreak=self.nbreak
                    ),
                    vertical=True,
                    division=0.65,
                    fixed=True
                ),
                left=0.02,
                right=0.02,
                top=0.02,
                bottom=0.02,
                fixed=True
            ),
            width=self.figure_width,
            height=self.figure_height,
            dpi=self.dpi
        ), view_elements, legend_elements

    def _make_doc_no_legend(self):

        view_containers = [
            mdom.MplMargin(
                left=0.1,
                right=0.1,
                bottom=0.1,
                top=0.1,
                fixed=True
            ) for _ in self.views
        ]
        view_elements = [c.child for c in view_containers]

        return mdom.MplDocument(
            root=mdom.MplMargin(
                mdom.MplGrid(
                    view_containers,
                    nbreak=self.nbreak
                ),
                left=0.02,
                right=0.02,
                top=0.02,
                bottom=0.02,
                fixed=True
            ),
            width=self.figure_width,
            height=self.figure_height,
            dpi=self.dpi
        ), view_elements, []

    def _render_document(
            self,
            views: List[View],
            legend_entries: List[Layer]) -> Tuple[mdom.MplDocument, List[mdom.MplElement], List[mdom.MplElement]]:

        if len(legend_entries) == 0:
            return self._make_doc_no_legend()

        return self._make_doc_legend(legend_entries)
