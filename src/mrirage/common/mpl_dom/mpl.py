"""
This module provides a simple HTML-DOM-like structure for constructing
matplotlib figures.
Because the matplotlib API is bad at margins and alignment, this module
provides an
overly complicated way to construct a figure with a grid of axes, with
margins and dividers.
"""

from math import ceil
from typing import Any, Generator, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt


class Box:
    def __init__(self, x: float = 0, y: float = 0, w: float = 1, h: float = 1) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def clone(self) -> "Box":
        return Box(self.x, self.y, self.w, self.h)

    def as_tuple(self) -> Tuple[float, float, float, float]:
        return self.x, self.y, self.w, self.h

    def valid(self, min_value: int | float = 0, max_value: int | float = 1) -> bool:
        t = self.as_tuple()
        for i in t:
            if i < min_value or i > max_value:
                return False
        return True

    def __repr__(self) -> str:
        return str(self.as_tuple())


class MplElement:
    def __init__(self) -> None:
        self.pos = Box()

    def pretty_str(self, indent: str = "", indent_add: str = "  ") -> str:
        if len(self.get_children()) == 0:
            return f"{indent}{self.get_descriptor()}"

        indent_next = indent + indent_add
        cs = ",\n".join(
            [c.pretty_str(indent_next, indent_add) for c in self.get_children()]
        )
        return f"{indent}{self.get_descriptor()}[\n{cs}\n{indent}]"

    def pretty_print(self, indent: str = "", indent_add: str = "  ") -> None:
        print(self.pretty_str(indent=indent, indent_add=indent_add))

    def get_children(self) -> Sequence["MplElement"]:
        return []

    def get_descriptor(self) -> str:
        return str(self.pos)

    def align_children(self, fix_w: float, fix_h: float) -> None:
        pass

    def align_recursive(self, fix_w: float, fix_h: float) -> bool:
        self.align_children(fix_w, fix_h)
        children_valid = self.children_valid()
        for child in self.get_children():
            if not child.align_recursive(fix_w, fix_h):
                children_valid = False
        return children_valid

    def align(self) -> bool:
        return self.align_recursive(1, 1)

    def create_axis(self, figure: plt.Figure) -> plt.Axes:
        return figure.add_axes(self.pos.as_tuple())

    @staticmethod
    def create(n: int) -> List["MplElement"]:
        return [MplElement() for _ in range(n)]

    @staticmethod
    def make_axes(
        figure: plt.Figure, axes_elements: List["MplElement"]
    ) -> List[plt.Axes]:
        return [ae.create_axis(figure) for ae in axes_elements]

    def children_valid(self) -> bool:
        for c in self.get_children():
            if not c.pos.valid():
                return False
        return True

    def __repr__(self) -> str:
        return self.get_descriptor()

    def iter_recursive(self) -> Generator["MplElement", Any, None]:
        for child in self.get_children():
            yield child
            yield from child.iter_recursive()


class MplDocument(MplElement):
    def __init__(
        self,
        root: Optional[MplElement] = None,
        width: float = 10,
        height: float = 8,
        dpi: float = 72,
    ) -> None:
        super().__init__()
        self.width: float = width
        self.height: float = height
        self.dpi = dpi
        self.root: MplElement = MplElement() if root is None else root
        self.pos = Box()

    def get_children(self) -> List["MplElement"]:
        return [self.root]

    def align_children(self, fix_w: float, fix_h: float) -> None:
        self.root.pos = self.pos.clone()

    def align(self) -> bool:
        return self.align_recursive(fix_w=self.width, fix_h=self.height)

    def get_descriptor(self) -> str:
        return f"Document{self.pos}"

    def make_figure(self) -> plt.Figure:
        return plt.figure(figsize=(self.width, self.height), dpi=self.dpi)


class MplDivider(MplElement):
    def __init__(
        self,
        first: Optional[MplElement] = None,
        second: Optional[MplElement] = None,
        vertical: bool = False,
        division: float = 0.5,
        fixed: bool = False,
    ) -> None:
        super().__init__()
        self.vertical = vertical
        self.division = division
        self.first = first if first is not None else MplElement()
        self.second = second if second is not None else MplElement()
        self.fixed = fixed

    def get_children(self) -> List["MplElement"]:
        return [self.first, self.second]

    def get_descriptor(self) -> str:
        return (
            f"Divider{self.pos}(fixed={self.fixed}, "
            "vertical={self.vertical}, division={self.division})"
        )

    def align_children(
        self, fix_w: float, fix_h: float
    ) -> None:  # todo avoid instance creation
        if self.fixed:
            ref_w = 1 / fix_w
            ref_h = 1 / fix_h
        else:
            ref_w = self.pos.w
            ref_h = self.pos.h

        p = self.pos
        if self.vertical:
            h_off = ref_h * self.division
            self.first.pos = Box(x=p.x, y=p.y, w=p.w, h=h_off)
            self.second.pos = Box(x=p.x, y=p.y + h_off, w=p.w, h=p.h - h_off)
        else:
            w_off = ref_w * self.division
            self.first.pos = Box(x=p.x, y=p.y, w=p.x + w_off, h=p.h)
            self.second.pos = Box(x=w_off, y=p.y, w=p.w - w_off, h=p.h)


