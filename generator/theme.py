"""Shared visual theme: colour palette + CSS for the 16:9 decks and the
A4 SOP document. Mirrors the FlowAgent navy/gold styling used by the
existing HR/Finance example outputs.
"""
from __future__ import annotations

import html as _html

# ---- Palette -------------------------------------------------------------
NAVY = "#0A1628"
NAVY2 = "#0F2044"
NAVY3 = "#162A55"
CARD = "#1A2E52"
CARD2 = "#1F3560"
GOLD = "#FFD700"
GOLD2 = "#E6B800"
GOLD3 = "#C8A000"
SUB = "#A8C0E8"
WHITE = "#FFFFFF"
GREEN = "#4CAF50"
GREEN_DK = "#0A2010"
RED = "#EF5350"
RED_DK = "#3A1212"
AMBER = "#FF9800"
BLUE = "#42A5F5"

# Status colours for fit-gap + flow node kinds
STATUS = {"FIT": GREEN, "PARTIAL": AMBER, "GAP": RED}
NODE = {
    "standard": GOLD,
    "new": GREEN,
    "enhanced": AMBER,
    "exception": RED,
    "decision": GOLD,
    "terminal": GREEN,
}


def esc(text: str) -> str:
    return _html.escape(str(text))


# ---- Deck CSS (16:9 landscape, 13.333in x 7.5in) -------------------------
DECK_CSS = f"""
@page {{ size: 13.333in 7.5in; margin: 0; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: Arial, Helvetica, sans-serif; background:{NAVY};
        color:{GOLD}; }}
.slide {{ position:relative; width:13.333in; height:7.5in; background:{NAVY};
          overflow:hidden; page-break-after:always; }}
.slide:last-child {{ page-break-after:auto; }}
.pad {{ padding:0.5in 0.6in; height:100%; }}

/* Header band used on content slides */
.shead {{ display:flex; align-items:center; gap:16px; padding:18px 36px;
          background:{NAVY2}; border-bottom:1px solid {NAVY3}; }}
.tag {{ background:{GOLD}; color:{NAVY}; font-weight:700; font-size:12px;
        letter-spacing:.06em; padding:8px 16px; border-radius:6px; }}
.shead h2 {{ font-size:30px; color:{GOLD}; font-weight:700; }}
.ssub {{ font-size:13px; color:{SUB}; padding:8px 36px 0; }}

.eyebrow {{ font-size:13px; letter-spacing:.28em; color:{BLUE};
            font-weight:700; }}
.kicker {{ font-size:11px; letter-spacing:.18em; color:{GOLD3};
           font-weight:700; text-transform:uppercase; }}

/* Cover slide */
.cover {{ display:flex; flex-direction:column; align-items:center;
          justify-content:center; height:100%; text-align:center; }}
.cover .band {{ position:absolute; left:0; right:0; top:34%; height:32%;
                background:{NAVY2}; }}
.cover h1 {{ font-size:54px; color:{GOLD}; font-weight:700; z-index:2;
             padding:0 1in; line-height:1.05; }}
.cover .sub {{ font-size:22px; color:{GOLD2}; margin-top:10px; z-index:2; }}
.cover .meta {{ font-size:15px; color:{SUB}; font-style:italic;
                margin-top:14px; z-index:2; }}
.cover .rule {{ width:42%; height:1px; background:{NAVY3}; margin:22px 0;
                z-index:2; }}

/* Stat cards row */
.stats {{ display:flex; gap:26px; justify-content:center; margin-top:6px;
          z-index:2; }}
.stat {{ background:{CARD}; border:1px solid {NAVY3}; border-radius:10px;
         padding:20px 30px; min-width:150px; }}
.stat .n {{ font-size:34px; font-weight:700; }}
.stat .l {{ font-size:12px; color:{SUB}; margin-top:4px; }}

.foot {{ position:absolute; bottom:16px; left:0; right:0; text-align:center;
         font-size:10px; letter-spacing:.14em; color:{NAVY3}; }}

/* Generic table for hierarchy phase tables */
table.grid {{ width:100%; border-collapse:collapse; font-size:12px; }}
table.grid th {{ background:{NAVY3}; color:{GOLD}; text-align:left;
                 padding:10px 12px; font-size:11px; letter-spacing:.04em; }}
table.grid td {{ background:{CARD}; color:{SUB}; padding:9px 12px;
                vertical-align:top; border-bottom:3px solid {NAVY}; }}
table.grid td.num {{ color:{GOLD}; font-weight:700; width:48px; }}
table.grid td.act {{ color:{GOLD}; }}
tr.decision td {{ background:{NAVY2}; border-left:4px solid {GOLD}; }}
tr.decision td.num {{ color:{GOLD}; font-size:18px; text-align:center; }}
.brn {{ color:{GREEN}; }} .brn .b {{ color:{GOLD2}; }}
"""

