# FlowAgent Output Generator

Reproducible Python pipeline that generates the six FlowAgent deliverables for
each insurance SOP, as PDF, into the numbered output directories
(`2_` flows · `2a_` accuracy reports · `2b_` corrected flows · `3_` fit-gap ·
`4_` optimised flows · `5_` optimised SOP). Source SOPs live in `1_`.

This is **not the app** — it is the deterministic renderer plus the authored,
structured analysis for each SOP. Re-running it regenerates every PDF exactly.

## What it produces (per SOP)

| Deliverable | Output directory | Filename pattern |
|---|---|---|
| a. Process flow — swimlane | `2_…/Swimlane Process Flow Output Files/` | `<ID>_<slug>_SWIMLANE.drawio.pdf` |
| a. Process flow — hierarchy | `2_…/Hierarchy Process Flow Output Files/` | `<ID>_<slug>_HIERARCHY.pdf` |
| b. Fit-gap analysis | `3_FitGap_Analyses/` | `<ID>_FitGap_Executive.pdf` |
| c. Optimised swimlane | `4_…/Optimized Swimlane Process Flow Output Files/` | `<ID>_Optimised_v<N>_SWIMLANE.drawio.pdf` |
| c. Optimised hierarchy | `4_…/Optimized Hierarchy Process Flow Output Files/` | `<ID>_Optimised_v<N>_HIERARCHY.pdf` |
| d. Optimised SOP document | `5_Optimized_SOP_Outputs/` | `<ID>_Optimised_v<N>.pdf` |

The swimlane, hierarchy and fit-gap decks are 16:9 landscape (navy/gold theme,
matching the existing HR/Finance examples). The optimised SOP is an A4 portrait
Word-style document with NEW / ENHANCED / CRITICAL change banners.

## Requirements

- **Python 3.9+** (developed on 3.12). No pip packages required.
- **Google Chrome** (or Chromium) — used headless to render HTML/CSS → PDF.
  Override the binary with `CHROME_BIN=/path/to/chrome` if it is not auto-detected.

## Usage

```bash
# Build every authored SOP (13 insurance SOPs → 78 PDFs)
python3 build.py

# Build a single SOP
python3 build.py SOP-INS-011

# Build several
python3 build.py SOP-INS-011 SOP-INS-012
```

## How it works

```
build.py                 CLI entry point
sop_data/                authored analysis, one module per SOP (ins_001 … ins_013)
  __init__.py            REGISTRY of SOP id → package; load()/available()
  ins_0NN.py             a fully-populated generator.model.SopPackage
generator/               the deterministic renderer (reusable across any SOP)
  model.py               dataclasses for the process model, fit-gap, optimised doc
  theme.py               colour palette + CSS (deck + SOP document)
  charts.py              inline-SVG donut / bar / radar / horizontal-bar charts
  swimlane.py            swimlane deck (grid layout + orthogonal connector routing)
  hierarchy.py           hierarchy deck (phase cards + per-phase tables)
  fitgap.py              fit-gap deck (cover, exec summary, phase detail, critical, roadmap)
  sop_doc.py             optimised SOP document (banners, tables, numbered sections)
  outputs.py             maps a SopPackage → the six output files
  render.py              HTML string → PDF via headless Chrome
```

The "intelligence" (process decomposition, fit-gap scoring, optimisation) lives
in the per-SOP `sop_data/ins_0NN.py` files — each was authored by analysing the
source SOP PDF against an appropriate insurance reference catalog. The
`generator/` package contains no SOP-specific content; it is a pure renderer, so
the same code produces consistent, on-brand outputs for any new SOP you add.

## Adding a new SOP

1. Create `sop_data/ins_0NN.py` defining a `package = SopPackage(...)`
   (copy an existing module as a template — `ins_011.py` is a good reference).
2. Register it in `sop_data/__init__.py` `_MODULES`.
3. Run `python3 build.py SOP-INS-0NN`.

## Reference catalogs used for fit-gap

Each SOP is graded against the platform/standard most appropriate to its domain:

| SOP | Domain | Reference catalog |
|---|---|---|
| INS-001, 004, 008, 010 | Sales / new business / underwriting | Guidewire PolicyCenter |
| INS-002 | Premium billing | Guidewire BillingCenter |
| INS-003 | Collections | Guidewire BillingCenter (Collections) |
| INS-005 | Producer licensing | Sircon (Vertafore) PLM |
| INS-006, 007 | Group benefits / quoting | Majesco Group Benefits / Distribution |
| INS-009 | Customer servicing | Salesforce Service Cloud |
| INS-011 | Medical claims | Guidewire ClaimCenter (Health) |
| INS-012 | P&C claims | Guidewire ClaimCenter (P&C) |
| INS-013 | Policy lifecycle | Guidewire PolicyCenter (system of record) |

