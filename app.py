"""FlowAgent — Streamlit front end.

Wires the existing deterministic renderer (generator/) and the swappable
Analyzer boundary (generator/analyzer.py) to a browser UI:

  * Demo mode  — render the 6 deliverables for a frozen, authored SOP. No API
                 call, no cost, fully deterministic (uses sop_data/).
  * Live mode  — upload a SOP (PDF / text); the LLM analyzer authors the
                 canonical JSON, it is validated against the contract, then
                 rendered. Needs an API key + Google Chrome/Chromium.

Run locally:   streamlit run app.py
Deploy:        see DEPLOY.md (Streamlit Community Cloud + chromium via packages.txt)
"""
from __future__ import annotations

import io
import os
import re
import shutil
import tempfile
import time
import zipfile
from pathlib import Path

import streamlit as st

# --- Make the API key available to the SDK before importing the analyzer ----
# st.secrets is empty (not an error) when no secrets file is present.
try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ.setdefault("ANTHROPIC_API_KEY", st.secrets["ANTHROPIC_API_KEY"])
except Exception:
    pass

import sop_data
from generator import contract, outputs
from generator.analyzer import LLMAnalyzer
from generator.render import find_chrome

REPO = Path(__file__).parent
LEGEND = REPO / "Swimlane_Flow_Legend.md"
SRC_DIR = REPO / "1_Example_Original_Input_SOPs"  # original SOPs the demo derives from

# Single model used for all authoring (backend detail; not shown to the client).
MODEL = "claude-opus-4-8"

st.set_page_config(page_title="FlowAgent", page_icon="🟠", layout="wide")

# Hide Streamlit's developer chrome (options menu + deploy button) so the customer
# gets a clean view. NOTE: keep this on ONE line with no indentation — indented
# HTML in st.markdown is rendered as a literal code block. The GitHub source/fork/
# edit badges are Community Cloud chrome shown for PUBLIC repos; they go away when
# the repo is private.
st.markdown(
    '<style>'
    '[data-testid="stToolbar"]{display:none!important;}'
    '[data-testid="stAppDeployButton"]{display:none!important;}'
    '#MainMenu{visibility:hidden!important;}'
    '</style>',
    unsafe_allow_html=True,
)


# --- Helpers ----------------------------------------------------------------
def chrome_ok() -> str | None:
    """Return the Chrome/Chromium path, or None if not found."""
    try:
        return find_chrome()
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def demo_catalog() -> dict[str, str]:
    """sop_id -> 'SOP-INS-0NN · Title' for the demo picker."""
    out = {}
    for sid in sop_data.available():
        m = sop_data.load(sid).meta
        out[sid] = f"{m.sop_id} · {m.title}"
    return out


def extract_text(name: str, data: bytes) -> str:
    """Pull plain text from uploaded PDF / txt / md bytes."""
    if name.lower().endswith(".pdf"):
        import pdfplumber

        text = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    return data.decode("utf-8", errors="replace")


def render_package(pkg) -> tuple[str, list[str]]:
    """Render the 6 deliverables for a SopPackage into a fresh temp dir."""
    tmp = tempfile.mkdtemp(prefix="flowagent_")
    # outputs.generate auto-copies the legend from <root>/Swimlane_Flow_Legend.md
    if LEGEND.exists():
        shutil.copy(LEGEND, Path(tmp) / LEGEND.name)
    paths = outputs.generate(pkg, tmp)
    return tmp, paths


def pdf_page_images(path: str, zoom: float = 1.6, max_pages: int = 12) -> list[bytes]:
    """Render PDF pages to PNG bytes (reliable preview — browsers won't embed
    base64 PDFs inside Streamlit's component frame). Uses PyMuPDF; no system libs."""
    import fitz  # PyMuPDF

    out = []
    doc = fitz.open(path)
    try:
        for i, page in enumerate(doc):
            if i >= max_pages:
                break
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            out.append(pix.tobytes("png"))
    finally:
        doc.close()
    return out


def source_pdf_for(sop_id: str) -> str | None:
    """Locate the original SOP PDF in 1_… for a given sop_id (e.g. SOP-INS-011
    matches SOP_INS_011_*.pdf). Returns None if not found."""
    norm = lambda s: re.sub(r"[^A-Za-z0-9]", "", s).upper()
    target = norm(sop_id)
    if not SRC_DIR.exists():
        return None
    for f in sorted(SRC_DIR.glob("*.pdf")):
        if norm(f.stem).startswith(target):
            return str(f)
    return None


