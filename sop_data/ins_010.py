"""SOP-INS-010 — Insurance Sales (General) (Meridian Insurance Group).

Fit-gap vs the Guidewire PolicyCenter conduct-aligned sales catalog.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Guidewire PolicyCenter — Conduct-Aligned Sales Best-Practice Catalog"
CATALOG_SHORT = "Guidewire PolicyCenter"

meta = Meta(
    sop_id="SOP-INS-010", slug="Insurance_Sales_General",
    title="Insurance Sales (General)", short_title="General insurance sales",
    version="1.3", owner="Sales Operations",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="2.0", effective_date="01 October 2026",
    supersedes="v1.3 dated 01 February 2025", approved_by="Chief Sales Officer",
    classification="Internal Use Only",
)

phases = [
    Phase("1", "Needs analysis & suitability", "Contact, needs, suitability, PDS", "blue",
          "Agent / CSR · Member Care", "Steps 1–4", "4 steps + 1 decision"),
    Phase("2", "Application completion", "Collect, submit, refer, confirm", "green",
          "Agent / CSR · PAS · Underwriting", "Steps 5–8", "4 steps + 1 decision"),
    Phase("3", "Issuance & post-sale", "Pay, issue, QA, record", "amber",
          "Agent / CSR · Policy Service · Team Leader", "Steps 9–12", "4 steps"),
]

steps = [
    Step("1", "1", "Client contact initiated (inbound or outbound)", "Agent / CSR",
         "Contact logged in CRM; prospect record created; channel and source code recorded", "Day 0", "Pipeline entry", kind="trigger"),
    Step("2", "1", "Needs analysis conducted", "Agent / CSR",
         "Needs, financial situation, existing coverage and risk profile assessed via Needs Analysis Framework", "Day 0", "Needs Analysis Framework"),
    Step("3", "1", "Product suitability confirmed", "Agent / CSR",
         "Suitable product identified or client referred; suitability decision documented in CRM", "Day 0", "Suitability decision"),
    Step("4", "1", "Product Disclosure Statement (PDS) provided", "Agent / CSR",
         "PDS provided; receipt confirmed (verbal on call or digital acknowledgement)", "Day 0", "PDS delivery control"),
    Step("", "1", "", "", "", "", "Suitability gate", kind="decision", decision="Suitability clear?",
         branches=["Clear → proceed", "Concern → escalate to Member Care (Sec 6.2)"]),
    Step("5", "2", "Application details collected", "Agent / CSR",
         "All fields completed; material information confirmed and recorded verbatim in CRM", "Day 0–1", "Material info capture"),
    Step("6", "2", "Application submitted in PAS / agent portal", "Agent / CSR",
         "Application ID generated; auto-accept or referral decision triggered", "Day 1", "Auto-accept rules"),
    Step("7", "2", "Underwriting referral handled (if applicable)", "Agent / Underwriting",
         "Client advised of referral; SLA communicated; agent follows up within timeframe", "≤2 days", "Referral handling"),
    Step("8", "2", "Terms and premium confirmed with client", "Agent / CSR",
         "Final premium, options, start date and coverage repeated back; confirmation obtained", "Day 1–2", "Read-back confirmation"),
    Step("9", "3", "First premium payment collected", "Agent / CSR / Payment Gateway",
         "Payment processed; receipt provided; GIRO/direct debit set up if instalment", "Day 2", "Payment & mandate"),
    Step("10", "3", "Policy issued and documents dispatched", "Policy Service Rep / PAS",
         "Policy number confirmed; documents dispatched per SOP-INS-004 timelines", "≤2 days", "Issuance"),
    Step("11", "3", "Post-sale quality check", "Team Leader",
         "10% of interactions reviewed for conduct and suitability; coaching provided", "Post-sale", "Quality assurance"),
    Step("12", "3", "CRM updated with policy outcome", "Agent / CSR",
         "Policy number, product, premium and payment recorded; annual review date set", "Day 2", "Record & review date", kind="complete"),
]

authority = [
    AuthorityRow("Standard sale (suitable)", "Agent / CSR", "—"),
    AuthorityRow("Suitability override", "Team Leader", "Client signed override"),
    AuthorityRow("Suitability doubt", "Member Care Rep", "Team Leader"),
    AuthorityRow("Backdated cover / substandard", "Team Leader", "Underwriting"),
    AuthorityRow("Vulnerable client", "Member Care Rep", "Compliance"),
]

swim_phases = [
    SwimPhase("1", "Needs analysis & suitability", "Steps 1–4 · contact to PDS",
        ["Client", "Agent / CSR", "Member Care"],
        [SwimNode("s1", "Agent / CSR", 0, "Client contact initiated", "logged in CRM"),
         SwimNode("s2", "Agent / CSR", 1, "Needs analysis", "Needs Analysis Framework"),
         SwimNode("s3", "Agent / CSR", 2, "Confirm suitability", "documented in CRM"),
         SwimNode("s4", "Agent / CSR", 3, "Provide PDS", "receipt confirmed"),
         SwimNode("s5", "Member Care", 2, "Suitability concern → escalate", "Sec 6.2", kind="exception")],
        [SwimEdge("s1", "s2"), SwimEdge("s2", "s3"), SwimEdge("s3", "s4"),
         SwimEdge("s3", "s5", dashed=True, kind="exception", label="doubt")],
        "Needs analysis and a documented suitability decision precede PDS delivery; suitability doubts escalate to Member Care."),
    SwimPhase("2", "Application completion", "Steps 5–8 · collect to confirm",
        ["Agent / CSR", "PAS / Rules", "Underwriting"],
        [SwimNode("a1", "Agent / CSR", 0, "Collect application", "material info verbatim"),
         SwimNode("a2", "PAS / Rules", 1, "Submit in PAS", "auto-accept / refer", kind="decision"),
         SwimNode("a3", "Underwriting", 2, "Handle referral", "SLA communicated"),
         SwimNode("a4", "Agent / CSR", 3, "Confirm terms & premium", "read-back")],
        [SwimEdge("a1", "a2"), SwimEdge("a2", "a4", label="auto"), SwimEdge("a2", "a3", label="ref"),
         SwimEdge("a3", "a4")],
        "Applications are captured with material information verbatim and either auto-accepted or referred before terms are confirmed by read-back."),
    SwimPhase("3", "Issuance & post-sale", "Steps 9–12 · pay to record",
        ["Agent / CSR", "Policy Service / PAS", "Team Leader"],
        [SwimNode("d1", "Agent / CSR", 0, "Collect first payment", "receipt / mandate"),
         SwimNode("d2", "Policy Service / PAS", 1, "Issue & dispatch documents", "policy number"),
         SwimNode("d3", "Team Leader", 2, "Post-sale QA (10%)", "conduct review", kind="exception"),
         SwimNode("d4", "Agent / CSR", 3, "Update CRM", "annual review date", kind="terminal")],
        [SwimEdge("d1", "d2"), SwimEdge("d2", "d4"),
         SwimEdge("d2", "d3", dashed=True, kind="exception", label="QA")],
        "On payment the policy issues; a sample of interactions is quality-reviewed and the sale is recorded with a review date."),
]

fg_items = [
    FitItem("1", "Needs analysis framework", "FIT",
        "A structured Needs Analysis Framework with documented assessment aligns with PolicyCenter suitability intake.",
        "Agent / CSR", "GW-PC-SUI-01", "p1"),
    FitItem("2", "Documented suitability decision", "FIT",
        "Suitability decisions documented in CRM with referral where unsuitable align with conduct controls.",
        "Agent / CSR", "GW-PC-SUI-02", "p1"),
    FitItem("3", "Agent ready-to-sell enforcement", "GAP",
        "Licensing is a stated prerequisite but not enforced. The catalog blocks selling by representatives not "
        "currently licensed and appointed for the product (links to SOP-INS-005).",
        "Agent / PAS", "GW-PC-RTS-01", "p1"),
    FitItem("4", "PDS delivery & e-consent", "PARTIAL",
        "PDS is provided with verbal/portal acknowledgement, but the catalog mandates an auditable digital consent "
        "with a captured timestamp — verbal receipt is hard to evidence.",
        "Agent / CSR", "GW-PC-DIS-02", "p1"),
    FitItem("5", "Vulnerable-customer detection", "PARTIAL",
        "A vulnerable-customer protocol exists but relies on representative judgement; the catalog adds systematic "
        "vulnerability indicators and handling.",
        "Member Care / Agent", "GW-PC-VUL-01", "p1"),
    FitItem("6", "Material information capture", "FIT",
        "Verbatim capture of material information in CRM aligns with PolicyCenter disclosure-of-material-facts control.",
        "Agent / CSR", "GW-PC-SUB-02", "p2"),
    FitItem("7", "Application submission & auto-accept", "PARTIAL",
        "Rules-based auto-accept/referral present, but no predictive scoring to widen straight-through binding.",
        "PAS / Rules", "GW-PC-UW-02", "p2"),
    FitItem("8", "KYC / sanctions screening", "GAP",
        "No identity/sanctions screening before binding. PolicyCenter screens applicants as a regulatory control.",
        "Underwriting / Compliance", "GW-PC-UW-05", "p2"),
    FitItem("9", "Referral handling & SLA", "FIT",
        "Referral with client advisory and SLA communication aligns with PolicyCenter referral workflow.",
        "Agent / Underwriting", "GW-PC-UW-03", "p2"),
    FitItem("10", "Read-back confirmation", "FIT",
        "Repeating terms, premium and start date back to the client aligns with PolicyCenter conduct confirmation.",
        "Agent / CSR", "GW-PC-DIS-03", "p2"),
    FitItem("11", "Payment, issuance & dispatch", "FIT",
        "Payment with mandate setup and issuance per dispatch timelines align with PolicyCenter billing/issuance.",
        "Agent / Policy Service", "GW-PC-ISS-01", "p3"),
    FitItem("12", "Post-sale conduct QA", "PARTIAL",
        "Only 10% of interactions are manually reviewed. The catalog QA's conduct at scale with call/interaction "
        "analytics, not a small manual sample.",
        "Team Leader", "GW-PC-QA-01", "p3"),
    FitItem("13", "Sale record & review date", "FIT",
        "CRM sale record with an annual review date aligns with PolicyCenter post-sale management.",
        "Agent / CSR", "GW-PC-ISS-06", "p3"),
]

fitgap = FitGap(
    overall_fit=70, partial_pct=20, fits=7, gaps=2, partials=4,
    steps_analysed=13, phases_count=3,
    summary_line="Overall alignment of SOP-INS-010 against the Guidewire PolicyCenter conduct-aligned sales catalog",
    metrics=[
        ("Steps analysed", "13 steps across 3 phases"),
        ("Fits confirmed", "7 steps aligned to catalog"),
        ("Gaps identified", "2 steps — remediation required"),
        ("Partial fits", "4 steps — enhancement recommended"),
        ("Highest risk area", "No ready-to-sell enforcement"),
        ("Conduct gap", "10% manual QA; no e-consent"),
        ("Ref standard", "Guidewire PolicyCenter Conduct Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Suitability", 68, ""),
        FitPhaseBar("Phase 2", "Application", 66, ""),
        FitPhaseBar("Phase 3", "Post-sale", 74, ""),
        FitPhaseBar("Conduct /", "QA", 50, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 68, "Needs & suitability"),
        PhaseScoreCard("Phase 2", 66, "Application"),
        PhaseScoreCard("Phase 3", 74, "Issuance & post-sale"),
        PhaseScoreCard("Conduct", 50, "QA & e-consent"),
    ],
    detail_slides=[
        ("Phase 1 — Needs analysis & suitability", "Steps 1–5 vs Guidewire PolicyCenter conduct catalog", ["p1"]),
        ("Phase 2 — Application completion", "Steps 6–10 vs Guidewire PolicyCenter conduct catalog", ["p2"]),
        ("Phase 3 — Issuance & post-sale", "Steps 11–13 vs Guidewire PolicyCenter conduct catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — NEEDS ANALYSIS & SUITABILITY"),
            ("p2", "PHASE 2 — APPLICATION COMPLETION"),
            ("p3", "PHASE 3 — ISSUANCE & POST-SALE")],
    critical_missing=[
        CriticalGap("Agent ready-to-sell enforcement",
            "Licensing is a stated prerequisite but not enforced at point of sale. The catalog blocks selling by "
            "representatives not currently licensed and appointed (links to SOP-INS-005)."),
        CriticalGap("KYC / sanctions screening",
            "No identity/sanctions screening before binding, a regulatory control required by the catalog."),
        CriticalGap("Auditable PDS e-consent & suitability e-signature",
            "PDS receipt is verbal/portal and suitability is documented free-text; the catalog mandates an auditable "
            "digital consent and signed suitability record — a conduct and evidencing gap."),
        CriticalGap("Conduct QA at scale & vulnerability detection",
            "Only 10% of interactions are manually reviewed and vulnerability relies on judgement; the catalog QA's "
            "conduct at scale with analytics and systematic vulnerability indicators."),
    ],
    radar=[("Suitability", 75), ("Ready-to-sell", 40), ("PDS / consent", 55), ("KYC / sanctions", 38),
           ("Application", 66), ("Conduct QA", 50), ("Post-sale", 76)],
    control_bars=[
        ControlBar("Suitability assessment", 75, "Structured needs analysis and decision"),
        ControlBar("Ready-to-sell", 40, "Licensing not enforced at point of sale"),
        ControlBar("PDS / e-consent", 55, "Verbal/portal receipt; no auditable e-consent"),
        ControlBar("KYC / sanctions", 38, "No screening before binding"),
        ControlBar("Application & rules", 66, "Rules-based auto-accept; no model"),
        ControlBar("Conduct QA", 50, "10% manual sampling; no analytics QA"),
        ControlBar("Post-sale management", 76, "Sale record with annual review date"),
    ],
    remediations=[
        Remediation(1, "Enforce agent ready-to-sell at point of sale",
            "Block selling by representatives not currently licensed/appointed for the product, integrated with the "
            "licensing system (SOP-INS-005). Effort: 3 weeks.", "High"),
        Remediation(2, "Add KYC / sanctions screening",
            "Screen identity and sanctions before binding; route hits to Compliance. Effort: 4 weeks.", "High"),
        Remediation(3, "Capture auditable PDS e-consent & suitability e-signature",
            "Replace verbal PDS receipt with auditable digital consent and a signed suitability record. "
            "Effort: 3 weeks.", "High"),
        Remediation(4, "Move conduct QA to analytics at scale",
            "QA conduct across all interactions with call/interaction analytics, replacing 10% sampling, and add "
            "systematic vulnerability indicators. Effort: 5 weeks.", "Medium"),
        Remediation(5, "Add suitability decision support & predictive scoring",
            "Provide next-best-product decision support and a predictive risk score to widen straight-through "
            "binding. Effort: 5 weeks.", "Medium"),
    ],
    risk_impact=[("Ready-to-sell", 85), ("KYC / sanctions", 78), ("PDS e-consent", 72),
                 ("Conduct QA at scale", 65), ("Vulnerability detection", 58), ("Predictive scoring", 50)],
    projected_fit=91,
)

opt_phases = [
    Phase("1", "Suitability, readiness & consent", "Ready-to-sell, needs, e-consent", "blue",
          "Agent / CSR · Member Care · Licensing", "Steps 1–6", "6 steps + 1 decision"),
    Phase("2", "Application & screening", "Capture, KYC, submit, confirm", "green",
          "Agent / CSR · PAS · Underwriting · Compliance", "Steps 7–10", "4 steps + 1 decision"),
    Phase("3", "Issuance & post-sale analytics", "Pay, issue, QA analytics, record", "amber",
          "Agent / CSR · Policy Service · Quality", "Steps 11–14", "4 steps"),
]

opt_steps = [
    Step("1", "1", "Client contact initiated", "Agent / CSR",
         "Logged in CRM; prospect record; source code", "Day 0", "Standard", kind="trigger"),
    Step("2", "1", "Agent ready-to-sell check", "Licensing System / PAS",
         "Selling enabled only if licensed and appointed for the product", "Day 0",
         "NEW (v2.0) — point-of-sale gate"),
    Step("3", "1", "Needs analysis conducted", "Agent / CSR",
         "Needs, finances, coverage and risk via Needs Analysis Framework", "Day 0", "Standard"),
    Step("4", "1", "Suitability confirmed with decision support", "Agent / CSR",
         "Next-best-product decision support; suitability decision documented", "Day 0", "ENHANCED (v2.0)"),
    Step("5", "1", "Systematic vulnerability check", "Agent / Member Care",
         "Vulnerability indicators applied; handling per protocol", "Day 0",
         "NEW (v2.0) — conduct control"),
    Step("6", "1", "PDS provided with auditable e-consent", "Agent / CSR",
         "Digital consent captured with timestamp before application", "Day 0",
         "ENHANCED (v2.0) — evidencing"),
    Step("", "1", "", "", "", "", "Suitability gate", kind="decision", decision="Suitability clear?",
         branches=["Clear → proceed", "Concern → Member Care (Sec 6.2)"]),
    Step("7", "2", "Application details collected", "Agent / CSR",
         "Material information confirmed and recorded verbatim", "Day 0–1", "Standard"),
    Step("8", "2", "KYC / sanctions screening", "Underwriting / Compliance",
         "Identity and sanctions screened before binding", "Instant", "NEW (v2.0) — regulatory"),
    Step("9", "2", "Submit with predictive scoring; refer if needed", "PAS / Model Engine",
         "Rules plus predictive score widen straight-through binding; refer otherwise", "Instant",
         "ENHANCED (v2.0)"),
    Step("10", "2", "Terms and premium confirmed (read-back)", "Agent / CSR",
         "Final premium, options, start date repeated back; confirmation obtained", "Day 1–2", "Standard"),
    Step("11", "3", "First premium payment collected", "Agent / CSR / Payment Gateway",
         "Payment processed; mandate set up if instalment", "Day 2", "Standard"),
    Step("12", "3", "Policy issued and documents dispatched", "Policy Service Rep / PAS",
         "Policy number; documents per SOP-INS-004 timelines", "≤2 days", "Standard"),
    Step("13", "3", "Post-sale conduct QA via analytics", "Quality / Team Leader",
         "All interactions QA'd with call/interaction analytics; coaching automated", "Post-sale",
         "ENHANCED (v2.0) — QA at scale"),
    Step("14", "3", "CRM updated with policy outcome", "Agent / CSR",
         "Policy, product, premium and payment recorded; annual review date set", "Day 2", "Standard", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "Suitability, readiness & consent", "Steps 1–6 · v2.0 adds RTS & e-consent",
        ["Client", "Agent / CSR", "Licensing / Member Care"],
        [SwimNode("o1", "Agent / CSR", 0, "Client contact initiated", "logged in CRM"),
         SwimNode("o2", "Licensing / Member Care", 1, "Ready-to-sell check", "licensed & appointed", kind="new"),
         SwimNode("o3", "Agent / CSR", 2, "Needs analysis", "framework"),
         SwimNode("o4", "Agent / CSR", 3, "Suitability + decision support", "next-best-product", kind="enhanced"),
         SwimNode("o5", "Licensing / Member Care", 3, "Vulnerability check", "indicators", kind="new"),
         SwimNode("o6", "Agent / CSR", 4, "PDS with e-consent", "timestamped", kind="enhanced")],
        [SwimEdge("o1", "o2", dashed=True, kind="new", label="RTS"), SwimEdge("o2", "o3"),
         SwimEdge("o3", "o4"), SwimEdge("o4", "o5", dashed=True, kind="new"), SwimEdge("o5", "o6")],
        "v2.0 enforces a ready-to-sell gate, adds suitability decision support and systematic vulnerability checks, and captures auditable PDS e-consent."),
    SwimPhase("2", "Application & screening", "Steps 7–10 · KYC and predictive scoring",
        ["Agent / CSR", "PAS / Model", "Underwriting / Compliance"],
        [SwimNode("p1", "Agent / CSR", 0, "Collect application", "material info verbatim"),
         SwimNode("p2", "Underwriting / Compliance", 1, "KYC / sanctions screening", "before bind", kind="new"),
         SwimNode("p3", "PAS / Model", 1, "Submit + predictive score", "auto-accept / refer", kind="enhanced"),
         SwimNode("p4", "Underwriting / Compliance", 2, "Handle referral", "SLA"),
         SwimNode("p5", "Agent / CSR", 2, "Confirm terms & premium", "read-back")],
        [SwimEdge("p1", "p2", dashed=True, kind="new"), SwimEdge("p2", "p3"),
         SwimEdge("p3", "p5", label="auto"), SwimEdge("p3", "p4", label="ref"), SwimEdge("p4", "p5")],
        "v2.0 screens applications for KYC/sanctions and scores risk predictively before terms are confirmed by read-back."),
    SwimPhase("3", "Issuance & post-sale analytics", "Steps 11–14 · v2.0 QA at scale",
        ["Agent / CSR", "Policy Service / PAS", "Quality"],
        [SwimNode("q1", "Agent / CSR", 0, "Collect first payment", "receipt / mandate"),
         SwimNode("q2", "Policy Service / PAS", 1, "Issue & dispatch documents", "policy number"),
         SwimNode("q3", "Quality", 2, "Conduct QA via analytics", "all interactions", kind="enhanced"),
         SwimNode("q4", "Agent / CSR", 3, "Update CRM", "annual review date", kind="terminal")],
        [SwimEdge("q1", "q2"), SwimEdge("q2", "q4"),
         SwimEdge("q2", "q3", dashed=True, label="QA")],
        "v2.0 QA's conduct across all interactions with analytics rather than a 10% manual sample."),
]

optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Guidewire PolicyCenter Conduct-Aligned Sales Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-010"),
                ("Version", "2.0 (Optimised)"),
                ("Effective Date", "01 October 2026"),
                ("Supersedes", "v1.3 dated 01 February 2025"),
                ("Owner", "Sales Operations"),
                ("Approved By", "Chief Sales Officer"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-010 dated 18 June 2026"),
                ("Catalog Alignment Score", "91% (up from 70% in v1.3)"),
                ("Classification", "Internal Use Only"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v2.0",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-010. Alignment to the "
              "Guidewire PolicyCenter conduct-aligned sales catalog increased from 70% to 91%. Critical additions: "
              "agent ready-to-sell enforcement, KYC/sanctions screening, auditable PDS e-consent with a signed "
              "suitability record, conduct QA at scale via analytics, and systematic vulnerability detection."],
             ["NEW STEP (green) — step added to close a gap vs the PolicyCenter catalog",
              "ENHANCED (amber) — existing step updated with additional controls or automation"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines the channel-agnostic process for signing up a new "
             "client across all product lines through the agent or call centre channel. Version 2.0 incorporates "
             "optimisations from fit-gap analysis against the Guidewire PolicyCenter Conduct-Aligned Sales "
             "Best-Practice Catalog, achieving 91% alignment (up from 70% in v1.3)."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to all new policy sales by a licensed agent or call centre "
             "representative across personal and commercial product lines where a product-specific SOP does not "
             "supersede it, for telephone and face-to-face interactions."),
            ("banner", "new", "Scope extended: ready-to-sell enforcement, KYC/sanctions screening and PDS e-consent "
             "now apply to every sale before binding."),
            ("para", "This procedure does NOT cover digital direct sales (SOP-INS-001), group enrolments "
             "(SOP-INS-006), or renewals (SOP-INS-004)."),
        ]),
        DocSection("3. Authority Matrix", [
            ("table", ["Item", "First Authority", "Second Authority"],
             [["Standard sale (suitable)", "Agent / CSR", "—"],
              ["Suitability override", "Team Leader", "Client signed override"],
              ["Suitability doubt", "Member Care Rep", "Team Leader"],
              ["Backdated cover / substandard", "Team Leader", "Underwriting"],
              ["Vulnerable client", "Member Care Rep", "Compliance"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Customer Service Representative / Agent", "Runs needs/suitability; discloses terms with e-consent; completes application; confirms understanding."],
              ["Member Care Representative", "Second-level support; reviews suitability concerns; owns vulnerable-customer handling."],
              ["Policy Service Representative", "Processes applications in PAS; issues documents; sets up premium with Finance."],
              ["Team Leader / Sales Supervisor", "Approves exceptions; owns analytics-driven post-sale quality."]], {}),
        ]),
        DocSection("5. Conduct & Screening Controls (New Section — v2.0)", [
            ("banner", "crit", "New section. Required by the PolicyCenter catalog. Ready-to-sell, KYC/sanctions and "
             "PDS e-consent now gate every sale."),
            ("table", ["#", "Control", "Responsible", "Output / System", "Timeline"],
             [["C1", "Agent ready-to-sell check", "Licensing / PAS", "Selling blocked if not licensed/appointed", "At sale start"],
              ["C2", "KYC / sanctions screening", "Compliance", "Identity and watchlist screened before bind", "Pre-bind"],
              ["C3", "PDS e-consent & suitability e-signature", "Agent / Client", "Auditable consent and signed suitability", "Pre-application"]],
             {0: "new", 1: "new", 2: "new"}),
        ]),
        DocSection("6. Process Steps", [
            ("h3", "6.1 Suitability, Readiness & Consent"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "Client contact initiated", "Agent / CSR", "Logged in CRM; source code", "Day 0"],
              ["2", "Agent ready-to-sell check", "Licensing / PAS", "Selling enabled if eligible", "Day 0"],
              ["3", "Needs analysis conducted", "Agent / CSR", "Needs Analysis Framework", "Day 0"],
              ["4", "Suitability confirmed with decision support", "Agent / CSR", "Next-best-product; documented", "Day 0"],
              ["5", "Systematic vulnerability check", "Agent / Member Care", "Indicators applied; protocol", "Day 0"],
              ["6", "PDS provided with auditable e-consent", "Agent / CSR", "Timestamped digital consent", "Day 0"]],
             {1: "new", 3: "enh", 4: "new", 5: "enh"}),
            ("h3", "6.2 Application & Screening"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["7", "Application details collected", "Agent / CSR", "Material info verbatim", "Day 0–1"],
              ["8", "KYC / sanctions screening", "Compliance", "Screened before bind", "Instant"],
              ["9", "Submit with predictive scoring", "PAS / Model Engine", "STP binding widened; refer otherwise", "Instant"],
              ["10", "Terms and premium confirmed (read-back)", "Agent / CSR", "Confirmation obtained", "Day 1–2"]],
             {1: "new", 2: "enh"}),
            ("h3", "6.3 Issuance & Post-Sale Analytics"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["11", "First premium payment collected", "Agent / CSR / Gateway", "Receipt; mandate if instalment", "Day 2"],
              ["12", "Policy issued and documents dispatched", "Policy Service / PAS", "Per SOP-INS-004 timelines", "≤2 days"],
              ["13", "Post-sale conduct QA via analytics", "Quality / Team Leader", "All interactions QA'd; coaching", "Post-sale"],
              ["14", "CRM updated with policy outcome", "Agent / CSR", "Annual review date set", "Day 2"]],
             {2: "enh"}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Client Declines Recommended Product"),
            ("numbered", [
                "Agent records the declination and stated reason in CRM.",
                "If the client proceeds against recommendation, a suitability override form is completed and e-signed by the client.",
                "All overrides are reviewed by a Team Leader within 24 hours."]),
            ("h3", "7.2 Suitability Concern Identified"),
            ("numbered_from", 4, [
                "If suitability is uncertain, the interaction is paused and escalated to Member Care or a Team Leader.",
                "No product is sold where a material suitability doubt exists without second-level approval."]),
            ("h3", "7.3 Vulnerable or Financially Distressed Client (Enhanced — v2.0)"),
            ("banner", "enh", "Systematic vulnerability indicators now support representative judgement in identifying at-risk clients."),
            ("numbered_from", 6, [
                "Vulnerable-customer protocols apply; the representative does not proceed if the product may not be in the client's best interest.",
                "The client is referred to financial counselling or government assistance where appropriate."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["CRM (Salesforce)", "Contact, needs analysis, suitability and post-sale records", "All roles"],
              ["Policy Administration System (PAS)", "Application processing, issuance, ready-to-sell gate", "CSR, Policy Service Rep"],
              ["Agent Portal (Meridian Connect)", "Quotation, application and payment for the agent channel", "Agent"],
              ["KYC / Sanctions Tool", "Identity and sanctions screening", "Compliance"],
              ["E-Consent / E-Signature", "PDS consent and suitability sign-off", "Agent, Client"],
              ["Call Recording & Interaction Analytics (NICE)", "Conduct QA at scale and coaching", "Quality, Team Leader"],
              ["Payment Gateway", "Premium collection at point of sale", "Agent, CSR"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v2.0: ready-to-sell enforcement, KYC/sanctions, PDS e-consent, "
             "analytics-based conduct QA and vulnerability detection."),
            ("bullets", [
                "Ready-to-sell gate: no selling by an unlicensed or unappointed representative.",
                "KYC/sanctions: identity and watchlists screened before binding.",
                "Evidenced consent: PDS e-consent and signed suitability record captured before application.",
                "Vulnerability: systematic indicators support fair treatment of at-risk clients.",
                "Conduct QA: all interactions reviewed via analytics, replacing 10% sampling.",
                "Suitability: documented decision with override governance.",
                "Immutable audit trail: needs, consent, screening, sale and QA events logged."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v1.3 Target", "v2.0 Target", "Measurement"],
             [["Suitability compliance", "100%", "100%", "Needs analysis + suitability on record"],
              ["Ready-to-sell breaches", "N/A (new)", "Zero (blocked)", "Gate enforcement"],
              ["PDS e-consent capture", "Verbal/portal", "100% auditable", "E-consent records"],
              ["Conduct QA coverage", "10% sample", "100% via analytics", "Interactions QA'd"],
              ["Post-sale quality score", "≥85%", "≥90%", "Conduct standards met"],
              ["Vulnerable-customer complaints", "Zero upheld", "Zero upheld", "Complaints register"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["1.3", "01 Feb 2025", "M. Reyes, Compliance", "Updated PDS delivery requirements; aligned KPIs to Salesforce reporting"],
              ["2.0", "01 Oct 2026", "M. Reyes, Compliance",
               "OPTIMISED: ready-to-sell enforcement; KYC/sanctions screening; PDS e-consent & suitability "
               "e-signature; analytics-based conduct QA; vulnerability detection; catalog alignment 70% → 91%"]], {}),
        ]),
    ],
)

package = SopPackage(
    meta=meta, phases=phases, steps=steps, authority=authority, swim_phases=swim_phases,
    n_phases=3, n_steps=12, n_roles=4, n_gateways=2,
    fitgap=fitgap,
    opt_phases=opt_phases, opt_steps=opt_steps, opt_swim_phases=opt_swim_phases,
    opt_n_phases=3, opt_n_steps=14, opt_n_gateways=2, opt_fit=91,
    optimised_doc=optimised_doc,
    swim_cover_tags="Suitability · Application · Issuance · Post-sale · Exception handling",
    hierarchy_cover_sub="Phase breakdown with sales-conduct tracks, suitability authority, and exception paths",
)
