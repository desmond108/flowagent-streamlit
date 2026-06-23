"""SOP-INS-001 — Online Insurance Sales (Meridian Insurance Group).

Fit-gap vs the Guidewire PolicyCenter digital sales & underwriting catalog.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Guidewire PolicyCenter — Digital Sales & Underwriting Best-Practice Catalog"
CATALOG_SHORT = "Guidewire PolicyCenter"

meta = Meta(
    sop_id="SOP-INS-001", slug="Online_Insurance_Sales",
    title="Online Insurance Sales", short_title="Online insurance sales",
    version="1.2", owner="Digital Sales & Distribution",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="2.0", effective_date="01 October 2026",
    supersedes="v1.2 dated 01 April 2025", approved_by="Chief Distribution Officer",
    classification="Internal Use Only",
)

phases = [
    Phase("1", "Quote generation", "Self-service quote on portal / app", "blue",
          "Applicant · Portal · Rating Engine", "Steps 1–4", "4 steps"),
    Phase("2", "Application & underwriting", "Validation, bureau checks, auto-accept", "green",
          "Applicant · Rules Engine · Underwriting", "Steps 5–8", "4 steps + 1 decision"),
    Phase("3", "Payment & issuance", "Payment, policy issuance, fulfilment", "amber",
          "Applicant · Payment Gateway · App Processing · CRM", "Steps 9–13", "5 steps + 1 decision"),
]

steps = [
    Step("1", "1", "Applicant enters vehicle/property and personal details", "Applicant",
         "Portal auto-saves progress; session valid 72 hours", "Real time", "Self-service capture", kind="trigger"),
    Step("2", "1", "Rating engine calculates premium", "Portal / Rating Engine",
         "Instant quote displayed; multi-product discount applied if eligible", "Instant", "Real-time rating"),
    Step("3", "1", "Quote presented with coverage options", "Portal",
         "Quote reference generated; valid 30 days", "Instant", "Quote retention 30 days"),
    Step("4", "1", "Applicant selects coverage tier and endorsements", "Applicant",
         "Selection recorded; premium recalculated in real time", "Real time", "Premium recalculated live"),
    Step("5", "2", "Applicant completes and submits full application", "Applicant",
         "Application ID assigned; data written to PAS", "Real time", "Application captured in PAS"),
    Step("6", "2", "Automated data validation and bureau checks", "PAS / External Bureau",
         "MVR, claims history and credit score retrieved within 60 seconds", "≤60 sec", "Bureau integration"),
    Step("7", "2", "Auto-accept or refer decision", "Underwriting Rules Engine",
         "Auto-accept → payment; refer → underwriting queue", "Instant", "Auto-accept rules"),
    Step("8", "2", "Manual underwriting review (referred)", "Underwriting Staff",
         "Decision within 2 business hours; applicant notified by email", "≤2 hours", "Referral SLA: 2 hours"),
    Step("", "2", "", "", "", "", "Rules-engine outcome", kind="decision", decision="Underwriting outcome?",
         branches=["Accept → payment (Phase 3)", "Refer → manual review", "Decline → adverse-action notice (Sec 6.3)"]),
    Step("9", "3", "Applicant proceeds to payment", "Applicant / Payment Gateway",
         "Secure PCI-DSS compliant payment page", "Real time", "PCI-DSS gateway"),
    Step("10", "3", "Payment authorised", "Payment Gateway",
         "Authorisation code recorded in PAS; failure triggers retry (max 3)", "Instant", "Retry flow on failure"),
    Step("11", "3", "Policy issued in PAS", "Application Processing Staff",
         "Policy number generated; coverage effective immediately on payment", "≤10 min", "Instant issuance"),
    Step("12", "3", "Policy documents emailed to applicant", "PAS / Email Engine",
         "Certificate, schedule and PDS dispatched within 5 minutes", "≤5 min", "Document delivery"),
    Step("13", "3", "Welcome SMS sent", "CRM",
         "Policy number, claims number and portal login link sent", "≤10 min", "Onboarding fulfilment", kind="complete"),
]

authority = [
    AuthorityRow("Auto-accept (rules-clear)", "Rules Engine", "—"),
    AuthorityRow("Referred — standard risk", "Underwriting Staff", "—"),
    AuthorityRow("Referred — elevated risk", "Senior Underwriter", "Underwriting Staff"),
    AuthorityRow("Manual rating adjustment", "Senior Underwriter", "—"),
    AuthorityRow("Decline / hard exclusion", "Underwriting Manager", "Senior Underwriter"),
]

swim_phases = [
    SwimPhase("1", "Quote generation", "Steps 1–4 · self-service",
        ["Applicant", "Portal / Rating", "Underwriting"],
        [SwimNode("s1", "Applicant", 0, "Enter details", "vehicle / property"),
         SwimNode("s2", "Portal / Rating", 1, "Rating engine quote", "instant premium"),
         SwimNode("s3", "Portal / Rating", 2, "Present quote & options", "30-day quote"),
         SwimNode("s4", "Applicant", 3, "Select tier & endorsements", "premium recalculated")],
        [SwimEdge("s1", "s2"), SwimEdge("s2", "s3"), SwimEdge("s3", "s4")],
        "Applicants self-serve a real-time quote on the portal or mobile app; quotes are retained for 30 days."),
    SwimPhase("2", "Application & underwriting", "Steps 5–8 · validation and auto-accept",
        ["Applicant", "Rules Engine / PAS", "Underwriting"],
        [SwimNode("a1", "Applicant", 0, "Submit application", "Application ID"),
         SwimNode("a2", "Rules Engine / PAS", 1, "Bureau checks & validation", "MVR · claims · credit"),
         SwimNode("a3", "Rules Engine / PAS", 2, "Auto-accept or refer", "rules engine", kind="decision"),
         SwimNode("a4", "Underwriting", 2, "Manual UW review", "referred · ≤2h"),
         SwimNode("a5", "Underwriting", 3, "Decline notice", "adverse action", kind="exception")],
        [SwimEdge("a1", "a2"), SwimEdge("a2", "a3"), SwimEdge("a3", "a4", label="ref"),
         SwimEdge("a4", "a5", dashed=True, kind="exception", label="dec")],
        "Applications are validated against bureau data and scored by the rules engine; only referred cases reach an underwriter."),
    SwimPhase("3", "Payment & issuance", "Steps 9–13 · payment, issuance, fulfilment",
        ["Applicant / Gateway", "Application Processing", "CRM / PAS"],
        [SwimNode("d1", "Applicant / Gateway", 0, "Proceed to payment", "PCI-DSS page"),
         SwimNode("d2", "Applicant / Gateway", 1, "Payment authorised", "max 3 retries"),
         SwimNode("d3", "Application Processing", 2, "Issue policy in PAS", "policy number"),
         SwimNode("d4", "CRM / PAS", 3, "Email documents", "cert · schedule · PDS"),
         SwimNode("d5", "CRM / PAS", 4, "Welcome SMS", "onboarding", kind="terminal")],
        [SwimEdge("d1", "d2"), SwimEdge("d2", "d3"), SwimEdge("d3", "d4"), SwimEdge("d4", "d5")],
        "On successful payment the policy is issued instantly; documents and a welcome SMS are dispatched within minutes."),
]

fg_items = [
    FitItem("1", "Real-time rating & quote", "FIT",
        "Instant rating with live recalculation and 30-day quote retention aligns with PolicyCenter digital quoting.",
        "Rating Engine", "GW-PC-QTE-01", "p1"),
    FitItem("2", "Multi-product discounting", "FIT",
        "Automatic multi-product discount at quote aligns with PolicyCenter bundling rules.",
        "Rating Engine", "GW-PC-QTE-03", "p1"),
    FitItem("3", "Identity verification (eKYC)", "GAP",
        "PolicyCenter requires applicant identity verification at quote/application. SOP captures details with "
        "no eKYC or identity-proofing step — application-fraud exposure.",
        "Digital Ops", "GW-PC-FR-01", "p1"),
    FitItem("4", "Abandoned-cart recovery", "PARTIAL",
        "24h/72h reminder emails present, but no proactive outbound or next-best-action beyond a weekly manual "
        "report for high-value quotes.",
        "Digital Ops", "GW-PC-QTE-05", "p1"),
    FitItem("5", "Application capture & ID", "FIT",
        "Full application captured to PAS with a unique Application ID aligns with PolicyCenter submission intake.",
        "Applicant / PAS", "GW-PC-SUB-01", "p2"),
    FitItem("6", "Bureau data integration", "FIT",
        "MVR, claims-history and credit retrieval within 60 seconds aligns with PolicyCenter third-party data calls.",
        "PAS / Bureau", "GW-PC-SUB-03", "p2"),
    FitItem("7", "Auto-accept rules engine", "PARTIAL",
        "Rules-based auto-accept present, but no predictive risk-model score to refine straight-through acceptance "
        "as recommended by the catalog.",
        "Rules Engine", "GW-PC-UW-02", "p2"),
    FitItem("8", "Sanctions / watchlist screening", "GAP",
        "PolicyCenter screens applicants against sanctions/PEP watchlists before binding. SOP has no screening step.",
        "Underwriting / Compliance", "GW-PC-UW-05", "p2"),
    FitItem("9", "Manual referral & adverse action", "FIT",
        "2-hour referral SLA and statutory adverse-action decline notices align with PolicyCenter referral handling.",
        "Underwriting Staff", "GW-PC-UW-03", "p2"),
    FitItem("10", "Usage-based / telematics rating", "GAP",
        "For auto, PolicyCenter supports a telematics/usage-based rating option at quote. SOP offers only "
        "traditional rating — competitiveness and pricing-accuracy gap.",
        "Rating Engine", "GW-PC-QTE-07", "p2"),
    FitItem("11", "PCI-DSS payment", "FIT",
        "PCI-DSS compliant gateway with retry flow aligns with PolicyCenter billing & payment security standard.",
        "Payment Gateway", "GW-PC-BIL-01", "p3"),
    FitItem("12", "Disclosure & e-signature capture", "GAP",
        "PolicyCenter captures an auditable disclosure acknowledgement / e-signature before issuance. SOP issues "
        "on payment with no recorded acceptance of terms — compliance and dispute exposure.",
        "Application Processing", "GW-PC-ISS-04", "p3"),
    FitItem("13", "Instant issuance & documents", "FIT",
        "Instant policy issuance with certificate, schedule and PDS within minutes aligns with PolicyCenter issuance.",
        "Application Processing / PAS", "GW-PC-ISS-01", "p3"),
    FitItem("14", "Onboarding & welcome", "FIT",
        "Welcome SMS with policy number, claims line and portal link aligns with PolicyCenter onboarding fulfilment.",
        "CRM", "GW-PC-ISS-06", "p3"),
    FitItem("15", "Cross-sell / next-best-action", "PARTIAL",
        "No cross-sell or next-best-action at bind. PolicyCenter recommends a post-bind cross-sell prompt "
        "(e.g. bundle renters with auto).",
        "Digital Ops / CRM", "GW-PC-ISS-07", "p3"),
]

fitgap = FitGap(
    overall_fit=70, partial_pct=14, fits=8, gaps=4, partials=3,
    steps_analysed=15, phases_count=3,
    summary_line="Overall alignment of SOP-INS-001 against the Guidewire PolicyCenter digital catalog",
    metrics=[
        ("Steps analysed", "15 steps across 3 phases"),
        ("Fits confirmed", "8 steps aligned to catalog"),
        ("Gaps identified", "4 steps — remediation required"),
        ("Partial fits", "3 steps — enhancement recommended"),
        ("Highest risk area", "Identity verification (missing)"),
        ("Compliance gap", "No disclosure / e-signature capture"),
        ("Ref standard", "Guidewire PolicyCenter Digital Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Quote", 74, ""),
        FitPhaseBar("Phase 2", "Underwriting", 62, ""),
        FitPhaseBar("Phase 3", "Issuance", 76, ""),
        FitPhaseBar("Identity /", "fraud", 40, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 74, "Quote generation"),
        PhaseScoreCard("Phase 2", 62, "Application & UW"),
        PhaseScoreCard("Phase 3", 76, "Payment & issuance"),
        PhaseScoreCard("Identity", 40, "eKYC & screening"),
    ],
    detail_slides=[
        ("Phase 1 — Quote generation", "Steps 1–4 vs Guidewire PolicyCenter digital catalog", ["p1"]),
        ("Phase 2 — Application & underwriting", "Steps 5–10 vs Guidewire PolicyCenter digital catalog", ["p2"]),
        ("Phase 3 — Payment & issuance", "Steps 11–15 vs Guidewire PolicyCenter digital catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — QUOTE GENERATION"),
            ("p2", "PHASE 2 — APPLICATION & UNDERWRITING"),
            ("p3", "PHASE 3 — PAYMENT & ISSUANCE")],
    critical_missing=[
        CriticalGap("Identity verification (eKYC)",
            "No identity-proofing or eKYC at quote/application. PolicyCenter requires identity verification before "
            "binding to control application fraud and synthetic-identity risk."),
        CriticalGap("Sanctions / PEP screening",
            "Applicants are not screened against sanctions/watchlists before issuance, a regulatory control in the catalog."),
        CriticalGap("Disclosure & e-signature",
            "Policies are issued on payment with no recorded acknowledgement of terms/PDS — compliance and dispute exposure."),
        CriticalGap("Usage-based rating option",
            "No telematics/usage-based rating for auto, a pricing-accuracy and competitiveness gap vs the catalog."),
    ],
    radar=[("Quote / rating", 80), ("Bureau data", 78), ("Auto-accept", 62), ("Identity / fraud", 35),
           ("Payment security", 85), ("Disclosure / e-sign", 30), ("Onboarding", 78)],
    control_bars=[
        ControlBar("Quote & rating", 80, "Real-time rating with live recalculation"),
        ControlBar("Bureau data integration", 78, "MVR, claims, credit within 60s"),
        ControlBar("Auto-accept rules", 62, "Rules-based; no predictive risk model"),
        ControlBar("Identity / fraud", 35, "No eKYC or identity proofing at application"),
        ControlBar("Sanctions screening", 30, "No watchlist/PEP screening before bind"),
        ControlBar("Payment security", 85, "PCI-DSS gateway with retry control"),
        ControlBar("Disclosure capture", 30, "No e-signature / terms acknowledgement"),
    ],
    remediations=[
        Remediation(1, "Add identity verification (eKYC) at application",
            "Insert an identity-proofing / eKYC step before underwriting, with device and document checks for "
            "elevated-risk applications. Effort: 4 weeks (vendor integration).", "High"),
        Remediation(2, "Add sanctions / PEP screening before issuance",
            "Screen every applicant against sanctions and PEP watchlists; auto-clear matches below threshold and "
            "route hits to Compliance. Effort: 3 weeks.", "High"),
        Remediation(3, "Capture disclosure acknowledgement & e-signature",
            "Require an auditable acceptance of the PDS/terms (e-signature) before issuance; store in PAS against "
            "the policy. Effort: 3 weeks.", "High"),
        Remediation(4, "Introduce usage-based / telematics rating for auto",
            "Offer an opt-in telematics rating tier at quote with a discount for safe-driving data. Effort: 8 weeks "
            "(telematics partner).", "Medium"),
        Remediation(5, "Add predictive risk scoring & post-bind cross-sell",
            "Layer a predictive risk-model score over the rules engine to widen straight-through acceptance, and add "
            "a post-bind cross-sell prompt. Effort: 6 weeks.", "Medium"),
    ],
    risk_impact=[("Identity / fraud", 90), ("Disclosure / e-sign", 78), ("Sanctions screening", 75),
                 ("Telematics pricing", 60), ("Predictive scoring", 55), ("Cross-sell", 45)],
    projected_fit=91,
)

opt_phases = [
    Phase("1", "Quote & identity", "Quote, eKYC, telematics option", "blue",
          "Applicant · Portal · Rating", "Steps 1–6", "6 steps"),
    Phase("2", "Application & underwriting", "Validation, screening, risk model", "green",
          "Applicant · Rules Engine · Underwriting", "Steps 7–11", "5 steps + 1 decision"),
    Phase("3", "Payment, issuance & onboarding", "Payment, e-sign, issuance, cross-sell", "amber",
          "Applicant · Gateway · App Processing · CRM", "Steps 12–17", "6 steps + 1 decision"),
]

opt_steps = [
    Step("1", "1", "Applicant enters vehicle/property and personal details", "Applicant",
         "Portal auto-saves; 72-hour session", "Real time", "Standard", kind="trigger"),
    Step("2", "1", "Identity verification (eKYC)", "Applicant / Identity Service",
         "Identity proofed; document and device checks for elevated risk", "Real time",
         "NEW (v2.0) — application-fraud control"),
    Step("3", "1", "Rating engine calculates premium", "Rating Engine",
         "Instant quote; multi-product discount applied", "Instant", "Standard"),
    Step("4", "1", "Telematics / usage-based rating option", "Applicant / Rating Engine",
         "Opt-in telematics tier offered for auto with safe-driving discount", "Real time", "NEW (v2.0)"),
    Step("5", "1", "Quote presented with coverage options", "Portal",
         "Quote reference; valid 30 days", "Instant", "Standard"),
    Step("6", "1", "Applicant selects coverage tier and endorsements", "Applicant",
         "Premium recalculated in real time", "Real time", "Standard"),
    Step("7", "2", "Application submitted with bureau checks", "Applicant / PAS",
         "Application ID; MVR, claims, credit within 60s", "≤60 sec", "Standard"),
    Step("8", "2", "Sanctions / PEP screening", "Underwriting / Compliance",
         "Applicant screened against sanctions and PEP watchlists before bind", "Instant",
         "NEW (v2.0) — regulatory control"),
    Step("9", "2", "Auto-accept with predictive risk score", "Rules + Model Engine",
         "Rules plus predictive risk-model score widen straight-through acceptance", "Instant",
         "ENHANCED (v2.0)"),
    Step("10", "2", "Manual underwriting review (referred)", "Underwriting Staff",
         "Decision within 2 business hours", "≤2 hours", "Standard"),
    Step("11", "2", "Disclosure acknowledgement & e-signature", "Applicant / PAS",
         "Auditable acceptance of PDS/terms captured before issuance", "Real time",
         "NEW (v2.0) — compliance control"),
    Step("12", "3", "Applicant proceeds to payment", "Applicant / Payment Gateway",
         "PCI-DSS payment page", "Real time", "Standard"),
    Step("13", "3", "Payment authorised", "Payment Gateway",
         "Authorisation recorded; retry on failure (max 3)", "Instant", "Standard"),
    Step("14", "3", "Policy issued in PAS", "Application Processing",
         "Policy number; coverage effective on payment", "≤10 min", "Standard"),
    Step("15", "3", "Policy documents emailed", "PAS / Email Engine",
         "Certificate, schedule and PDS within 5 minutes", "≤5 min", "Standard"),
    Step("16", "3", "Welcome SMS & onboarding", "CRM",
         "Policy number, claims line and portal link sent", "≤10 min", "Standard"),
    Step("17", "3", "Post-bind cross-sell prompt", "Digital Ops / CRM",
         "Next-best-action offer (e.g. bundle renters with auto) presented", "Post-bind",
         "NEW (v2.0) — growth", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "Quote & identity", "Steps 1–6 · v2.0 adds eKYC & telematics",
        ["Applicant", "Portal / Rating", "Identity Service"],
        [SwimNode("o1", "Applicant", 0, "Enter details", "vehicle / property"),
         SwimNode("o2", "Identity Service", 1, "Identity verification", "eKYC", kind="new"),
         SwimNode("o3", "Portal / Rating", 2, "Rating engine quote", "instant premium"),
         SwimNode("o4", "Portal / Rating", 3, "Telematics option", "usage-based", kind="new"),
         SwimNode("o5", "Applicant", 4, "Select tier & endorsements", "premium recalculated")],
        [SwimEdge("o1", "o2", dashed=True, kind="new", label="KYC"), SwimEdge("o2", "o3"),
         SwimEdge("o3", "o4", dashed=True, kind="new"), SwimEdge("o4", "o5")],
        "v2.0 adds identity proofing (eKYC) and an opt-in telematics/usage-based rating tier for auto."),
    SwimPhase("2", "Application & underwriting", "Steps 7–11 · screening & predictive scoring",
        ["Applicant / PAS", "Rules / Model Engine", "Underwriting / Compliance"],
        [SwimNode("p1", "Applicant / PAS", 0, "Submit & bureau checks", "MVR · claims · credit"),
         SwimNode("p2", "Underwriting / Compliance", 1, "Sanctions / PEP screening", "watchlists", kind="new"),
         SwimNode("p3", "Rules / Model Engine", 1, "Auto-accept + risk model", "predictive score", kind="enhanced"),
         SwimNode("p4", "Underwriting / Compliance", 2, "Manual UW review", "referred · ≤2h"),
         SwimNode("p5", "Applicant / PAS", 2, "Disclosure & e-signature", "PDS acceptance", kind="new")],
        [SwimEdge("p1", "p2", dashed=True, kind="new"), SwimEdge("p1", "p3"),
         SwimEdge("p3", "p4", label="ref"), SwimEdge("p3", "p5", dashed=True, kind="new", label="ok")],
        "v2.0 screens applicants against sanctions lists, adds a predictive risk score, and captures an auditable disclosure e-signature before issuance."),
    SwimPhase("3", "Payment, issuance & onboarding", "Steps 12–17 · v2.0 adds cross-sell",
        ["Applicant / Gateway", "Application Processing", "CRM / PAS"],
        [SwimNode("q1", "Applicant / Gateway", 0, "Proceed to payment", "PCI-DSS page"),
         SwimNode("q2", "Applicant / Gateway", 1, "Payment authorised", "max 3 retries"),
         SwimNode("q3", "Application Processing", 2, "Issue policy in PAS", "policy number"),
         SwimNode("q4", "CRM / PAS", 3, "Email documents & SMS", "cert · schedule · PDS"),
         SwimNode("q5", "CRM / PAS", 4, "Post-bind cross-sell", "next-best-action", kind="new")],
        [SwimEdge("q1", "q2"), SwimEdge("q2", "q3"), SwimEdge("q3", "q4"),
         SwimEdge("q4", "q5", dashed=True, kind="new", label="x-sell")],
        "On payment the policy issues instantly; v2.0 adds a post-bind cross-sell prompt to the onboarding flow."),
]

optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Guidewire PolicyCenter Digital Sales & Underwriting Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-001"),
                ("Version", "2.0 (Optimised)"),
                ("Effective Date", "01 October 2026"),
                ("Supersedes", "v1.2 dated 01 April 2025"),
                ("Owner", "Digital Sales & Distribution"),
                ("Approved By", "Chief Distribution Officer"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-001 dated 18 June 2026"),
                ("Catalog Alignment Score", "91% (up from 70% in v1.2)"),
                ("Classification", "Internal Use Only"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v2.0",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-001. Alignment to the "
              "Guidewire PolicyCenter digital catalog increased from 70% to 91%. Critical additions: identity "
              "verification (eKYC), sanctions/PEP screening, disclosure e-signature capture, a telematics rating "
              "option, predictive risk scoring, and a post-bind cross-sell prompt."],
             ["NEW STEP (green) — step added to close a gap vs the PolicyCenter catalog",
              "ENHANCED (amber) — existing step updated with additional controls or automation"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines the end-to-end process for receiving, processing "
             "and converting online insurance applications submitted through the Meridian digital portal for auto "
             "and renter's products. Version 2.0 incorporates optimisations from fit-gap analysis against the "
             "Guidewire PolicyCenter Digital Sales & Underwriting Best-Practice Catalog, achieving 91% alignment "
             "(up from 70% in v1.2)."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to all auto and renter's insurance applications submitted via the "
             "Meridian online portal or mobile app, including quote generation, underwriting, payment and issuance."),
            ("banner", "new", "Scope extended: identity verification (eKYC) and sanctions screening now apply to "
             "every online application before binding."),
            ("para", "This procedure does NOT cover agent/broker applications (SOP-INS-008), commercial lines, or "
             "life insurance products."),
        ]),
        DocSection("3. Underwriting Authority Matrix", [
            ("table", ["Decision", "First Authority", "Second Authority"],
             [["Auto-accept (rules + model clear)", "Rules + Model Engine", "—"],
              ["Referred — standard risk", "Underwriting Staff", "—"],
              ["Referred — elevated risk", "Senior Underwriter", "Underwriting Staff"],
              ["Manual rating adjustment", "Senior Underwriter", "—"],
              ["Decline / hard exclusion", "Underwriting Manager", "Senior Underwriter"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Applicant", "Provides accurate information; completes identity verification; accepts disclosures; pays premium."],
              ["Digital Operations Analyst", "Monitors the application queue; manages abandonment recovery; escalates fraud and identity flags."],
              ["Underwriting Staff", "Reviews referred applications; sets manual rating; approves or declines borderline cases."],
              ["Compliance", "Owns sanctions/PEP screening dispositions and adverse-action governance."],
              ["Application Processing Staff", "Validates data; issues policy documents; maintains PAS records."],
              ["Customer Service", "Assists with status, payment failures and manual completion."]], {}),
        ]),
        DocSection("5. Identity & Screening (New Section — v2.0)", [
            ("banner", "crit", "New section. Required by the PolicyCenter catalog. Identity verification and sanctions "
             "screening must complete before any policy is bound."),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["I1", "Identity verification (eKYC)", "Identity Service",
               "Identity proofed; document/device checks for elevated risk", "Real time"],
              ["I2", "Sanctions / PEP screening", "Compliance",
               "Applicant screened against sanctions and PEP watchlists; hits routed to Compliance", "Instant"],
              ["I3", "Disclosure acknowledgement & e-signature", "Applicant / PAS",
               "Auditable acceptance of PDS/terms captured before issuance", "Real time"]],
             {0: "new", 1: "new", 2: "new"}),
        ]),
        DocSection("6. Process Steps", [
            ("h3", "6.1 Quote & Identity"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "Applicant enters vehicle/property and personal details", "Applicant", "Portal auto-saves; 72h session", "Real time"],
              ["2", "Identity verification (eKYC)", "Identity Service", "Identity proofed before underwriting", "Real time"],
              ["3", "Rating engine calculates premium", "Rating Engine", "Instant quote; discounts applied", "Instant"],
              ["4", "Telematics / usage-based rating option", "Applicant / Rating Engine", "Opt-in safe-driving discount (auto)", "Real time"],
              ["5", "Quote presented with coverage options", "Portal", "Quote reference; valid 30 days", "Instant"],
              ["6", "Applicant selects coverage tier and endorsements", "Applicant", "Premium recalculated live", "Real time"]],
             {1: "new", 3: "new"}),
            ("h3", "6.2 Application & Underwriting"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["7", "Application submitted with bureau checks", "Applicant / PAS", "MVR, claims, credit within 60s", "≤60 sec"],
              ["8", "Sanctions / PEP screening", "Compliance", "Watchlist screening before bind", "Instant"],
              ["9", "Auto-accept with predictive risk score", "Rules + Model Engine", "Rules + model widen straight-through acceptance", "Instant"],
              ["10", "Manual underwriting review (referred)", "Underwriting Staff", "Decision within 2 business hours", "≤2 hours"],
              ["11", "Disclosure acknowledgement & e-signature", "Applicant / PAS", "PDS/terms acceptance captured", "Real time"]],
             {1: "new", 2: "enh", 4: "new"}),
            ("h3", "6.3 Payment, Issuance & Onboarding"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["12", "Applicant proceeds to payment", "Applicant / Gateway", "PCI-DSS payment page", "Real time"],
              ["13", "Payment authorised", "Payment Gateway", "Authorisation recorded; retry on failure", "Instant"],
              ["14", "Policy issued in PAS", "Application Processing", "Policy number; effective on payment", "≤10 min"],
              ["15", "Policy documents emailed", "PAS / Email Engine", "Certificate, schedule, PDS within 5 min", "≤5 min"],
              ["16", "Welcome SMS & onboarding", "CRM", "Policy number, claims line, portal link", "≤10 min"],
              ["17", "Post-bind cross-sell prompt", "Digital Ops / CRM", "Next-best-action bundle offer", "Post-bind"]],
             {5: "new"}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Abandoned Application"),
            ("numbered", [
                "Automated reminder emails at 24 and 72 hours after last activity.",
                "No completion after 7 days: application archived; applicant may restart with the saved quote reference.",
                "Digital Operations reviews the weekly abandonment report and may call high-value quotes."]),
            ("h3", "7.2 Payment Failure"),
            ("numbered_from", 4, [
                "Applicant may retry with the same or an alternate method (maximum 3 attempts per session).",
                "After 3 failures the applicant is directed to Customer Service; the application is held 24 hours.",
                "Customer Service may complete payment via an alternate channel and issue manually."]),
            ("h3", "7.3 Identity or Screening Hold (New — v2.0)"),
            ("banner", "new", "New exception. Applications failing eKYC or hitting a sanctions match are held pending Compliance review."),
            ("numbered_from", 7, [
                "eKYC failure: applicant offered a document-upload fallback; unresolved cases are referred to Digital Operations.",
                "Sanctions/PEP hit: application held; Compliance dispositions within 1 business day before any bind."]),
            ("h3", "7.4 Underwriting Decline"),
            ("numbered_from", 9, [
                "Applicant receives a written decline notice within 2 business hours with statutory reason codes.",
                "Application flagged in PAS; applicant may reapply after 90 days unless a hard exclusion applies."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["Meridian Customer Portal", "Application capture, quote display, document delivery", "Applicants, Digital Ops"],
              ["Policy Administration System (PAS)", "Policy creation, documents, status tracking", "Digital Ops, Underwriting, App Processing"],
              ["Rating Engine", "Real-time and telematics rating", "Automated"],
              ["Identity / eKYC Service", "Identity proofing and document/device checks", "Applicants, Digital Ops"],
              ["Underwriting Rules + Model Engine", "Auto-accept rules and predictive risk scoring", "Automated, Underwriting"],
              ["Sanctions Screening Tool", "Sanctions / PEP watchlist screening", "Compliance"],
              ["Payment Gateway (Stripe)", "PCI-DSS payment, authorisation, refunds", "Applicants, Customer Service"],
              ["CRM (Salesforce)", "Communications, abandonment, cross-sell", "Digital Ops, Customer Service"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v2.0: identity verification, sanctions screening, disclosure "
             "e-signature, and predictive risk scoring."),
            ("bullets", [
                "Identity gate: no application proceeds to underwriting without eKYC.",
                "Sanctions screening: every applicant screened before binding; hits dispositioned by Compliance.",
                "Disclosure capture: auditable PDS/terms acceptance recorded before issuance.",
                "Predictive scoring: rules-engine acceptance refined by a governed risk model.",
                "Payment security: PCI-DSS gateway with controlled retry.",
                "Adverse action: statutory reason codes on every decline.",
                "Immutable audit trail: quote, identity, screening, payment and issuance events logged."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v1.2 Target", "v2.0 Target", "Measurement"],
             [["Quote-to-bind conversion", "≥18%", "≥22%", "Bound policies / completed quotes"],
              ["Straight-through acceptance", "Rules only", "≥75% with model", "Auto-accept rate"],
              ["Identity pass rate", "N/A (new)", "≥97% eKYC pass", "eKYC service report"],
              ["Sanctions screening", "N/A (new)", "100% screened pre-bind", "Screening log"],
              ["Issuance time (auto-accept)", "≤10 min", "≤10 min", "Payment to issuance"],
              ["Payment failure rate", "<4%", "<3%", "Failed / total attempts"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["1.2", "01 Apr 2025", "P. Santos, Digital Ops", "Added SMS welcome step; aligned bureau check SLAs"],
              ["2.0", "01 Oct 2026", "P. Santos, Digital Ops",
               "OPTIMISED: eKYC; sanctions screening; disclosure e-signature; telematics rating; predictive "
               "scoring; post-bind cross-sell; catalog alignment 70% → 91%"]], {}),
        ]),
    ],
)

package = SopPackage(
    meta=meta, phases=phases, steps=steps, authority=authority, swim_phases=swim_phases,
    n_phases=3, n_steps=13, n_roles=5, n_gateways=3,
    fitgap=fitgap,
    opt_phases=opt_phases, opt_steps=opt_steps, opt_swim_phases=opt_swim_phases,
    opt_n_phases=3, opt_n_steps=17, opt_n_gateways=3, opt_fit=91,
    optimised_doc=optimised_doc,
    swim_cover_tags="Quote · Underwriting · Payment · Issuance · Exception handling",
    hierarchy_cover_sub="Phase breakdown with digital sales tracks, underwriting authority, and exception paths",
)
