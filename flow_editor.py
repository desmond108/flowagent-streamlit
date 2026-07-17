"""FlowAgent — flow chart editor.

Edits the CANONICAL JSON, never the PDF. The browser canvas drags handles over
markup produced by `generator/swimlane.py`; on drop, the new position is written
back into the package as an x/y override, Python re-renders (re-routing the
arrows), and that render replaces what the browser drew. One layout engine, so
the PDF cannot disagree with the screen.

Because manual placement lives in dedicated override fields, an edit that only
touches them is provably cosmetic — see `contract.classify`.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os

import streamlit as st
import streamlit.components.v1 as components

from generator import contract, swimlane

KINDS = ["standard", "new", "enhanced", "exception", "decision", "terminal"]
EDGE_KINDS = ["standard", "new", "exception"]

# Declared at import time so the components' static files are registered when the
# app starts, not on first use of the editor.
_HERE = os.path.dirname(os.path.abspath(__file__))
_CANVAS = components.declare_component("flow_canvas", path=os.path.join(_HERE, "flow_canvas"))
# SPIKE: client-side canvas. React Flow owns interaction; the canonical JSON still
# owns position; Python still renders the PDF. Loaded from a CDN as ES modules so
# there is no npm build step — fine for a spike, must be vendored for production.
_CANVAS_RF = components.declare_component("flow_canvas_rf", path=os.path.join(_HERE, "flow_canvas_rf"))


def _canvas():
    return _CANVAS


# --- state ------------------------------------------------------------------
def load(pkg_dict: dict, sop_id: str) -> None:
    """Open a package in the editor. Keeps a pristine copy for comparison."""
    st.session_state["ed_cur"] = copy.deepcopy(pkg_dict)
    st.session_state["ed_orig"] = copy.deepcopy(pkg_dict)
    st.session_state["ed_sop"] = sop_id
    st.session_state["ed_sel"] = None
    st.session_state["ed_undo"] = []


def is_loaded() -> bool:
    return "ed_cur" in st.session_state


def _cur() -> dict:
    return st.session_state["ed_cur"]


def _push_undo() -> None:
    st.session_state.setdefault("ed_undo", []).append(copy.deepcopy(_cur()))
    del st.session_state["ed_undo"][:-40]   # keep the last 40 steps


def _phases(d: dict, opt: bool) -> list:
    return d["opt_swim_phases" if opt else "swim_phases"]


def _find(nodes: list, nid: str):
    return next((n for n in nodes if n["nid"] == nid), None)


# --- editing operations (all operate on canonical JSON) ---------------------
def _move(ph: dict, nid: str, x: float, y: float) -> None:
    n = _find(ph["nodes"], nid)
    if n is not None:
        n["x"], n["y"] = float(x), float(y)


def _reset_node(ph: dict, nid: str) -> None:
    n = _find(ph["nodes"], nid)
    if n is not None:
        n["x"] = n["y"] = None


def _bend(ph: dict, i: int, x: float, y: float, view: dict) -> None:
    """Drag a point on an arrow. The first bend converts an auto-routed arrow to
    a manual one, seeded from the route it already had, so it doesn't jump."""
    if not (0 <= i < len(ph["edges"])):
        return
    e = ph["edges"][i]
    ev = next((v for v in view["edges"] if v["i"] == i), None)
    wp = e.get("waypoints")
    if not wp:
        # Seed from the current route's interior points (drop the two endpoints,
        # which are anchored to the boxes), then add this one.
        interior = [list(p) for p in (ev["points"][1:-1] if ev else [])]
        wp = interior
    # Replace the nearest existing waypoint, or add one.
    pt = [round(float(x), 1), round(float(y), 1)]
    if wp:
        j = min(range(len(wp)),
                key=lambda k: (wp[k][0] - pt[0]) ** 2 + (wp[k][1] - pt[1]) ** 2)
        near = (wp[j][0] - pt[0]) ** 2 + (wp[j][1] - pt[1]) ** 2
        if near < 60 ** 2:
            wp[j] = pt
        else:
            wp.append(pt)
    else:
        wp = [pt]
    e["waypoints"] = wp


def _straighten(ph: dict, i: int) -> None:
    if 0 <= i < len(ph["edges"]):
        ph["edges"][i]["waypoints"] = None