# ---- SOP document CSS (A4 portrait, Word-style) --------------------------
DOC_INK = "#1F3864"      # navy heading ink
DOC_INK2 = "#2E4D7B"
DOC_RULE = "#BFC9DA"
DOC_HEAD_BG = "#1F3864"
DOC_SUBHEAD = "#2E5496"

DOC_CSS = f"""
@page {{ size: A4; margin: 22mm 18mm 20mm 18mm; }}
* {{ box-sizing:border-box; }}
html, body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: Arial, Helvetica, sans-serif; color:#1a1a1a;
        font-size:10.5pt; line-height:1.5; }}
.title-block {{ text-align:center; margin-bottom:18px; }}
.title-block .ey {{ font-size:11pt; font-weight:700; color:{DOC_INK};
                    letter-spacing:.02em; }}
.title-block h1 {{ font-size:21pt; color:{DOC_INK}; margin:4px 0; }}
.title-block .it {{ font-style:italic; color:#444; font-size:10pt; }}
h2 {{ color:{DOC_INK}; font-size:15pt; margin:20px 0 8px;
      border-bottom:1px solid {DOC_RULE}; padding-bottom:3px; }}
h3 {{ color:{DOC_SUBHEAD}; font-size:12pt; margin:14px 0 6px; }}
p {{ margin:7px 0; }}
ul, ol {{ margin:7px 0 7px 22px; }}
li {{ margin:3px 0; }}
table.doc {{ width:100%; border-collapse:collapse; margin:8px 0; font-size:9.5pt; }}
table.doc th {{ background:{DOC_HEAD_BG}; color:#fff; text-align:left;
                padding:6px 8px; border:1px solid {DOC_HEAD_BG}; }}
table.doc td {{ padding:6px 8px; border:1px solid {DOC_RULE};
                vertical-align:top; }}
table.meta td {{ padding:6px 9px; border:1px solid {DOC_RULE}; }}
table.meta td.k {{ background:#DCE6F1; font-weight:700; color:{DOC_INK};
                   width:34%; }}
.summary {{ background:#DCE6F1; border:1px solid #B6C7E0; border-radius:3px;
            padding:12px 14px; margin:14px 0; }}
.summary h4 {{ color:{DOC_INK}; font-size:11pt; margin-bottom:6px; }}
.banner {{ display:flex; border:1px solid {DOC_RULE}; margin:8px 0;
           font-size:9.5pt; }}
.banner .lab {{ flex:0 0 92px; padding:8px; font-weight:700; font-size:8.5pt;
                display:flex; align-items:center; }}
.banner .txt {{ padding:8px 10px; font-style:italic; color:#333; }}
.banner.new {{ background:#E2EFDA; }} .banner.new .lab {{ color:#375623; }}
.banner.enh {{ background:#FCE9D5; }} .banner.enh .lab {{ color:#9C5700; }}
.banner.crit {{ background:#FBE0E0; }} .banner.crit .lab {{ color:#A11; }}
tr.row-new td {{ background:#E2EFDA; }}
tr.row-new td.num {{ color:#375623; font-weight:700; }}
tr.row-enh td {{ background:#FCE9D5; }}
tr.row-enh td.num {{ color:#9C5700; font-weight:700; }}
td.green {{ color:#2E7D32; }} td.amber {{ color:#B26A00; }}
.endmark {{ text-align:center; color:#888; letter-spacing:.1em;
            margin-top:20px; }}
"""


def deck_page(html: str) -> str:
    """Wrap full deck HTML body in a document with the deck CSS."""
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{DECK_CSS}</style></head><body>{html}</body></html>"
    )


def doc_page(html: str) -> str:
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{DOC_CSS}</style></head><body>{html}</body></html>"
    )
