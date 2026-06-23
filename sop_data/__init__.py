"""Authored, structured analysis for each insurance SOP.

Each module (ins_001 … ins_013) exposes `package`, a fully-populated
generator.model.SopPackage. REGISTRY maps SOP id -> package. The analysis
content (process model, fit-gap, optimisation) is authored from reading the
source SOP PDFs; the generator package turns it into the six deliverables.
"""
from __future__ import annotations

import importlib

# (module_name, sop_id)
_MODULES = [
    ("ins_001", "SOP-INS-001"),
    ("ins_002", "SOP-INS-002"),
    ("ins_003", "SOP-INS-003"),
    ("ins_004", "SOP-INS-004"),
    ("ins_005", "SOP-INS-005"),
    ("ins_006", "SOP-INS-006"),
    ("ins_007", "SOP-INS-007"),
    ("ins_008", "SOP-INS-008"),
    ("ins_009", "SOP-INS-009"),
    ("ins_010", "SOP-INS-010"),
    ("ins_011", "SOP-INS-011"),
    ("ins_012", "SOP-INS-012"),
    ("ins_013", "SOP-INS-013"),
]


def load(sop_id: str):
    for mod, sid in _MODULES:
        if sid == sop_id:
            return importlib.import_module(f"sop_data.{mod}").package
    raise KeyError(sop_id)


def available() -> list[str]:
    out = []
    for mod, sid in _MODULES:
        try:
            importlib.import_module(f"sop_data.{mod}")
            out.append(sid)
        except ModuleNotFoundError:
            continue
    return out
