#!/usr/bin/env python3
"""Generate the six FlowAgent deliverables, and manage the deterministic
JSON boundary.

Rendering:
    python3 build.py                 # build every authored SOP from sop_data/*.py
    python3 build.py SOP-INS-011     # build one SOP
    python3 build.py --json SOP-INS-011   # build from the frozen sop_data/json/*.json

Deterministic boundary:
    python3 build.py export-json     # freeze every package to sop_data/json/<id>.json
                                     #   + write sop_data/json/manifest.sha256
    python3 build.py verify          # re-hash the JSON files and diff vs the manifest
                                     #   (detects any drift in the frozen analyses)

Requires Google Chrome (see generator/render.py); no pip packages needed.
Only `verify`/`export-json` of the JSON layer are pure-Python (no Chrome).
"""
from __future__ import annotations

import json
import os
import sys
import time

import sop_data
from generator import outputs, contract
from generator.analyzer import CachedAnalyzer

ROOT = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(ROOT, "sop_data", "json")
MANIFEST = os.path.join(JSON_DIR, "manifest.sha256")


def _render(ids, from_json):
    if from_json:
        analyzer = CachedAnalyzer(JSON_DIR)
    total = 0
    for sid in ids:
        t0 = time.time()
        if from_json:
            pkg = contract.from_dict(analyzer.analyze(sid))
        else:
            pkg = sop_data.load(sid)
        paths = outputs.generate(pkg, ROOT)
        total += len(paths)
        print(f"✓ {sid} — {len(paths)} files in {time.time()-t0:.1f}s"
              f"{'  [from JSON]' if from_json else ''}")
    print(f"\nDone: {total} PDFs across {len(ids)} SOP(s).")


def export_json(ids):
    os.makedirs(JSON_DIR, exist_ok=True)
    manifest = {}
    for sid in ids:
        pkg = sop_data.load(sid)
        path = os.path.join(JSON_DIR, f"{sid}.json")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(contract.to_json(pkg))
        manifest[f"{sid}.json"] = contract.sha256(pkg)
        print(f"  wrote {os.path.relpath(path, ROOT)}  sha256={manifest[f'{sid}.json'][:12]}…")
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(dict(sorted(manifest.items())), fh, indent=2)
    print(f"\nFroze {len(ids)} package(s); manifest at {os.path.relpath(MANIFEST, ROOT)}")


def verify():
    if not os.path.exists(MANIFEST):
        print("No manifest — run `python3 build.py export-json` first.")
        return 1
    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)
    ok, drift = 0, 0
    for name, expected in manifest.items():
        path = os.path.join(JSON_DIR, name)
        if not os.path.exists(path):
            print(f"  ✗ {name}: MISSING"); drift += 1; continue
        with open(path, encoding="utf-8") as fh:
            actual = contract.sha256(json.load(fh))
        if actual == expected:
            ok += 1
        else:
            print(f"  ✗ {name}: DRIFT  expected {expected[:12]}… got {actual[:12]}…")
            drift += 1
    print(f"\nverify: {ok} unchanged, {drift} drifted (of {len(manifest)}).")
    return 1 if drift else 0


REPORT_DIR = os.path.join(ROOT, "2a_Flow_Accuracy_Reports")


def check(ids):
    """Log discrepancies between each source SOP and its generated flows.
    Deterministic — no LLM, no API. Writes to 2a_Flow_Accuracy_Reports/."""
    from generator import accuracy
    os.makedirs(REPORT_DIR, exist_ok=True)
    rows = []
    for sid in ids:
        pkg = sop_data.load(sid)
        r = accuracy.analyze(pkg, ROOT)
        path = os.path.join(REPORT_DIR, f"{sid}_Flow_Accuracy.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(accuracy.to_markdown(r))
        row = accuracy.summary_row(r)
        rows.append(row)
        print(f"  {sid}: groundedness {row['groundedness']*100:.0f}% · "
              f"{row['flags']} flag(s) · {row['consistency']} consistency issue(s)"
              f" → {os.path.relpath(path, ROOT)}")
    # combined summary
    lines = ["# Flow Accuracy — Summary", "",
             "Deterministic lexical grounding of each baseline flow against its source SOP "
             "(no LLM / no API). See per-SOP reports for detail.", "",
             "| SOP | Title | Groundedness | Review flags | Consistency issues |",
             "|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda x: x["id"]):
        lines.append(f"| {r['id']} | {r['title']} | {r['groundedness']*100:.0f}% | "
                     f"{r['flags']} | {r['consistency']} |")
    with open(os.path.join(REPORT_DIR, "_SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nWrote {len(rows)} report(s) + _SUMMARY.md to "
          f"{os.path.relpath(REPORT_DIR, ROOT)}/")
    return 0


CORRECTED_DIR = os.path.join(ROOT, "2b_Corrected_Flow_Outputs")


def corrected(ids):
    """Render strict-fidelity corrected baseline flows (swimlane + hierarchy)
    into 2b_Corrected_Flow_Outputs/, with an audit log. Deterministic, no API."""
    from generator import corrections, outputs as O
    os.makedirs(CORRECTED_DIR, exist_ok=True)
    log = ["# Corrected Flows — Change Log",
           "",
           "Strict-fidelity corrections to the **baseline** swimlane/hierarchy, from "
           "human review of the `2a_Flow_Accuracy_Reports/`. No LLM / no API.",
           "Originals remain in `2_Process_Flow_Outputs/`.", ""]
    total = 0
    for sid in ids:
        pkg = corrections.corrected(sop_data.load(sid))
        paths = O.generate_corrected(pkg, ROOT)
        total += len(paths)
        print(f"✓ {sid} — {len(paths)} corrected flow(s)")
        log.append(f"## {sid} — {pkg.meta.title}")
        for d in corrections.decisions(sid):
            log.append(f"- {d}")
        log.append("")
    with open(os.path.join(CORRECTED_DIR, "_CORRECTIONS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(log))
    print(f"\nWrote {total} PDFs + _CORRECTIONS.md to "
          f"{os.path.relpath(CORRECTED_DIR, ROOT)}/")
    return 0


def main(argv):
    args = argv[1:]
    if args and args[0] == "export-json":
        ids = args[1:] or sop_data.available()
        export_json(ids); return 0
    if args and args[0] == "verify":
        return verify()
    if args and args[0] == "check":
        return check(args[1:] or sop_data.available())
    if args and args[0] == "corrected":
        return corrected(args[1:] or sop_data.available())
    from_json = "--json" in args
    args = [a for a in args if a != "--json"]
    ids = sop_data.available() if (not args or args == ["all"]) else args
    if not ids:
        print("No authored SOP packages found in sop_data/."); return 1
    _render(ids, from_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