def _route_set(ph: dict, i: int, wp) -> None:
    """Set an arrow's whole route. The client-side canvas knows exactly which
    bends exist, so it sends the full list rather than a single point to be
    guessed at. An empty list means 'back to automatic'."""
    if 0 <= i < len(ph["edges"]):
        pts = [[round(float(p[0]), 1), round(float(p[1]), 1)]
               for p in (wp or []) if len(p) >= 2]
        ph["edges"][i]["waypoints"] = pts or None


def _reconnect(ph: dict, i: int, src: str, dst: str) -> None:
    """Move an arrow's end onto a different box. The hand-drawn route is dropped:
    bends chosen for the old geometry are meaningless against the new one."""
    if 0 <= i < len(ph["edges"]):
        ph["edges"][i].update(src=src, dst=dst, waypoints=None)


def _reset_phase(ph: dict) -> None:
    for n in ph["nodes"]:
        n["x"] = n["y"] = None
    for e in ph["edges"]:
        e["waypoints"] = None


# --- UI ---------------------------------------------------------------------
def render_editor() -> None:
    d = _cur()
    sop_id = st.session_state.get("ed_sop", "SOP")

    opt = st.toggle("Edit the optimised flow instead of the baseline", value=False)
    phases = _phases(d, opt)
    if not phases:
        st.info("This package has no swimlane phases to edit.")
        return

    labels = [f"Phase {p['pid']} — {p['name']}" for p in phases]
    idx = st.selectbox("Phase", range(len(phases)), format_func=lambda i: labels[i])
    ph = phases[idx]

    # Rebuild the package so the renderer sees current edits, then draw.
    try:
        pkg = contract.from_dict(d)
    except (TypeError, KeyError, ValueError) as e:
        st.error(f"The edited package is no longer valid: {e}")
        return
    phase_obj = (pkg.opt_swim_phases if opt else pkg.swim_phases)[idx]

    try:
        view = swimlane.phase_view(phase_obj)
    except ValueError as e:
        st.error(f"Cannot draw this phase: {e}")
        return

    c0, c1, c2, c3 = st.columns([1.4, 1, 1, 1.6])
    with c0:
        engine = st.radio("Canvas", ["React Flow (spike)", "Classic"],
                          horizontal=True, label_visibility="collapsed",
                          help="React Flow: dragging happens in the browser, so it "
                               "should feel native. Classic: every drop round-trips "
                               "to Python.")
    with c1:
        snap = st.selectbox("Snap", [0, 5, 10, 20], index=2,
                            format_func=lambda v: "Off" if v == 0 else f"{v}px")
    with c2:
        if st.button("↺ Undo", disabled=not st.session_state.get("ed_undo")):
            st.session_state["ed_cur"] = st.session_state["ed_undo"].pop()
            st.rerun()
    with c3:
        if st.button("Reset this phase to automatic layout"):
            _push_undo()
            _reset_phase(ph)
            st.rerun()

    if engine.startswith("React"):
        evt = _rf_canvas(phase_obj, ph, snap, sop_id, opt, idx)
    else:
        # Selection is deliberately NOT in the stamp: the canvas repaints selection
        # itself, so clicking a box doesn't re-inject the whole diagram.
        stamp = hashlib.md5(view["html"].encode()).hexdigest()
        evt = _canvas()(
            html=view["html"], rects=view["rects"], edges=view["edges"],
            width=view["width"], height=view["height"], snap=snap,
            selected=st.session_state.get("ed_sel"), stamp=stamp,
            key=f"canvas_{sop_id}_{opt}_{idx}", default=None,
        )

    # Apply an event coming back from the browser (guarded so a rerun doesn't
    # replay the same one).
    if evt and evt.get("t") != st.session_state.get("ed_evt"):
        st.session_state["ed_evt"] = evt["t"]
        action = evt.get("action")
        if action == "select":
            st.session_state["ed_sel"] = evt.get("nid")
            st.rerun()
        elif action == "move":
            _push_undo()
            st.session_state["ed_sel"] = evt.get("nid")
            _move(ph, evt["nid"], evt["x"], evt["y"])
            st.rerun()
        elif action == "bend":
            _push_undo()
            _bend(ph, evt["edge"], evt["x"], evt["y"], view)
            st.rerun()
        elif action == "straighten":
            _push_undo()
            _straighten(ph, evt["edge"])
            st.rerun()
        # --- events only the React Flow canvas raises ---
        elif action == "connect":
            _push_undo()
            ph["edges"].append({"src": evt["src"], "dst": evt["dst"], "label": "",
                                "dashed": False, "kind": "standard", "waypoints": None})
            st.rerun()
        elif action == "delete_nodes":
            _push_undo()
            ids = set(evt.get("ids") or [])
            ph["nodes"] = [n for n in ph["nodes"] if n["nid"] not in ids]
            ph["edges"] = [e for e in ph["edges"]
                           if e["src"] not in ids and e["dst"] not in ids]
            if st.session_state.get("ed_sel") in ids:
                st.session_state["ed_sel"] = None
            st.rerun()
        elif action == "delete_edges":
            _push_undo()
            drop = set(evt.get("idx") or [])
            ph["edges"] = [e for i, e in enumerate(ph["edges"]) if i not in drop]
            st.rerun()
        elif action == "route":
            _push_undo()
            _route_set(ph, evt["edge"], evt.get("waypoints"))
            st.rerun()
        elif action == "reconnect":
            _push_undo()
            _reconnect(ph, evt["edge"], evt["src"], evt["dst"])
            st.rerun()

    _properties(ph, view)
    st.divider()
    _edges(ph)
    st.divider()
    _review(d)


