"""Fit-gap analysis deck: cover + executive summary (donut/bar/metrics) +
phase detail slides (FIT/PARTIAL/GAP) + critical gaps (radar + control bars)
+ remediation roadmap (ranked actions + risk bar + projected fit)."""
from __future__ import annotations

from . import theme as T
from . import charts


def _bar_colour(value):
    if value >= 75:
        return T.GREEN
    if value >= 60:
        return T.AMBER
    return T.RED


def _cover(meta, fg):
    return f"""
    <div class="slide"><div class="cover">
      <div class="band"></div>
      <div class="eyebrow" style="position:absolute;top:16%;letter-spacing:.16em">FIT-GAP ANALYSIS</div>
      <h1>{T.esc(meta.title)}</h1>
      <div class="sub">{T.esc(meta.sop_id)} · v{T.esc(meta.version)}</div>
      <div class="meta">Reference: {T.esc(meta.catalog)}</div>
      <div class="rule"></div>
      <div class="stats">
        <div class="stat" style="border-color:{T.GREEN}"><div class="n" style="color:{T.GREEN}">{fg.overall_fit}%</div><div class="l">Overall fit score</div></div>
        <div class="stat" style="border-color:{T.RED}"><div class="n" style="color:{T.RED}">{fg.gaps}</div><div class="l">Gaps identified</div></div>
        <div class="stat" style="border-color:{T.AMBER}"><div class="n" style="color:{T.AMBER}">{fg.partials}</div><div class="l">Partial fits</div></div>
      </div>
      <div class="foot">Prepared by Flow Agent · Confidential · 2026</div>
    </div></div>"""


def _exec_summary(meta, fg):
    gap_pct = 100 - fg.overall_fit - fg.partial_pct
    donut = charts.donut(fg.overall_fit, gap_pct, fg.partial_pct)
    bars = charts.vbars(
        [(b.line1, b.line2, b.value, _bar_colour(b.value)) for b in fg.phase_bars])
    legend = f"""
      <div style="display:flex;gap:18px;margin-top:8px;font-size:12px;color:{T.SUB}">
        <span><span style="color:{T.GREEN}">■</span> Fit ({fg.overall_fit}%)</span>
        <span><span style="color:{T.RED}">■</span> Gap ({gap_pct}%)</span>
        <span><span style="color:{T.AMBER}">■</span> Partial ({fg.partial_pct}%)</span>
      </div>"""
    cards = "".join(
        f"<div style='flex:1;background:{T.NAVY2};border:1px solid {_bar_colour(c.value)};"
        f"border-radius:8px;padding:10px;text-align:center'>"
        f"<div style='font-size:11px;color:{T.GOLD2};font-weight:700'>{T.esc(c.label)}</div>"
        f"<div style='font-size:24px;font-weight:700;color:{_bar_colour(c.value)}'>{c.value}%</div>"
        f"<div style='font-size:10px;color:{T.SUB}'>{T.esc(c.sub)}</div></div>"
        for c in fg.phase_cards)
    metrics = "".join(
        f"<div style='background:{T.CARD};border-radius:7px;padding:9px 12px;margin-bottom:8px'>"
        f"<div style='font-size:11px;color:{T.GOLD};font-weight:700'>{T.esc(k)}</div>"
        f"<div style='font-size:11px;color:{T.SUB}'>{T.esc(v)}</div></div>"
        for k, v in fg.metrics)
    return f"""
    <div class="slide">
      <div class="shead"><span class="tag">SUMMARY</span><h2>Executive summary</h2></div>
      <div class="ssub">Overall alignment of {T.esc(meta.sop_id)} against {T.esc(meta.catalog)}</div>
      <div style="display:flex;gap:20px;padding:18px 36px;height:540px">
        <div style="flex:0 0 300px;background:{T.NAVY2};border-radius:10px;padding:14px;
             display:flex;flex-direction:column;align-items:center;justify-content:center">
          {donut}{legend}
        </div>
        <div style="flex:1;background:{T.NAVY2};border-radius:10px;padding:16px">
          <div style="text-align:center;font-size:14px;color:{T.GOLD2};margin-bottom:4px">Fit % by phase</div>
          {bars}
          <div style="display:flex;gap:10px;margin-top:10px">{cards}</div>
        </div>
        <div style="flex:0 0 300px">
          <div class="kicker" style="margin-bottom:8px">Key metrics</div>
          {metrics}
        </div>
      </div>
      <div class="foot">Fit-gap analysis · Flow Agent · Powered by {T.esc(meta.catalog_short)}</div>
    </div>"""


