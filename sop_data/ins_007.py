"""SOP-INS-007 — Group Quote Marketing (Meridian Insurance Group).

Fit-gap vs the Majesco Distribution & Group Quoting best-practice catalog.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Majesco Distribution & Group Quoting Best-Practice Catalog"
CATALOG_SHORT = "Majesco DM"

meta = Meta(
    sop_id="SOP-INS-007", slug="Group_Quote_Marketing",
    title="Group Quote Marketing", short_title="Group quote marketing",
    version="1.1", owner="Group Marketing & Distribution",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="2.0", effective_date="01 October 2026",
    supersedes="v1.1 dated 15 March 2025", approved_by="Chief Marketing Officer",
    classification="Internal Use Only",
)

phases = [
    Phase("1", "Prospect identification & qualification", "Source, discover, census", "blue",
          "Field Agent · Marketing · New Business", "Steps 1–4", "4 steps"),
    Phase("2", "Quote preparation", "Pricing, proposal, approval", "green",
          "New Business · Underwriting · Actuarial", "Steps 5–8", "4 steps + 1 decision"),
    Phase("3", "Presentation & conversion", "Present, negotiate, accept, handover", "amber",
          "Field Agent · Prospect · New Business", "Steps 9–12", "4 steps + 1 decision"),
]

steps = [
    Step("1", "1", "Group prospect identified (campaign, referral, sourcing)", "Field Agent / Marketing Manager",
         "Prospect logged in CRM; preliminary group size and benefit type recorded", "Day 0", "Pipeline entry", kind="trigger"),
    Step("2", "1", "Initial meeting / needs discovery", "Field Agent",
         "Needs, current insurer, renewal date and decision timeline established", "Day 1–5", "Needs discovery"),
    Step("3", "1", "Census data request sent to prospect", "Field Agent",
         "Meridian Group Census Data Form provided; completion deadline set", "Day 5", "Census request"),
    Step("4", "1", "Completed census data received", "Field Agent / New Business Specialist",
         "Data validated for completeness; missing data followed up within 2 days", "Day 5–10", "Census validation"),
    Step("5", "2", "Census data submitted to Underwriting and Actuarial", "New Business Specialist",
         "Quote request logged with target presentation date; urgency assigned", "Day 10", "Quote request"),
    Step("6", "2", "Risk assessment and pricing", "Underwriting / Actuarial",
         "Experience or community rating by group size; pricing within 5 days for standard groups", "≤5 days", "Pricing SLA"),
    Step("7", "2", "Formal quote document prepared", "New Business Specialist",
         "Proposal: benefits schedule, rates by tier, 30-day validity, key terms", "Day +1", "Proposal generation"),
    Step("8", "2", "Quote reviewed and approved", "Marketing Manager / Underwriting",
         "Final accuracy and marketing-compliance review; approved quote released to agent", "Day +1", "Compliance review"),
    Step("", "2", "", "", "", "", "Quote governance", kind="decision", decision="Standard or non-standard group?",
         branches=["Standard → approve & release", "Non-standard (>80% loss ratio) → Head of Group (Sec 6.3)"]),
    Step("9", "3", "Proposal presented to prospect", "Field Agent",
         "Presentation held; proposal submitted; competitor comparison if requested", "Day +2", "Presentation"),
    Step("10", "3", "Prospect negotiation (if applicable)", "Field Agent / New Business Specialist",
         "Revised terms to Underwriting; max 2 revisions without escalation", "Day +2–10", "Revision control"),
    Step("11", "3", "Prospect accepts proposal", "Field Agent",
         "Signed acceptance or heads of agreement received; accepted in CRM", "Day +10", "Acceptance"),
    Step("12", "3", "Handover to Group Benefits Administration", "New Business Specialist",
         "Case file transferred to SOP-INS-006 for master policy setup", "Day +10", "Handover", kind="complete"),
]

authority = [
    AuthorityRow("Standard group quote", "Underwriting / Actuarial", "Marketing review"),
    AuthorityRow("Up to 2 quote revisions", "New Business Specialist", "Underwriting"),
    AuthorityRow("Non-standard group", "Head of Group Insurance", "Compliance"),
    AuthorityRow("Loss ratio >80% (prior 3y)", "Head of Group Insurance", "Underwriting"),
    AuthorityRow("Marketing collateral approval", "Marketing Manager", "Compliance"),
]

swim_phases = [
    SwimPhase("1", "Prospect identification & qualification", "Steps 1–4 · source to census",
        ["Prospect", "Field Agent", "New Business"],
        [SwimNode("s1", "Field Agent", 0, "Prospect identified", "logged in CRM"),
         SwimNode("s2", "Field Agent", 1, "Needs discovery", "current insurer · renewal"),
         SwimNode("s3", "Field Agent", 2, "Census data request", "Census Data Form"),
         SwimNode("s4", "New Business", 3, "Census validated", "completeness check")],
        [SwimEdge("s1", "s2"), SwimEdge("s2", "s3"), SwimEdge("s3", "s4")],
        "Prospects with 10+ lives are qualified and a census data form is collected before quoting can begin."),
    SwimPhase("2", "Quote preparation", "Steps 5–8 · pricing to approval",
        ["New Business", "Underwriting / Actuarial", "Marketing"],
        [SwimNode("a1", "New Business", 0, "Submit census to UW", "urgency assigned"),
         SwimNode("a2", "Underwriting / Actuarial", 1, "Risk assessment & pricing", "experience / community"),
         SwimNode("a3", "New Business", 2, "Prepare formal quote", "30-day validity"),
         SwimNode("a4", "Marketing", 3, "Review & approve", "compliance check", kind="decision"),
         SwimNode("a5", "Underwriting / Actuarial", 2, "Non-standard → Head of Group", "Sec 6.3", kind="exception")],
        [SwimEdge("a1", "a2"), SwimEdge("a2", "a3"), SwimEdge("a3", "a4"),
         SwimEdge("a2", "a5", dashed=True, kind="exception", label="n-std")],
        "Census data is priced by Underwriting/Actuarial and the proposal is compliance-reviewed before release; non-standard groups escalate."),
    SwimPhase("3", "Presentation & conversion", "Steps 9–12 · present to handover",
        ["Field Agent", "Prospect", "New Business"],
        [SwimNode("d1", "Field Agent", 0, "Present proposal", "competitor comparison"),
         SwimNode("d2", "Field Agent", 1, "Negotiate (≤2 revisions)", "revised terms"),
         SwimNode("d3", "Prospect", 2, "Accept proposal", "signed acceptance"),
         SwimNode("d4", "New Business", 3, "Handover to GBA", "SOP-INS-006", kind="terminal"),
         SwimNode("d5", "Field Agent", 2, "Not proceed → lost", "reason code", kind="exception")],
        [SwimEdge("d1", "d2"), SwimEdge("d2", "d3"), SwimEdge("d3", "d4"),
         SwimEdge("d2", "d5", dashed=True, kind="exception", label="lost")],
        "Proposals are presented and negotiated within revision limits; acceptance hands the case to Group Benefits Administration."),
]

fg_items = [
    FitItem("1", "Pipeline & prospect capture", "FIT",
        "CRM prospect logging with size and benefit type aligns with Majesco distribution pipeline management.",
        "Field Agent / Marketing", "MJ-DM-PIP-01", "p1"),
    FitItem("2", "Needs discovery", "FIT",
        "Structured needs discovery capturing incumbent and renewal date aligns with Majesco opportunity qualification.",
        "Field Agent", "MJ-DM-PIP-03", "p1"),
    FitItem("3", "Digital census intake", "GAP",
        "Census is collected via a manual form. Majesco supports digital census intake and API import from broker "
        "benefits-admin systems, cutting turnaround and transcription error.",
        "Field Agent / New Business", "MJ-DM-CEN-01", "p1"),
    FitItem("4", "Census validation", "PARTIAL",
        "Completeness is checked manually with 2-day follow-up. Majesco auto-validates census structure and data "
        "quality on import.",
        "New Business Specialist", "MJ-DM-CEN-02", "p1"),
    FitItem("5", "Quote request orchestration", "FIT",
        "Quote request logging with urgency and target date aligns with Majesco quote workflow.",
        "New Business Specialist", "MJ-DM-QTE-01", "p2"),
    FitItem("6", "Automated group quoting", "GAP",
        "Even standard groups are manually underwritten. Majesco auto-quotes standard groups via a rating engine "
        "with what-if modelling, reserving underwriter time for complex risks.",
        "Underwriting / Actuarial", "MJ-DM-QTE-03", "p2"),
    FitItem("7", "Risk-data enrichment", "PARTIAL",
        "Pricing uses census only. Majesco enriches with industry-risk and group claims-history data to refine "
        "rating and control anti-selection.",
        "Underwriting / Actuarial", "MJ-DM-QTE-05", "p2"),
    FitItem("8", "Proposal generation & validity", "FIT",
        "Formal proposal with tiered rates and 30-day validity aligns with Majesco proposal generation.",
        "New Business Specialist", "MJ-DM-PRO-01", "p2"),
    FitItem("9", "Compliance review of proposal", "PARTIAL",
        "Marketing-compliance review is manual. Majesco applies automated disclosure/compliance checks to proposals "
        "before release.",
        "Marketing / Underwriting", "MJ-DM-PRO-03", "p2"),
    FitItem("10", "Digital proposal & e-signature", "GAP",
        "Proposals are presented and accepted via signed letters. Majesco delivers a digital e-proposal with "
        "e-signature acceptance and full audit — a conduct and cycle-time gap.",
        "Field Agent", "MJ-DM-PRO-05", "p3"),
    FitItem("11", "Negotiation & revision control", "FIT",
        "Revision limits with underwriter re-approval align with Majesco quote-revision governance.",
        "Field Agent / New Business", "MJ-DM-NEG-01", "p3"),
    FitItem("12", "Win/loss & pipeline analytics", "PARTIAL",
        "Lost business is reviewed monthly by hand. Majesco provides win/loss and conversion analytics with "
        "competitor benchmarking for pricing feedback.",
        "Marketing Manager", "MJ-DM-ANL-01", "p3"),
    FitItem("13", "Handover to administration", "FIT",
        "Structured case-file handover to group administration aligns with Majesco sale-to-service transition.",
        "New Business Specialist", "MJ-DM-HND-01", "p3"),
]

fitgap = FitGap(
    overall_fit=66, partial_pct=20, fits=6, gaps=3, partials=4,
    steps_analysed=13, phases_count=3,
    summary_line="Overall alignment of SOP-INS-007 against the Majesco distribution & group quoting catalog",
    metrics=[
        ("Steps analysed", "13 steps across 3 phases"),
        ("Fits confirmed", "6 steps aligned to catalog"),
        ("Gaps identified", "3 steps — remediation required"),
        ("Partial fits", "4 steps — enhancement recommended"),
        ("Highest risk area", "Manual census & quoting"),
        ("Conduct gap", "No digital e-proposal / e-signature"),
        ("Ref standard", "Majesco Distribution & Quoting Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Qualify", 66, ""),
        FitPhaseBar("Phase 2", "Quote", 62, ""),
        FitPhaseBar("Phase 3", "Convert", 70, ""),
        FitPhaseBar("Digital /", "analytics", 48, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 66, "Qualification"),
        PhaseScoreCard("Phase 2", 62, "Quote preparation"),
        PhaseScoreCard("Phase 3", 70, "Conversion"),
        PhaseScoreCard("Digital", 48, "Proposal & analytics"),
    ],
    detail_slides=[
        ("Phase 1 — Prospect identification & qualification", "Steps 1–4 vs Majesco distribution catalog", ["p1"]),
        ("Phase 2 — Quote preparation", "Steps 5–9 vs Majesco distribution catalog", ["p2"]),
        ("Phase 3 — Presentation & conversion", "Steps 10–13 vs Majesco distribution catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — PROSPECT IDENTIFICATION & QUALIFICATION"),
            ("p2", "PHASE 2 — QUOTE PREPARATION"),
            ("p3", "PHASE 3 — PRESENTATION & CONVERSION")],
    critical_missing=[
        CriticalGap("Digital census intake & validation",
            "Census is collected on a manual form and checked by hand. The catalog imports digital census via "
            "API/upload with automated validation, cutting turnaround and error."),
        CriticalGap("Automated group quoting",
            "Standard groups are manually underwritten. The catalog auto-quotes standard groups with what-if "
            "modelling, freeing underwriters for complex risks and speeding response."),
        CriticalGap("Digital e-proposal & e-signature",
            "Proposals are presented and accepted on paper. The catalog delivers a digital e-proposal with "
            "e-signature acceptance and audit — a conduct and cycle-time gap."),
        CriticalGap("Win/loss & competitor analytics",
            "Lost business is reviewed manually; the catalog provides win/loss and competitor benchmarking analytics "
            "that feed pricing and product competitiveness."),
    ],
    radar=[("Pipeline", 72), ("Census intake", 45), ("Quoting", 55), ("Risk data", 50),
           ("Proposal", 70), ("E-signature", 38), ("Analytics", 52)],
    control_bars=[
        ControlBar("Pipeline & qualification", 72, "CRM pipeline and needs discovery solid"),
        ControlBar("Census intake", 45, "Manual form; no digital/API import"),
        ControlBar("Group quoting", 55, "Manual UW even for standard groups"),
        ControlBar("Risk-data enrichment", 50, "Census-only; no industry/claims data"),
        ControlBar("Proposal generation", 70, "Tiered proposal with validity"),
        ControlBar("E-proposal / e-signature", 38, "Paper acceptance; no digital signature"),
        ControlBar("Win/loss analytics", 52, "Manual monthly lost-business review"),
    ],
    remediations=[
        Remediation(1, "Implement digital census intake & validation",
            "Accept census via secure upload/API with automated structure and data-quality validation. "
            "Effort: 4 weeks.", "High"),
        Remediation(2, "Automate quoting for standard groups",
            "Auto-quote standard groups via the rating engine with what-if modelling; route only complex risks to "
            "underwriters. Effort: 6 weeks.", "High"),
        Remediation(3, "Deliver digital e-proposal & e-signature",
            "Generate a digital e-proposal with e-signature acceptance and full audit trail. Effort: 4 weeks.", "High"),
        Remediation(4, "Add win/loss & competitor analytics",
            "Provide conversion, win/loss and competitor-benchmarking dashboards to feed pricing and product. "
            "Effort: 3 weeks.", "Medium"),
        Remediation(5, "Enrich pricing with risk data & auto compliance checks",
            "Append industry-risk and group claims-history data and apply automated disclosure/compliance checks to "
            "proposals. Effort: 4 weeks.", "Medium"),
    ],
    risk_impact=[("Manual census", 80), ("Manual quoting", 78), ("E-proposal / e-sign", 72),
                 ("Win/loss analytics", 58), ("Risk-data enrichment", 55), ("Compliance checks", 50)],
    projected_fit=90,
)

opt_phases = [
    Phase("1", "Qualification & digital census", "Source, discover, digital census", "blue",
          "Field Agent · Marketing · New Business", "Steps 1–4", "4 steps"),
    Phase("2", "Automated quote preparation", "Auto-quote, enrich, e-proposal", "green",
          "New Business · Underwriting · Actuarial", "Steps 5–9", "5 steps + 1 decision"),
    Phase("3", "Presentation & conversion", "E-proposal, negotiate, accept, analytics", "amber",
          "Field Agent · Prospect · New Business", "Steps 10–14", "5 steps + 1 decision"),
]

opt_steps = [
    Step("1", "1", "Group prospect identified", "Field Agent / Marketing Manager",
         "Logged in CRM; size and benefit type recorded", "Day 0", "Standard", kind="trigger"),
    Step("2", "1", "Initial meeting / needs discovery", "Field Agent",
         "Needs, incumbent and renewal date established", "Day 1–5", "Standard"),
    Step("3", "1", "Digital census intake & validation", "Field Agent / System",
         "Census imported via secure upload/API; structure and data quality auto-validated", "Day 5",
         "NEW (v2.0) — faster, cleaner"),
    Step("4", "1", "Census enriched with risk data", "New Business / System",
         "Industry-risk and group claims-history data appended", "Day 5–7", "NEW (v2.0)"),
    Step("5", "2", "Automated quote for standard groups", "Rating Engine",
         "Standard groups auto-quoted with what-if modelling; complex routed to UW", "Same day",
         "ENHANCED (v2.0) — STP quoting"),
    Step("6", "2", "Risk assessment and pricing (complex)", "Underwriting / Actuarial",
         "Experience/community rating for non-standard groups within 5 days", "≤5 days", "Standard"),
    Step("7", "2", "Formal e-proposal prepared", "New Business Specialist",
         "Digital proposal: benefits schedule, tiered rates, 30-day validity", "Day +1", "ENHANCED (v2.0)"),
    Step("8", "2", "Automated compliance / disclosure check", "System / Marketing",
         "Disclosure and marketing-compliance checks applied before release", "Day +1",
         "NEW (v2.0) — conduct control"),
    Step("9", "2", "Quote approved and released", "Marketing Manager / Underwriting",
         "Approved e-proposal released to agent", "Day +1", "Standard"),
    Step("", "2", "", "", "", "", "Quote governance", kind="decision", decision="Standard or non-standard?",
         branches=["Standard → auto-quote & release", "Non-standard → Head of Group (Sec 6.3)"]),
    Step("10", "3", "E-proposal presented to prospect", "Field Agent",
         "Digital proposal presented; competitor comparison if requested", "Day +2", "ENHANCED (v2.0)"),
    Step("11", "3", "Prospect negotiation (if applicable)", "Field Agent / New Business",
         "Revised terms via what-if modelling; max 2 revisions without escalation", "Day +2–10", "Standard"),
    Step("12", "3", "Prospect accepts via e-signature", "Field Agent / Prospect",
         "E-signature acceptance captured with audit; accepted in CRM", "Day +10",
         "NEW (v2.0) — digital acceptance"),
    Step("13", "3", "Handover to Group Benefits Administration", "New Business Specialist",
         "Case file transferred to SOP-INS-006", "Day +10", "Standard"),
    Step("14", "3", "Win/loss analytics updated", "Marketing Manager / System",
         "Conversion, win/loss and competitor benchmarking dashboards updated", "Ongoing",
         "NEW (v2.0) — pricing feedback", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "Qualification & digital census", "Steps 1–4 · v2.0 adds digital census & enrichment",
        ["Prospect", "Field Agent", "New Business / System"],
        [SwimNode("o1", "Field Agent", 0, "Prospect identified", "logged in CRM"),
         SwimNode("o2", "Field Agent", 1, "Needs discovery", "incumbent · renewal"),
         SwimNode("o3", "New Business / System", 2, "Digital census intake", "auto-validate", kind="new"),
         SwimNode("o4", "New Business / System", 3, "Enrich with risk data", "industry · claims", kind="new")],
        [SwimEdge("o1", "o2"), SwimEdge("o2", "o3", dashed=True, kind="new", label="census"),
         SwimEdge("o3", "o4")],
        "v2.0 imports and validates census digitally and enriches it with industry-risk and claims data before pricing."),
    SwimPhase("2", "Automated quote preparation", "Steps 5–9 · auto-quote & e-proposal",
        ["New Business", "Rating / Underwriting", "Marketing / System"],
        [SwimNode("p1", "Rating / Underwriting", 0, "Auto-quote standard groups", "what-if modelling", kind="enhanced"),
         SwimNode("p2", "Rating / Underwriting", 1, "Price complex groups", "experience / community"),
         SwimNode("p3", "New Business", 2, "Prepare e-proposal", "digital · 30-day", kind="enhanced"),
         SwimNode("p4", "Marketing / System", 2, "Compliance / disclosure check", "automated", kind="new"),
         SwimNode("p5", "Marketing / System", 3, "Approve & release", "to agent", kind="decision")],
        [SwimEdge("p1", "p3", label="std"), SwimEdge("p2", "p3", label="cx"),
         SwimEdge("p3", "p4", dashed=True, kind="new"), SwimEdge("p4", "p5")],
        "v2.0 auto-quotes standard groups, generates a digital e-proposal, and applies automated compliance checks before release."),
    SwimPhase("3", "Presentation & conversion", "Steps 10–14 · v2.0 adds e-signature & analytics",
        ["Field Agent", "Prospect", "New Business / Marketing"],
        [SwimNode("q1", "Field Agent", 0, "Present e-proposal", "competitor comparison", kind="enhanced"),
         SwimNode("q2", "Field Agent", 1, "Negotiate (≤2 revisions)", "what-if terms"),
         SwimNode("q3", "Prospect", 2, "Accept via e-signature", "audited", kind="new"),
         SwimNode("q4", "New Business / Marketing", 3, "Handover to GBA", "SOP-INS-006", kind="terminal"),
         SwimNode("q5", "New Business / Marketing", 2, "Win/loss analytics", "benchmarking", kind="new")],
        [SwimEdge("q1", "q2"), SwimEdge("q2", "q3"), SwimEdge("q3", "q4"),
         SwimEdge("q2", "q5", dashed=True, kind="new", label="w/l")],
        "v2.0 captures e-signature acceptance and feeds win/loss analytics with competitor benchmarking into pricing."),
]

optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Majesco Distribution & Group Quoting Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-007"),
                ("Version", "2.0 (Optimised)"),
                ("Effective Date", "01 October 2026"),
                ("Supersedes", "v1.1 dated 15 March 2025"),
                ("Owner", "Group Marketing & Distribution"),
                ("Approved By", "Chief Marketing Officer"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-007 dated 18 June 2026"),
                ("Catalog Alignment Score", "90% (up from 66% in v1.1)"),
                ("Classification", "Internal Use Only"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v2.0",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-007. Alignment to the "
              "Majesco distribution & group quoting catalog increased from 66% to 90%. Critical additions: digital "
              "census intake with validation, automated quoting for standard groups, a digital e-proposal with "
              "e-signature, win/loss analytics, and risk-data enrichment with automated compliance checks."],
             ["NEW STEP (green) — step added to close a gap vs the Majesco catalog",
              "ENHANCED (amber) — existing step updated with additional automation or controls"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines how group insurance is marketed, quoted and sold to "
             "prospective group clients. Version 2.0 incorporates optimisations from fit-gap analysis against the "
             "Majesco Distribution & Group Quoting Best-Practice Catalog, achieving 90% alignment (up from 66% in v1.1)."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to group opportunities with 10 or more covered lives across "
             "employer-sponsored life, health, disability and accident programmes, and affinity/association groups."),
            ("banner", "new", "Scope extended: digital census intake and automated quoting now apply to all standard "
             "group opportunities."),
            ("para", "This procedure does NOT cover individual product campaigns (SOP-INS-001/008), wholesale "
             "distribution marketing, or reinsurance treaty placements."),
        ]),
        DocSection("3. Authority Matrix", [
            ("table", ["Item", "First Authority", "Second Authority"],
             [["Standard group quote", "Underwriting / Actuarial", "Marketing review"],
              ["Up to 2 quote revisions", "New Business Specialist", "Underwriting"],
              ["Non-standard group", "Head of Group Insurance", "Compliance"],
              ["Loss ratio >80% (prior 3y)", "Head of Group Insurance", "Underwriting"],
              ["Marketing collateral approval", "Marketing Manager", "Compliance"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Field Agent", "Identifies and qualifies prospects; collects census; presents proposals; manages the relationship."],
              ["Marketing Manager", "Runs campaigns and collateral; owns win/loss analytics and competitor benchmarking."],
              ["New Business Specialist", "Coordinates quoting; prepares e-proposals; manages validity and handover."],
              ["Underwriting / Actuarial", "Reviews census; sets pricing and conditions; approves quotes for release."]], {}),
        ]),
        DocSection("5. Digital Quoting Controls (New Section — v2.0)", [
            ("banner", "crit", "New section. Required by the Majesco catalog. Digital census, automated quoting and "
             "e-signature acceptance now govern the group quote lifecycle."),
            ("table", ["#", "Control", "Responsible", "Output / System", "Timeline"],
             [["Q1", "Digital census intake & validation", "New Business", "Auto-validated census via upload/API", "At census"],
              ["Q2", "Automated quoting for standard groups", "Rating Engine", "Standard groups auto-quoted with what-if", "Same day"],
              ["Q3", "E-proposal with e-signature acceptance", "Field Agent", "Digital proposal and audited acceptance", "At present/accept"]],
             {0: "new", 1: "new", 2: "new"}),
        ]),
        DocSection("6. Process Steps", [
            ("h3", "6.1 Qualification & Digital Census"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "Group prospect identified", "Field Agent / Marketing", "Logged in CRM", "Day 0"],
              ["2", "Initial meeting / needs discovery", "Field Agent", "Needs, incumbent, renewal", "Day 1–5"],
              ["3", "Digital census intake & validation", "Field Agent / System", "Auto-validated census", "Day 5"],
              ["4", "Census enriched with risk data", "New Business / System", "Industry/claims data appended", "Day 5–7"]],
             {2: "new", 3: "new"}),
            ("h3", "6.2 Automated Quote Preparation"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["5", "Automated quote for standard groups", "Rating Engine", "Auto-quote with what-if", "Same day"],
              ["6", "Risk assessment and pricing (complex)", "Underwriting / Actuarial", "Experience/community rating", "≤5 days"],
              ["7", "Formal e-proposal prepared", "New Business Specialist", "Digital proposal; 30-day validity", "Day +1"],
              ["8", "Automated compliance / disclosure check", "System / Marketing", "Checks applied before release", "Day +1"],
              ["9", "Quote approved and released", "Marketing / Underwriting", "E-proposal released to agent", "Day +1"]],
             {0: "enh", 2: "enh", 3: "new"}),
            ("h3", "6.3 Presentation & Conversion"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["10", "E-proposal presented to prospect", "Field Agent", "Digital proposal; competitor comparison", "Day +2"],
              ["11", "Prospect negotiation (if applicable)", "Field Agent / New Business", "What-if revisions; ≤2", "Day +2–10"],
              ["12", "Prospect accepts via e-signature", "Field Agent / Prospect", "Audited e-signature; CRM", "Day +10"],
              ["13", "Handover to Group Benefits Administration", "New Business Specialist", "Case file to SOP-INS-006", "Day +10"],
              ["14", "Win/loss analytics updated", "Marketing Manager", "Benchmarking dashboards", "Ongoing"]],
             {0: "enh", 2: "new", 4: "new"}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Prospect Does Not Proceed"),
            ("numbered", [
                "Reason for loss recorded in CRM with standard 'Lost Business' reason codes.",
                "Win/loss analytics surface pricing or product competitiveness issues automatically.",
                "Agent may request a post-decision debrief to capture prospect feedback."]),
            ("h3", "7.2 Quote Exceeds Validity Period"),
            ("numbered_from", 4, [
                "New Business Specialist notifies the field agent 7 days before expiry.",
                "If an extension is needed, Underwriting re-confirms pricing and reissues with a revised validity date."]),
            ("h3", "7.3 Non-Standard Group (High-Risk or Adverse Experience)"),
            ("numbered_from", 6, [
                "Underwriting flags non-standard groups to Compliance and Head of Group Insurance before quoting.",
                "Pricing is loaded with risk margin and exclusions as required.",
                "Head of Group Insurance must approve quotes for groups with loss ratios above 80% over the prior 3 years."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["CRM (Salesforce)", "Prospect tracking, pipeline, proposal history", "Field Agent, Marketing, New Business"],
              ["Group Quotation Tool (Actuarial)", "Census input, automated pricing, proposal generation", "New Business, Actuarial"],
              ["Census Intake / API", "Digital census import and validation", "New Business"],
              ["E-Proposal / E-Signature", "Digital proposal delivery and audited acceptance", "Field Agent, Prospect"],
              ["Marketing Automation (HubSpot)", "Campaigns, leads, win/loss analytics", "Marketing Manager"],
              ["Document Management System", "Proposal storage and collateral library", "All roles"],
              ["PAS", "Handover to policy setup on acceptance", "New Business Specialist"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v2.0: digital census validation, automated quoting, e-signature "
             "acceptance, and automated compliance checks."),
            ("bullets", [
                "Digital census: imported and validated automatically before pricing.",
                "Automated quoting: standard groups auto-quoted; underwriters focus on complex risks.",
                "Compliance check: disclosure and marketing-compliance applied to every proposal.",
                "E-signature: audited digital acceptance replaces paper sign-off.",
                "Risk-data enrichment: industry and claims data improve pricing accuracy.",
                "Revision control: maximum two revisions without escalation, underwriter re-approved.",
                "Immutable audit trail: census, quote, proposal and acceptance events logged."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v1.1 Target", "v2.0 Target", "Measurement"],
             [["Group pipeline conversion", "≥25%", "≥30%", "Quotes converting to bound policies"],
              ["Quote preparation cycle time", "≤5 business days", "Same day (standard)", "Census to quote"],
              ["Quote validity compliance", "100%", "100%", "Presented within validity"],
              ["Digital census adoption", "N/A (new)", "≥80%", "Digital vs manual census"],
              ["E-signature acceptance", "N/A (new)", "≥75%", "E-sign vs paper acceptance"],
              ["Lost-business documentation", "100%", "100%", "Lost opportunities with reason code"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["1.1", "15 Mar 2025", "F. Okonkwo, Group Marketing", "Added non-standard group exception; updated CRM steps; revised conversion KPI targets"],
              ["2.0", "01 Oct 2026", "F. Okonkwo, Group Marketing",
               "OPTIMISED: digital census intake; automated quoting; e-proposal & e-signature; win/loss analytics; "
               "risk-data enrichment & compliance checks; catalog alignment 66% → 90%"]], {}),
        ]),
    ],
)

package = SopPackage(
    meta=meta, phases=phases, steps=steps, authority=authority, swim_phases=swim_phases,
    n_phases=3, n_steps=12, n_roles=4, n_gateways=2,
    fitgap=fitgap,
    opt_phases=opt_phases, opt_steps=opt_steps, opt_swim_phases=opt_swim_phases,
    opt_n_phases=3, opt_n_steps=14, opt_n_gateways=2, opt_fit=90,
    optimised_doc=optimised_doc,
    swim_cover_tags="Qualify · Quote · Present · Convert · Exception handling",
    hierarchy_cover_sub="Phase breakdown with group sales tracks, quoting authority, and exception paths",
)