def _rf_canvas(phase_obj, ph: dict, snap: int, sop_id: str, opt: bool, idx: int):
    """SPIKE: the client-side canvas.

    The stamp covers STRUCTURE only (ids, wording, connections) — never position.
    So a drag sends x/y back, Python stores it, and the returned props don't reset
    the canvas. That is the whole trick: the browser keeps its state while
    dragging, and Python is still the only thing that renders the PDF."""
    v = swimlane.phase_rf(phase_obj)
    structure = json.dumps(
        [[(n["id"], n["title"], n["sub"], n["kind"], n["lane"]) for n in v["nodes"]],
         [(e["source"], e["target"], e["label"], e["kind"], e["dashed"]) for e in v["edges"]],
         [L["label"] for L in v["lanes"]]], sort_keys=True)
    return _CANVAS_RF(
        nodes=v["nodes"], edges=v["edges"], lanes=v["lanes"],
        laneX=v["laneX"], laneW=v["laneW"], labelW=v["labelW"],
        palette=v["palette"], snap=snap,
        frameHeight=int(min(760, max(460, v["height"]))),
        stamp=hashlib.md5(structure.encode()).hexdigest(),
        key=f"rf_{sop_id}_{opt}_{idx}", default=None,
    )


def _properties(ph: dict, view: dict) -> None:
    sel = st.session_state.get("ed_sel")
    st.subheader("Box")
    if not sel:
        st.caption("Click a box on the diagram to edit it, or add one below.")
    else:
        n = _find(ph["nodes"], sel)
        if n is None:
            st.session_state["ed_sel"] = None
            st.rerun()
        a, b = st.columns(2)
        with a:
            title = st.text_input("Title", value=n["title"], key=f"t_{sel}")
            sub = st.text_input("Subtitle", value=n.get("sub", ""), key=f"s_{sel}")
        with b:
            lane = st.selectbox("Lane", view["lanes"],
                                index=view["lanes"].index(n["lane"])
                                if n["lane"] in view["lanes"] else 0, key=f"l_{sel}")
            kind = st.selectbox("Type", KINDS,
                                index=KINDS.index(n.get("kind", "standard"))
                                if n.get("kind") in KINDS else 0, key=f"k_{sel}")
        if (title, sub, lane, kind) != (n["title"], n.get("sub", ""), n["lane"], n.get("kind")):
            _push_undo()
            n.update(title=title, sub=sub, lane=lane, kind=kind)
            st.rerun()

        placed = n.get("x") is not None or n.get("y") is not None
        st.caption(f"Position: {'moved by hand' if placed else 'automatic'}"
                   + (f" · x={n['x']:.0f} y={n['y']:.0f}" if placed else ""))
        x, y, z = st.columns(3)
        with x:
            if st.button("Reset position", disabled=not placed, key=f"rp_{sel}"):
                _push_undo(); _reset_node(ph, sel); st.rerun()
        with y:
            if st.button("🗑 Delete box", key=f"db_{sel}"):
                _push_undo()
                ph["nodes"] = [q for q in ph["nodes"] if q["nid"] != sel]
                ph["edges"] = [e for e in ph["edges"]
                               if e["src"] != sel and e["dst"] != sel]
                st.session_state["ed_sel"] = None
                st.rerun()

    with st.expander("Add a box"):
        a, b, c = st.columns(3)
        nid = a.text_input("Id", key="new_nid", placeholder="n99")
        title = b.text_input("Title", key="new_title")
        lane = c.selectbox("Lane", view["lanes"], key="new_lane")
        d1, d2, d3 = st.columns(3)
        col = d1.number_input("Column", 0, 20, 0, key="new_col")
        kind = d2.selectbox("Type", KINDS, key="new_kind")
        sub = d3.text_input("Subtitle", key="new_sub")
        if st.button("Add box", type="primary", disabled=not (nid and title)):
            if _find(ph["nodes"], nid):
                st.error(f"Id {nid!r} already exists in this phase.")
            else:
                _push_undo()
                ph["nodes"].append({"nid": nid, "lane": lane, "col": int(col),
                                    "title": title, "sub": sub, "kind": kind,
                                    "x": None, "y": None})
                st.session_state["ed_sel"] = nid
                st.rerun()