def _detail_slide(title, sub, group_keys, fg):
    blocks = []
    groups_map = dict(fg.groups)
    for gk in group_keys:
        heading = groups_map.get(gk, "")
        if heading:
            blocks.append(f"<div class='kicker' style='margin:10px 0 6px'>{T.esc(heading)}</div>")
        for it in [i for i in fg.items if i.group == gk]:
            colour = T.STATUS[it.status]
            blocks.append(f"""
            <div style="display:flex;gap:14px;align-items:stretch;
                 background:{T.CARD};border:1px solid {colour};border-radius:8px;
                 padding:10px 12px;margin-bottom:7px">
              <div style="flex:0 0 56px;display:flex;align-items:center;justify-content:center">
                <span style="background:{colour};color:{T.NAVY};font-weight:700;font-size:10px;
                      padding:5px 7px;border-radius:5px;text-align:center;line-height:1.1">{T.esc(it.status)}</span>
              </div>
              <div style="flex:0 0 220px">
                <div style="font-size:11px;color:{colour};font-weight:700">{T.esc(it.num)}</div>
                <div style="font-size:12px;color:{T.GOLD};font-weight:700">{T.esc(it.name)}</div>
              </div>
              <div style="flex:1;font-size:11px;color:{T.SUB};line-height:1.4">{T.esc(it.detail)}</div>
              <div style="flex:0 0 150px;font-size:10px;color:{T.GOLD2}">
                Owner: {T.esc(it.owner)}<br><i style="color:{T.SUB}">Ref: {T.esc(it.ref)}</i></div>
            </div>""")
    return f"""
    <div class="slide">
      <div class="shead"><span class="tag">DETAIL</span><h2>{T.esc(title)}</h2></div>
      <div class="ssub">{T.esc(sub)}</div>
      <div style="padding:10px 36px">{''.join(blocks)}</div>
      <div class="foot">Fit-gap analysis · Flow Agent</div>
    </div>"""


def _critical_slide(meta, fg):
    missing = "".join(f"""
      <div style="display:flex;gap:10px;background:{T.NAVY2};border:1px solid {T.RED};
           border-radius:7px;padding:7px 12px;margin-bottom:6px">
        <div style="flex:0 0 22px;font-size:16px;color:{T.RED}">✖</div>
        <div><div style="font-size:12px;color:{T.RED};font-weight:700">MISSING — {T.esc(g.title)}</div>
        <div style="font-size:10px;color:{T.SUB};margin-top:2px;line-height:1.35">{T.esc(g.detail)}</div></div>
      </div>""" for g in fg.critical_missing)
    radar = charts.radar(fg.radar)
    bars = "".join(f"""
      <div style="display:flex;align-items:center;gap:9px;background:{T.CARD};
           border-radius:6px;padding:5px 10px;margin-bottom:4px">
        <div style="flex:0 0 140px;font-size:10.5px;color:{T.GOLD};font-weight:700">{T.esc(b.name)}</div>
        <div style="flex:0 0 120px">{charts.hbars([(b.name, b.value, _bar_colour(b.value))], width=120, row_h=18)}</div>
        <div style="flex:0 0 36px;font-size:11px;color:{_bar_colour(b.value)};font-weight:700">{b.value}%</div>
        <div style="flex:1;font-size:9.5px;color:{T.SUB}">{T.esc(b.note)}</div>
      </div>""" for b in fg.control_bars)
    return f"""
    <div class="slide">
      <div class="shead"><span class="tag">CRITICAL</span><h2>Critical gaps — missing steps &amp; controls</h2></div>
      <div class="ssub">Steps absent or non-compliant vs {T.esc(meta.catalog_short)}</div>
      <div style="padding:6px 36px">
        {missing}
        <div style="display:flex;gap:18px;margin-top:4px;align-items:flex-start">
          <div style="flex:0 0 300px;background:{T.NAVY2};border-radius:10px;padding:8px;text-align:center">
            <div style="font-size:12px;color:{T.GOLD2}">Controls coverage vs catalog</div>{radar}</div>
          <div style="flex:1">{bars}</div>
        </div>
      </div>
      <div class="foot">Fit-gap analysis · Flow Agent</div>
    </div>"""