class MplMargin(MplElement):
    def __init__(
        self,
        child: Optional[MplElement] = None,
        left: float = 0,
        right: float = 0,
        top: float = 0,
        bottom: float = 0,
        fixed: bool = False,
    ) -> None:
        super().__init__()
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.fixed = fixed
        self.child = child if child is not None else MplElement()

    def get_children(self) -> List["MplElement"]:
        return [self.child]

    def get_descriptor(self) -> str:
        return (
            f"Margin{self.pos}(fixed={self.fixed}, left={self.left}, "
            f"right={self.right}, top={self.top}, bottom={self.bottom})"
        )

    def align_children(self, fix_w: float, fix_h: float) -> None:
        if self.fixed:
            ref_w = 1 / fix_w
            ref_h = 1 / fix_h
        else:
            ref_w = self.pos.w
            ref_h = self.pos.h

        self.child.pos.x = self.pos.x + (self.left * ref_w)
        self.child.pos.y = self.pos.y + (self.bottom * ref_h)
        self.child.pos.w = self.pos.w - ((self.left + self.right) * ref_w)
        self.child.pos.h = self.pos.h - ((self.bottom + self.top) * ref_h)


class MplGrid(MplElement):
    def __init__(
        self,
        children: Optional[Sequence["MplElement"]] = None,
        nbreak: int = 3,
        vertical: bool = False,
    ) -> None:
        super().__init__()
        self.children: Sequence["MplElement"] = [] if children is None else children
        self.nbreak = nbreak
        self.vertical = vertical

    def get_children(self) -> Sequence["MplElement"]:
        return self.children

    def get_descriptor(self) -> str:
        return f"Grid{self.pos}()"

    def align_children(self, fix_w: float, fix_h: float) -> None:
        nrows = ceil(len(self.children) / self.nbreak)
        ncols = min(len(self.children), self.nbreak)

        gw = self.pos.w / ncols
        gh = self.pos.h / nrows

        for i, child in enumerate(self.get_children()):
            xg = i % ncols
            yg = nrows - 1 - (i // ncols)

            child.pos.x = self.pos.x + (xg * gw)
            child.pos.y = self.pos.y + (yg * gh)
            child.pos.w = gw
            child.pos.h = gh


def _debug_axes(axes: List[plt.Axes]) -> List[plt.Axes]:
    color_map: Any = plt.get_cmap("Set1")
    for i, ax in enumerate(axes):
        col = color_map.colors[i % len(color_map.colors)]
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.patch.set_facecolor(col)
        ax.patch.set_alpha(0.1)
        for pos in ["top", "bottom", "right", "left"]:
            ax.spines[pos].set_edgecolor(col)
    return axes


def _debug_document(
    doc: MplDocument, fig: Optional[plt.Figure] = None, align: bool = True
) -> None:
    if align:
        doc.align()
    fig = fig if fig is not None else doc.make_figure()
    _debug_axes(doc.make_axes(fig, list(doc.iter_recursive())))
    fig.show()


def main() -> None:
    doc = MplDocument(width=10, height=8, dpi=72)

    view_containers = [
        MplMargin(MplElement(), left=0.4, bottom=0.32, fixed=True) for _ in range(7)
    ]
    view_elements = [c.child for c in view_containers]

    legend_containers = [MplMargin(MplElement()) for _ in range(3)]
    legend_elements = [c.child for c in legend_containers]

    doc.root = MplMargin(
        MplDivider(
            MplMargin(MplGrid(legend_containers), left=0.2, right=0.2),
            MplGrid(view_containers),
            vertical=True,
            division=0.3,
            fixed=True,
        ),
        left=0.05,
        right=0.05,
        top=0.05,
        bottom=0.05,
    )

    if not doc.align():
        print("Margin error")
        return
    doc.pretty_print()

    _debug_document(doc)

    fig = doc.make_figure()
    view_axes = doc.make_axes(fig, view_elements)
    legend_axes = doc.make_axes(fig, legend_elements)

    for i, a in enumerate(view_axes):
        a.plot([1, 0], [0, 1])
        a.text(0, 0, f"#{i}")
    for i, a in enumerate(legend_axes):
        a.axis("off")
        a.imshow([[1]], aspect="auto")
        a.text(0, 0, f"#{i}", color="w")

    fig.suptitle("Hello")
    fig.show()


if __name__ == "__main__":
    main()