def _edges(ph: dict) -> None:
    st.subheader("Arrows")
    ids = [n["nid"] for n in ph["nodes"]]
    if not ph["edges"]:
        st.caption("No arrows in this phase.")
    for i, e in enumerate(list(ph["edges"])):
        a, b, c, d_, f = st.columns([2, 2, 2, 1.4, 0.8])
        src = a.selectbox("From", ids, index=ids.index(e["src"]) if e["src"] in ids else 0,
                          key=f"es_{i}", label_visibility="collapsed")
        dst = b.selectbox("To", ids, index=ids.index(e["dst"]) if e["dst"] in ids else 0,
                          key=f"ed_{i}", label_visibility="collapsed")
        lab = c.text_input("Label", value=e.get("label", ""), key=f"el_{i}",
                           label_visibility="collapsed", placeholder="label")
        kind = d_.selectbox("Kind", EDGE_KINDS,
                            index=EDGE_KINDS.index(e.get("kind", "standard"))
                            if e.get("kind") in EDGE_KINDS else 0,
                            key=f"ek_{i}", label_visibility="collapsed")
        if (src, dst, lab, kind) != (e["src"], e["dst"], e.get("label", ""), e.get("kind")):
            _push_undo()
            e.update(src=src, dst=dst, label=lab, kind=kind)
            st.rerun()
        if f.button("🗑", key=f"ex_{i}"):
            _push_undo()
            ph["edges"].pop(i)
            st.rerun()

    with st.expander("Add an arrow"):
        a, b, c, d_ = st.columns(4)
        src = a.selectbox("From", ids, key="ne_src")
        dst = b.selectbox("To", ids, key="ne_dst")
        lab = c.text_input("Label", key="ne_lab")
        kind = d_.selectbox("Type", EDGE_KINDS, key="ne_kind")
        if st.button("Add arrow", type="primary", disabled=not ids or src == dst):
            _push_undo()
            ph["edges"].append({"src": src, "dst": dst, "label": lab,
                                "dashed": False, "kind": kind, "waypoints": None})
            st.rerun()


def _review(d: dict) -> None:
    """The two-button step: FlowAgent states what it found, the user decides."""
    orig = st.session_state["ed_orig"]
    if contract.sha256(orig) == contract.sha256(d):
        st.caption("No changes yet.")
        return

    c = contract.classify(orig, d)
    st.subheader("Your changes")
    summary = ", ".join(c["cosmetic"] + c["material_changes"]) or "package edited"

    if c["material"]:
        st.warning(
            f"**{summary}.** This changes the process, so the hierarchy, fit-gap and "
            "optimised documents no longer match the flow chart.", icon="⚠️")
    else:
        st.success(
            f"**{summary}.** No process changes detected — this is cosmetic, so the "
            "other five deliverables are unaffected.", icon="✅")

    a, b = st.columns(2)
    with a:
        st.button("Cosmetic only — flow chart only", use_container_width=True,
                  type="primary" if not c["material"] else "secondary",
                  help="Re-render the flow chart. The other deliverables stay as they are.")
    with b:
        st.button("Material — reprocess the others", use_container_width=True,
                  type="primary" if c["material"] else "secondary", disabled=True,
                  help="AI re-derivation of the other five deliverables is Stage 2 "
                       "(task G2a) and is not built yet.")
    if c["material"]:
        st.caption(
            "Reprocessing is not implemented yet — it needs the AI to re-derive the "
            "other five deliverables from your edited flow (Stage 2, G2a). For now the "
            "flow chart renders correctly and the other five are stale.")

    st.download_button(
        "⬇️ Download edited analysis (canonical JSON)",
        data=json.dumps(d, indent=2, ensure_ascii=False),
        file_name=f"{st.session_state.get('ed_sop','package')}_edited.json",
        mime="application/json")
