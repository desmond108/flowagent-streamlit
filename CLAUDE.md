# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

FlowAgent generates, from Standard Operating Procedure (SOP) documents, six
deliverables as styled PDFs: a process-flow **swimlane** + **hierarchy**, a
**fit-gap analysis**, an **optimised** swimlane + hierarchy, and an **optimised
SOP** document. The repo contains a working **deterministic Python pipeline**
that produces these for 13 insurance SOPs, plus the original HR/Finance example
outputs and an HTML UI mockup.

It is **not an app**: it's a renderer plus authored, structured analysis. There
is no server and no runtime LLM/API call — see *Determinism* below.

- `git` is not initialised here.
- Full developer docs: **`GENERATOR_README.md`** (read it for any pipeline work).

## Commands

```bash
python3 build.py                  # generate all 6 deliverables for every SOP → 78 PDFs
python3 build.py SOP-INS-011      # one SOP
python3 build.py --json SOP-INS-011   # render from the frozen JSON instead of the .py
python3 build.py export-json      # freeze sop_data/*.py → sop_data/json/<id>.json + manifest
python3 build.py verify           # re-hash the frozen JSON vs manifest (drift check; no Chrome)
python3 build.py check            # flow-accuracy reports → 2a_Flow_Accuracy_Reports/ (no LLM)
python3 build.py corrected        # strict-fidelity corrected flows → 2b_Corrected_Flow_Outputs/
```

Requirements: **Python 3.9+** and **Google Chrome** (driven headless for
HTML→PDF; set `CHROME_BIN` if not auto-detected). `pdfplumber` is used by
`check`. No other pip packages.

## Architecture

```
build.py            CLI: render / export-json / verify / check / corrected
sop_data/           AUTHORED analysis, one module per SOP (ins_001 … ins_013)
  __init__.py       REGISTRY: SOP id → package; load()/available()
  ins_0NN.py        a fully-populated generator.model.SopPackage (the "intelligence")
  json/             frozen canonical JSON of each package + manifest.sha256
generator/          the DETERMINISTIC renderer (no SOP-specific content)
  model.py          dataclasses: process model, fit-gap, optimised doc
  theme.py          navy/gold deck CSS + A4 SOP CSS
  charts.py         inline-SVG donut / bar / radar / hbar
  swimlane.py       swimlane deck (grid layout + obstacle-avoiding orthogonal routing)
  hierarchy.py      hierarchy deck (phase cards + per-phase tables)
  fitgap.py         fit-gap deck; sop_doc.py  optimised SOP document
  outputs.py        SopPackage → the six PDFs; auto-copies the legend beside swimlanes
  render.py         HTML string → PDF via headless Chrome
  contract.py       canonical JSON ⇄ SopPackage + sha256 + JSON Schema (the boundary)
  analyzer.py       Analyzer Protocol: CachedAnalyzer (deterministic) / LLMAnalyzer (opt-in)
  accuracy.py       lexical grounding of a flow vs its source SOP (the `check` command)
  corrections.py    strict-fidelity edits for `corrected` (per-SOP, human-reviewed)
```

The big idea (detailed in `GENERATOR_README.md`): a swappable **author** produces
a canonical JSON `SopPackage`; a deterministic **renderer** turns it into PDFs.
The two example `.py`/`.json` SOP forms are equivalent canonical sources.

## Determinism (a core constraint — keep it)

The pipeline must stay reproducible: **no LLM/API call at runtime.** The SOP
analysis was authored once (by me, Claude, reading each SOP) and is frozen in
`sop_data/`. Any LLM use — authoring (`LLMAnalyzer`) or a future semantic judge —
is a deliberate, opt-in, **cached** step behind the JSON boundary, reviewed and
committed, never a build dependency. Current models don't even expose
`temperature`, so determinism comes from *freezing the output*, not the model.
`build.py verify` proves the frozen analyses haven't drifted.

## Output directories

| Dir | Contents |
|---|---|
| `1_Example_Original_Input_SOPs/` | source SOP PDFs (HR-001, FIN-003, and INS-001…013) |
| `2_Process_Flow_Outputs/` | baseline swimlane + hierarchy (`Swimlane …` / `Hierarchy …` subfolders) |
| `2a_Flow_Accuracy_Reports/` | per-SOP discrepancy logs from `check` + `_SUMMARY.md` |
| `2b_Corrected_Flow_Outputs/` | strict-fidelity corrected baseline flows + `_CORRECTIONS.md` |
| `3_FitGap_Analyses/` | `<ID>_FitGap_Executive.pdf` |
| `4_Optimized_Process_Flow_Outputs/` | optimised swimlane + hierarchy (where green=new / amber=enhanced appear) |
| `5_Optimized_SOP_Outputs/` | `<ID>_Optimised_v<N>.pdf` |
| `Swimlane_Flow_Legend.md` | canonical legend (box colours + connector colour/style) |

## Conventions & gotchas

- **Filenames** are load-bearing: `_SWIMLANE.drawio.pdf`, `_HIERARCHY.pdf`,
  `_FitGap_Executive.pdf`, `_Optimised_v<N>` (mirror existing names).
- **Legend** lives only at the repo root; the build auto-copies it into the
  three swimlane folders. Edit the root file, not the copies.
- **Reference catalogs** for fit-gap are per-SOP/domain (Guidewire PolicyCenter /
  BillingCenter / ClaimCenter, Majesco, Sircon, Salesforce Service Cloud) — see
  the table in `GENERATOR_README.md`.
- **Swimlane authoring**: nodes sit on a `(lane, column)` grid; the renderer
  errors on duplicate cells and on edges referencing unknown node ids, and warns
  on orphan boxes. Connectors auto-route around boxes.
- To change a SOP's content, edit its `sop_data/ins_0NN.py` (then re-run
  `export-json` to refresh the frozen JSON). To change look/layout, edit
  `generator/`.

## Adding a new SOP

1. Create `sop_data/ins_0NN.py` with `package = SopPackage(...)` (copy
   `ins_011.py` as a template).
2. Register it in `sop_data/__init__.py` `_MODULES`.
3. `python3 build.py SOP-INS-0NN` (and `export-json` to freeze it).

## Legacy / reference

`FlowAgent_SOP_Upload.html` is the original self-contained UI mockup (inline
CSS/JS, mocked processing). `FlowAgent_Executive_Summary.pdf` is the product
brief. The HR-001 / FIN-003 PDFs in the output dirs are the original hand-made
examples whose visual style the generator reproduces.

The exec summary deck was authored externally (PptxGenJS → LibreOffice, 16:9
960×540pt = 13.333in×7.5in — same page size as the generated decks; no source
file in the repo). `tools/build_faq_appendix.py` appends a brand-matched FAQ
(reusing `generator/theme` palette + the Chrome renderer) to the end of it. It
is **idempotent**: it merges from the pristine `FlowAgent_Executive_Summary_orig.pdf`
(the unmodified 9-page original, created once on first run) onto the live
`FlowAgent_Executive_Summary.pdf`, so re-running after editing the FAQ text
regenerates a clean 12-page deck rather than double-appending. Requires
`pdfunite` (poppler). Edit the FAQ content in the script, not the PDF.
