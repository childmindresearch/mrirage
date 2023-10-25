import dataclasses
from typing import Any, Tuple, Union

from matplotlib import pyplot as plt

_t_color = Union[str, Tuple[float, float, float]]


@dataclasses.dataclass
class Style:  # pylint: disable=too-many-instance-attributes
    color: _t_color | None = None
    alpha: float | None = None

    font_family: str | None = None
    font_family_math: str | None = None

    font_size: float | None = None
    font_size_title: float | None = 12

    line_width: float | None = None
    line_style: str | None = None
    cap_style: str | None = None

    def render(self, *args: Any, plt_ax: plt.Axes, **kwargs: Any):
        return plt_ax.plot(
            *args,
            color=self.color,
            lw=self.line_width,
            linestyle=self.line_style,
            solid_capstyle=self.cap_style,
            dash_capstyle=self.cap_style,
            alpha=self.alpha,
            **kwargs
        )

    def render_text(self, *args: Any, plt_ax: plt.Axes, **kwargs: Any):
        return plt_ax.text(
            *args,
            fontsize=self.font_size,
            family=self.font_family,
            math_fontfamily=self.font_family_math,
            color=self.color,
            **kwargs
        )

    def render_set_title(self, label: str, *args: Any, plt_ax: plt.Axes, **kwargs: Any):
        # mypy bug: https://github.com/python/mypy/issues/6799
        plt_ax.set_title(
            *args,
            label=label,  # type: ignore
            fontsize=self.font_size_title,
            family=self.font_family,
            math_fontfamily=self.font_family_math,
            color="black" if self.color is None else self.color,
            **kwargs
        )

    def render_set_ticklabels(self, plt_ax: plt.Axes):
        for lab in plt_ax.get_xticklabels():
            lab.set_fontproperties({"family": self.font_family})  # type: ignore
        for lab in plt_ax.get_yticklabels():
            lab.set_fontproperties({"family": self.font_family})  # type: ignore

    def override(self, other: "Style"):
        fields = dataclasses.fields(Style)
        re = Style()
        for f in fields:
            s_val = getattr(self, f.name)
            o_val = getattr(other, f.name)
            setattr(re, f.name, o_val if s_val is None else s_val)
        return re
