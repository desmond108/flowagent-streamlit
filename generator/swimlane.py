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
    """Place every node. A node with x/y set is where the human put it; a node
    without is auto-placed from its (lane, col) grid slot exactly as before.

    The duplicate-cell check applies only to auto-placed nodes — once a box has
    been positioned by hand it no longer occupies a grid slot."""
    lane_index = {ln: i for i, ln in enumerate(phase.lanes)}
    n = len(phase.lanes)
    lane_h = min(LANE_CAP, (720 - DIAG_TOP - 96) / max(n, 1))
    rects = {}
    seen = {}
    for nd in phase.nodes:
        if nd.lane not in lane_index:
            raise ValueError(f"[{phase.pid}] node {nd.nid}: unknown lane {nd.lane!r}")
        row = lane_index[nd.lane]
        x = DIAG_X + LANE_LABEL_W + COL0 + nd.col * COL_W
        y = DIAG_TOP + row * lane_h + (lane_h - BOX_H) / 2
        placed = getattr(nd, "x", None) is not None or getattr(nd, "y", None) is not None
        if not placed:
            key = (nd.lane, nd.col)
            if key in seen:
                raise ValueError(
                    f"[{phase.pid}] nodes {seen[key]!r} and {nd.nid!r} collide at "
                    f"lane={nd.lane!r} col={nd.col}")
            seen[key] = nd.nid
        if getattr(nd, "x", None) is not None:
            x = float(nd.x)
        if getattr(nd, "y", None) is not None:
            y = float(nd.y)
        rects[nd.nid] = _Rect(x, y, BOX_W, BOX_H, row, nd.col)
    return rects, lane_h, n


def _anchor(r, toward):
    """Point on r's edge closest to `toward` — where a manual route attaches."""
    tx, ty = toward
    sides = [(r.cx, r.y), (r.cx, r.y + r.h), (r.x, r.cy), (r.x + r.w, r.cy)]
    return min(sides, key=lambda p: (p[0] - tx) ** 2 + (p[1] - ty) ** 2)


def _orthogonalise(pts):
    """Insert elbows so a hand-drawn route stays axis-aligned.

    A user drags a bend to an arbitrary point, but every connector in the deck is
    orthogonal — joining waypoints with straight lines would produce diagonals
    that read as a different diagram (and a diagonal arrowhead). So each pair of
    consecutive points is connected by an L rather than a line."""
    out = [pts[0]]
    for cx, cy in pts[1:]:
        px, py = out[-1]
        if abs(px - cx) < 0.5 and abs(py - cy) < 0.5:
            continue                      # duplicate point
        if abs(px - cx) > 0.5 and abs(py - cy) > 0.5:
            out.append((cx, py))          # elbow: travel horizontally, then turn
        out.append((cx, cy))
    return out


def _route_manual(a, b, wpts):
    """Honour a hand-drawn route: attach to each box, pass through the waypoints,
    kept orthogonal throughout."""
    pts = [(float(p[0]), float(p[1])) for p in wpts if len(p) >= 2]
    if not pts:
        return None
    poly = _orthogonalise([_anchor(a, pts[0])] + pts + [_anchor(b, pts[-1])])
    if len(poly) < 2:
        return None
    return poly, _arrow_of(poly)


def _arrow(x, y, dx, dy):
    """Small triangle arrowhead pointing in (dx,dy) direction."""
    import math
    ang = math.atan2(dy, dx)
    size = 7
    p1 = (x, y)
    p2 = (x - size * math.cos(ang - 0.4), y - size * math.sin(ang - 0.4))
    p3 = (x - size * math.cos(ang + 0.4), y - size * math.sin(ang + 0.4))
    return f"{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}"


# --------------------------------------------------------------------------
# Connector routing
#
# Routes are scored, not guessed. Each candidate polyline is penalised for
# crossing a box (heavily) and for running along a connector that has already
# been drawn (lightly, by shared length). The cheapest candidate wins.
#
# This replaces a best-of-two-L-routes rule that had two failure modes users
# reported: it had no idea other arrows existed, so two connectors between
# similar boxes were handed the SAME path and drawn on top of each other; and
# with only 2-segment routes available it had nowhere to escape to, so it picked
# the route through the *fewest* boxes even when that was still one or more.
# Geometry is used directly (not grid cells) so hand-placed boxes route correctly.
# --------------------------------------------------------------------------
BOX_PENALTY = 1000.0    # crossing a box is always worse than any overlap
OUT = 14                # stub length before a detour turns
JOGS = (-20, 20, -34, 34, -48, 48)   # lateral offsets tried for a dodge


