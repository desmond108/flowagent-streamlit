# FlowAgent on Streamlit

A browser front end for the FlowAgent pipeline. It wires the existing
deterministic renderer (`generator/`) and the swappable `Analyzer` boundary
(`generator/analyzer.py`) to a Streamlit UI.

- **Demo mode** — renders the six deliverables for a frozen, authored SOP from
  `sop_data/`. No API call, no cost, fully deterministic.
- **Live mode** — upload a SOP (PDF/text); Claude authors the canonical JSON,
  it is validated against the contract, then rendered. Needs an API key.

## Run locally

```bash
cd FlowAgent_Streamlit
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Live mode also needs an API key (Demo mode does not):
#   echo 'ANTHROPIC_API_KEY = "sk-ant-..."' >> .streamlit/secrets.toml
streamlit run app.py
```

Requires **Google Chrome or Chromium** on the machine (the renderer drives it
headless to make PDFs). On macOS the bundled Chrome is auto-detected; otherwise
set `CHROME_BIN=/path/to/chrome`.

## Deploy to Streamlit Community Cloud

1. Push this directory to a **public** GitHub repo (free tier requirement).
2. On [share.streamlit.io](https://share.streamlit.io): **New app** → pick the
   repo/branch → main file `app.py`.
3. **Settings → Secrets** → add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
   Use a **low spend-limit** key — this is a public URL.
4. Deploy. `packages.txt` installs `chromium` (the renderer auto-detects
   `/usr/bin/chromium`); `requirements.txt` installs the Python deps.

### If chromium is flaky on Community Cloud

Community Cloud's apt `chromium` occasionally has sandbox/library issues. The
more robust alternative is Playwright's chromium:

- add `playwright` to `requirements.txt`,
- add a `postinstall`/setup step running `playwright install --with-deps chromium`,
- set `CHROME_BIN` to the Playwright chromium path.

Or host on a platform where you control the image (Hugging Face Spaces /
Fly.io / Render via a Dockerfile that installs Chrome) — `app.py` is unchanged.

## Notes & limits

- **Cost (Live mode):** ~$1/SOP on Opus 4.8, ~$0.60 Sonnet, ~$0.20 Haiku. The
  Batch API would halve this for offline authoring.
- **Resources:** Community Cloud is ~1 GB RAM; Chrome is memory-hungry and each
  SOP is ~11–12 s of rendering plus the API call (30 s–2 min). Fine for
  one-at-a-time demo use, not for concurrent load.
- **Determinism:** Live mode makes a runtime LLM call, which the core repo
  deliberately avoids. The faithful pattern is author → review the JSON → commit
  → render deterministically (Demo mode is that committed path). The app shows
  the canonical JSON so you can review before trusting Live output.
- **What's copied here:** `generator/`, `sop_data/`, `1_Example_Original_Input_SOPs/`
  (sample inputs), `build.py`, and the docs. The generated PDF output dirs from
  the original repo are **not** copied — they are regenerated at runtime.
