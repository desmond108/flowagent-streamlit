"""Flow-accuracy reporting: log discrepancies between a source SOP and the
generated process flows — deterministically, with NO LLM and NO API calls.

The swimlane and hierarchy are both rendered from one structured model
(SopPackage), so "do the flows match the SOP" reduces to "does the baseline
model match the source SOP text". We check that with lexical grounding:

  * internal consistency  — cover stats vs real counts, referential integrity
  * role grounding        — every role in the model appears in the SOP
  * system/acronym         — named systems/acronyms in the model appear in the SOP
  * numeric facts         — thresholds (SGD, T+N, %, days) in the model appear in the SOP
  * per-step grounding    — fraction of each step's significant words found in the SOP

Limitation (by design): this is lexical, not semantic. It catches fabricated
roles/systems/numbers and steps whose wording isn't reflected in the SOP, but
it cannot judge paraphrase ("validate completeness" ≈ "completeness check").
Flags are advisory — a discrepancy LOG, never a build gate. True semantic
equivalence is a separate, LLM-judge step.
"""
from __future__ import annotations

import datetime
import os
import re

SRC_DIR = "1_Example_Original_Input_SOPs"

_STOP = set((
    "the a an of to and or for with via per in on at by is are be as if no not "
    "within into from each any all only via via1 that this these those it its he "
    "she they them their will may must can should before after when where which "
    "who whom whose than then else also etc e g eg ie via"
).split())


# --------------------------------------------------------------------------
# Source SOP text
# --------------------------------------------------------------------------
def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def _find_source(root: str, sop_id: str) -> str | None:
    num = sop_id.split("-")[-1]            # "SOP-INS-011" -> "011"
    d = os.path.join(root, SRC_DIR)
    if not os.path.isdir(d):
        return None
    for f in os.listdir(d):
        if f.lower().endswith(".pdf") and (f"INS_{num}" in f or f"INS-{num}" in f):
            return os.path.join(d, f)
    return None


def _read_pdf(path: str) -> str:
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)


# --------------------------------------------------------------------------
# Extract entities/facts from the BASELINE model only
# --------------------------------------------------------------------------
def _split_roles(text):
    for part in re.split(r"[/·&,]| and ", text or ""):
        part = part.strip()
        if part and part.lower() not in ("system", "auto", "automated", "—"):
            yield part


def _baseline_fields(pkg):
    """All free-text from the baseline process model (not fit-gap, not optimised)."""
    out = []
    for s in pkg.steps:
        out += [s.activity, s.responsible, s.output, s.controls]
    for ph in pkg.swim_phases:
        out += ph.lanes
        for n in ph.nodes:
            out += [n.title, n.sub]
        out.append(ph.note)
    for a in pkg.authority:
        out += [a.band, a.first, a.second]
    return [x for x in out if x]


def _roles(pkg):
    seen, roles = set(), []
    for s in pkg.steps:
        for r in _split_roles(s.responsible):
            if _norm(r) not in seen:
                seen.add(_norm(r)); roles.append(r)
    for ph in pkg.swim_phases:
        for ln in ph.lanes:
            for r in _split_roles(ln):
                if _norm(r) not in seen:
                    seen.add(_norm(r)); roles.append(r)
    return roles


def _acronyms(pkg):
    text = " ".join(_baseline_fields(pkg))
    found = set(re.findall(r"\b[A-Z][A-Z0-9]{1,}\b", text))
    found -= {"SOP", "INS", "NEW", "GR", "SES", "PO", "ID",  # cross-refs / too-generic
              "SGD", "USD", "EUR", "GBP"}                    # currencies → covered by numeric facts
    found = {a for a in found if not a.startswith("INS")}
    return sorted(found)


_FACT_PATS = [r"SGD\s?[\d,]+", r"T\+\d+", r"\d+\s?%", r"\d+\s+business\s+days?",
              r"\d+\s+calendar\s+days?", r"\d+\s+days?", r"\d+\s+business\s+hours?",
              r"\d+\s+hours?", r"\d+\s+months?"]


def _facts(pkg):
    text = " ".join(_baseline_fields(pkg))
    seen, facts = set(), []
    for pat in _FACT_PATS:
        for m in re.findall(pat, text):
            if _norm(m) not in seen:
                seen.add(_norm(m)); facts.append(m.strip())
    return facts


def _sig_words(activity):
    words = re.findall(r"[a-z][a-z0-9\-]{3,}", activity.lower())
    return [w for w in words if w not in _STOP]


