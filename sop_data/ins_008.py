"""SOP-INS-008 — Auto and Home Insurance Sales (Meridian Insurance Group).

Fit-gap vs the Guidewire PolicyCenter agent-channel personal-lines catalog.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Guidewire PolicyCenter — Agent-Channel Personal Lines Catalog"
CATALOG_SHORT = "Guidewire PolicyCenter"

meta = Meta(
    sop_id="SOP-INS-008", slug="Auto_and_Home_Sales",
    title="Auto and Home Insurance Sales", short_title="Auto & home sales",
    version="2.2", owner="Personal Lines Distribution",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="3.0", effective_date="01 October 2026",
    supersedes="v2.2 dated 01 March 2025", approved_by="Head of Personal Lines",
    classification="Internal Use Only",
)

phases = [
    Phase("1", "Prospect & needs analysis", "Source, contact, needs, bundle", "blue",
          "Agent · Customer Service", "Steps 1–4", "4 steps"),
    Phase("2", "Quotation", "Rate, present, underwrite", "green",
          "Agent · Rating Engine · Underwriting", "Steps 5–8", "4 steps + 1 decision"),
    Phase("3", "Conversion & issuance", "Finalise, pay, issue, fulfil", "amber",
          "Agent · Payment Gateway · PAS", "Steps 9–13", "5 steps"),
]

steps = [
    Step("1", "1", "Prospect identified (referral, campaign, inbound)", "Agent / Customer Service",
         "Prospect record created in CRM; source code recorded", "Day 0", "Pipeline entry", kind="trigger"),
    Step("2", "1", "Initial contact made and appointment scheduled", "Agent",
         "Contact within 1 business day of lead assignment; appointment confirmed", "Day 0–1", "Contact SLA"),
    Step("3", "1", "Needs analysis conducted", "Agent",
         "Current insurer, coverage gaps, claims history and risk characteristics; notes in CRM", "Day 1–3", "Needs analysis"),
    Step("4", "1", "Multi-product opportunity assessed", "Agent",
         "Bundled auto + home discount opportunity presented if applicable", "Day 1–3", "Cross-sell"),
    Step("5", "2", "Application data entered into agent portal", "Agent",
         "Vehicle/property, personal and claims history entered; address verified", "Day 3", "Application capture"),
    Step("6", "2", "Rating engine generates premium", "Agent Portal / Rating Engine",
         "Instant quote for auto-accept; referral cases routed to Underwriting", "Instant", "Auto-accept rules"),
    Step("7", "2", "Quote presented and explained to prospect", "Agent",
         "Benefits, exclusions, excess and payment options explained per disclosure obligations", "Day 3", "Disclosure obligations"),
    Step("8", "2", "Underwriting review (if referred)", "Underwriter",
         "Decision within 2 business hours; agent notified of outcome and revised terms", "≤2 hours", "Referral SLA"),
    Step("", "2", "", "", "", "", "Rating + underwriter outcome", kind="decision", decision="Auto-accept or referral?",
         branches=["Auto-accept → conversion", "Referral → underwriter (high-risk hold, Sec 6.2)"]),
    Step("9", "3", "Prospect agrees; application finalised and signed", "Agent / Prospect",
         "Application signed; agent confirms scope of cover and prospect understanding", "Day 3–5", "Sales conduct"),
    Step("10", "3", "First premium payment collected", "Agent / Payment Gateway",
         "Payment processed via agent portal; receipt issued", "Day 5", "Payment"),
    Step("11", "3", "Policy issued in PAS", "Agent Portal / PAS",
         "Policy number generated; coverage effective from agreed start date", "Day 5", "Issuance"),
    Step("12", "3", "Policy documents dispatched to policyholder", "PAS (auto)",
         "Schedule, certificate and PDS dispatched within 2 business days", "≤2 days", "Document SLA"),
    Step("13", "3", "CRM updated with sale outcome", "Agent",
         "Policy number, premium, product type and commission logged", "Day 5", "Sale logged", kind="complete"),
]

authority = [
    AuthorityRow("Auto-accept (rules-clear)", "Rating Engine", "—"),
    AuthorityRow("Standard referral", "Underwriter", "—"),
    AuthorityRow("High-risk property/vehicle", "Senior Underwriter", "Underwriter"),
    AuthorityRow("Non-standard terms / exclusions", "Senior Underwriter", "—"),
    AuthorityRow("Misrepresentation (void/voidable)", "Compliance", "Underwriting Manager"),
]

swim_phases = [
    SwimPhase("1", "Prospect & needs analysis", "Steps 1–4 · source to bundle",
        ["Prospect", "Agent", "Customer Service"],
        [SwimNode("s1", "Agent", 0, "Prospect identified", "source code"),
         SwimNode("s2", "Agent", 1, "Contact & appointment", "≤1 business day"),
         SwimNode("s3", "Agent", 2, "Needs analysis", "gaps · claims history"),
         SwimNode("s4", "Agent", 3, "Multi-product assessment", "bundle discount")],
        [SwimEdge("s1", "s2"), SwimEdge("s2", "s3"), SwimEdge("s3", "s4")],
        "Leads are contacted within a day; needs analysis identifies coverage gaps and auto+home bundling opportunities."),
    SwimPhase("2", "Quotation", "Steps 5–8 · rate, present, underwrite",
        ["Agent", "Rating Engine / Portal", "Underwriting"],
        [SwimNode("a1", "Agent", 0, "Enter application", "address verified"),
         SwimNode("a2", "Rating Engine / Portal", 1, "Rating engine quote", "auto-accept / refer", kind="decision"),
         SwimNode("a3", "Agent", 2, "Present & explain quote", "disclosure"),
         SwimNode("a4", "Underwriting", 2, "Underwriting review", "referred · ≤2h"),
         SwimNode("a5", "Underwriting", 3, "High-risk hold", "no verbal bind", kind="exception")],
        [SwimEdge("a1", "a2"), SwimEdge("a2", "a3", label="auto"), SwimEdge("a2", "a4", label="ref"),
         SwimEdge("a4", "a3"), SwimEdge("a4", "a5", dashed=True, kind="exception", label="hi-risk")],
        "The rating engine auto-accepts or refers; high-risk applications are held for written underwriting approval before any bind."),
    SwimPhase("3", "Conversion & issuance", "Steps 9–13 · finalise to fulfil",
        ["Prospect", "Agent", "Payment / PAS"],
        [SwimNode("d1", "Agent", 0, "Finalise & sign application", "scope confirmed"),
         SwimNode("d2", "Payment / PAS", 1, "Collect first payment", "receipt issued"),
         SwimNode("d3", "Payment / PAS", 2, "Issue policy in PAS", "policy number"),
         SwimNode("d4", "Payment / PAS", 3, "Dispatch documents", "schedule · cert · PDS"),
         SwimNode("d5", "Agent", 4, "Update CRM", "commission logged", kind="terminal")],
        [SwimEdge("d1", "d2"), SwimEdge("d2", "d3"), SwimEdge("d3", "d4"), SwimEdge("d4", "d5")],
        "On agreement the application is signed and paid, the policy issues, documents dispatch, and the sale is logged in CRM."),
]

fg_items = [
    FitItem("1", "Lead capture & contact SLA", "FIT",
        "CRM lead capture with a 1-day contact SLA aligns with PolicyCenter agent lead management.",
        "Agent / Customer Service", "GW-PC-LED-01", "p1"),
    FitItem("2", "Needs analysis", "PARTIAL",
        "Needs are discussed and noted, but not captured as a structured, auditable suitability record as the "
        "catalog requires for conduct compliance.",
        "Agent", "GW-PC-SUI-01", "p1"),
    FitItem("3", "Multi-product cross-sell", "FIT",
        "Auto+home bundling assessment aligns with PolicyCenter account-rounding/cross-sell prompts.",
        "Agent", "GW-PC-XSL-01", "p1"),
    FitItem("4", "Agent ready-to-sell enforcement", "GAP",
        "Licensing is a stated prerequisite but not enforced at point of sale. PolicyCenter blocks quote/bind for "
        "agents not currently licensed and appointed for the product/territory.",
        "Agent / PAS", "GW-PC-RTS-01", "p1"),
    FitItem("5", "Application capture & address verify", "FIT",
        "Portal capture with address verification aligns with PolicyCenter submission intake.",
        "Agent", "GW-PC-SUB-01", "p2"),
    FitItem("6", "Risk-data enrichment", "GAP",
        "Rating uses entered data only. PolicyCenter enriches with property/flood, VIN and prior-claims data (and "
        "a telematics option for auto) for pricing accuracy and anti-selection control.",
        "Rating Engine", "GW-PC-QTE-08", "p2"),
    FitItem("7", "Auto-accept rules engine", "PARTIAL",
        "Rules-based auto-accept present, but no predictive risk-model score to widen straight-through binding.",
        "Rating Engine", "GW-PC-UW-02", "p2"),
    FitItem("8", "Disclosure at quote", "FIT",
        "Benefits, exclusions and excess explained per disclosure obligations align with PolicyCenter conduct controls.",
        "Agent", "GW-PC-DIS-01", "p2"),
    FitItem("9", "Underwriting referral & SLAs", "FIT",
        "2-hour referral with revised-terms handling aligns with PolicyCenter referral workflow.",
        "Underwriter", "GW-PC-UW-03", "p2"),
    FitItem("10", "KYC / application-fraud screening", "GAP",
        "No KYC/sanctions or application-fraud screening at sale; misrepresentation is only handled post-issuance. "
        "PolicyCenter screens and fraud-scores applications before binding.",
        "Underwriting / Compliance", "GW-PC-FR-01", "p2"),
    FitItem("11", "Signed application & e-signature", "PARTIAL",
        "Application is 'digital or paper'; the catalog mandates an auditable e-signature with a captured disclosure "
        "acknowledgement before issuance.",
        "Agent / Prospect", "GW-PC-ISS-04", "p3"),
    FitItem("12", "Payment & instant issuance", "FIT",
        "Portal payment and instant issuance with effective date align with PolicyCenter billing and issuance.",
        "Agent / Payment Gateway", "GW-PC-ISS-01", "p3"),
    FitItem("13", "Document dispatch & sale logging", "FIT",
        "2-day document dispatch and CRM sale logging align with PolicyCenter fulfilment and reporting.",
        "PAS / Agent", "GW-PC-ISS-06", "p3"),
]

fitgap = FitGap(
    overall_fit=68, partial_pct=16, fits=8, gaps=3, partials=3,
    steps_analysed=13, phases_count=3,
    summary_line="Overall alignment of SOP-INS-008 against the Guidewire PolicyCenter agent-channel catalog",
    metrics=[
        ("Steps analysed", "13 steps across 3 phases"),
        ("Fits confirmed", "8 steps aligned to catalog"),
        ("Gaps identified", "3 steps — remediation required"),
        ("Partial fits", "3 steps — enhancement recommended"),
        ("Highest risk area", "No ready-to-sell enforcement"),
        ("Pricing gap", "No risk-data enrichment / telematics"),
        ("Ref standard", "Guidewire PolicyCenter Agent Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Needs", 68, ""),
        FitPhaseBar("Phase 2", "Quotation", 60, ""),
        FitPhaseBar("Phase 3", "Issuance", 80, ""),
        FitPhaseBar("Screening /", "data", 46, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 68, "Prospect & needs"),
        PhaseScoreCard("Phase 2", 60, "Quotation"),
        PhaseScoreCard("Phase 3", 80, "Conversion & issue"),
        PhaseScoreCard("Screening", 46, "RTS, KYC & data"),
    ],
    detail_slides=[
        ("Phase 1 — Prospect & needs analysis", "Steps 1–4 vs Guidewire PolicyCenter agent catalog", ["p1"]),
        ("Phase 2 — Quotation", "Steps 5–10 vs Guidewire PolicyCenter agent catalog", ["p2"]),
        ("Phase 3 — Conversion & issuance", "Steps 11–13 vs Guidewire PolicyCenter agent catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — PROSPECT & NEEDS ANALYSIS"),
            ("p2", "PHASE 2 — QUOTATION"),
            ("p3", "PHASE 3 — CONVERSION & ISSUANCE")],
    critical_missing=[
        CriticalGap("Agent ready-to-sell enforcement",
            "Licensing is a stated prerequisite but not enforced in the portal. The catalog blocks quote/bind for "
            "agents not currently licensed and appointed for the product and territory (links to SOP-INS-005)."),
        CriticalGap("Third-party risk-data enrichment",
            "Rating relies on entered data only, with no property/flood, VIN or prior-claims enrichment and no "
            "telematics option for auto — a pricing-accuracy and anti-selection gap."),
        CriticalGap("KYC / application-fraud screening",
            "No identity/sanctions or application-fraud screening at sale; misrepresentation is only addressed "
            "after issuance, increasing fraud and conduct exposure."),
        CriticalGap("Mandatory e-signature & suitability",
            "Application acceptance is 'digital or paper' with no mandated e-signature or structured suitability "
            "record, a conduct and dispute exposure."),
    ],
    radar=[("Lead & needs", 70), ("Ready-to-sell", 40), ("Risk data", 46), ("Auto-accept", 60),
           ("KYC / fraud", 42), ("Issuance", 82), ("Conduct / e-sign", 55)],
    control_bars=[
        ControlBar("Lead & needs", 70, "CRM capture and needs analysis"),
        ControlBar("Ready-to-sell", 40, "Licensing not enforced at point of sale"),
        ControlBar("Risk-data enrichment", 46, "Entered data only; no enrichment/telematics"),
        ControlBar("Auto-accept rules", 60, "Rules-based; no predictive model"),
        ControlBar("KYC / fraud screening", 42, "No screening before binding"),
        ControlBar("Issuance & fulfilment", 82, "Instant issuance with 2-day documents"),
        ControlBar("Conduct / e-signature", 55, "Disclosure good; e-signature not mandated"),
    ],
    remediations=[
        Remediation(1, "Enforce agent ready-to-sell at point of sale",
            "Block quote/bind for agents not currently licensed and appointed for the product/territory, integrated "
            "with the licensing system (SOP-INS-005). Effort: 3 weeks.", "High"),
        Remediation(2, "Enrich rating with risk data & telematics",
            "Append property/flood, VIN and prior-claims data and offer a telematics rating option for auto. "
            "Effort: 6 weeks (data partners).", "High"),
        Remediation(3, "Add KYC / application-fraud screening",
            "Screen identity/sanctions and fraud-score applications before binding; route hits to Compliance. "
            "Effort: 4 weeks.", "High"),
        Remediation(4, "Mandate e-signature & structured suitability",
            "Require an auditable e-signature with captured disclosure acknowledgement and a structured suitability "
            "record before issuance. Effort: 3 weeks.", "Medium"),
        Remediation(5, "Add predictive risk scoring",
            "Layer a predictive risk-model score over the rules engine to widen straight-through binding for "
            "low-risk applications. Effort: 5 weeks.", "Medium"),
    ],
    risk_impact=[("Ready-to-sell", 85), ("KYC / fraud", 80), ("Risk-data enrichment", 75),
                 ("E-signature / suitability", 62), ("Predictive scoring", 55), ("Telematics", 50)],
    projected_fit=91,
)

opt_phases = [
    Phase("1", "Prospect, readiness & needs", "Ready-to-sell, needs, bundle", "blue",
          "Agent · Customer Service · Licensing", "Steps 1–5", "5 steps"),
    Phase("2", "Quotation & screening", "Enrich, rate, screen, underwrite", "green",
          "Agent · Rating · Underwriting · Compliance", "Steps 6–11", "6 steps + 1 decision"),
    Phase("3", "Conversion & issuance", "E-sign, pay, issue, fulfil", "amber",
          "Agent · Payment Gateway · PAS", "Steps 12–16", "5 steps"),
]

opt_steps = [
    Step("1", "1", "Prospect identified (referral, campaign, inbound)", "Agent / Customer Service",
         "Prospect record in CRM; source code", "Day 0", "Standard", kind="trigger"),
    Step("2", "1", "Agent ready-to-sell check", "Licensing System / PAS",
         "Quote/bind enabled only if agent is currently licensed and appointed", "Day 0",
         "NEW (v3.0) — point-of-sale gate"),
    Step("3", "1", "Initial contact and appointment", "Agent",
         "Contact within 1 business day; appointment confirmed", "Day 0–1", "Standard"),
    Step("4", "1", "Structured needs analysis & suitability", "Agent",
         "Auditable suitability record captured; coverage gaps identified", "Day 1–3", "ENHANCED (v3.0)"),
    Step("5", "1", "Multi-product opportunity assessed", "Agent",
         "Bundled auto+home discount presented if applicable", "Day 1–3", "Standard"),
    Step("6", "2", "Application entered with risk-data enrichment", "Agent / Rating Engine",
         "Property/flood, VIN and prior-claims data appended; address verified", "Day 3",
         "NEW (v3.0) — pricing accuracy"),
    Step("7", "2", "KYC / application-fraud screening", "Underwriting / Compliance",
         "Identity/sanctions screened and application fraud-scored before binding", "Instant",
         "NEW (v3.0) — fraud & conduct control"),
    Step("8", "2", "Rating engine quote with predictive score", "Rating + Model Engine",
         "Rules plus predictive score widen straight-through binding; refer otherwise", "Instant",
         "ENHANCED (v3.0)"),
    Step("9", "2", "Quote presented and explained", "Agent",
         "Benefits, exclusions, excess and payment options per disclosure", "Day 3", "Standard"),
    Step("10", "2", "Underwriting review (if referred)", "Underwriter",
         "Decision within 2 business hours; revised terms communicated", "≤2 hours", "Standard"),
    Step("11", "2", "Telematics rating option (auto)", "Agent / Rating Engine",
         "Opt-in usage-based rating offered for auto with safe-driving discount", "Day 3", "NEW (v3.0)"),
    Step("", "2", "", "", "", "", "Outcome", kind="decision", decision="Auto-accept or referral?",
         branches=["Auto-accept → conversion", "Referral / high-risk → underwriter (Sec 6.2)"]),
    Step("12", "3", "Application finalised with mandatory e-signature", "Agent / Prospect",
         "Auditable e-signature and disclosure acknowledgement captured", "Day 3–5",
         "ENHANCED (v3.0) — conduct control"),
    Step("13", "3", "First premium payment collected", "Agent / Payment Gateway",
         "Payment via portal; receipt issued", "Day 5", "Standard"),
    Step("14", "3", "Policy issued in PAS", "Agent Portal / PAS",
         "Policy number; coverage effective from start date", "Day 5", "Standard"),
    Step("15", "3", "Policy documents dispatched", "PAS (auto)",
         "Schedule, certificate, PDS within 2 business days", "≤2 days", "Standard"),
    Step("16", "3", "CRM updated with sale outcome", "Agent",
         "Policy number, premium, product and commission logged", "Day 5", "Standard", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "Prospect, readiness & needs", "Steps 1–5 · v3.0 adds ready-to-sell gate",
        ["Prospect", "Agent", "Licensing System"],
        [SwimNode("o1", "Agent", 0, "Prospect identified", "source code"),
         SwimNode("o2", "Licensing System", 1, "Ready-to-sell check", "licensed & appointed", kind="new"),
         SwimNode("o3", "Agent", 2, "Contact & appointment", "≤1 business day"),
         SwimNode("o4", "Agent", 3, "Structured needs & suitability", "auditable record", kind="enhanced"),
         SwimNode("o5", "Agent", 4, "Multi-product assessment", "bundle discount")],
        [SwimEdge("o1", "o2", dashed=True, kind="new", label="RTS"), SwimEdge("o2", "o3"),
         SwimEdge("o3", "o4"), SwimEdge("o4", "o5")],
        "v3.0 enforces a ready-to-sell gate before any selling activity and captures a structured suitability record."),
    SwimPhase("2", "Quotation & screening", "Steps 6–11 · enrichment, KYC, model",
        ["Agent", "Rating / Model", "Underwriting / Compliance"],
        [SwimNode("p1", "Agent", 0, "Enter application + enrichment", "property · VIN · claims", kind="new"),
         SwimNode("p2", "Underwriting / Compliance", 1, "KYC / fraud screening", "before bind", kind="new"),
         SwimNode("p3", "Rating / Model", 1, "Quote + predictive score", "auto-accept / refer", kind="enhanced"),
         SwimNode("p4", "Agent", 2, "Present & explain quote", "disclosure"),
         SwimNode("p5", "Underwriting / Compliance", 2, "Underwriting review", "referred · ≤2h"),
         SwimNode("p6", "Rating / Model", 3, "Telematics option (auto)", "usage-based", kind="new")],
        [SwimEdge("p1", "p2", dashed=True, kind="new"), SwimEdge("p2", "p3"),
         SwimEdge("p3", "p4", label="auto"), SwimEdge("p3", "p5", label="ref"),
         SwimEdge("p4", "p6", dashed=True, kind="new", label="telem")],
        "v3.0 enriches rating, screens applications for KYC/fraud, scores risk predictively, and offers a telematics option."),
    SwimPhase("3", "Conversion & issuance", "Steps 12–16 · v3.0 mandates e-signature",
        ["Prospect", "Agent", "Payment / PAS"],
        [SwimNode("q1", "Agent", 0, "Finalise + e-signature", "audited acceptance", kind="enhanced"),
         SwimNode("q2", "Payment / PAS", 1, "Collect first payment", "receipt"),
         SwimNode("q3", "Payment / PAS", 2, "Issue policy in PAS", "policy number"),
         SwimNode("q4", "Payment / PAS", 3, "Dispatch documents", "schedule · cert · PDS"),
         SwimNode("q5", "Agent", 4, "Update CRM", "commission logged", kind="terminal")],
        [SwimEdge("q1", "q2"), SwimEdge("q2", "q3"), SwimEdge("q3", "q4"), SwimEdge("q4", "q5")],
        "v3.0 mandates an auditable e-signature acceptance before payment and issuance."),
]

optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Guidewire PolicyCenter Agent-Channel Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-008"),
                ("Version", "3.0 (Optimised)"),
                ("Effective Date", "01 October 2026"),
                ("Supersedes", "v2.2 dated 01 March 2025"),
                ("Owner", "Personal Lines Distribution"),
                ("Approved By", "Head of Personal Lines"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-008 dated 18 June 2026"),
                ("Catalog Alignment Score", "91% (up from 68% in v2.2)"),
                ("Classification", "Internal Use Only"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v3.0",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-008. Alignment to the "
              "Guidewire PolicyCenter agent-channel catalog increased from 68% to 91%. Critical additions: agent "
              "ready-to-sell enforcement, third-party risk-data enrichment with telematics, KYC/application-fraud "
              "screening, mandatory e-signature with structured suitability, and predictive risk scoring."],
             ["NEW STEP (green) — step added to close a gap vs the PolicyCenter catalog",
              "ENHANCED (amber) — existing step updated with additional controls or automation"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines the process for quoting and converting prospects into "
             "auto and home policyholders through the Meridian agent channel. Version 3.0 incorporates optimisations "
             "from fit-gap analysis against the Guidewire PolicyCenter Agent-Channel Personal Lines Catalog, "
             "achieving 91% alignment (up from 68% in v2.2)."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to agent-sourced and inbound auto and home enquiries, new business, "
             "cross-sales and account rounding, via the agent portal or telephony channel."),
            ("banner", "new", "Scope extended: a ready-to-sell gate and KYC/application-fraud screening now apply to "
             "every agent-assisted sale before binding."),
            ("para", "This procedure does NOT cover online direct sales (SOP-INS-001), commercial vehicle fleets, or "
             "landlord insurance beyond standard residential."),
        ]),
        DocSection("3. Underwriting Authority Matrix", [
            ("table", ["Decision", "First Authority", "Second Authority"],
             [["Auto-accept (rules + model clear)", "Rating + Model Engine", "—"],
              ["Standard referral", "Underwriter", "—"],
              ["High-risk property/vehicle", "Senior Underwriter", "Underwriter"],
              ["Non-standard terms / exclusions", "Senior Underwriter", "—"],
              ["Misrepresentation (void/voidable)", "Compliance", "Underwriting Manager"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Personal Lines Agent", "Identifies prospects; runs needs/suitability; presents options; completes and e-signs application."],
              ["Underwriter", "Reviews referrals; sets non-standard terms; approves high-risk cases in writing."],
              ["Compliance", "Owns KYC/sanctions and application-fraud dispositions and misrepresentation handling."],
              ["Customer Service", "Handles inbound enquiries and channel-assisted applications."]], {}),
        ]),
        DocSection("5. Readiness & Screening (New Section — v3.0)", [
            ("banner", "crit", "New section. Required by the PolicyCenter catalog. A ready-to-sell gate and "
             "KYC/application-fraud screening now precede any bind."),
            ("table", ["#", "Control", "Responsible", "Output / System", "Timeline"],
             [["R1", "Agent ready-to-sell check", "Licensing / PAS", "Quote/bind blocked if not licensed/appointed", "At sale start"],
              ["R2", "KYC / sanctions screening", "Compliance", "Identity and watchlist screened before bind", "Pre-bind"],
              ["R3", "Application-fraud scoring", "Underwriting", "Application fraud-scored; misrepresentation flagged", "Pre-bind"],
              ["R4", "Mandatory e-signature & suitability", "Agent / Prospect", "Audited e-signature and suitability record", "Pre-issue"]],
             {0: "new", 1: "new", 2: "new", 3: "new"}),
        ]),
        DocSection("6. Process Steps", [
            ("h3", "6.1 Prospect, Readiness & Needs"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "Prospect identified", "Agent / Customer Service", "CRM record; source code", "Day 0"],
              ["2", "Agent ready-to-sell check", "Licensing / PAS", "Quote/bind enabled if eligible", "Day 0"],
              ["3", "Initial contact and appointment", "Agent", "Contact within 1 business day", "Day 0–1"],
              ["4", "Structured needs analysis & suitability", "Agent", "Auditable suitability record", "Day 1–3"],
              ["5", "Multi-product opportunity assessed", "Agent", "Bundle discount presented", "Day 1–3"]],
             {1: "new", 3: "enh"}),
            ("h3", "6.2 Quotation & Screening"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["6", "Application entered with risk-data enrichment", "Agent / Rating Engine", "Property/VIN/claims appended", "Day 3"],
              ["7", "KYC / application-fraud screening", "Compliance", "Screened and fraud-scored before bind", "Instant"],
              ["8", "Rating engine quote with predictive score", "Rating + Model Engine", "STP binding widened", "Instant"],
              ["9", "Quote presented and explained", "Agent", "Disclosure obligations met", "Day 3"],
              ["10", "Underwriting review (if referred)", "Underwriter", "Decision within 2 business hours", "≤2 hours"],
              ["11", "Telematics rating option (auto)", "Agent / Rating Engine", "Usage-based discount opt-in", "Day 3"]],
             {0: "new", 1: "new", 2: "enh", 5: "new"}),
            ("h3", "6.3 Conversion & Issuance"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["12", "Application finalised with mandatory e-signature", "Agent / Prospect", "Audited e-signature & disclosure", "Day 3–5"],
              ["13", "First premium payment collected", "Agent / Payment Gateway", "Receipt issued", "Day 5"],
              ["14", "Policy issued in PAS", "Agent Portal / PAS", "Policy number; effective date", "Day 5"],
              ["15", "Policy documents dispatched", "PAS", "Schedule, cert, PDS within 2 days", "≤2 days"],
              ["16", "CRM updated with sale outcome", "Agent", "Premium, product, commission logged", "Day 5"]],
             {0: "enh"}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Prospect Declines Quote"),
            ("numbered", [
                "Agent records declination with reason code in CRM; follow-up task set for 30 days.",
                "If price was the objection, the agent may request a pricing review where the risk profile warrants an exception."]),
            ("h3", "7.2 High-Risk Property or Vehicle"),
            ("numbered_from", 3, [
                "Applications outside standard guidelines are held for underwriting review before any verbal commitment.",
                "The agent must not communicate binding confirmation until written underwriting approval is received."]),
            ("h3", "7.3 Misrepresentation (Enhanced — v3.0)"),
            ("banner", "enh", "Application-fraud scoring now flags likely misrepresentation before binding, not only after issuance."),
            ("numbered_from", 5, [
                "Pre-bind: a high fraud score routes the application to Compliance before any cover is bound.",
                "Post-issuance: material misrepresentation is notified to Underwriting and Compliance within 1 business day.",
                "Compliance determines whether the policy is void or voidable and advises required action."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["Agent Portal (Meridian Connect)", "Quotation, submission, issuance, documents", "Agent"],
              ["Policy Administration System (PAS)", "Policy record, documents, endorsements, ready-to-sell gate", "Agent, Customer Service, Underwriting"],
              ["CRM (Salesforce)", "Prospect/customer records and pipeline", "Agent, Customer Service"],
              ["Rating + Model Engine", "Premium calculation, enrichment, predictive scoring, telematics", "Automated"],
              ["KYC / Fraud Screening", "Identity/sanctions and application-fraud scoring", "Compliance, Underwriting"],
              ["E-Signature Service", "Audited application acceptance", "Agent, Prospect"],
              ["Payment Gateway", "Premium collection and receipts", "Agent, Customer Service"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v3.0: ready-to-sell enforcement, risk-data enrichment, "
             "KYC/fraud screening, e-signature and predictive scoring."),
            ("bullets", [
                "Ready-to-sell gate: no quote/bind by an unlicensed or unappointed agent.",
                "Risk-data enrichment: property/flood, VIN and claims data improve pricing.",
                "KYC/fraud screening: identity, sanctions and fraud scored before binding.",
                "E-signature: audited acceptance with disclosure acknowledgement before issuance.",
                "Suitability: structured needs/suitability record captured for conduct compliance.",
                "Predictive scoring: rules-engine binding refined by a governed risk model.",
                "Immutable audit trail: needs, screening, quote, acceptance and issuance events logged."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v2.2 Target", "v3.0 Target", "Measurement"],
             [["Lead-to-quote", "≥70%", "≥72%", "Quotes per assigned lead"],
              ["Quote-to-bind", "≥28%", "≥32%", "Bound / quoted"],
              ["Cross-product attach", "≥35%", "≥40%", "Auto with home attached"],
              ["Ready-to-sell breaches", "N/A (new)", "Zero (blocked)", "Gate enforcement"],
              ["E-signature acceptance", "N/A (new)", "≥90%", "E-sign vs paper"],
              ["Sales-conduct complaints", "Zero upheld /1,000", "Zero upheld /1,000", "Complaints register"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["2.2", "01 Mar 2025", "B. Osei, Underwriting", "Aligned to revised product disclosure obligations; updated payment gateway steps"],
              ["3.0", "01 Oct 2026", "B. Osei, Underwriting",
               "OPTIMISED: ready-to-sell enforcement; risk-data enrichment & telematics; KYC/fraud screening; "
               "mandatory e-signature & suitability; predictive scoring; catalog alignment 68% → 91%"]], {}),
        ]),
    ],
)

package = SopPackage(
    meta=meta, phases=phases, steps=steps, authority=authority, swim_phases=swim_phases,
    n_phases=3, n_steps=13, n_roles=4, n_gateways=2,
    fitgap=fitgap,
    opt_phases=opt_phases, opt_steps=opt_steps, opt_swim_phases=opt_swim_phases,
    opt_n_phases=3, opt_n_steps=16, opt_n_gateways=2, opt_fit=91,
    optimised_doc=optimised_doc,
    swim_cover_tags="Needs · Quotation · Underwriting · Issuance · Exception handling",
    hierarchy_cover_sub="Phase breakdown with agent sales tracks, underwriting authority, and exception paths",
)
