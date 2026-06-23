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

# Single model used for all authoring (backend detail; not shown to the client).
MODEL = "claude-opus-4-8"

st.set_page_config(page_title="FlowAgent", page_icon="🟠", layout="wide")


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


def extract_text(uploaded) -> str:
    """Pull plain text from an uploaded PDF / txt / md file."""
    name = uploaded.name.lower()
    data = uploaded.read()
    if name.endswith(".pdf"):
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


def zip_bytes(paths: list[str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, arcname=os.path.basename(p))
    return buf.getvalue()


def show_results(sop_id: str, paths: list[str]) -> None:
    """Download buttons, a zip, and an inline preview of one PDF."""
    pdfs = [p for p in paths if p.lower().endswith(".pdf")]
    st.success(f"Generated {len(pdfs)} deliverables for {sop_id}.")

    st.download_button(
        "⬇️  Download all (.zip)",
        data=zip_bytes(pdfs),
        file_name=f"{sop_id}_FlowAgent.zip",
        mime="application/zip",
        type="primary",
    )

    cols = st.columns(3)
    for i, p in enumerate(sorted(pdfs)):
        with cols[i % 3]:
            with open(p, "rb") as fh:
                st.download_button(
                    os.path.basename(p),
                    data=fh.read(),
                    file_name=os.path.basename(p),
                    mime="application/pdf",
                    key=f"dl_{i}_{os.path.basename(p)}",
                )

    st.divider()
    choice = st.selectbox(
        "Preview", sorted(pdfs), format_func=os.path.basename, key=f"prev_{sop_id}"
    )
    if choice:
        try:
            pages = pdf_page_images(choice)
            for n, png in enumerate(pages, 1):
                st.image(png, use_container_width=True, caption=f"Page {n}")
        except Exception:
            st.info(
                "Inline preview unavailable here — use the download button above "
                "to open the PDF."
            )


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
    ["Demo — frozen SOPs (free)", "Live — upload a SOP (uses Claude API)"],
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
        st.caption(f"Rendered in {time.time() - t0:.1f}s")
        show_results(sid, paths)


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
                text = extract_text(uploaded)
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
                status.update(label="Done", state="complete")

            show_results(sop_id, paths)
            with st.expander("Canonical JSON (review before trusting)"):
                st.json(pkg_dict)
        except Exception as e:  # surface SDK / render errors to the user
            st.exception(e)