def _remediation_slide(meta, fg):
    actions = "".join(f"""
      <div style="display:flex;gap:12px;background:{T.NAVY2};border:1px solid {T.NAVY3};
           border-left:4px solid {T.RED if r.priority=='High' else T.AMBER};
           border-radius:8px;padding:10px 12px;margin-bottom:8px">
        <div style="flex:0 0 26px;height:26px;background:{T.RED if r.priority=='High' else T.AMBER};
             color:{T.NAVY};font-weight:700;border-radius:6px;display:flex;
             align-items:center;justify-content:center;font-size:13px">{r.rank}</div>
        <div style="flex:1">
          <div style="display:flex;justify-content:space-between">
            <div style="font-size:12px;color:{T.WHITE};font-weight:700">{T.esc(r.title)}</div>
            <span style="background:{T.RED if r.priority=='High' else T.AMBER};color:{T.NAVY};
                  font-size:10px;font-weight:700;padding:2px 9px;border-radius:5px;height:18px">{T.esc(r.priority)}</span></div>
          <div style="font-size:10px;color:{T.SUB};margin-top:3px;line-height:1.4">{T.esc(r.detail)}</div>
        </div></div>""" for r in fg.remediations)
    risk_rows = "".join(f"""
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
        <div style="flex:0 0 120px;font-size:10px;color:{T.SUB};text-align:right">{T.esc(l)}</div>
        <div style="flex:1">{charts.hbars([(l, v, T.RED if v>=70 else T.AMBER)], width=180, row_h=20)}</div>
        <div style="flex:0 0 28px;font-size:11px;color:{T.GOLD}">{v}</div>
      </div>""" for (l, v) in fg.risk_impact)
    proj = charts.grouped_bars([fg.overall_fit, fg.projected_fit],
                               ["Current", "Post-remediation"], [T.AMBER, T.GREEN])
    return f"""
    <div class="slide">
      <div class="shead"><span class="tag">ACTIONS</span><h2>Recommendations &amp; remediation roadmap</h2></div>
      <div class="ssub">Priority actions to close gaps and reach {T.esc(meta.catalog_short)} alignment</div>
      <div style="display:flex;gap:20px;padding:10px 36px">
        <div style="flex:1.4">
          <div class="kicker" style="margin-bottom:6px">Remediation actions — ranked by priority</div>
          {actions}
        </div>
        <div style="flex:1">
          <div class="kicker" style="margin-bottom:8px">Risk impact by gap</div>
          {risk_rows}
          <div class="kicker" style="margin:14px 0 4px">Projected fit score</div>
          <div style="background:{T.NAVY2};border-radius:8px;padding:6px">{proj}</div>
        </div>
      </div>
      <div class="foot">Fit-gap analysis · Flow Agent</div>
    </div>"""


def render(pkg) -> str:
    meta, fg = pkg.meta, pkg.fitgap
    slides = [_cover(meta, fg), _exec_summary(meta, fg)]
    for (title, sub, keys) in fg.detail_slides:
        slides.append(_detail_slide(title, sub, keys, fg))
    slides.append(_critical_slide(meta, fg))
    slides.append(_remediation_slide(meta, fg))
    return T.deck_page("".join(slides))
