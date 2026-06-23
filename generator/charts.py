"""Inline-SVG chart generators for the fit-gap deck. Deterministic, no
external chart library — every chart is a plain SVG string."""
from __future__ import annotations

import math
from . import theme as T


def donut(fit: int, gap: int, partial: int, size: int = 280) -> str:
    """Donut chart of FIT / GAP / PARTIAL percentages with centre label."""
    cx = cy = size / 2
    r = size * 0.38
    stroke = size * 0.16
    circ = 2 * math.pi * r
    segs = [(fit, T.GREEN), (gap, T.RED), (partial, T.AMBER)]
    out = [f"<svg viewBox='0 0 {size} {size}' width='{size}' height='{size}'>"]
    offset = 0.0
    for pct, colour in segs:
        length = circ * pct / 100.0
        out.append(
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' "
            f"stroke='{colour}' stroke-width='{stroke}' "
            f"stroke-dasharray='{length:.2f} {circ - length:.2f}' "
            f"stroke-dashoffset='{-offset:.2f}' "
            f"transform='rotate(-90 {cx} {cy})'/>"
        )
        offset += length
    out.append(
        f"<text x='{cx}' y='{cy - 4}' text-anchor='middle' "
        f"font-size='{size*0.16:.0f}' font-weight='700' fill='{T.GREEN}'>{fit}%</text>"
        f"<text x='{cx}' y='{cy + size*0.10:.0f}' text-anchor='middle' "
        f"font-size='{size*0.05:.0f}' fill='{T.SUB}'>fit score</text>"
    )
    out.append("</svg>")
    return "".join(out)


def vbars(items, width: int = 520, height: int = 300, ymax: int = 100) -> str:
    """Vertical bar chart. items = [(label_line1, label_line2, value, colour)]."""
    n = len(items)
    pad_l, pad_b, pad_t = 36, 56, 20
    plot_w = width - pad_l - 10
    plot_h = height - pad_b - pad_t
    bw = plot_w / n * 0.5
    gap = plot_w / n
    out = [f"<svg viewBox='0 0 {width} {height}' width='{width}' height='{height}'>"]
    # y gridlines / axis labels
    for g in range(0, ymax + 1, 10):
        y = pad_t + plot_h * (1 - g / ymax)
        out.append(
            f"<text x='{pad_l-8}' y='{y+4}' text-anchor='end' font-size='11' "
            f"fill='{T.SUB}'>{g}</text>"
        )
    out.append(f"<line x1='{pad_l}' y1='{pad_t}' x2='{pad_l}' y2='{pad_t+plot_h}' "
               f"stroke='{T.NAVY3}'/>")
    out.append(f"<line x1='{pad_l}' y1='{pad_t+plot_h}' x2='{width-10}' "
               f"y2='{pad_t+plot_h}' stroke='{T.NAVY3}'/>")
    for i, (l1, l2, val, colour) in enumerate(items):
        x = pad_l + gap * i + (gap - bw) / 2
        bh = plot_h * val / ymax
        y = pad_t + plot_h - bh
        out.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bw:.1f}' height='{bh:.1f}' "
                   f"fill='{colour}' rx='2'/>")
        out.append(f"<text x='{x+bw/2:.1f}' y='{y-6:.1f}' text-anchor='middle' "
                   f"font-size='13' font-weight='700' fill='{T.GOLD}'>{val}</text>")
        cx = x + bw / 2
        out.append(f"<text x='{cx:.1f}' y='{pad_t+plot_h+18}' text-anchor='middle' "
                   f"font-size='12' fill='{T.SUB}'>{T.esc(l1)}</text>")
        if l2:
            out.append(f"<text x='{cx:.1f}' y='{pad_t+plot_h+34}' text-anchor='middle' "
                       f"font-size='12' fill='{T.SUB}'>{T.esc(l2)}</text>")
    out.append("</svg>")
    return "".join(out)


