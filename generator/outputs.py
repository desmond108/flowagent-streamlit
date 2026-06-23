"""Maps a SopPackage to the six output PDFs in the 2_/3_/4_/5_ directories,
using the same filename convention as the existing HR/Finance examples."""
from __future__ import annotations

import os
import shutil

from . import swimlane, hierarchy, fitgap, sop_doc
from .render import html_to_pdf

# Canonical legend at the repo root; auto-copied beside every swimlane output so
# each swimlane folder carries a current copy without manual upkeep.
LEGEND = "Swimlane_Flow_Legend.md"

# Output sub-directories relative to repo root.
DIR_SWIM = "2_Process_Flow_Outputs/Swimlane Process Flow Output Files"
DIR_HIER = "2_Process_Flow_Outputs/Hierarchy Process Flow Output Files"
DIR_FITGAP = "3_FitGap_Analyses"
DIR_OPT_SWIM = "4_Optimized_Process_Flow_Outputs/Optimized Swimlane Process Flow Output Files"
DIR_OPT_HIER = "4_Optimized_Process_Flow_Outputs/Optimized Hierarchy Process Flow Output Files"
DIR_OPT_SOP = "5_Optimized_SOP_Outputs"
DIR_CORR_SWIM = "2b_Corrected_Flow_Outputs/Swimlane Process Flow Output Files"
DIR_CORR_HIER = "2b_Corrected_Flow_Outputs/Hierarchy Process Flow Output Files"


def _p(root, sub, name):
    return os.path.join(root, sub, name)


def _place_legend(root, *swim_subdirs):
    """Copy the canonical root legend into each swimlane output dir (idempotent;
    overwrites so the copies stay in sync with the source). No-op if missing."""
    src = os.path.join(root, LEGEND)
    if not os.path.exists(src):
        return
    for sub in swim_subdirs:
        dst_dir = os.path.join(root, sub)
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copyfile(src, os.path.join(dst_dir, LEGEND))


def generate_corrected(pkg, root: str) -> list[str]:
    """Render the strict-fidelity BASELINE swimlane + hierarchy into 2b_."""
    base = f"{pkg.meta.sop_id}_{pkg.meta.slug}"
    written = []
    for sub, name, html in [
        (DIR_CORR_SWIM, f"{base}_SWIMLANE.drawio.pdf", swimlane.render(pkg, False)),
        (DIR_CORR_HIER, f"{base}_HIERARCHY.pdf", hierarchy.render(pkg, False)),
    ]:
        path = _p(root, sub, name)
        html_to_pdf(html, path)
        written.append(path)
    _place_legend(root, DIR_CORR_SWIM)
    return written


def generate(pkg, root: str) -> list[str]:
    """Render all six deliverables for one SOP. Returns list of written paths."""
    m = pkg.meta
    base = f"{m.sop_id}_{m.slug}"
    opt = f"{m.sop_id}_Optimised_v{m.new_version}"
    written = []

    targets = [
        (DIR_SWIM, f"{base}_SWIMLANE.drawio.pdf", swimlane.render(pkg, False)),
        (DIR_HIER, f"{base}_HIERARCHY.pdf", hierarchy.render(pkg, False)),
        (DIR_FITGAP, f"{m.sop_id}_FitGap_Executive.pdf", fitgap.render(pkg)),
        (DIR_OPT_SWIM, f"{opt}_SWIMLANE.drawio.pdf", swimlane.render(pkg, True)),
        (DIR_OPT_HIER, f"{opt}_HIERARCHY.pdf", hierarchy.render(pkg, True)),
        (DIR_OPT_SOP, f"{opt}.pdf", sop_doc.render(pkg)),
    ]
    for sub, name, html in targets:
        path = _p(root, sub, name)
        html_to_pdf(html, path)
        written.append(path)
    _place_legend(root, DIR_SWIM, DIR_OPT_SWIM)
    return written
