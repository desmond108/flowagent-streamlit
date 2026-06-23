"""Strict-fidelity corrections to the BASELINE flows, derived from human review
of the 2a accuracy reports.

Policy (chosen): strict fidelity — the corrected flow contains only content
grounded in the source SOP. Source: human review (no LLM / no API).

What the review concluded from the report flags:

  * GENUINE fabrications → removed. Every report-flagged SGD threshold and the
    `CFO` role live in synthesized **authority/approval matrices** that the
    source SOPs do not contain. We drop those matrices (or, where the source
    *does* state bands — SOP-INS-012 — keep only the grounded rows).
  * PARAPHRASE / abbreviation → kept. Acronym flags (PDS, AML, ACV/RCV, CMS,
    DOB, QC, GBA, "Group Account Mgr") and "N days" vs "N business days" are
    abbreviations of concepts that ARE in the SOP — not fabricated content.
  * SWIMLANES needed no removals. They DO carry some report-flagged tokens
    (the acronyms and "N days" wording above), but every one is either kept
    paraphrase or a lexical false positive — none is a fabrication warranting
    removal. The synthesized SGD/CFO content lived only in the hierarchy's
    authority matrix, so swimlanes are re-rendered unchanged.
    Notable false positive: SOP-INS-003's swimlane node "External agency
    referral · >SGD 1,000" is grounded — the SOP states "balances above SGD
    1,000 at T+60" — but the 2a check flagged "SGD 1,000" because the source
    PDF's table extraction split "SGD" and "1,000" across columns.

`corrected(pkg)` returns a deep copy of the package with these edits applied to
the baseline model. Rendering it is deterministic.
"""
from __future__ import annotations

import copy

from . import model as M

# Per-SOP grounded authority rows to KEEP. A key mapping to [] drops the whole
# synthesized matrix; a SOP absent from this map keeps its authority unchanged.
_AUTHORITY = {
    "SOP-INS-002": [],   # CFO + SGD 11/500/25,000 — all synthesized
    "SOP-INS-003": [],   # CFO + SGD 5,000/2,000 — all synthesized
    "SOP-INS-011": [],   # entire SGD band matrix synthesized; SOP states no $ thresholds
    "SOP-INS-012": [     # settlement bands ARE in the SOP; drop only "Reserve > SGD 100,000"
        ("Settlement up to SGD 50,000", "Claims Adjuster", "—"),
        ("SGD 50,001–250,000", "Claims Manager", "Adjuster recommendation"),
        ("Above SGD 250,000", "Chief Claims Officer", "Claims Manager"),
        ("Litigation referral", "Claims Manager", "Legal"),
        ("Catastrophe / reinsurance loss", "Chief Claims Officer", "Reinsurance (SOP-RE-001)"),
    ],
}


def corrected(pkg):
    """Return a strict-fidelity copy of the baseline model."""
    p = copy.deepcopy(pkg)
    if pkg.meta.sop_id in _AUTHORITY:
        p.authority = [M.AuthorityRow(*r) for r in _AUTHORITY[pkg.meta.sop_id]]
    # mark the covers so corrected flows are distinguishable from the originals
    p.swim_cover_tags = (pkg.swim_cover_tags + " · Corrected to source").strip(" ·")
    p.hierarchy_cover_sub = (pkg.hierarchy_cover_sub + " · corrected (strict fidelity)")
    return p


def decisions(sop_id: str) -> list[str]:
    """Human-readable change log for one SOP (for _CORRECTIONS.md)."""
    out = []
    if sop_id in _AUTHORITY:
        kept = _AUTHORITY[sop_id]
        if not kept:
            out.append("Removed the approval/authority matrix entirely — its SGD "
                       "thresholds and the CFO role are not stated in the source SOP "
                       "(synthesized). This clears all SGD/CFO report flags.")
        else:
            out.append("Trimmed the authority matrix to the rows the SOP actually states "
                       "(kept the grounded settlement bands; removed the synthesized "
                       "'Reserve > SGD 100,000' row).")
    else:
        out.append("No authority-matrix changes — its rows are grounded in the SOP.")
    out.append("Kept abbreviations of grounded concepts (e.g. PDS, AML, ACV/RCV, CMS, "
               "DOB, QC) and 'N days' wording — these are paraphrase, not fabrication.")
    out.append("Swimlane unchanged — the report-flagged tokens it does carry are "
               "all kept paraphrase (acronyms, 'N days') or lexical false positives, "
               "none warranting removal.")
    if sop_id == "SOP-INS-003":
        out.append("Note: the swimlane node 'External agency referral · >SGD 1,000' is "
                   "grounded — the SOP states 'balances above SGD 1,000 at T+60'. The 2a "
                   "'SGD 1,000' flag is a false positive from PDF table-column extraction.")
    return out