## Determinism & the JSON boundary

The pipeline separates a **non-deterministic author** from a **deterministic
renderer**, with a frozen, hashable JSON contract between them:

```
SOP text → [ Analyzer ] → canonical JSON → [ Renderer ] → PDFs
            swappable       FROZEN +          pure function
            (LLM / human)    HASHED + COMMITTED of the JSON
```

- `generator/contract.py` — canonical JSON ⇄ `SopPackage`, plus `sha256()` and
  the JSON Schema that defines the contract. Same JSON → identical document
  content, always (verified: rendered-HTML hashes match across a round-trip).
- `generator/analyzer.py` — the swappable author interface:
  - `CachedAnalyzer` reads the committed JSON — **deterministic** (the default).
  - `LLMAnalyzer` calls the Claude API to *author* JSON — non-deterministic; you
    run it deliberately, review the diff, and commit. (Current models don't even
    expose `temperature`, so determinism can't come from sampling — it comes from
    freezing this output.)
  - Any model (a fine-tuned small model later) or a human drops in behind the
    same `Analyzer` Protocol without touching the renderer.

Commands:

```bash
python3 build.py export-json     # freeze sop_data/*.py → sop_data/json/<id>.json + manifest.sha256
python3 build.py verify          # re-hash the JSON and diff vs the manifest (drift detection, no Chrome)
python3 build.py --json SOP-INS-011   # render from the frozen JSON via CachedAnalyzer
```

`sop_data/json/` is the canonical, committable source of truth: re-running the
renderer over it reproduces every deliverable exactly, and `verify` proves the
frozen analyses haven't changed.

## Flow-accuracy reporting (no LLM / no API)

`python3 build.py check [SOP-ID …]` logs discrepancies between each **source SOP**
and its generated **flows**, into `2a_Flow_Accuracy_Reports/` (one Markdown report
per SOP + `_SUMMARY.md`). It never fails the build — it's an advisory log.

Because the swimlane and hierarchy are both rendered from one model, the check
grounds the **baseline** model against the source SOP text (extracted with
`pdfplumber`) using deterministic lexical matching:

- **Internal consistency** — cover stats vs real counts, referential integrity, no orphans.
- **Role / system / numeric grounding** — every role, named system/acronym, and
  threshold (SGD, T+N, %, days) in the flow is checked for presence in the SOP.
- **Per-step grounding** — fraction of each step's wording found in the SOP.
- **Optimised additions** are listed separately as *expected* (the fit-gap NEW/ENHANCED
  steps are intentionally absent from the original SOP), not flagged as inaccuracies.

It is lexical, not semantic — it catches fabricated roles/systems/numbers and
ungrounded step wording, but can't judge paraphrase. ⚠ items are review
candidates; true semantic equivalence is a separate LLM-judge step (the only part
that would need API calls).

## Corrected flows (strict fidelity, no LLM / no API)

`python3 build.py corrected [SOP-ID …]` re-renders the **baseline** swimlane +
hierarchy with the report-flagged fabrications removed, into
`2b_Corrected_Flow_Outputs/` (+ `_CORRECTIONS.md` audit log). Originals stay in
`2_Process_Flow_Outputs/`.

The correction policy is **strict fidelity**: the corrected flow contains only
content grounded in the source SOP. The edits come from human review of the 2a
reports and live in `generator/corrections.py`:

- **Removed** — the synthesized approval/authority matrices (every flagged SGD
  threshold and the CFO role lived there). Where the SOP *does* state bands
  (SOP-INS-012), only the grounded rows are kept.
- **Kept** — abbreviations of grounded concepts (PDS, AML, ACV/RCV, CMS, DOB, QC…)
  and "N days" wording. These are paraphrase, not fabrication; removing them
  would lose faithful content. Swimlanes carried no flagged content, so they are
  re-rendered unchanged.

`corrections.corrected(pkg)` returns a strict-fidelity copy of the model;
rendering it is deterministic. (Note: the 2a check is lexical, so it only drives
corrections for the fabrications it can evidence — acronyms/numbers/roles — not
qualitative synthesis; that boundary is called out in the report and log.)

## Notes

- `Swimlane_Flow_Legend.md` (repo root) is the single source of truth for the
  box/connector legend. Every build auto-copies it beside the swimlanes — into
  the baseline (`2_`), optimised (`4_`) and corrected (`2b_`) swimlane folders —
  so each copy stays in sync; edit only the root file.
- Rendering is fully deterministic — no network calls, no randomness.
- The swimlane layout validates that no two nodes share a `(lane, column)`
  cell and raises a clear error if they do, catching authoring mistakes early.
- Each full build takes roughly 11–12 seconds per SOP (one headless Chrome
  invocation per PDF).
