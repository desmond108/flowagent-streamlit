"""FlowAgent — Streamlit front end.

Wires the existing deterministic renderer (generator/) and the swappable
Analyzer boundary (generator/analyzer.py) to a browser UI:

  * Demo mode  — render the 6 deliverables for a frozen, authored SOP. No API
                 call, no cost, fully deterministic (uses sop_data/).
  * Live mode  — upload a SOP (PDF / text); LLMAnalyzer authors the canonical
                 JSON via the Claude API, it is validated against the contract,
                 then rendered. Needs ANTHROPIC_API_KEY + Google Chrome/Chromium.

Run locally:   streamlit run app.py
Deploy:        see DEPLOY.md (Streamlit Community Cloud + chromium via packages.txt)
"""
from __future__ import annotations

import base64
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

# Cost estimate per SOP (one authoring run): see the chat thread / DEPLOY.md.
MODELS = {
    "Opus 4.8 — best analysis (~$1.00/SOP)": "claude-opus-4-8",
    "Sonnet 4.6 — balanced (~$0.60/SOP)": "claude-sonnet-4-6",
    "Haiku 4.5 — cheapest (~$0.20/SOP)": "claude-haiku-4-5",
}

st.set_page_config(page_title="FlowAgent", page_icon="🟡", layout="wide")


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
        b64 = base64.b64encode(Path(choice).read_bytes()).decode()
        st.components.v1.html(
            f'<iframe src="data:application/pdf;base64,{b64}" '
            f'width="100%" height="640" style="border:none"></iframe>',
            height=660,
        )


# --- Sidebar ----------------------------------------------------------------
st.sidebar.title("🟡 FlowAgent")
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
        "Claude authors the canonical analysis from your SOP, it is validated "
        "against the contract, then rendered. ⚠️ This makes a billed API call."
    )

    if not has_key:
        st.warning(
            "No `ANTHROPIC_API_KEY` found. Set it in **Streamlit Cloud → Settings "
            "→ Secrets**, or in `.streamlit/secrets.toml` for local dev.",
            icon="🔑",
        )

    uploaded = st.file_uploader("SOP document", type=["pdf", "txt", "md"])
    c1, c2 = st.columns(2)
    sop_id = c1.text_input("SOP id", value="SOP-UPLOAD-001")
    model_label = c2.selectbox("Model", list(MODELS))
    model = MODELS[model_label]

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

                st.write(f"Authoring analysis with {model} (this can take 30s–2min) …")
                analyzer = LLMAnalyzer(model=model, max_tokens=64000)
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
