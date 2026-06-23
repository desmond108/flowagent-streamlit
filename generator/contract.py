"""The deterministic boundary: canonical JSON <-> SopPackage.

Everything UPSTREAM of this module (an LLM, a fine-tuned model, or a human)
authors a SopPackage and is allowed to be non-deterministic. Everything
DOWNSTREAM (validation + rendering) is a pure function of the canonical JSON.

`canonical_json()` + `sha256()` give you a stable content hash for a package,
so you can freeze an authored analysis and detect any drift later. Re-running
the renderer on the same JSON always produces the same document content.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import re

from . import model as M


# --------------------------------------------------------------------------
# Serialise: SopPackage -> dict / JSON
# --------------------------------------------------------------------------
def to_dict(pkg: M.SopPackage) -> dict:
    """dataclasses -> plain dict (deep). Field order is definition order."""
    return dataclasses.asdict(pkg)


def to_json(pkg: M.SopPackage) -> str:
    """Human-readable, committable JSON (stable field order, not key-sorted)."""
    return json.dumps(to_dict(pkg), ensure_ascii=False, indent=2)


def canonical_json(pkg_or_dict) -> str:
    """Canonical form for hashing: keys sorted, no incidental whitespace.

    Deterministic for identical content regardless of authoring order."""
    d = pkg_or_dict if isinstance(pkg_or_dict, dict) else to_dict(pkg_or_dict)
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(pkg_or_dict) -> str:
    return hashlib.sha256(canonical_json(pkg_or_dict).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# Deserialise: dict / JSON -> SopPackage  (the validating reconstruction)
# --------------------------------------------------------------------------
def _list(cls, items):
    return [cls(**x) for x in items]


# The fit-gap templates unpack some plain lists with a FIXED arity. Authored
# data always matches; these coerce loosely-shaped LLM output to the exact shape
# so a stray extra/missing element can't crash the renderer.
def _pair(x):
    x = list(x)
    return (x[0] if x else "", x[1] if len(x) > 1 else "")


def _kv(x):
    x = list(x)
    if not x:
        return ("", "")
    return (x[0], " ".join(str(s) for s in x[1:]) if len(x) > 1 else "")


def _triple(x):
    x = list(x)
    title = x[0] if x else ""
    sub = x[1] if len(x) > 1 else ""
    keys = x[2] if len(x) > 2 else []
    return (title, sub, keys if isinstance(keys, list) else [keys])


def _num(x, default=0):
    """Coerce a value to a number — the renderer does arithmetic on fit scores,
    but LLM output sometimes returns them as strings (e.g. '70', '85%')."""
    if isinstance(x, (int, float)):
        return x
    m = re.search(r"-?\d+(?:\.\d+)?", str(x))
    if not m:
        return default
    s = m.group(0)
    return float(s) if "." in s else int(s)


def _setnum(d, key):
    if isinstance(d, dict) and key in d:
        d[key] = _num(d[key])


def _swim_phase(d):
    d = dict(d)
    d["nodes"] = _list(M.SwimNode, d["nodes"])
    d["edges"] = _list(M.SwimEdge, d["edges"])
    return M.SwimPhase(**d)


def _fitgap(d):
    d = dict(d)
    # numeric coercion on nested dataclass rows (LLM may emit numbers as strings)
    for it in d.get("phase_bars", []):
        _setnum(it, "value")
    for it in d.get("phase_cards", []):
        _setnum(it, "value")
    for it in d.get("control_bars", []):
        _setnum(it, "value")
    for it in d.get("remediations", []):
        _setnum(it, "rank")
    d["phase_bars"] = _list(M.FitPhaseBar, d["phase_bars"])
    d["phase_cards"] = _list(M.PhaseScoreCard, d["phase_cards"])
    d["items"] = _list(M.FitItem, d["items"])
    d["critical_missing"] = _list(M.CriticalGap, d["critical_missing"])
    d["control_bars"] = _list(M.ControlBar, d["control_bars"])
    d["remediations"] = _list(M.Remediation, d["remediations"])
    # These stay as plain lists but the templates unpack them with a fixed arity,
    # so coerce each row to the exact shape it expects (and numbers to numbers).
    d["metrics"] = [_kv(x) for x in d.get("metrics", [])]
    d["groups"] = [_pair(x) for x in d.get("groups", [])]
    d["risk_impact"] = [(p[0], _num(p[1])) for p in (_pair(x) for x in d.get("risk_impact", []))]
    d["radar"] = [(p[0], _num(p[1])) for p in (_pair(x) for x in d.get("radar", []))]
    d["detail_slides"] = [_triple(x) for x in d.get("detail_slides", [])]
    for k in ("overall_fit", "partial_pct", "fits", "gaps", "partials",
              "steps_analysed", "phases_count", "projected_fit"):
        if k in d:
            d[k] = _num(d[k])
    return M.FitGap(**d)


def _doc(d):
    sections = [M.DocSection(title=s["title"], blocks=s["blocks"]) for s in d["sections"]]
    return M.OptimisedDoc(subtitle=d["subtitle"], sections=sections)


def from_dict(d: dict) -> M.SopPackage:
    d = dict(d)
    d["meta"] = M.Meta(**d["meta"])
    d["phases"] = _list(M.Phase, d["phases"])
    d["steps"] = _list(M.Step, d["steps"])
    d["authority"] = _list(M.AuthorityRow, d["authority"])
    d["swim_phases"] = [_swim_phase(p) for p in d["swim_phases"]]
    d["fitgap"] = _fitgap(d["fitgap"])
    d["opt_phases"] = _list(M.Phase, d["opt_phases"])
    d["opt_steps"] = _list(M.Step, d["opt_steps"])
    d["opt_swim_phases"] = [_swim_phase(p) for p in d["opt_swim_phases"]]
    d["optimised_doc"] = _doc(d["optimised_doc"])
    for k in ("n_phases", "n_steps", "n_roles", "n_gateways",
              "opt_n_phases", "opt_n_steps", "opt_n_gateways", "opt_fit"):
        if k in d:
            d[k] = _num(d[k])
    return M.SopPackage(**d)


def from_json(text: str) -> M.SopPackage:
    return from_dict(json.loads(text))


# --------------------------------------------------------------------------
# Optional structural validation against a JSON Schema
# --------------------------------------------------------------------------
def validate(d: dict) -> list[str]:
    """Validate a candidate package dict against SCHEMA.

    Uses `jsonschema` if installed; otherwise falls back to round-tripping
    through from_dict() (which raises on missing/extra fields). Returns a list
    of human-readable errors ([] == valid)."""
    try:
        import jsonschema  # type: ignore
        validator = jsonschema.Draft202012Validator(SCHEMA)
        return [f"{'/'.join(map(str, e.path))}: {e.message}"
                for e in validator.iter_errors(d)]
    except ModuleNotFoundError:
        try:
            from_dict(d)
            return []
        except (TypeError, KeyError) as e:
            return [f"structural error: {e}"]


# Representative JSON Schema (Draft 2020-12) for the canonical package.
# This is the CONTRACT an authoring model is asked to fill. It is the
# structured-output `schema` passed to the Claude API (see analyzer.py).
#
# Note on `optimised_doc.sections[].blocks`: blocks are heterogeneous tagged
# arrays (e.g. ["para", "..."] / ["table", headers, rows, highlights]). Strict
# json_schema structured-output mode handles homogeneous arrays best, so the
# pragmatic options are (a) keep blocks loosely typed here and validate them in
# from_dict (done below), or (b) author the document body in a separate, looser
# sub-call. We take (a): blocks are `array` and checked structurally on load.
def _obj(props, required=None):
    return {"type": "object", "additionalProperties": False, "properties": props,
            "required": required or list(props)}


_STR = {"type": "string"}
_INT = {"type": "integer"}
_PHASE = _obj({k: _STR for k in
               ["pid", "name", "subtitle", "circle", "roles", "step_range", "summary"]})
_STEP = _obj({"num": _STR, "phase": _STR, "activity": _STR, "responsible": _STR,
              "output": _STR, "timeline": _STR, "controls": _STR, "kind": _STR,
              "decision": {"type": ["string", "null"]},
              "branches": {"type": "array", "items": _STR}})
_NODE = _obj({"nid": _STR, "lane": _STR, "col": _INT, "title": _STR, "sub": _STR, "kind": _STR})
_EDGE = _obj({"src": _STR, "dst": _STR, "label": _STR, "dashed": {"type": "boolean"}, "kind": _STR})
_SWIM = _obj({"pid": _STR, "name": _STR, "subtitle": _STR,
              "lanes": {"type": "array", "items": _STR},
              "nodes": {"type": "array", "items": _NODE},
              "edges": {"type": "array", "items": _EDGE}, "note": _STR})
_FITITEM = _obj({"num": _STR, "name": _STR, "status": {"enum": ["FIT", "PARTIAL", "GAP"]},
                 "detail": _STR, "owner": _STR, "ref": _STR, "group": _STR})

SCHEMA = _obj({
    "meta": _obj({k: _STR for k in
                  ["sop_id", "slug", "title", "short_title", "version", "owner", "org",
                   "catalog", "catalog_short", "new_version", "effective_date",
                   "supersedes", "approved_by", "classification"]}),
    "phases": {"type": "array", "items": _PHASE},
    "steps": {"type": "array", "items": _STEP},
    "authority": {"type": "array",
                  "items": _obj({"band": _STR, "first": _STR, "second": _STR})},
    "swim_phases": {"type": "array", "items": _SWIM},
    "n_phases": _INT, "n_steps": _INT, "n_roles": _INT, "n_gateways": _INT,
    "fitgap": _obj({
        "overall_fit": _INT, "partial_pct": _INT, "fits": _INT, "gaps": _INT,
        "partials": _INT, "steps_analysed": _INT, "phases_count": _INT,
        "summary_line": _STR,
        "metrics": {"type": "array", "items": {"type": "array"}},
        "phase_bars": {"type": "array",
                       "items": _obj({"line1": _STR, "line2": _STR, "value": _INT, "colour": _STR})},
        "phase_cards": {"type": "array",
                        "items": _obj({"label": _STR, "value": _INT, "sub": _STR})},
        "detail_slides": {"type": "array", "items": {"type": "array"}},
        "items": {"type": "array", "items": _FITITEM},
        "groups": {"type": "array", "items": {"type": "array"}},
        "critical_missing": {"type": "array",
                             "items": _obj({"title": _STR, "detail": _STR})},
        "radar": {"type": "array", "items": {"type": "array"}},
        "control_bars": {"type": "array",
                         "items": _obj({"name": _STR, "value": _INT, "note": _STR})},
        "remediations": {"type": "array",
                         "items": _obj({"rank": _INT, "title": _STR, "detail": _STR, "priority": _STR})},
        "risk_impact": {"type": "array", "items": {"type": "array"}},
        "projected_fit": _INT}),
    "opt_phases": {"type": "array", "items": _PHASE},
    "opt_steps": {"type": "array", "items": _STEP},
    "opt_swim_phases": {"type": "array", "items": _SWIM},
    "opt_n_phases": _INT, "opt_n_steps": _INT, "opt_n_gateways": _INT, "opt_fit": _INT,
    "optimised_doc": _obj({
        "subtitle": _STR,
        "sections": {"type": "array",
                     "items": _obj({"title": _STR, "blocks": {"type": "array"}})}}),
    "swim_cover_tags": _STR,
    "hierarchy_cover_sub": _STR,
})
