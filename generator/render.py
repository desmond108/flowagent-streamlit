"""HTML -> PDF rendering via headless Google Chrome.

Chrome is used (rather than weasyprint/wkhtmltopdf) because it renders the
navy/gold deck styling, absolutely-positioned swimlane diagrams, and inline
SVG charts with full fidelity. CSS @page controls page size:

  * 16:9 decks  -> 13.333in x 7.5in landscape (standard PowerPoint 16:9)
  * SOP document -> A4 portrait

Nothing needs to be pip-installed; only Google Chrome is required.
"""
from __future__ import annotations

import os
import subprocess
import tempfile

# Resolve a Chrome/Chromium binary.
_CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]


def find_chrome() -> str:
    env = os.environ.get("CHROME_BIN")
    if env and os.path.exists(env):
        return env
    for path in _CHROME_CANDIDATES:
        if os.path.exists(path):
            return path
    raise RuntimeError(
        "Could not find Google Chrome / Chromium. Set CHROME_BIN to the binary."
    )


def html_to_pdf(html: str, out_path: str) -> str:
    """Render an HTML string to a PDF file at out_path."""
    chrome = find_chrome()
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        html_path = os.path.join(tmp, "page.html")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=10000",
            f"--print-to-pdf={out_path}",
            f"file://{html_path}",
        ]
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )
        if not os.path.exists(out_path):
            raise RuntimeError(
                f"Chrome failed to produce {out_path}\n"
                f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
            )
    return out_path


if __name__ == "__main__":
    # Smoke test: two pages, deck-sized, with a coloured background + SVG.
    test_html = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
      @page { size: 13.333in 7.5in; margin: 0; }
      * { margin:0; padding:0; box-sizing:border-box; }
      html,body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      .slide { width:13.333in; height:7.5in; background:#0A1628; color:#FFD700;
               display:flex; align-items:center; justify-content:center;
               flex-direction:column; page-break-after:always; font-family:Arial; }
      .slide:last-child { page-break-after:auto; }
      h1 { font-size:48px; }
    </style></head><body>
      <div class="slide"><h1>Render OK</h1>
        <svg width="200" height="200"><circle cx="100" cy="100" r="80"
          fill="none" stroke="#4CAF50" stroke-width="30"
          stroke-dasharray="300 502" transform="rotate(-90 100 100)"/></svg>
      </div>
      <div class="slide" style="background:#0F2044;"><h1>Page 2</h1></div>
    </body></html>"""
    out = html_to_pdf(test_html, os.path.join(os.path.dirname(__file__), "_smoketest.pdf"))
    print("wrote", out)