def radar(axes, size: int = 300, ymax: int = 100, disp_w: int = 320) -> str:
    """Radar/spider chart. axes = [(label, value)]. Horizontal padding is
    baked into the viewBox so side labels are never clipped."""
    pad = 64
    cx = cy = size / 2
    r = size * 0.30
    n = len(axes)
    vb_w = size + 2 * pad
    disp_h = disp_w * size / vb_w
    out = [f"<svg viewBox='{-pad} 0 {vb_w} {size}' width='{disp_w}' "
           f"height='{disp_h:.0f}'>"]

    def pt(i, frac):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        return cx + r * frac * math.cos(ang), cy + r * frac * math.sin(ang)

    # rings
    for frac in (0.5, 1.0):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, frac) for i in range(n)))
        out.append(f"<polygon points='{pts}' fill='none' stroke='{T.NAVY3}'/>")
    for i in range(n):
        x, y = pt(i, 1.0)
        out.append(f"<line x1='{cx}' y1='{cy}' x2='{x:.1f}' y2='{y:.1f}' "
                   f"stroke='{T.NAVY3}'/>")
    # data polygon
    dpts = " ".join(
        f"{x:.1f},{y:.1f}" for x, y in (pt(i, axes[i][1] / ymax) for i in range(n))
    )
    out.append(f"<polygon points='{dpts}' fill='{T.AMBER}33' "
               f"stroke='{T.AMBER}' stroke-width='2'/>")
    # ring scale labels
    out.append(f"<text x='{cx+4}' y='{cy-r+4}' font-size='10' fill='{T.SUB}'>{ymax}</text>")
    out.append(f"<text x='{cx+4}' y='{cy-r/2+4}' font-size='10' fill='{T.SUB}'>{ymax//2}</text>")
    out.append(f"<text x='{cx+4}' y='{cy+4}' font-size='10' fill='{T.SUB}'>0</text>")
    # axis labels
    for i, (label, _) in enumerate(axes):
        x, y = pt(i, 1.18)
        anchor = "middle"
        if x < cx - 6:
            anchor = "end"
        elif x > cx + 6:
            anchor = "start"
        out.append(f"<text x='{x:.1f}' y='{y:.1f}' text-anchor='{anchor}' "
                   f"font-size='11' fill='{T.GOLD2}'>{T.esc(label)}</text>")
    out.append("</svg>")
    return "".join(out)


def hbars(items, width: int = 380, ymax: int = 100, row_h: int = 34) -> str:
    """Horizontal bars. items = [(label, value, colour)]."""
    pad_l = 4
    bar_x = 4
    plot_w = width - 8
    height = row_h * len(items) + 24
    out = [f"<svg viewBox='0 0 {width} {height}' width='{width}' height='{height}'>"]
    for i, (label, val, colour) in enumerate(items):
        y = i * row_h + 6
        bw = plot_w * val / ymax
        out.append(f"<rect x='{bar_x}' y='{y}' width='{plot_w}' height='18' "
                   f"rx='4' fill='{T.NAVY3}'/>")
        out.append(f"<rect x='{bar_x}' y='{y}' width='{bw:.1f}' height='18' "
                   f"rx='4' fill='{colour}'/>")
    out.append("</svg>")
    return "".join(out)


def grouped_bars(pairs, labels, colours, width=300, height=240, ymax=100):
    """Two-bar comparison (current vs projected). pairs=[v1,v2]."""
    out = [f"<svg viewBox='0 0 {width} {height}' width='{width}' height='{height}'>"]
    pad_b, pad_t, pad_l = 40, 24, 30
    plot_h = height - pad_b - pad_t
    gap = (width - pad_l - 20) / len(pairs)
    bw = gap * 0.45
    out.append(f"<line x1='{pad_l}' y1='{pad_t+plot_h}' x2='{width-10}' "
               f"y2='{pad_t+plot_h}' stroke='{T.NAVY3}'/>")
    for i, val in enumerate(pairs):
        x = pad_l + gap * i + (gap - bw) / 2
        bh = plot_h * val / ymax
        y = pad_t + plot_h - bh
        out.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bw:.1f}' height='{bh:.1f}' "
                   f"fill='{colours[i]}' rx='2'/>")
        out.append(f"<text x='{x+bw/2:.1f}' y='{y-6:.1f}' text-anchor='middle' "
                   f"font-size='14' font-weight='700' fill='{T.GOLD}'>{val}</text>")
        out.append(f"<text x='{x+bw/2:.1f}' y='{pad_t+plot_h+18:.1f}' "
                   f"text-anchor='middle' font-size='11' fill='{T.SUB}'>"
                   f"{T.esc(labels[i])}</text>")
    out.append("</svg>")
    return "".join(out)