# --------------------------------------------------------------------------
# Analyse one package against its source SOP
# --------------------------------------------------------------------------
def analyze(pkg, root: str) -> dict:
    src = _find_source(root, pkg.meta.sop_id)
    norm_sop = _norm(_read_pdf(src)) if src else ""

    def present(s):
        n = _norm(s)
        return bool(n) and n in norm_sop

    # --- internal consistency (flows ↔ model) ---
    proc_steps = [s for s in pkg.steps if s.kind != "decision"]
    decisions = [s for s in pkg.steps if s.kind == "decision"]
    consistency = []
    consistency.append(("cover step count", pkg.n_steps, len(proc_steps),
                        pkg.n_steps == len(proc_steps)))
    consistency.append(("cover phase count", pkg.n_phases, len(pkg.phases),
                        pkg.n_phases == len(pkg.phases)))
    phase_ids = {p.pid for p in pkg.phases}
    bad_phase = [s.num for s in pkg.steps if s.phase not in phase_ids]
    consistency.append(("steps reference a declared phase", "", bad_phase or "ok", not bad_phase))
    lane_issues = []
    for ph in pkg.swim_phases:
        for n in ph.nodes:
            if n.lane not in ph.lanes:
                lane_issues.append(f"{ph.pid}:{n.nid}")
    consistency.append(("swim nodes use declared lanes", "", lane_issues or "ok", not lane_issues))
    orphans = []
    for ph in pkg.swim_phases:
        touched = {e.src for e in ph.edges} | {e.dst for e in ph.edges}
        orphans += [f"{ph.pid}:{n.nid}" for n in ph.nodes if n.nid not in touched]
    consistency.append(("no orphan swim nodes", "", orphans or "ok", not orphans))
    empty_phases = [p.pid for p in pkg.phases
                    if not any(s.phase == p.pid for s in pkg.steps)]
    consistency.append(("every phase has steps", "", empty_phases or "ok", not empty_phases))

    # --- groundedness vs source SOP (baseline only) ---
    roles = [(r, present(r)) for r in _roles(pkg)]
    acronyms = [(a, present(a)) for a in _acronyms(pkg)]
    facts = [(f, present(f)) for f in _facts(pkg)]
    steps = []
    for s in proc_steps:
        sig = _sig_words(s.activity)
        hits = [w for w in sig if w in norm_sop]
        score = (len(hits) / len(sig)) if sig else 1.0
        steps.append((s.num, s.activity, score, sig, hits))

    # --- optimised additions (intentional; NOT inaccuracies) ---
    additions = []
    for s in pkg.opt_steps:
        tag = ("NEW" if "NEW (" in s.controls else
               "ENHANCED" if "ENHANCED (" in s.controls else None)
        if tag and s.kind != "decision":
            additions.append((tag, s.num, s.activity))

    grounded_steps = sum(1 for _, _, sc, _, _ in steps if sc >= 0.5)
    return {
        "meta": pkg.meta,
        "source": os.path.relpath(src, root) if src else None,
        "consistency": consistency,
        "roles": roles,
        "acronyms": acronyms,
        "facts": facts,
        "steps": steps,
        "additions": additions,
        "scores": {
            "groundedness": (sum(sc for _, _, sc, _, _ in steps) / len(steps)) if steps else 1.0,
            "grounded_steps": grounded_steps,
            "total_steps": len(steps),
            "roles_matched": sum(1 for _, ok in roles if ok),
            "roles_total": len(roles),
            "acronyms_matched": sum(1 for _, ok in acronyms if ok),
            "acronyms_total": len(acronyms),
            "facts_matched": sum(1 for _, ok in facts if ok),
            "facts_total": len(facts),
            "consistency_issues": sum(1 for *_, ok in consistency if not ok),
        },
    }


# --------------------------------------------------------------------------
# Render a Markdown report
# --------------------------------------------------------------------------
def _pct(n, d):
    return f"{100*n/d:.0f}%" if d else "n/a"


