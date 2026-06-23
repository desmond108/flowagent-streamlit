"""Optimised SOP document: A4 portrait, Word-style, with NEW/ENHANCED/
CRITICAL change banners, highlighted table rows, and a version-control table.

Driven by an OptimisedDoc (list of DocSection, each a list of block tuples).
Block grammar (see model.py):
  ("para", text)
  ("bullets", [items])
  ("numbered", [items])
  ("numbered_from", start, [items])
  ("banner", kind, text)            kind: new/enh/crit
  ("summary", title, [paras], [bullets])
  ("meta", [(k, v)])
  ("table", headers, rows, highlights)  highlights: {row_index: "new"|"enh"}
"""
from __future__ import annotations

from . import theme as T

_BANNER = {"new": ("new", "NEW STEP"), "enh": ("enh", "ENHANCED"),
           "crit": ("crit", "CRITICAL ADD")}


def _block(b):
    try:
        return _render_block(b)
    except Exception:
        return ""  # skip a malformed block rather than crash the whole document


def _render_block(b):
    if not b:
        return ""
    tag = b[0]
    if tag == "para":
        return f"<p>{T.esc(b[1])}</p>"
    if tag == "bullets":
        return "<ul>" + "".join(f"<li>{T.esc(x)}</li>" for x in b[1]) + "</ul>"
    if tag == "numbered":
        return "<ol>" + "".join(f"<li>{T.esc(x)}</li>" for x in b[1]) + "</ol>"
    if tag == "numbered_from":
        start, items = b[1], b[2]
        return (f"<ol start='{start}'>" +
                "".join(f"<li>{T.esc(x)}</li>" for x in items) + "</ol>")
    if tag == "banner":
        kind, text = b[1], b[2]
        cls, lab = _BANNER[kind]
        return (f"<div class='banner {cls}'><div class='lab'>{lab}</div>"
                f"<div class='txt'>{T.esc(text)}</div></div>")
    if tag == "summary":
        _, title, paras, bullets = b
        pp = "".join(f"<p>{T.esc(x)}</p>" for x in paras)
        bl = ("<ul>" + "".join(f"<li>{T.esc(x)}</li>" for x in bullets) + "</ul>"
              if bullets else "")
        return f"<div class='summary'><h4>{T.esc(title)}</h4>{pp}{bl}</div>"
    if tag == "meta":
        rows = "".join(f"<tr><td class='k'>{T.esc(k)}</td><td>{T.esc(v)}</td></tr>"
                       for k, v in b[1])
        return f"<table class='meta'><tbody>{rows}</tbody></table>"
    if tag == "table":
        headers, rows = b[1], b[2]
        highlights = b[3] if len(b) > 3 else {}
        head = "".join(f"<th>{T.esc(h)}</th>" for h in headers)
        body = []
        for i, row in enumerate(rows):
            cls = highlights.get(i, "")
            rowcls = f" class='row-{cls}'" if cls else ""
            tds = []
            for j, cell in enumerate(row):
                ccls = " class='num'" if j == 0 and len(str(cell)) <= 4 else ""
                tds.append(f"<td{ccls}>{T.esc(cell)}</td>")
            body.append(f"<tr{rowcls}>{''.join(tds)}</tr>")
        return (f"<table class='doc'><thead><tr>{head}</tr></thead>"
                f"<tbody>{''.join(body)}</tbody></table>")
    return ""


def render(pkg) -> str:
    meta = pkg.meta
    doc = pkg.optimised_doc
    parts = [f"""
      <div class="title-block">
        <div class="ey">STANDARD OPERATING PROCEDURE — OPTIMISED</div>
        <h1>{T.esc(meta.title)}</h1>
        <div class="it">{T.esc(doc.subtitle)}</div>
      </div>"""]
    for sec in doc.sections:
        if sec.title:
            parts.append(f"<h2>{T.esc(sec.title)}</h2>")
        for blk in sec.blocks:
            # allow ("h3", text) inline sub-headings
            if blk and blk[0] == "h3":
                parts.append(f"<h3>{T.esc(blk[1]) if len(blk) > 1 else ''}</h3>")
            else:
                parts.append(_block(blk))
    parts.append("<div class='endmark'>— END OF DOCUMENT —</div>")
    return T.doc_page("".join(parts))