def _segments(pts):
    return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def _is_h(s):
    return abs(s[0][1] - s[1][1]) < 0.5


def _is_v(s):
    return abs(s[0][0] - s[1][0]) < 0.5


def _overlap_len(s1, s2):
    """Length over which two axis-aligned segments run along the same line."""
    if _is_h(s1) and _is_h(s2) and abs(s1[0][1] - s2[0][1]) <= 2.0:
        lo = max(min(s1[0][0], s1[1][0]), min(s2[0][0], s2[1][0]))
        hi = min(max(s1[0][0], s1[1][0]), max(s2[0][0], s2[1][0]))
        return max(0.0, hi - lo)
    if _is_v(s1) and _is_v(s2) and abs(s1[0][0] - s2[0][0]) <= 2.0:
        lo = max(min(s1[0][1], s1[1][1]), min(s2[0][1], s2[1][1]))
        hi = min(max(s1[0][1], s1[1][1]), max(s2[0][1], s2[1][1]))
        return max(0.0, hi - lo)
    return 0.0


def _seg_crosses_rect(s, r):
    (x1, y1), (x2, y2) = s
    if _is_h(s):
        if not (r.y + 1 < y1 < r.y + r.h - 1):
            return False
        return min(max(x1, x2), r.x + r.w) - max(min(x1, x2), r.x) > 1
    if _is_v(s):
        if not (r.x + 1 < x1 < r.x + r.w - 1):
            return False
        return min(max(y1, y2), r.y + r.h) - max(min(y1, y2), r.y) > 1
    return False


def _score(poly, rects, skip, drawn):
    segs = _segments(poly)
    boxes = sum(1 for s in segs for nid, r in rects.items()
                if nid not in skip and _seg_crosses_rect(s, r))
    overlap = sum(_overlap_len(s, d) for s in segs for d in drawn)
    # Mild preference for shorter, simpler routes when nothing else separates them.
    length = sum(abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]) for s in segs)
    return boxes * BOX_PENALTY + overlap * 2.0 + length * 0.01 + len(segs) * 0.5


def _arrow_of(poly):
    (x1, y1), (x2, y2) = poly[-2], poly[-1]
    return (x2, y2, x2 - x1, y2 - y1)


def _candidates(a, b):
    """Every reasonable orthogonal route from a to b, cheapest-first order
    irrelevant — the scorer decides."""
    out = []
    right = b.cx >= a.cx
    down = b.cy >= a.cy
    sx = a.x + a.w if right else a.x          # horizontal exit from a
    ex = b.x if right else b.x + b.w          # horizontal entry to b
    sy = a.y + a.h if down else a.y           # vertical exit from a
    ey = b.y if down else b.y + b.h           # vertical entry to b
    dx = OUT if right else -OUT
    dy = OUT if down else -OUT

    same_row = abs(a.cy - b.cy) < 1.0
    same_col = abs(a.cx - b.cx) < 1.0

    if same_row:
        out.append([(sx, a.cy), (ex, a.cy)])
        # Dodges: out, offset, across, back in — for when a straight run would
        # sit on top of another connector or cut through an intervening box.
        for j in JOGS:
            out.append([(sx, a.cy), (sx + dx, a.cy), (sx + dx, a.cy + j),
                        (ex - dx, a.cy + j), (ex - dx, b.cy), (ex, b.cy)])
    elif same_col:
        out.append([(a.cx, sy), (a.cx, ey)])
        for j in JOGS:
            out.append([(a.cx, sy), (a.cx, sy + dy), (a.cx + j, sy + dy),
                        (a.cx + j, ey - dy), (b.cx, ey - dy), (b.cx, ey)])
    else:
        # Vertical-first and horizontal-first L-routes (the original two).
        out.append([(a.cx, sy), (a.cx, b.cy), (ex, b.cy)])
        out.append([(sx, a.cy), (b.cx, a.cy), (b.cx, ey)])
        # Z-routes: the 3-segment detours the old router could not express.
        mx = (a.cx + b.cx) / 2
        my = (a.cy + b.cy) / 2
        out.append([(sx, a.cy), (mx, a.cy), (mx, b.cy), (ex, b.cy)])
        out.append([(a.cx, sy), (a.cx, my), (b.cx, my), (b.cx, ey)])
        for j in JOGS[:4]:
            out.append([(sx, a.cy), (mx + j, a.cy), (mx + j, b.cy), (ex, b.cy)])
            out.append([(a.cx, sy), (a.cx, my + j), (b.cx, my + j), (b.cx, ey)])
    return out