def to_markdown(r: dict) -> str:
    m, sc = r["meta"], r["scores"]
    flags = [w for w, ok in r["roles"] if not ok] + [w for w, ok in r["acronyms"] if not ok]
    fact_flags = [w for w, ok in r["facts"] if not ok]
    low_steps = [(num, act, s) for num, act, s, _, _ in r["steps"] if s < 0.4]
    L = []
    L.append(f"# Flow Accuracy Report — {m.sop_id} {m.title}")
    L.append(f"*Source:* `{r['source'] or 'NOT FOUND — grounding skipped'}`  ")
    L.append(f"*Generated:* {datetime.date.today().isoformat()} · "
             f"*Method:* deterministic lexical grounding (no LLM / no API)\n")
    status = ("✅ strong match" if sc["groundedness"] >= 0.7 and sc["consistency_issues"] == 0
              and not flags else "⚠ review recommended")
    L.append("## Summary")
    L.append(f"- **Overall:** {status}")
    L.append(f"- Baseline step groundedness: **{sc['groundedness']*100:.0f}%** "
             f"({sc['grounded_steps']}/{sc['total_steps']} steps grounded)")
    L.append(f"- Roles matched in SOP: **{sc['roles_matched']}/{sc['roles_total']}** "
             f"({_pct(sc['roles_matched'], sc['roles_total'])})")
    L.append(f"- Systems/acronyms matched: **{sc['acronyms_matched']}/{sc['acronyms_total']}** "
             f"({_pct(sc['acronyms_matched'], sc['acronyms_total'])})")
    L.append(f"- Numeric facts matched: **{sc['facts_matched']}/{sc['facts_total']}** "
             f"({_pct(sc['facts_matched'], sc['facts_total'])})")
    L.append(f"- Internal consistency issues: **{sc['consistency_issues']}**\n")

    if flags or fact_flags or low_steps:
        L.append("### ⚠ Discrepancies to review")
        for w in flags:
            L.append(f"- Role/term **{w}** in the flow was not found in the source SOP "
                     f"(possible fabrication or different wording).")
        for w in fact_flags:
            L.append(f"- Numeric fact **{w}** in the flow was not found in the source SOP.")
        for num, act, s in low_steps:
            L.append(f"- Step {num} *“{act}”* — only {s*100:.0f}% of its wording appears "
                     f"in the SOP (paraphrase, or possibly not grounded).")
        L.append("")

    L.append("## 1. Internal consistency (flows ↔ model)")
    L.append("The swimlane and hierarchy are rendered from one model, so these verify the "
             "model is well-formed and the cover figures are truthful.\n")
    for label, exp, got, ok in r["consistency"]:
        tick = "✅" if ok else "❌"
        detail = f" — expected {exp}, got {got}" if exp != "" else (f" — {got}" if got != "ok" else "")
        L.append(f"- {tick} {label}{'' if ok and got=='ok' else detail}")
    L.append("")

    L.append("## 2. Baseline flow grounded in the source SOP")
    L.append("### Roles")
    L.append(" ".join(f"{'✅' if ok else '⚠'} {w}" for w, ok in r["roles"]) or "_none_")
    L.append("\n### Systems / acronyms")
    L.append(" ".join(f"{'✅' if ok else '⚠'} {w}" for w, ok in r["acronyms"]) or "_none_")
    L.append("\n### Numeric facts")
    L.append(" · ".join(f"{'✅' if ok else '⚠'} {w}" for w, ok in r["facts"]) or "_none_")
    L.append("\n### Step-by-step grounding")
    L.append("| # | Step (baseline) | Wording found in SOP | Status |")
    L.append("|---|---|---|---|")
    for num, act, s, _, _ in r["steps"]:
        st = "grounded" if s >= 0.5 else ("partial" if s >= 0.4 else "⚠ review")
        L.append(f"| {num} | {act} | {s*100:.0f}% | {st} |")
    L.append("")

    L.append("## 3. Optimised flow — intentional additions (NOT inaccuracies)")
    L.append("These steps were introduced by the fit-gap optimisation and are *expected* to be "
             "absent from the original SOP. They are listed for transparency, not flagged.\n")
    if r["additions"]:
        for tag, num, act in r["additions"]:
            L.append(f"- **{tag}** (opt step {num}): {act}")
    else:
        L.append("_none_")
    L.append("\n---\n*Lexical grounding only. It cannot judge paraphrase or semantic "
             "equivalence; treat ⚠ items as candidates for human (or LLM-judge) review.*")
    return "\n".join(L)


def summary_row(r: dict) -> dict:
    sc, m = r["scores"], r["meta"]
    flags = sum(1 for _, ok in r["roles"] if not ok) + \
        sum(1 for _, ok in r["acronyms"] if not ok) + \
        sum(1 for _, ok in r["facts"] if not ok)
    return {"id": m.sop_id, "title": m.title,
            "groundedness": sc["groundedness"], "flags": flags,
            "consistency": sc["consistency_issues"]}
