"""Structured data model for a single SOP. Each insurance SOP is authored as
one SopPackage instance (see sop_data/). The templates render purely from
these objects, so regenerating a PDF is deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# --------------------------------------------------------------------------
# Shared / meta
# --------------------------------------------------------------------------
@dataclass
class Meta:
    sop_id: str            # "SOP-INS-011"
    slug: str              # "Medical_Claims" (used in output filenames)
    title: str             # "Medical Claims Processing"
    short_title: str       # "Medical claims" (cover sub-lines)
    version: str           # "2.3"
    owner: str             # "Medical Claims — Claims Operations"
    org: str               # "Meridian Insurance Group"
    catalog: str           # full reference catalog name
    catalog_short: str     # short catalog name for chips
    new_version: str       # optimised version, e.g. "3.0"
    effective_date: str    # optimised effective date
    supersedes: str        # "v2.3 dated 01 March 2025"
    approved_by: str
    classification: str


# --------------------------------------------------------------------------
# Process model (used by swimlane + hierarchy)
# --------------------------------------------------------------------------
@dataclass
class Phase:
    pid: str               # "1", "2A"
    name: str              # "Claim receipt & registration"
    subtitle: str          # "All claims entering Claims Ops"
    circle: str            # circle colour key: blue/green/amber/gold
    roles: str             # "Claims Processor · PAS"
    step_range: str        # "Steps 1-4"
    summary: str           # "4 steps + 1 decision"


@dataclass
class Step:
    num: str               # "1", "9-10"
    phase: str             # phase id this step belongs to
    activity: str
    responsible: str
    output: str
    timeline: str
    controls: str
    kind: str = "process"  # trigger/process/control/handoff/complete/decision
    decision: Optional[str] = None        # decision question
    branches: list = field(default_factory=list)  # ["Yes → ...", "No → ..."]


@dataclass
class AuthorityRow:
    band: str
    first: str
    second: str = ""


# Swimlane: lanes are roles; nodes placed on a (lane, col) grid per phase.
@dataclass
class SwimNode:
    nid: str
    lane: str              # role lane label
    col: int               # 0-based column (left→right sequence)
    title: str
    sub: str = ""          # subtitle line (role/system/condition)
    kind: str = "standard"  # standard/new/enhanced/exception/decision/terminal


@dataclass
class SwimEdge:
    src: str
    dst: str
    label: str = ""
    dashed: bool = False
    kind: str = "standard"  # standard/new/exception


@dataclass
class SwimPhase:
    pid: str
    name: str
    subtitle: str
    lanes: list            # ordered role lane labels (top→bottom)
    nodes: list            # list[SwimNode]
    edges: list            # list[SwimEdge]
    note: str = ""         # caption under the diagram


# --------------------------------------------------------------------------
# Fit-gap model
# --------------------------------------------------------------------------
@dataclass
class FitItem:
    num: str
    name: str
    status: str            # FIT/PARTIAL/GAP
    detail: str
    owner: str
    ref: str               # catalog reference code
    group: str             # phase-group key -> which detail slide


@dataclass
class FitPhaseBar:
    line1: str
    line2: str
    value: int
    colour: str            # green/amber/red (resolved in template)


@dataclass
class PhaseScoreCard:
    label: str             # "Phase 1"
    value: int
    sub: str               # "Receipt & routing"


@dataclass
class CriticalGap:
    title: str
    detail: str


@dataclass
class ControlBar:
    name: str
    value: int
    note: str


@dataclass
class Remediation:
    rank: int
    title: str
    detail: str
    priority: str          # High/Medium/Low


@dataclass
class FitGap:
    overall_fit: int       # weighted fit %  (donut green segment)
    partial_pct: int       # weighted partial %  (donut amber segment)
    fits: int              # count of FIT steps
    gaps: int              # count of GAP steps
    partials: int          # count of PARTIAL steps
    steps_analysed: int
    phases_count: int
    summary_line: str
    metrics: list          # [(label, value)]
    phase_bars: list       # list[FitPhaseBar]  (exec summary bar chart)
    phase_cards: list      # list[PhaseScoreCard]
    detail_slides: list    # list[(slide_title, slide_sub, [group_keys])]
    items: list            # list[FitItem]
    groups: list           # list[(group_key, group_heading)] order within slides
    critical_missing: list # list[CriticalGap]
    radar: list            # [(axis, value)]
    control_bars: list     # list[ControlBar]
    remediations: list     # list[Remediation]
    risk_impact: list      # [(label, value)] for risk bar chart
    projected_fit: int


# --------------------------------------------------------------------------
# Optimised SOP document model
# --------------------------------------------------------------------------
# Blocks are tuples interpreted by sop_doc template:
#   ("para", text)
#   ("bullets", [items])
#   ("numbered", [items])           -> continues document-wide numbering if start given
#   ("numbered_from", start, [items])
#   ("banner", kind, text)          kind: new/enh/crit
#   ("summary", title, [paras], [bullets])
#   ("meta", [(k, v)])
#   ("table", [headers], [rows], {row_index: "new"|"enh"})  rows = list[list[str]]
@dataclass
class DocSection:
    title: str
    blocks: list


@dataclass
class OptimisedDoc:
    subtitle: str          # under-title italic line
    sections: list         # list[DocSection]


# --------------------------------------------------------------------------
# Top-level package
# --------------------------------------------------------------------------
@dataclass
class SopPackage:
    meta: Meta
    # baseline process
    phases: list           # list[Phase]
    steps: list            # list[Step]
    authority: list        # list[AuthorityRow] (may be empty)
    swim_phases: list      # list[SwimPhase] baseline
    # process headline stats (for covers)
    n_phases: int
    n_steps: int
    n_roles: int
    n_gateways: int
    # fit-gap
    fitgap: FitGap
    # optimised process
    opt_phases: list       # list[Phase]
    opt_steps: list        # list[Step] for optimised hierarchy tables
    opt_swim_phases: list  # list[SwimPhase]
    opt_n_phases: int
    opt_n_steps: int
    opt_n_gateways: int
    opt_fit: int           # post-optimisation D365/catalog alignment %
    # optimised SOP document
    optimised_doc: OptimisedDoc
    # extra cover descriptors
    swim_cover_tags: str = ""        # cover sub-line for swimlane
    hierarchy_cover_sub: str = ""    # cover sub-line for hierarchy
