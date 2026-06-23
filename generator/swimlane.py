"""Swimlane process-flow deck: cover + one swimlane diagram per phase.

Nodes are placed on a (lane, column) grid; connectors are routed
orthogonally between node boxes and drawn as an SVG layer behind the boxes.
"""
from __future__ import annotations

from . import theme as T

# Geometry (px @ 96dpi; slide is 1280 x 720)
DIAG_X = 40
LANE_LABEL_W = 60
COL0 = 26          # gap from lane label to first column
COL_W = 200
BOX_W = 156
BOX_H = 58
DIAG_TOP = 100
LANE_CAP = 122     # max lane height

NODE_STYLE = {
    "standard": (T.GOLD, "#16284A", T.GOLD),
    "new": (T.GREEN, "#0F2A1A", T.GREEN),
    "enhanced": (T.AMBER, "#2A2008", T.AMBER),
    "exception": (T.RED, "#2E1414", T.RED),
    "decision": (T.GOLD, "#1C3056", T.GOLD),
    "terminal": (T.GOLD, "#16284A", T.GOLD),  # render as standard; green means "new" only
}

EDGE_COLOUR = {"standard": T.GOLD, "new": T.GREEN, "exception": T.RED}


class _Rect:
    __slots__ = ("x", "y", "w", "h", "row", "col")

    def __init__(self, x, y, w, h, row, col):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.row, self.col = row, col

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2


def _layout(phase):
    lane_index = {ln: i for i, ln in enumerate(phase.lanes)}
    n = len(phase.lanes)
    lane_h = min(LANE_CAP, (720 - DIAG_TOP - 96) / max(n, 1))
    rects = {}
    seen = {}
    for nd in phase.nodes:
        if nd.lane not in lane_index:
            raise ValueError(f"[{phase.pid}] node {nd.nid}: unknown lane {nd.lane!r}")
        key = (nd.lane, nd.col)
        if key in seen:
            raise ValueError(
                f"[{phase.pid}] nodes {seen[key]!r} and {nd.nid!r} collide at "
                f"lane={nd.lane!r} col={nd.col}")
        seen[key] = nd.nid
        row = lane_index[nd.lane]
        x = DIAG_X + LANE_LABEL_W + COL0 + nd.col * COL_W
        y = DIAG_TOP + row * lane_h + (lane_h - BOX_H) / 2
        rects[nd.nid] = _Rect(x, y, BOX_W, BOX_H, row, nd.col)
    return rects, lane_h, n


def _arrow(x, y, dx, dy):
    """Small triangle arrowhead pointing in (dx,dy) direction."""
    import math
    ang = math.atan2(dy, dx)
    size = 7
    p1 = (x, y)
    p2 = (x - size * math.cos(ang - 0.4), y - size * math.sin(ang - 0.4))
    p3 = (x - size * math.cos(ang + 0.4), y - size * math.sin(ang + 0.4))
    return f"{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}"


def _path_cells(corners):
    """Grid cells (row, col) an axis-aligned polyline passes through.
    corners are (col, row) grid points."""
    cells = set()
    for (c0, r0), (c1, r1) in zip(corners, corners[1:]):
        if c0 == c1:
            for r in range(min(r0, r1), max(r0, r1) + 1):
                cells.add((r, c0))
        else:
            for c in range(min(c0, c1), max(c0, c1) + 1):
                cells.add((r0, c))
    return cells


def _route(a, b, occupied):
    """Return (polyline_points, arrow). For cross-lane links, choose the
    L-route ordering (vertical-first vs horizontal-first) that passes through
    the fewest other boxes, so connectors don't disappear under a box."""
    if a.row == b.row:
        if b.x >= a.x:
            x1, x2, y = a.x + a.w, b.x, a.cy
        else:
            x1, x2, y = a.x, b.x + b.w, a.cy
        return [(x1, y), (x2, y)], (x2, y, x2 - x1, 0)
    if a.col == b.col:
        if b.y >= a.y:
            y1, y2, x = a.y + a.h, b.y, a.cx
        else:
            y1, y2, x = a.y, b.y + b.h, a.cx
        return [(x, y1), (x, y2)], (x, y2, 0, y2 - y1)

    endpoints = {(a.row, a.col), (b.row, b.col)}
    vf_hits = len((_path_cells([(a.col, a.row), (a.col, b.row), (b.col, b.row)])
                   - endpoints) & occupied)
    hf_hits = len((_path_cells([(a.col, a.row), (b.col, a.row), (b.col, b.row)])
                   - endpoints) & occupied)
    if hf_hits < vf_hits:  # horizontal-first: travel in src row, drop in dst column
        sx = a.x + a.w if b.cx >= a.cx else a.x
        ey = b.y if b.cy >= a.cy else b.y + b.h
        dy = 1 if b.cy >= a.cy else -1
        return [(sx, a.cy), (b.cx, a.cy), (b.cx, ey)], (b.cx, ey, 0, dy)
    # vertical-first: drop in src column, travel in dst row
    sy = a.y + a.h if b.cy >= a.cy else a.y
    ex = b.x if b.cx >= a.cx else b.x + b.w
    dx = 1 if b.cx >= a.cx else -1
    return [(a.cx, sy), (a.cx, b.cy), (ex, b.cy)], (ex, b.cy, dx, 0)