def _route(a, b, rects, skip, drawn):
    """Return (polyline_points, arrow) for the best-scoring orthogonal route."""
    best = min(_candidates(a, b), key=lambda p: _score(p, rects, skip, drawn))
    return best, _arrow_of(best)


def _routes(phase, rects):
    """Route every edge of a phase, in order. Yields (edge, points, arrow).

    Shared by the renderer and the editor so the handles you drag sit on the
    exact polyline the PDF prints — there is no second routing pass to drift."""
    drawn: list = []
    out = []
    for e in phase.edges:
        if e.src not in rects or e.dst not in rects:
            raise ValueError(f"[{phase.pid}] edge {e.src!r}->{e.dst!r}: unknown node id")
        a, b = rects[e.src], rects[e.dst]
        wp = getattr(e, "waypoints", None)
        manual = _route_manual(a, b, wp) if wp else None
        pts, arr = manual if manual else _route(a, b, rects, {e.src, e.dst}, drawn)
        drawn.extend(_segments(pts))
        out.append((e, pts, arr))
    return out


def _diagram(phase):
    rects, lane_h, n = _layout(phase)
    diag_w = 1280 - 2 * DIAG_X
    diag_h = DIAG_TOP + n * lane_h
    # A hand-placed box may sit below the lanes; grow the canvas so the legend
    # and note stay clear of it. No-op when nothing has been moved.
    if rects:
        diag_h = max(diag_h, max(r.y + r.h for r in rects.values()) + 12)

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

    svg = [f"<svg style='position:absolute;left:0;top:0' width='1280' height='{diag_h:.0f}'>"]
    for e, pts, arr in _routes(phase, rects):
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
            f"<div data-nid='{T.esc(nd.nid)}' "
            f"style='position:absolute;left:{r.x:.0f}px;top:{r.y:.0f}px;"
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


# --------------------------------------------------------------------------
# Editor support
#
# The browser editor drags handles over THIS renderer's output rather than
# drawing its own diagram. One layout engine, one source of truth: what you
# drag is what the PDF prints. See phase_view().
# --------------------------------------------------------------------------
def phase_view(phase) -> dict:
    """Everything the editor needs to make a phase interactive: the rendered
    markup, each box's rectangle, and every arrow's actual routed polyline."""
    rects, lane_h, n = _layout(phase)
    diag_h = DIAG_TOP + n * lane_h
    if rects:
        diag_h = max(diag_h, max(r.y + r.h for r in rects.values()) + 12)
    edges = [{
        "i": i,
        "src": e.src,
        "dst": e.dst,
        "points": [[round(x, 1), round(y, 1)] for x, y in pts],
        "manual": bool(getattr(e, "waypoints", None)),
        "kind": e.kind,
    } for i, (e, pts, _) in enumerate(_routes(phase, rects))]
    return {
        "html": _diagram(phase),
        "rects": {nid: {"x": r.x, "y": r.y, "w": r.w, "h": r.h}
                  for nid, r in rects.items()},
        "edges": edges,
        "width": 1280,
        "height": diag_h + 70,   # room for the note + legend
        "lane_h": lane_h,
        "lanes": list(phase.lanes),
        "diag_top": DIAG_TOP,
    }


def auto_xy(phase, nid: str) -> tuple:
    """Where auto-layout would put this node — used to seed a drag and to
    implement 'reset to automatic'."""
    saved = [(n, getattr(n, "x", None), getattr(n, "y", None)) for n in phase.nodes]
    try:
        for n in phase.nodes:
            n.x = n.y = None
        rects, _, _ = _layout(phase)
        r = rects[nid]
        return r.x, r.y
    finally:
        for n, x, y in saved:
            n.x, n.y = x, y