def zip_bytes(paths: list[str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, arcname=os.path.basename(p))
    return buf.getvalue()


def show_results(sop_id: str, paths: list[str], source: str | None = None) -> None:
    """Download buttons, a zip, and an inline preview. If `source` (the original
    SOP PDF) is given, it's offered first as a preview/download option."""
    pdfs = [p for p in paths if p.lower().endswith(".pdf")]

    # Ordered (label, path): the source SOP first, then the generated deliverables.
    items: list[tuple[str, str]] = []
    if source and os.path.exists(source):
        items.append(("📄 Source SOP (original)", source))
    items += [(os.path.basename(p), p) for p in sorted(pdfs)]

    st.success(f"Generated {len(pdfs)} deliverables for {sop_id}.")

    st.download_button(
        "⬇️  Download all (.zip)",
        data=zip_bytes([p for _, p in items]),
        file_name=f"{sop_id}_FlowAgent.zip",
        mime="application/zip",
        type="primary",
    )

    def _mime(p: str) -> str:
        pl = p.lower()
        if pl.endswith(".pdf"):
            return "application/pdf"
        if pl.endswith((".txt", ".md")):
            return "text/plain"
        return "application/octet-stream"

    cols = st.columns(3)
    for i, (label, p) in enumerate(items):
        with cols[i % 3]:
            with open(p, "rb") as fh:
                st.download_button(
                    label,
                    data=fh.read(),
                    file_name=os.path.basename(p),
                    mime=_mime(p),
                    key=f"dl_{i}_{os.path.basename(p)}",
                )

    st.divider()
    by_label = {label: p for label, p in items}
    choice = st.selectbox("Preview", list(by_label), key=f"prev_{sop_id}")
    if choice:
        p = by_label[choice]
        if p.lower().endswith(".pdf"):
            try:
                for n, png in enumerate(pdf_page_images(p), 1):
                    st.image(png, width="stretch", caption=f"Page {n}")
            except Exception:
                st.info(
                    "Inline preview unavailable here — use the download button "
                    "above to open the PDF."
                )
        else:  # text upload (txt / md) used as a Live-mode source
            try:
                st.text(Path(p).read_text(encoding="utf-8", errors="replace"))
            except Exception:
                st.info("Inline preview unavailable — use the download button above.")


def remember_results(mode, sop_id, tmp, paths, elapsed=None, payload=None, source=None) -> None:
    """Persist the last render so it survives Streamlit re-runs (e.g. when the
    user changes the preview dropdown). Cleans up the previous temp dir."""
    old = st.session_state.get("results")
    if old and old.get("tmp") and old["tmp"] != tmp:
        shutil.rmtree(old["tmp"], ignore_errors=True)
    st.session_state["results"] = {
        "mode": mode, "sop_id": sop_id, "tmp": tmp,
        "paths": paths, "elapsed": elapsed, "payload": payload, "source": source,
    }


def render_stored(mode: str) -> None:
    """Re-draw the most recent results for this mode on every run."""
    res = st.session_state.get("results")
    if not (res and res.get("mode") == mode):
        return
    if res.get("elapsed") is not None:
        st.caption(f"Rendered in {res['elapsed']:.1f}s")
    show_results(res["sop_id"], res["paths"], source=res.get("source"))
    if res.get("payload") is not None:
        with st.expander("Canonical JSON (review before trusting)"):
            st.json(res["payload"])


# --- Sidebar ----------------------------------------------------------------
st.sidebar.title("🟠 FlowAgent")
st.sidebar.caption("SOP → swimlane · hierarchy · fit-gap · optimised flows + SOP")

chrome = chrome_ok()
if chrome:
    st.sidebar.success("Chrome/Chromium found", icon="✅")
else:
    st.sidebar.error(
        "No Chrome/Chromium — PDF rendering will fail. "
        "On Streamlit Cloud add `chromium` to packages.txt.",
        icon="⚠️",
    )

has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
mode = st.sidebar.radio(
    "Mode",
    ["Demo — frozen SOPs (free)", "Live — upload a SOP (uses API)"],
)


# --- Demo mode --------------------------------------------------------------
if mode.startswith("Demo"):
    st.header("Demo — frozen, authored SOPs")
    st.caption(
        "Renders the six deliverables from the committed analysis in `sop_data/`. "
        "Deterministic, no API call, no cost."
    )
    catalog = demo_catalog()
    sid = st.selectbox(
        "Choose a SOP", list(catalog), format_func=lambda s: catalog[s]
    )
    if st.button("Generate 6 deliverables", type="primary", disabled=not chrome):
        with st.spinner(f"Rendering {sid} …"):
            t0 = time.time()
            pkg = sop_data.load(sid)
            tmp, paths = render_package(pkg)
        remember_results("demo", sid, tmp, paths, elapsed=time.time() - t0,
                         source=source_pdf_for(sid))
    render_stored("demo")


# --- Live mode --------------------------------------------------------------
else:
    st.header("Live — upload a SOP")
    st.caption(
        "FlowAgent reads your SOP, builds the canonical analysis, validates it "
        "against the contract, then renders the deliverables."
    )

    if not has_key:
        st.warning(
            "The analysis service isn't configured yet. Add the API key in the "
            "app settings to enable Live mode.",
            icon="🔑",
        )

    uploaded = st.file_uploader("SOP document", type=["pdf", "txt", "md"])
    sop_id = st.text_input("SOP id", value="SOP-UPLOAD-001")

    go = st.button(
        "Analyze & generate",
        type="primary",
        disabled=not (chrome and has_key and uploaded),
    )
    if go:
        try:
            with st.status("Working …", expanded=True) as status:
                st.write("Extracting text from the SOP …")
                data = uploaded.getvalue()
                text = extract_text(uploaded.name, data)
                st.write(f"Extracted {len(text):,} characters.")

                st.write("Building the analysis (this can take 30s–2min) …")
                analyzer = LLMAnalyzer(model=MODEL, max_tokens=64000)
                t0 = time.time()
                pkg_dict = analyzer.analyze(sop_id, text)
                st.write(f"Authored in {time.time() - t0:.0f}s.")

                st.write("Validating against the contract …")
                errors = contract.validate(pkg_dict)
                if errors:
                    status.update(label="Contract validation failed", state="error")
                    st.error("Model output failed validation:")
                    st.code("\n".join(errors[:10]))
                    st.stop()

                st.write("Rendering the six deliverables …")
                pkg = contract.from_dict(pkg_dict)
                tmp, paths = render_package(pkg)
                # Keep the uploaded SOP alongside the outputs so it's previewable.
                src_path = os.path.join(tmp, uploaded.name)
                with open(src_path, "wb") as fh:
                    fh.write(data)
                status.update(label="Done", state="complete")

            remember_results("live", sop_id, tmp, paths, payload=pkg_dict, source=src_path)
        except Exception as e:  # surface SDK / render errors to the user
            st.exception(e)

    render_stored("live")