def _diagram(phase):
    rects, lane_h, n = _layout(phase)
    diag_w = 1280 - 2 * DIAG_X
    diag_h = DIAG_TOP + n * lane_h

    # lane backgrounds + labels
    lanes_html = []
    for i, ln in enumerate(phase.lanes):
        top = DIAG_TOP + i * lane_h
        bg = T.NAVY2 if i % 2 == 0 else "#0C1A33"
        lanes_html.append(
            f"<div style='position:absolute;left:{DIAG_X}px;top:{top}px;"
            f"width:{diag_w}px;height:{lane_h}px;background:{bg};'></div>"
            f"<div style='position:absolute;left:{DIAG_X}px;top:{top}px;"
            f"width:{LANE_LABEL_W}px;height:{lane_h}px;display:flex;"
            f"align-items:center;justify-content:center;'>"
            f"<div style='writing-mode:vertical-rl;transform:rotate(180deg);"
            f"font-size:11px;color:{T.SUB};letter-spacing:.03em;'>{T.esc(ln)}</div></div>"
        )

    # warn on orphan boxes (a box no connector touches looks broken)
    import sys
    touched = {e.src for e in phase.edges} | {e.dst for e in phase.edges}
    for nd in phase.nodes:
        if nd.nid not in touched:
            print(f"[warn] swimlane phase {phase.pid}: node {nd.nid!r} "
                  f"({nd.title!r}) has no connector", file=sys.stderr)

    occupied = {(r.row, r.col) for r in rects.values()}
    svg = [f"<svg style='position:absolute;left:0;top:0' width='1280' height='{diag_h:.0f}'>"]
    for e in phase.edges:
        if e.src not in rects or e.dst not in rects:
            raise ValueError(f"[{phase.pid}] edge {e.src!r}->{e.dst!r}: unknown node id")
        a, b = rects[e.src], rects[e.dst]
        pts, arr = _route(a, b, occupied)
        colour = EDGE_COLOUR.get(e.kind, T.GOLD)
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        dash = "stroke-dasharray='6 5'" if e.dashed else ""
        svg.append(f"<polyline points='{d}' fill='none' stroke='{colour}' "
                   f"stroke-width='2' {dash}/>")
        svg.append(f"<polygon points='{_arrow(*arr)}' fill='{colour}'/>")
        if e.label:
            lx = (pts[0][0] + pts[1][0]) / 2
            ly = (pts[0][1] + pts[1][1]) / 2 - 1
            svg.append(f"<rect x='{lx-15:.0f}' y='{ly-9:.0f}' width='30' height='15' "
                       f"fill='{T.NAVY}' rx='3'/>"
                       f"<text x='{lx:.0f}' y='{ly+3:.0f}' text-anchor='middle' "
                       f"font-size='11' fill='{colour}'>{T.esc(e.label)}</text>")
    svg.append("</svg>")

    # node boxes
    boxes = []
    for nd in phase.nodes:
        r = rects[nd.nid]
        border, bg, text = NODE_STYLE.get(nd.kind, NODE_STYLE["standard"])
        sub = (f"<div style='font-size:11px;color:{T.SUB};margin-top:3px'>{T.esc(nd.sub)}</div>"
               if nd.sub else "")
        boxes.append(
            f"<div style='position:absolute;left:{r.x:.0f}px;top:{r.y:.0f}px;"
            f"width:{BOX_W}px;height:{BOX_H}px;background:{bg};border:2px solid {border};"
            f"border-radius:8px;display:flex;flex-direction:column;align-items:center;"
            f"justify-content:center;text-align:center;padding:4px 6px;'>"
            f"<div style='font-size:14px;font-weight:700;color:{text};line-height:1.15'>{T.esc(nd.title)}</div>"
            f"{sub}</div>"
        )

    note = (f"<div style='position:absolute;left:{DIAG_X}px;top:{diag_h+10:.0f}px;"
            f"font-size:11px;color:{T.SUB};font-style:italic'>{T.esc(phase.note)}</div>"
            if phase.note else "")
    legend = _legend(diag_h + (34 if phase.note else 18))
    return "".join(lanes_html) + "".join(svg) + "".join(boxes) + note + legend


