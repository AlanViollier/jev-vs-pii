"""The README chart: word-level F2 against cost, one panel per dataset, as a static SVG in ember style."""

from __future__ import annotations

import math
from collections.abc import Sequence
from html import escape

from jev_vs_pii.schema import ResultRow

_PAPER, _INK, _ACCENT, _MUTED, _HAIRLINE = "#FBF8F3", "#1C1A17", "#C2410C", "#97907F", "#E8E2D6"
_FONT = "IBM Plex Mono, ui-monospace, monospace"
_PANEL_W, _PANEL_H = 520, 400
_LEFT, _RIGHT, _TOP, _BOTTOM = 44, 150, 50, 46
## Cost axis in $/1k docs, log scale; free lanes sit in their own column left of it.
_X_MIN, _X_MAX = 0.01, 10.0
_FREE_W = 56
_Y_MIN, _Y_MAX = 0.3, 1.0
_LABEL_GAP = 11


def pareto_svg(panels: Sequence[tuple[str, Sequence[ResultRow]]]) -> str:
    """Draw each panel's headline word-level rows as F2 vs $/1k docs.

    Parameters
    ----------
    panels:
        (title, rows) per dataset. `mask_all` and `human` rows become dashed reference
        lines; every other row is a labelled point, Jev lanes in the accent colour.

    Returns
    -------
    str
        A standalone SVG document.
    """
    width = _PANEL_W * len(panels)
    body = [_panel(title, rows, i * _PANEL_W) for i, (title, rows) in enumerate(panels)]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{_PANEL_H}" '
        f'viewBox="0 0 {width} {_PANEL_H}" font-family="{_FONT}" font-size="10" fill="{_INK}">'
        f'<rect width="{width}" height="{_PANEL_H}" fill="{_PAPER}"/>{"".join(body)}</svg>\n'
    )


def _panel(title: str, rows: Sequence[ResultRow], x0: int) -> str:
    plot_left = x0 + _LEFT + _FREE_W
    plot_right = x0 + _PANEL_W - _RIGHT
    plot_bottom = _PANEL_H - _BOTTOM

    def x_of(cost: float) -> float:
        if cost <= 0:
            return x0 + _LEFT + 18
        share = (math.log10(min(max(cost, _X_MIN), _X_MAX)) - math.log10(_X_MIN)) / (
            math.log10(_X_MAX) - math.log10(_X_MIN)
        )
        return plot_left + share * (plot_right - plot_left)

    def y_of(f2: float) -> float:
        share = (min(max(f2, _Y_MIN), _Y_MAX) - _Y_MIN) / (_Y_MAX - _Y_MIN)
        return plot_bottom - share * (plot_bottom - _TOP)

    parts = [
        f'<rect x="{x0 + _LEFT}" y="{_TOP - 34}" width="18" height="2" fill="{_ACCENT}"/>',
        f'<text x="{x0 + _LEFT}" y="{_TOP - 16}" font-size="12" font-weight="600">{escape(title)}</text>',
    ]
    for f2 in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        y = y_of(f2)
        parts.append(_line(x0 + _LEFT, y, plot_right, y, _HAIRLINE))
        parts.append(_text(x0 + _LEFT - 6, y + 3, f"{f2:.1f}", _MUTED, anchor="end"))
    for cost in (0.01, 0.1, 1.0, 10.0):
        x = x_of(cost)
        parts.append(_line(x, _TOP, x, plot_bottom, _HAIRLINE))
        parts.append(_text(x, plot_bottom + 14, f"${cost:g}", _MUTED, anchor="middle"))
    parts.append(_text(x0 + _LEFT + 18, plot_bottom + 14, "free", _MUTED, anchor="middle"))
    parts.append(_text(plot_right, plot_bottom + 30, "$ per 1k docs (log) →", _MUTED, anchor="end"))

    for row in rows:
        if row.lane.family in ("human", "baseline"):
            y = y_of(row.scores.f2)
            label = "human agreement" if row.lane.family == "human" else "mask everything"
            parts.append(_line(x0 + _LEFT, y, plot_right, y, _MUTED, dashed=True))
            parts.append(_text(plot_right + 6, y + 3, f"{label} {row.scores.f2:.2f}", _MUTED))

    points = sorted(
        (row for row in rows if row.lane.family not in ("human", "baseline")),
        key=lambda row: row.scores.f2,
    )
    label_y: list[float] = []
    for row in points:
        x, y = x_of(float(row.cost.usd_per_1k_docs)), y_of(row.scores.f2)
        colour = _ACCENT if row.lane.family == "jev" else _INK
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{colour}"/>')
        ## Push a label up until it clears the ones already placed.
        ly = y + 3
        while any(abs(ly - taken) < _LABEL_GAP for taken in label_y):
            ly -= 2
        label_y.append(ly)
        parts.append(_text(x + 7, ly, f"{row.lane.id} {row.scores.f2:.2f}", colour))
    return "".join(parts)


def _line(x1: float, y1: float, x2: float, y2: float, colour: str, dashed: bool = False) -> str:
    dash = ' stroke-dasharray="4 3"' if dashed else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{colour}" stroke-width="1"{dash}/>'
    )


def _text(x: float, y: float, content: str, colour: str, anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" fill="{colour}" text-anchor="{anchor}">'
        f"{escape(content)}</text>"
    )
