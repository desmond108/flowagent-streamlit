"""SOP-INS-004 — Prospect-to-Issue (Meridian Insurance Group).

Fit-gap vs the Guidewire PolicyCenter new-business & renewal underwriting catalog.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Guidewire PolicyCenter — New Business & Renewal Underwriting Catalog"
CATALOG_SHORT = "Guidewire PolicyCenter"

meta = Meta(
    sop_id="SOP-INS-004", slug="Prospect_to_Issue",
    title="Prospect-to-Issue", short_title="Prospect-to-issue",
    version="2.1", owner="Member Services — Policy Operations",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="3.0", effective_date="01 October 2026",
    supersedes="v2.1 dated 01 January 2025", approved_by="Chief Underwriting Officer",
    classification="Internal Use Only",
)

phases = [
    Phase("1", "Prospect qualification & quote", "Enquiry, needs, quote", "blue",
          "Prospect · Member Services · Rating", "Steps 1–4", "4 steps"),
    Phase("2", "Underwriting assessment", "Rules engine, referral, decision", "green",
          "PAS · Underwriter · Actuarial", "Steps 5–7", "3 steps + 1 decision"),
    Phase("3", "Acceptance & issuance", "Terms, payment, issuance, fulfilment", "amber",
          "Applicant · Member Services · PAS · Broker", "Steps 8–12", "5 steps + 1 decision"),
]

steps = [
    Step("1", "1", "Prospect enquiry received via channel", "Member Services Rep",
         "Enquiry logged in CRM; prospect record created if new", "Day 0", "Multi-channel intake", kind="trigger"),
    Step("2", "1", "Needs assessment conducted", "Member Services Rep",
         "Product suitability confirmed; information gathered per product checklist", "Day 0", "Suitability checklist"),
    Step("3", "1", "Application data entered into PAS", "Member Services Rep",
         "Application ID generated; data validated for completeness", "Day 0–1", "Application capture"),
    Step("4", "1", "Premium quoted to prospect", "PAS / Rating Engine",
         "Quote valid 30 days; reference logged in CRM", "Day 1", "Real-time rating"),
    Step("5", "2", "Application submitted to underwriting rules engine", "PAS (auto)",
         "Auto-accept → issuance; refer → underwriter queue", "Instant", "Auto-accept rules"),
    Step("6", "2", "Underwriter reviews referred application", "Underwriter",
         "Risk assessed within 2 days (personal) / 5 days (commercial); info requested if needed", "≤2–5 days", "Referral SLA"),
    Step("7", "2", "Underwriting decision made", "Underwriter",
         "Accept standard / accept substandard / decline; recorded in PAS", "≤5 days", "Decision recorded"),
    Step("", "2", "", "", "", "", "Rules + underwriter outcome", kind="decision", decision="Underwriting outcome?",
         branches=["Accept (standard/substandard) → issuance", "Decline → written notice (Sec 6.3)"]),
    Step("8", "3", "Terms communicated to prospect / policyholder", "Member Services Rep",
         "Acceptance letter or renewal notice; payment instructions included", "Day +1", "Terms communication"),
    Step("9", "3", "Prospect accepts terms and pays premium", "Applicant / Policyholder",
         "Payment received; acceptance confirmed in CRM", "Day +1–3", "Acceptance & payment"),
    Step("10", "3", "Policy issued in PAS", "Member Services Rep",
         "Policy number assigned; coverage start date confirmed", "Day +1", "Issuance"),
    Step("11", "3", "Policy documents dispatched", "PAS / Document Engine",
         "Schedule, certificate and PDS sent within 2 business days", "≤2 days", "Document SLA"),
    Step("12", "3", "Broker / agent notification (if applicable)", "PAS (auto)",
         "Commission statement generated; confirmation sent to producing broker", "Day +1", "Producer notification", kind="complete"),
]

authority = [
    AuthorityRow("Auto-accept (rules-clear)", "Rules Engine", "—"),
    AuthorityRow("Personal lines referral", "Underwriter", "—"),
    AuthorityRow("Commercial SME referral", "Senior Underwriter", "Underwriter"),
    AuthorityRow("Substandard / non-standard terms", "Senior Underwriter", "Actuarial pricing"),
    AuthorityRow("Large risk (above treaty limit)", "Chief Underwriting Officer", "Reinsurance referral"),
]

swim_phases = [
    SwimPhase("1", "Prospect qualification & quote", "Steps 1–4 · enquiry to quote",
        ["Prospect", "Member Services", "PAS / Rating"],
        [SwimNode("s1", "Prospect", 0, "Enquiry received", "any channel"),
         SwimNode("s2", "Member Services", 1, "Needs assessment", "suitability checklist"),
         SwimNode("s3", "Member Services", 2, "Enter application in PAS", "Application ID"),
         SwimNode("s4", "PAS / Rating", 3, "Premium quoted", "30-day quote")],
        [SwimEdge("s1", "s2", dashed=True), SwimEdge("s2", "s3"), SwimEdge("s3", "s4")],
        "Prospects are qualified against a product suitability checklist before a 30-day quote is issued."),
    SwimPhase("2", "Underwriting assessment", "Steps 5–7 · rules, referral, decision",
        ["PAS / Rules", "Underwriter", "Actuarial"],
        [SwimNode("a1", "PAS / Rules", 0, "Rules engine", "auto-accept / refer", kind="decision"),
         SwimNode("a2", "Underwriter", 1, "Review referred application", "≤2–5 days"),
         SwimNode("a3", "Actuarial", 1, "Price non-standard risk", "if substandard"),
         SwimNode("a4", "Underwriter", 2, "Underwriting decision", "std / substd / decline", kind="decision"),
         SwimNode("a5", "Underwriter", 3, "Decline notice", "Sec 6.3", kind="exception")],
        [SwimEdge("a1", "a2", label="ref"), SwimEdge("a2", "a3", dashed=True), SwimEdge("a3", "a4"),
         SwimEdge("a2", "a4"), SwimEdge("a4", "a5", dashed=True, kind="exception", label="dec")],
        "Only referred applications reach an underwriter; non-standard risks are priced with Actuarial before a decision."),
    SwimPhase("3", "Acceptance & issuance", "Steps 8–12 · terms to fulfilment",
        ["Applicant", "Member Services", "PAS / Broker"],
        [SwimNode("d1", "Member Services", 0, "Communicate terms", "letter / renewal"),
         SwimNode("d2", "Applicant", 1, "Accept & pay premium", "confirmed in CRM"),
         SwimNode("d3", "Member Services", 2, "Issue policy in PAS", "policy number"),
         SwimNode("d4", "PAS / Broker", 3, "Dispatch documents", "schedule · cert · PDS"),
         SwimNode("d5", "PAS / Broker", 4, "Broker / agent notification", "commission", kind="terminal")],
        [SwimEdge("d1", "d2", dashed=True), SwimEdge("d2", "d3"), SwimEdge("d3", "d4"), SwimEdge("d4", "d5")],
        "On acceptance and payment the policy issues, documents dispatch within two days, and producers are notified."),
]

fg_items = [
    FitItem("1", "Multi-channel prospect intake", "FIT",
        "Enquiry capture and CRM prospect creation across channels align with PolicyCenter submission intake.",
        "Member Services", "GW-PC-SUB-01", "p1"),
    FitItem("2", "Needs assessment & suitability", "PARTIAL",
        "A product checklist is used, but suitability is not captured as a structured, auditable needs analysis as "
        "the catalog recommends for conduct compliance.",
        "Member Services", "GW-PC-SUB-02", "p1"),
    FitItem("3", "Real-time rating & quote", "FIT",
        "Rating-engine quote with 30-day validity aligns with PolicyCenter quoting.",
        "Rating Engine", "GW-PC-QTE-01", "p1"),
    FitItem("4", "Third-party risk-data enrichment", "GAP",
        "Quotes use applicant-supplied data only. PolicyCenter enriches submissions with third-party risk data "
        "(property, flood, credit, prior-claims) for pricing accuracy and anti-selection control.",
        "Rating Engine", "GW-PC-QTE-08", "p1"),
    FitItem("5", "Auto-accept rules engine", "PARTIAL",
        "Rules-based auto-accept present, but no predictive risk-model score to widen straight-through processing.",
        "Rules Engine", "GW-PC-UW-02", "p2"),
    FitItem("6", "KYC / sanctions screening", "GAP",
        "No KYC or sanctions/PEP screening at new business. PolicyCenter screens applicants before binding.",
        "Underwriter / Compliance", "GW-PC-UW-05", "p2"),
    FitItem("7", "Underwriter referral & SLAs", "FIT",
        "Referral with 2-day/5-day SLAs and additional-info handling aligns with PolicyCenter referral workflow.",
        "Underwriter", "GW-PC-UW-03", "p2"),
    FitItem("8", "Substandard terms & actuarial pricing", "FIT",
        "Accept/substandard/decline with actuarial pricing for non-standard risk aligns with PolicyCenter decisioning.",
        "Underwriter / Actuarial", "GW-PC-UW-04", "p2"),
    FitItem("9", "Reinsurance / facultative referral", "GAP",
        "No facultative reinsurance referral or treaty-capacity check for large commercial risks above retention — "
        "a capacity and accumulation-control gap vs the catalog.",
        "Underwriter / Reinsurance", "GW-PC-RI-01", "p2"),
    FitItem("10", "Terms communication & acceptance", "FIT",
        "Acceptance letter / renewal notice with payment instructions aligns with PolicyCenter offer handling.",
        "Member Services", "GW-PC-ISS-02", "p3"),
    FitItem("11", "Disclosure & e-signature", "GAP",
        "Acceptance is confirmed in CRM with no auditable e-signature on terms/PDS. PolicyCenter captures a signed "
        "acceptance before issuance — conduct and dispute exposure.",
        "Member Services", "GW-PC-ISS-04", "p3"),
    FitItem("12", "Instant issuance & document dispatch", "FIT",
        "Policy issuance with 2-day document dispatch aligns with PolicyCenter issuance and fulfilment.",
        "Member Services / PAS", "GW-PC-ISS-01", "p3"),
    FitItem("13", "Renewal re-rating & retention", "PARTIAL",
        "Renewals trigger at 60 days but without retention/price-optimisation modelling or proactive win-back for "
        "non-take-up recommended by the catalog.",
        "Actuarial / Member Services", "GW-PC-REN-02", "p3"),
    FitItem("14", "Producer / commission notification", "FIT",
        "Automated commission statement and broker confirmation align with PolicyCenter producer management.",
        "PAS", "GW-PC-PRD-01", "p3"),
]

fitgap = FitGap(
    overall_fit=69, partial_pct=15, fits=8, gaps=3, partials=3,
    steps_analysed=14, phases_count=3,
    summary_line="Overall alignment of SOP-INS-004 against the Guidewire PolicyCenter underwriting catalog",
    metrics=[
        ("Steps analysed", "14 steps across 3 phases"),
        ("Fits confirmed", "8 steps aligned to catalog"),
        ("Gaps identified", "3 steps — remediation required"),
        ("Partial fits", "3 steps — enhancement recommended"),
        ("Highest risk area", "KYC / sanctions screening (missing)"),
        ("Capacity gap", "No reinsurance facultative referral"),
        ("Ref standard", "Guidewire PolicyCenter UW Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Quote", 70, ""),
        FitPhaseBar("Phase 2", "Underwriting", 64, ""),
        FitPhaseBar("Phase 3", "Issuance", 78, ""),
        FitPhaseBar("Screening /", "data", 46, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 70, "Prospect & quote"),
        PhaseScoreCard("Phase 2", 64, "Underwriting"),
        PhaseScoreCard("Phase 3", 78, "Acceptance & issue"),
        PhaseScoreCard("Screening", 46, "KYC & risk data"),
    ],
    detail_slides=[
        ("Phase 1 — Prospect qualification & quote", "Steps 1–4 vs Guidewire PolicyCenter catalog", ["p1"]),
        ("Phase 2 — Underwriting assessment", "Steps 5–9 vs Guidewire PolicyCenter catalog", ["p2"]),
        ("Phase 3 — Acceptance & issuance", "Steps 10–14 vs Guidewire PolicyCenter catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — PROSPECT QUALIFICATION & QUOTE"),
            ("p2", "PHASE 2 — UNDERWRITING ASSESSMENT"),
            ("p3", "PHASE 3 — ACCEPTANCE & ISSUANCE")],
    critical_missing=[
        CriticalGap("KYC / sanctions screening",
            "Applicants are not KYC-verified or screened against sanctions/PEP lists before binding, a regulatory "
            "control required by the catalog at new business."),
        CriticalGap("Third-party risk-data enrichment",
            "Quotes rely on applicant-supplied data only, with no property/flood/credit/prior-claims enrichment — "
            "an anti-selection and pricing-accuracy gap."),
        CriticalGap("Reinsurance / facultative referral",
            "No facultative reinsurance referral or treaty-capacity check for large commercial risks above "
            "retention, a capacity and accumulation-control gap."),
        CriticalGap("Disclosure & e-signature acceptance",
            "Acceptance is confirmed only in CRM with no auditable signed acceptance of terms/PDS before issuance."),
    ],
    radar=[("Intake / quote", 76), ("Risk data", 45), ("Auto-accept", 64), ("KYC / sanctions", 38),
           ("Decisioning", 78), ("Reinsurance", 40), ("Issuance", 82)],
    control_bars=[
        ControlBar("Intake & quote", 76, "Multi-channel capture with real-time rating"),
        ControlBar("Risk-data enrichment", 45, "Applicant data only; no third-party enrichment"),
        ControlBar("Auto-accept rules", 64, "Rules-based; no predictive model"),
        ControlBar("KYC / sanctions", 38, "No screening at new business"),
        ControlBar("Underwriting decisioning", 78, "Referral, substandard terms and pricing solid"),
        ControlBar("Reinsurance referral", 40, "No facultative/treaty-capacity check"),
        ControlBar("Issuance & fulfilment", 82, "Instant issuance with 2-day document SLA"),
    ],
    remediations=[
        Remediation(1, "Add KYC / sanctions screening at new business",
            "Verify identity and screen applicants against sanctions/PEP lists before any bind; route hits to "
            "Compliance. Effort: 4 weeks.", "High"),
        Remediation(2, "Enrich submissions with third-party risk data",
            "Call property, flood, credit and prior-claims data at quote to improve pricing accuracy and control "
            "anti-selection. Effort: 5 weeks (data partners).", "High"),
        Remediation(3, "Introduce reinsurance facultative referral",
            "Add a treaty-capacity check and automatic facultative referral for risks above retention before "
            "binding large commercial business. Effort: 4 weeks.", "High"),
        Remediation(4, "Capture disclosure acknowledgement & e-signature",
            "Require an auditable signed acceptance of terms/PDS before issuance, stored against the policy. "
            "Effort: 3 weeks.", "Medium"),
        Remediation(5, "Add predictive scoring & renewal retention modelling",
            "Layer a predictive risk score over the rules engine and a retention/price-optimisation model on "
            "renewals with automated NTU win-back. Effort: 7 weeks.", "Medium"),
    ],
    risk_impact=[("KYC / sanctions", 88), ("Risk-data enrichment", 80), ("Reinsurance referral", 75),
                 ("E-signature", 62), ("Predictive scoring", 55), ("Retention modelling", 50)],
    projected_fit=91,
)

opt_phases = [
    Phase("1", "Prospect, quote & enrichment", "Needs, risk data, quote", "blue",
          "Prospect · Member Services · Rating", "Steps 1–5", "5 steps"),
    Phase("2", "Underwriting & screening", "Screening, rules+model, referral", "green",
          "PAS · Underwriter · Actuarial · Reinsurance", "Steps 6–10", "5 steps + 1 decision"),
    Phase("3", "Acceptance & issuance", "Terms, e-sign, issuance, fulfilment", "amber",
          "Applicant · Member Services · PAS · Broker", "Steps 11–15", "5 steps + 1 decision"),
]

opt_steps = [
    Step("1", "1", "Prospect enquiry received via channel", "Member Services Rep",
         "Logged in CRM; prospect record created", "Day 0", "Standard", kind="trigger"),
    Step("2", "1", "Structured needs analysis & suitability", "Member Services Rep",
         "Auditable needs analysis captured for conduct compliance", "Day 0", "ENHANCED (v3.0)"),
    Step("3", "1", "Application entered into PAS", "Member Services Rep",
         "Application ID; completeness validated", "Day 0–1", "Standard"),
    Step("4", "1", "Third-party risk-data enrichment", "Rating Engine / Data Service",
         "Property, flood, credit and prior-claims data appended before rating", "Day 1",
         "NEW (v3.0) — anti-selection control"),
    Step("5", "1", "Premium quoted to prospect", "PAS / Rating Engine",
         "Quote valid 30 days; reference logged", "Day 1", "Standard"),
    Step("6", "2", "KYC / sanctions screening", "Underwriter / Compliance",
         "Identity verified; applicant screened against sanctions/PEP lists", "Instant",
         "NEW (v3.0) — regulatory control"),
    Step("7", "2", "Auto-accept with predictive risk score", "Rules + Model Engine",
         "Rules plus predictive score widen straight-through acceptance", "Instant", "ENHANCED (v3.0)"),
    Step("8", "2", "Underwriter reviews referred application", "Underwriter",
         "Risk assessed within 2–5 days; info requested if needed", "≤2–5 days", "Standard"),
    Step("9", "2", "Reinsurance facultative referral (large risk)", "Underwriter / Reinsurance",
         "Treaty-capacity check; facultative placement for risks above retention", "≤3 days",
         "NEW (v3.0) — capacity control"),
    Step("10", "2", "Underwriting decision made", "Underwriter",
         "Accept standard/substandard or decline; recorded in PAS", "≤5 days", "Standard"),
    Step("", "2", "", "", "", "", "Decision", kind="decision", decision="Underwriting outcome?",
         branches=["Accept → issuance", "Decline → written notice (Sec 6.3)"]),
    Step("11", "3", "Terms communicated to prospect", "Member Services Rep",
         "Acceptance letter or renewal notice; payment instructions", "Day +1", "Standard"),
    Step("12", "3", "Disclosure acknowledgement & e-signature", "Applicant / PAS",
         "Auditable signed acceptance of terms/PDS captured before issuance", "Day +1–3",
         "NEW (v3.0) — conduct control"),
    Step("13", "3", "Policy issued in PAS", "Member Services Rep",
         "Policy number; coverage start date confirmed", "Day +1", "Standard"),
    Step("14", "3", "Policy documents dispatched", "PAS / Document Engine",
         "Schedule, certificate and PDS within 2 business days", "≤2 days", "Standard"),
    Step("15", "3", "Producer notification & renewal retention tag", "PAS / Actuarial",
         "Commission statement issued; retention/price-optimisation flag set for renewal", "Day +1",
         "ENHANCED (v3.0)", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "Prospect, quote & enrichment", "Steps 1–5 · v3.0 adds risk-data enrichment",
        ["Prospect", "Member Services", "Rating / Data"],
        [SwimNode("o1", "Prospect", 0, "Enquiry received", "any channel"),
         SwimNode("o2", "Member Services", 1, "Structured needs analysis", "auditable suitability", kind="enhanced"),
         SwimNode("o3", "Member Services", 2, "Enter application in PAS", "Application ID"),
         SwimNode("o4", "Rating / Data", 3, "Risk-data enrichment", "property · flood · credit", kind="new"),
         SwimNode("o5", "Rating / Data", 4, "Premium quoted", "30-day quote")],
        [SwimEdge("o1", "o2", dashed=True), SwimEdge("o2", "o3"),
         SwimEdge("o3", "o4", dashed=True, kind="new", label="enrich"), SwimEdge("o4", "o5")],
        "v3.0 enriches every submission with third-party risk data before rating, improving pricing accuracy."),
    SwimPhase("2", "Underwriting & screening", "Steps 6–10 · screening, model, reinsurance",
        ["PAS / Rules", "Underwriter", "Compliance / Reinsurance"],
        [SwimNode("p1", "Compliance / Reinsurance", 0, "KYC / sanctions screening", "before bind", kind="new"),
         SwimNode("p2", "PAS / Rules", 1, "Auto-accept + risk model", "predictive score", kind="enhanced"),
         SwimNode("p3", "Underwriter", 1, "Review referred application", "≤2–5 days"),
         SwimNode("p4", "Compliance / Reinsurance", 2, "Reinsurance facultative referral", "treaty capacity", kind="new"),
         SwimNode("p5", "Underwriter", 2, "Underwriting decision", "std / substd / decline", kind="decision")],
        [SwimEdge("p1", "p2", dashed=True, kind="new"), SwimEdge("p2", "p3", label="ref"),
         SwimEdge("p3", "p4", dashed=True, kind="new", label="large"), SwimEdge("p4", "p5"),
         SwimEdge("p3", "p5")],
        "v3.0 screens applicants before binding, scores them with a predictive model, and refers large risks to reinsurance."),
    SwimPhase("3", "Acceptance & issuance", "Steps 11–15 · v3.0 adds e-signature",
        ["Applicant", "Member Services", "PAS / Broker"],
        [SwimNode("q1", "Member Services", 0, "Communicate terms", "letter / renewal"),
         SwimNode("q2", "Applicant", 1, "Disclosure & e-signature", "signed acceptance", kind="new"),
         SwimNode("q3", "Member Services", 2, "Issue policy in PAS", "policy number"),
         SwimNode("q4", "PAS / Broker", 3, "Dispatch documents", "schedule · cert · PDS"),
         SwimNode("q5", "PAS / Broker", 4, "Producer & retention tag", "commission · retention", kind="enhanced")],
        [SwimEdge("q1", "q2", dashed=True, kind="new"), SwimEdge("q2", "q3"), SwimEdge("q3", "q4"),
         SwimEdge("q4", "q5")],
        "v3.0 captures an auditable e-signature acceptance before issuance and tags renewals for retention modelling."),
]

optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Guidewire PolicyCenter Underwriting Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-004"),
                ("Version", "3.0 (Optimised)"),
                ("Effective Date", "01 October 2026"),
                ("Supersedes", "v2.1 dated 01 January 2025"),
                ("Owner", "Member Services — Policy Operations"),
                ("Approved By", "Chief Underwriting Officer"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-004 dated 18 June 2026"),
                ("Catalog Alignment Score", "91% (up from 69% in v2.1)"),
                ("Classification", "Internal Use Only"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v3.0",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-004. Alignment to the "
              "Guidewire PolicyCenter underwriting catalog increased from 69% to 91%. Critical additions: KYC/sanctions "
              "screening, third-party risk-data enrichment, reinsurance facultative referral, disclosure e-signature, "
              "predictive risk scoring, and renewal retention modelling."],
             ["NEW STEP (green) — step added to close a gap vs the PolicyCenter catalog",
              "ENHANCED (amber) — existing step updated with additional controls or automation"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines the end-to-end process from prospect enquiry to "
             "policy issuance for new business and renewals. Version 3.0 incorporates optimisations from fit-gap "
             "analysis against the Guidewire PolicyCenter New Business & Renewal Underwriting Catalog, achieving 91% "
             "alignment (up from 69% in v2.1)."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to new business across personal lines and commercial SME products and "
             "to renewals, received via online, agent, broker and bancassurance channels."),
            ("banner", "new", "Scope extended: KYC/sanctions screening and risk-data enrichment now apply to every "
             "application before binding."),
            ("para", "This procedure does NOT cover claims-triggered reinstatements, group enrolments (SOP-INS-006), "
             "or life and health products."),
        ]),
        DocSection("3. Underwriting Authority Matrix", [
            ("table", ["Decision", "First Authority", "Second Authority"],
             [["Auto-accept (rules + model clear)", "Rules + Model Engine", "—"],
              ["Personal lines referral", "Underwriter", "—"],
              ["Commercial SME referral", "Senior Underwriter", "Underwriter"],
              ["Substandard / non-standard terms", "Senior Underwriter", "Actuarial pricing"],
              ["Large risk (above treaty limit)", "Chief Underwriting Officer", "Reinsurance referral"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Member Services Representative", "Captures enquiries and needs analysis; initiates applications; communicates terms; coordinates to issuance."],
              ["Underwriter", "Reviews referred applications; sets terms and pricing; approves/declines; manages reinsurance referral."],
              ["Actuarial", "Maintains rating and models; prices non-standard risk; owns renewal retention modelling."],
              ["Compliance", "Owns KYC/sanctions dispositions and conduct/suitability governance."]], {}),
        ]),
        DocSection("5. Screening & Risk Data (New Section — v3.0)", [
            ("banner", "crit", "New section. Required by the PolicyCenter catalog. KYC/sanctions screening and "
             "risk-data enrichment must complete before any policy is bound."),
            ("table", ["#", "Control", "Responsible", "Output / System", "Timeline"],
             [["S1", "Third-party risk-data enrichment", "Rating / Data Service", "Property, flood, credit, prior-claims appended", "At quote"],
              ["S2", "KYC / sanctions screening", "Compliance", "Identity verified; sanctions/PEP screened", "Pre-bind"],
              ["S3", "Reinsurance facultative referral", "Underwriter / Reinsurance", "Treaty capacity checked; facultative placement", "Pre-bind"],
              ["S4", "Disclosure acknowledgement & e-signature", "Applicant / PAS", "Signed acceptance of terms/PDS", "Pre-issue"]],
             {0: "new", 1: "new", 2: "new", 3: "new"}),
        ]),
        DocSection("6. Process Steps", [
            ("h3", "6.1 Prospect, Quote & Enrichment"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "Prospect enquiry received", "Member Services", "Logged in CRM", "Day 0"],
              ["2", "Structured needs analysis & suitability", "Member Services", "Auditable needs analysis", "Day 0"],
              ["3", "Application entered into PAS", "Member Services", "Application ID; validated", "Day 0–1"],
              ["4", "Third-party risk-data enrichment", "Rating / Data Service", "Risk data appended", "Day 1"],
              ["5", "Premium quoted to prospect", "PAS / Rating Engine", "30-day quote", "Day 1"]],
             {1: "enh", 3: "new"}),
            ("h3", "6.2 Underwriting & Screening"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["6", "KYC / sanctions screening", "Compliance", "Identity + watchlist before bind", "Instant"],
              ["7", "Auto-accept with predictive risk score", "Rules + Model Engine", "STP acceptance widened", "Instant"],
              ["8", "Underwriter reviews referred application", "Underwriter", "Risk assessed 2–5 days", "≤2–5 days"],
              ["9", "Reinsurance facultative referral (large risk)", "Underwriter / Reinsurance", "Treaty capacity; facultative", "≤3 days"],
              ["10", "Underwriting decision made", "Underwriter", "Accept/substandard/decline", "≤5 days"]],
             {0: "new", 1: "enh", 3: "new"}),
            ("h3", "6.3 Acceptance & Issuance"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["11", "Terms communicated to prospect", "Member Services", "Acceptance/renewal notice", "Day +1"],
              ["12", "Disclosure acknowledgement & e-signature", "Applicant / PAS", "Signed acceptance captured", "Day +1–3"],
              ["13", "Policy issued in PAS", "Member Services", "Policy number; start date", "Day +1"],
              ["14", "Policy documents dispatched", "PAS / Document Engine", "Schedule, cert, PDS within 2 days", "≤2 days"],
              ["15", "Producer notification & retention tag", "PAS / Actuarial", "Commission; retention flag", "Day +1"]],
             {1: "new", 4: "enh"}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Prospect Does Not Accept Terms"),
            ("numbered", [
                "Application status set to 'Not Taken Up' in PAS with a reason code.",
                "CRM follow-up task set for 14 days; an automated win-back offer is sent where pricing flexibility exists."]),
            ("h3", "7.2 Renewal — Policyholder Non-Response"),
            ("numbered_from", 3, [
                "If no response within 21 days of expiry, a final reminder is sent.",
                "Policy lapses on expiry if no renewal payment received; reinstatement per SOP-INS-011."]),
            ("h3", "7.3 Decline"),
            ("numbered_from", 5, [
                "Applicant notified in writing within 1 business day with reasons permitted by guidelines and regulation.",
                "Applicant referred to an alternative market where a known placement pathway exists."]),
            ("h3", "7.4 Screening Hold (New — v3.0)"),
            ("banner", "new", "New exception. Applications failing KYC or hitting a sanctions match are held pending Compliance review."),
            ("numbered_from", 7, [
                "KYC failure: document-upload fallback offered; unresolved cases referred to Underwriting.",
                "Sanctions/PEP hit: application held; Compliance dispositions within 1 business day before any bind."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["Policy Administration System (PAS)", "Application capture, underwriting workflow, issuance", "All roles"],
              ["CRM (Salesforce)", "Prospect/customer records, renewal tracking, win-back", "Member Services, Underwriting"],
              ["Rating + Model Engine", "Premium calculation, auto-accept rules and predictive scoring", "Automated"],
              ["Risk-Data Service", "Property, flood, credit and prior-claims enrichment", "Rating, Underwriting"],
              ["KYC / Sanctions Tool", "Identity verification and watchlist screening", "Compliance"],
              ["Reinsurance System", "Treaty-capacity checks and facultative placement", "Underwriting, Reinsurance"],
              ["Document Management System", "Policy document generation and dispatch", "PAS integration"],
              ["Broker Portal", "Broker submission, quotes, commission statements", "Broker, Member Services"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v3.0: KYC/sanctions screening, risk-data enrichment, reinsurance "
             "referral, e-signature acceptance and predictive scoring."),
            ("bullets", [
                "Screening gate: no bind without KYC and sanctions clearance.",
                "Risk-data enrichment: third-party data appended to every submission before rating.",
                "Capacity control: large risks referred to reinsurance with a treaty-capacity check.",
                "Disclosure capture: auditable e-signature on terms/PDS before issuance.",
                "Predictive scoring: rules-engine acceptance refined by a governed risk model.",
                "Suitability: structured needs analysis recorded for conduct compliance.",
                "Immutable audit trail: enquiry, screening, decision, acceptance and issuance events logged."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v2.1 Target", "v3.0 Target", "Measurement"],
             [["Quote-to-bind (new business)", "≥22%", "≥26%", "Bound / quoted"],
              ["Straight-through acceptance", "Rules only", "≥70% with model", "Auto-accept rate"],
              ["Sanctions screening", "N/A (new)", "100% pre-bind", "Screening log"],
              ["Application-to-issue (auto)", "≤1 day", "≤1 day", "Submission to issuance"],
              ["Renewal retention", "≥82%", "≥86%", "Retained / eligible renewals"],
              ["Large-risk reinsurance referral", "N/A (new)", "100% above retention", "Facultative referral log"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["2.1", "01 Jan 2025", "A. Ibrahim, Underwriting", "Updated underwriting SLAs; added broker portal steps; revised retention KPIs"],
              ["3.0", "01 Oct 2026", "A. Ibrahim, Underwriting",
               "OPTIMISED: KYC/sanctions screening; risk-data enrichment; reinsurance facultative referral; "
               "e-signature acceptance; predictive scoring; renewal retention modelling; catalog alignment 69% → 91%"]], {}),
        ]),
    ],
)

package = SopPackage(
    meta=meta, phases=phases, steps=steps, authority=authority, swim_phases=swim_phases,
    n_phases=3, n_steps=12, n_roles=4, n_gateways=2,
    fitgap=fitgap,
    opt_phases=opt_phases, opt_steps=opt_steps, opt_swim_phases=opt_swim_phases,
    opt_n_phases=3, opt_n_steps=15, opt_n_gateways=2, opt_fit=91,
    optimised_doc=optimised_doc,
    swim_cover_tags="Prospect · Underwriting · Acceptance · Issuance · Exception handling",
    hierarchy_cover_sub="Phase breakdown with new-business tracks, underwriting authority, and exception paths",
)