def _dot(label, colour):
    return (f"<span style='display:inline-flex;align-items:center;gap:6px;"
            f"font-size:11px;color:{T.SUB};margin-right:20px'>"
            f"<span style='width:11px;height:11px;border-radius:50%;"
            f"background:{colour};display:inline-block'></span>{label}</span>")


def _line(label, colour, dashed):
    dash = "stroke-dasharray='5 4'" if dashed else ""
    return (f"<span style='display:inline-flex;align-items:center;gap:7px;"
            f"font-size:11px;color:{T.SUB};margin-right:20px'>"
            f"<svg width='26' height='8'><line x1='0' y1='4' x2='26' y2='4' "
            f"stroke='{colour}' stroke-width='2' {dash}/></svg>{label}</span>")


def _legend(top):
    """Two rows: box (step) colours, then connector (flow) colours/styles."""
    boxes = ("<span style='font-size:10px;color:" + T.GOLD3 +
             ";font-weight:700;margin-right:10px'>BOXES</span>"
             + _dot("Standard step", T.GOLD) + _dot("New step", T.GREEN)
             + _dot("Enhanced step", T.AMBER) + _dot("Exception step", T.RED))
    lines = ("<span style='font-size:10px;color:" + T.GOLD3 +
             ";font-weight:700;margin-right:10px'>FLOW</span>"
             + _line("Sequential", T.GOLD, False)
             + _line("Hand-off / conditional", T.GOLD, True)
             + _line("To a new step", T.GREEN, False)
             + _line("Exception / reject", T.RED, True))
    return (f"<div style='position:absolute;left:{DIAG_X}px;top:{top:.0f}px'>{boxes}</div>"
            f"<div style='position:absolute;left:{DIAG_X}px;top:{top+22:.0f}px'>{lines}</div>")


def _cover(pkg, optimised):
    meta = pkg.meta
    n_phases = pkg.opt_n_phases if optimised else pkg.n_phases
    n_steps = pkg.opt_n_steps if optimised else pkg.n_steps
    n_gate = pkg.opt_n_gateways if optimised else pkg.n_gateways
    line = (f"{meta.sop_id} · Optimised v{meta.new_version}" if optimised
            else f"{meta.sop_id} · Swimlane View")
    tags = pkg.swim_cover_tags or "Process tracks · Decision gateways · Exception handling"
    return f"""
    <div class="slide"><div class="cover">
      <div class="band"></div>
      <h1>{T.esc(meta.title)}</h1>
      <div class="sub">{T.esc(line)}</div>
      <div class="meta">{T.esc(tags)}</div>
      <div class="stats">
        <div class="stat"><div class="n" style="color:{T.BLUE}">{n_phases}</div><div class="l">Phases</div></div>
        <div class="stat"><div class="n" style="color:{T.GOLD}">{n_steps}</div><div class="l">Steps</div></div>
        <div class="stat"><div class="n" style="color:{T.AMBER}">{n_gate}</div><div class="l">Gateways</div></div>
      </div>
      <div class="foot">Generated by Flow Agent · Confidential · {T.esc(meta.sop_id)} · {T.esc(meta.title)}</div>
    </div></div>"""


def _phase_slide(phase, optimised):
    pill = T.AMBER if optimised else T.GOLD
    return f"""
    <div class="slide">
      <div style="display:flex;align-items:center;gap:16px;padding:14px 36px;
           background:{T.NAVY2};border-bottom:1px solid {T.NAVY3}">
        <span style="background:{pill};color:{T.NAVY};font-weight:700;font-size:12px;
              padding:6px 14px;border-radius:6px">PHASE {T.esc(phase.pid)}</span>
        <div>
          <div style="font-size:22px;font-weight:700;color:{T.GOLD}">Phase {T.esc(phase.pid)} — {T.esc(phase.name)}</div>
          <div style="font-size:12px;color:{T.SUB};margin-top:1px">{T.esc(phase.subtitle)}</div>
        </div>
      </div>
      {_diagram(phase)}
    </div>"""


def render(pkg, optimised: bool = False) -> str:
    phases = pkg.opt_swim_phases if optimised else pkg.swim_phases
    slides = [_cover(pkg, optimised)]
    for ph in phases:
        slides.append(_phase_slide(ph, optimised))
    return T.deck_page("".join(slides))
