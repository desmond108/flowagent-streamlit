"""SOP-INS-005 — Insurance Licensing and Contracting (Meridian Insurance Group).

Fit-gap vs the Sircon (Vertafore) Producer Lifecycle Management catalog.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Sircon (Vertafore) — Producer Lifecycle Management Best-Practice Catalog"
CATALOG_SHORT = "Sircon PLM"

meta = Meta(
    sop_id="SOP-INS-005", slug="Licensing_and_Contracting",
    title="Insurance Licensing and Contracting", short_title="Licensing & contracting",
    version="1.4", owner="Distribution & Licensing",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="2.0", effective_date="01 October 2026",
    supersedes="v1.4 dated 01 February 2025", approved_by="Chief Distribution Officer",
    classification="Internal Use Only",
)

phases = [
    Phase("1", "New agent appointment", "Verify, screen, train, appoint", "blue",
          "Sales Mgr · Licensing · Compliance · DMS", "Steps 1–7", "7 steps + 1 decision"),
    Phase("2", "Licence renewal", "Alerts, CE, renewal filing", "green",
          "Licensing System · Licensing Specialist", "Steps 8–11", "4 steps"),
    Phase("3", "Termination", "Terminate, file, deactivate", "amber",
          "Sales Mgr · Document Mgr · Licensing", "Steps 12–15", "4 steps"),
]

steps = [
    Step("1", "1", "Onboarding request submitted by Regional Sales Manager", "Regional Sales Manager",
         "Candidate details, product lines, territory and proposed date", "Day 0", "Appointment trigger", kind="trigger"),
    Step("2", "1", "Licence verification with regulatory authority", "Licensing Specialist",
         "Status, expiry and CE compliance confirmed via regulator portal; recorded in AgentOS", "Day 1–2", "Regulator verification"),
    Step("3", "1", "Background check initiated", "Licensing Specialist / Compliance",
         "Criminal, credit and conduct check; Compliance reviews adverse findings within 3 days", "Day 1–4", "Compliance review"),
    Step("4", "1", "Pre-appointment compliance training assigned", "Licensing Specialist",
         "Code of Conduct, AML and Product Knowledge via LMS; complete before filing", "Day 2–6", "Mandatory training gate"),
    Step("5", "1", "Distribution agreement executed", "Document Manager / Representative",
         "Standard agreement signed via DocuSign; filed in DMS", "Day 6", "Executed agreement"),
    Step("6", "1", "Appointment filing submitted to regulator", "Licensing Specialist",
         "Filed via regulator portal; confirmation recorded; 5–15 business days processing", "Day 6", "Regulatory filing"),
    Step("7", "1", "Appointment confirmed; agent activated in PAS and CRM", "Licensing Specialist",
         "Agent record created; product authorities, territory and commission tier set", "Day 10", "Activation", kind="complete"),
    Step("", "1", "", "", "", "", "Compliance disposition", kind="decision", decision="Adverse background findings?",
         branches=["None / minor (justified) → proceed", "Material → automatic rejection (Sec 6.1)"]),
    Step("8", "2", "Renewal alert triggered 90 days before expiry", "Licensing System (auto)",
         "Agent and Licensing Specialist notified by email", "Expiry −90", "Automated renewal alert", kind="trigger"),
    Step("9", "2", "CE credit verification", "Licensing Specialist",
         "CE transcript reviewed; shortfall notified with required hours and providers", "Expiry −60", "CE compliance check"),
    Step("10", "2", "Renewal application filed with regulator", "Licensing Specialist",
         "Filed at least 30 days before expiry; renewal fee paid from licensing budget", "Expiry −30", "Renewal filing SLA"),
    Step("11", "2", "Renewal confirmation recorded", "Licensing Specialist",
         "New expiry date updated in AgentOS and PAS; agent notified", "Expiry −15", "Confirmation"),
    Step("12", "3", "Termination request initiated (voluntary or for cause)", "Sales Manager / Compliance",
         "Reason code recorded; final commission run initiated; open cases reviewed", "Day 0", "Termination trigger", kind="trigger"),
    Step("13", "3", "Distribution agreement terminated", "Document Manager",
         "Termination notice executed per agreement terms; copy filed in DMS", "Day 1–3", "Agreement termination"),
    Step("14", "3", "Termination filing submitted to regulator", "Licensing Specialist",
         "Appointment withdrawal filed within 30 days of effective termination", "≤30 days", "Withdrawal filing"),
    Step("15", "3", "Agent record deactivated in PAS and CRM", "Licensing Specialist",
         "System access revoked; policy book transferred to replacement agent", "Day 3–5", "Deactivation", kind="complete"),
]

authority = [
    AuthorityRow("Standard appointment", "Licensing Specialist", "—"),
    AuthorityRow("Minor adverse history", "Compliance Officer", "Licensing Specialist"),
    AuthorityRow("Material adverse / rejection", "Compliance Officer", "Chief Distribution Officer"),
    AuthorityRow("For-cause termination", "Compliance Officer", "Regional Sales Manager"),
    AuthorityRow("Reinstatement after lapse", "Compliance Officer", "Licensing Specialist"),
]

swim_phases = [
    SwimPhase("1", "New agent appointment", "Steps 1–7 · verify, screen, train, appoint",
        ["Sales / Rep", "Licensing Specialist", "Compliance", "DMS"],
        [SwimNode("s1", "Sales / Rep", 0, "Onboarding request", "Regional Sales Mgr"),
         SwimNode("s2", "Licensing Specialist", 1, "Licence verification", "regulator portal"),
         SwimNode("s3", "Compliance", 1, "Background check", "criminal · credit · conduct"),
         SwimNode("s4", "Licensing Specialist", 2, "Assign pre-appointment training", "AML · conduct"),
         SwimNode("s5", "Compliance", 2, "Material adverse → reject", "Sec 6.1", kind="exception"),
         SwimNode("s6", "DMS", 2, "Execute distribution agreement", "DocuSign"),
         SwimNode("s7", "Licensing Specialist", 3, "Appointment filing", "regulator portal"),
         SwimNode("s8", "Licensing Specialist", 4, "Activate agent", "PAS · CRM", kind="terminal")],
        [SwimEdge("s1", "s2", dashed=True), SwimEdge("s2", "s3"),
         SwimEdge("s3", "s4"), SwimEdge("s3", "s5", dashed=True, kind="exception", label="adv"),
         SwimEdge("s4", "s6"), SwimEdge("s6", "s7"), SwimEdge("s7", "s8")],
        "Appointments require regulator verification, background screening, mandatory training and an executed agreement before filing."),
    SwimPhase("2", "Licence renewal", "Steps 8–11 · alerts, CE, filing",
        ["Licensing System", "Licensing Specialist", "Regulator"],
        [SwimNode("a1", "Licensing System", 0, "Renewal alert (90 days)", "auto email"),
         SwimNode("a2", "Licensing Specialist", 1, "CE credit verification", "transcript review"),
         SwimNode("a3", "Regulator", 2, "Renewal application filed", "≥30 days before expiry"),
         SwimNode("a4", "Licensing Specialist", 3, "Record confirmation", "new expiry in PAS", kind="terminal")],
        [SwimEdge("a1", "a2", dashed=True), SwimEdge("a2", "a3"), SwimEdge("a3", "a4")],
        "Renewals are driven by a 90-day alert; CE shortfalls are notified before the renewal is filed at least 30 days pre-expiry."),
    SwimPhase("3", "Termination", "Steps 12–15 · terminate, file, deactivate",
        ["Sales / Compliance", "Document Manager", "Licensing Specialist"],
        [SwimNode("d1", "Sales / Compliance", 0, "Termination request", "voluntary / for cause"),
         SwimNode("d2", "Document Manager", 1, "Terminate agreement", "DMS filed"),
         SwimNode("d3", "Licensing Specialist", 2, "Termination filing", "≤30 days"),
         SwimNode("d4", "Licensing Specialist", 3, "Deactivate agent", "access revoked", kind="terminal")],
        [SwimEdge("d1", "d2"), SwimEdge("d2", "d3"), SwimEdge("d3", "d4")],
        "Terminations execute the agreement, file the regulator withdrawal within 30 days, and revoke access with book transfer."),
]

fg_items = [
    FitItem("1", "Onboarding request capture", "FIT",
        "Structured onboarding request with product lines and territory aligns with Sircon producer onboarding intake.",
        "Regional Sales Manager", "GW-SIR-ONB-01", "p1"),
    FitItem("2", "Regulator licence verification", "PARTIAL",
        "Licence status is verified at appointment via the regulator portal, but checks are point-in-time. Sircon "
        "maintains continuous, real-time licence/appointment synchronisation with regulator (PDB/NIPR) data.",
        "Licensing Specialist", "GW-SIR-LIC-02", "p1"),
    FitItem("3", "Background screening", "FIT",
        "Criminal, credit and conduct screening with Compliance review aligns with Sircon background-check workflow.",
        "Licensing Specialist / Compliance", "GW-SIR-SCR-01", "p1"),
    FitItem("4", "Continuous compliance monitoring", "GAP",
        "Screening occurs only at appointment. Sircon continuously monitors adverse actions, watchlists and licence "
        "standing between renewals — without it, mid-term disqualifying events go undetected.",
        "Compliance Officer", "GW-SIR-MON-01", "p1"),
    FitItem("5", "Pre-appointment training gate", "FIT",
        "Mandatory AML/conduct/product training before filing aligns with Sircon readiness requirements.",
        "Licensing Specialist", "GW-SIR-EDU-01", "p1"),
    FitItem("6", "Distribution agreement execution", "FIT",
        "DocuSign execution with DMS filing and version control aligns with Sircon contracting/onboarding.",
        "Document Manager", "GW-SIR-CON-01", "p1"),
    FitItem("7", "Appointment filing", "PARTIAL",
        "Filing is performed manually through the regulator portal. Sircon automates appointment/termination filings "
        "via direct NIPR/PDB integration, cutting cycle time and transcription error.",
        "Licensing Specialist", "GW-SIR-FIL-01", "p1"),
    FitItem("8", "Agent activation & authorities", "FIT",
        "Agent activation with product authorities, territory and commission tier aligns with Sircon producer setup.",
        "Licensing Specialist", "GW-SIR-ONB-04", "p1"),
    FitItem("9", "Renewal alerting", "FIT",
        "90-day renewal alerting aligns with Sircon licence-expiry management.",
        "Licensing System", "GW-SIR-REN-01", "p2"),
    FitItem("10", "CE tracking", "PARTIAL",
        "CE transcripts are reviewed manually. Sircon auto-syncs CE completions from providers and flags shortfalls "
        "without manual transcript review.",
        "Licensing Specialist", "GW-SIR-EDU-03", "p2"),
    FitItem("11", "Renewal filing", "FIT",
        "Renewal filed at least 30 days before expiry with fee payment aligns with Sircon renewal processing.",
        "Licensing Specialist", "GW-SIR-REN-03", "p2"),
    FitItem("12", "Ready-to-sell enforcement", "GAP",
        "Selling during a lapse is detected after the fact and reviewed for rescission. Sircon enforces a real-time "
        "'ready-to-sell' gate that blocks unlicensed/unappointed sales at point of sale.",
        "Licensing Specialist / PAS", "GW-SIR-RTS-01", "p2"),
    FitItem("13", "Termination & withdrawal filing", "FIT",
        "For-cause/voluntary termination with regulator withdrawal within 30 days aligns with Sircon termination.",
        "Licensing Specialist", "GW-SIR-TRM-01", "p3"),
    FitItem("14", "Deactivation & book transfer", "FIT",
        "Access revocation and policy-book transfer on deactivation align with Sircon offboarding.",
        "Licensing Specialist", "GW-SIR-TRM-03", "p3"),
]

fitgap = FitGap(
    overall_fit=72, partial_pct=16, fits=9, gaps=2, partials=3,
    steps_analysed=14, phases_count=3,
    summary_line="Overall alignment of SOP-INS-005 against the Sircon producer lifecycle catalog",
    metrics=[
        ("Steps analysed", "14 steps across 3 phases"),
        ("Fits confirmed", "9 steps aligned to catalog"),
        ("Gaps identified", "2 steps — remediation required"),
        ("Partial fits", "3 steps — enhancement recommended"),
        ("Highest risk area", "Continuous monitoring (missing)"),
        ("Automation gap", "Manual regulator filing & CE"),
        ("Ref standard", "Sircon Producer Lifecycle Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Appointment", 72, ""),
        FitPhaseBar("Phase 2", "Renewal", 70, ""),
        FitPhaseBar("Phase 3", "Termination", 82, ""),
        FitPhaseBar("Continuous", "monitoring", 40, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 72, "New appointment"),
        PhaseScoreCard("Phase 2", 70, "Renewal"),
        PhaseScoreCard("Phase 3", 82, "Termination"),
        PhaseScoreCard("Monitor", 40, "Continuous compliance"),
    ],
    detail_slides=[
        ("Phase 1 — New agent appointment", "Steps 1–7 vs Sircon producer lifecycle catalog", ["p1"]),
        ("Phase 2 — Licence renewal", "Steps 8–12 vs Sircon producer lifecycle catalog", ["p2"]),
        ("Phase 3 — Termination", "Steps 13–14 vs Sircon producer lifecycle catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — NEW AGENT APPOINTMENT"),
            ("p2", "PHASE 2 — LICENCE RENEWAL"),
            ("p3", "PHASE 3 — TERMINATION")],
    critical_missing=[
        CriticalGap("Continuous compliance monitoring",
            "Screening and licence checks occur only at appointment and renewal. The catalog monitors adverse "
            "actions, watchlists and licence standing continuously, so mid-term disqualifying events are caught early."),
        CriticalGap("Ready-to-sell enforcement at point of sale",
            "Sales during a lapse are only detected after the fact and reviewed for rescission. The catalog enforces "
            "a real-time ready-to-sell gate that blocks unlicensed/unappointed sales."),
        CriticalGap("Automated regulator filing (NIPR/PDB)",
            "Appointment, renewal and termination filings are manual through the regulator portal; the catalog "
            "integrates filings directly with NIPR/PDB, reducing cycle time and transcription error."),
        CriticalGap("Automated CE synchronisation",
            "CE is verified by manual transcript review; the catalog auto-syncs CE completions from providers."),
    ],
    radar=[("Onboarding", 82), ("Verification", 65), ("Screening", 78), ("Monitoring", 38),
           ("Renewal", 70), ("Ready-to-sell", 42), ("Termination", 84)],
    control_bars=[
        ControlBar("Onboarding & contracting", 82, "Structured intake and DocuSign execution"),
        ControlBar("Licence verification", 65, "Point-in-time; no continuous sync"),
        ControlBar("Background screening", 78, "Criminal/credit/conduct at appointment"),
        ControlBar("Continuous monitoring", 38, "No between-renewal adverse-action monitoring"),
        ControlBar("Renewal & CE", 70, "90-day alert; manual CE transcript review"),
        ControlBar("Ready-to-sell", 42, "Lapse detected after the fact"),
        ControlBar("Termination", 84, "For-cause handling and withdrawal filing solid"),
    ],
    remediations=[
        Remediation(1, "Implement continuous compliance monitoring",
            "Subscribe to adverse-action, watchlist and licence-standing feeds so disqualifying events between "
            "renewals are flagged and dispositioned. Effort: 5 weeks (AgentOS + feeds).", "High"),
        Remediation(2, "Enforce a ready-to-sell gate at point of sale",
            "Block quote/bind in PAS for any producer not currently licensed and appointed for the product and "
            "territory. Effort: 4 weeks.", "High"),
        Remediation(3, "Automate regulator filings via NIPR/PDB integration",
            "Replace manual portal filings with direct appointment/renewal/termination filing integration. "
            "Effort: 6 weeks.", "High"),
        Remediation(4, "Automate CE synchronisation",
            "Auto-sync CE completions from approved providers and flag shortfalls without manual transcript review. "
            "Effort: 3 weeks.", "Medium"),
        Remediation(5, "Add producer self-service onboarding portal",
            "Let producers submit documents, sign agreements and track status in a self-service portal. "
            "Effort: 5 weeks.", "Medium"),
    ],
    risk_impact=[("Continuous monitoring", 85), ("Ready-to-sell gate", 80), ("Regulator filing", 70),
                 ("CE automation", 58), ("Self-service onboarding", 48), ("Verification sync", 55)],
    projected_fit=92,
)

opt_phases = [
    Phase("1", "Appointment & monitoring", "Verify, screen, train, monitor", "blue",
          "Sales · Licensing · Compliance · DMS", "Steps 1–8", "8 steps + 1 decision"),
    Phase("2", "Renewal & readiness", "Alerts, CE sync, ready-to-sell", "green",
          "Licensing System · Specialist · PAS", "Steps 9–12", "4 steps"),
    Phase("3", "Termination", "Terminate, file, deactivate", "amber",
          "Sales · Document Mgr · Licensing", "Steps 13–16", "4 steps"),
]

opt_steps = [
    Step("1", "1", "Onboarding request submitted by Regional Sales Manager", "Regional Sales Manager",
         "Candidate details, product lines, territory", "Day 0", "Standard", kind="trigger"),
    Step("2", "1", "Continuous licence verification (regulator sync)", "Licensing Specialist / System",
         "Real-time licence/appointment sync with regulator (PDB/NIPR) data", "Day 1",
         "ENHANCED (v2.0) — continuous"),
    Step("3", "1", "Background check initiated", "Licensing Specialist / Compliance",
         "Criminal, credit and conduct check; Compliance review within 3 days", "Day 1–4", "Standard"),
    Step("4", "1", "Enrol in continuous compliance monitoring", "Compliance Officer / System",
         "Adverse-action and watchlist feeds enabled for ongoing monitoring", "Day 1",
         "NEW (v2.0) — between-renewal monitoring"),
    Step("5", "1", "Pre-appointment compliance training", "Licensing Specialist",
         "AML, conduct and product modules via LMS before filing", "Day 2–6", "Standard"),
    Step("6", "1", "Distribution agreement executed", "Document Manager / Representative",
         "DocuSign execution; filed in DMS", "Day 6", "Standard"),
    Step("7", "1", "Automated appointment filing (NIPR/PDB)", "Licensing Specialist / System",
         "Appointment filed via direct regulator integration; confirmation auto-recorded", "Day 6",
         "ENHANCED (v2.0) — automated filing"),
    Step("8", "1", "Appointment confirmed; agent activated", "Licensing Specialist",
         "Agent record, authorities, territory, commission tier set", "Day 8", "Standard", kind="complete"),
    Step("", "1", "", "", "", "", "Compliance disposition", kind="decision", decision="Adverse findings?",
         branches=["None / minor (justified) → proceed", "Material → rejection (Sec 6.1)"]),
    Step("9", "2", "Renewal alert triggered 90 days before expiry", "Licensing System",
         "Agent and Specialist notified", "Expiry −90", "Standard", kind="trigger"),
    Step("10", "2", "Automated CE synchronisation", "Licensing System",
         "CE completions auto-synced from providers; shortfalls flagged automatically", "Expiry −60",
         "NEW (v2.0) — automated CE"),
    Step("11", "2", "Automated renewal filing", "Licensing Specialist / System",
         "Renewal filed ≥30 days before expiry via regulator integration; fee paid", "Expiry −30",
         "ENHANCED (v2.0)"),
    Step("12", "2", "Ready-to-sell status published to PAS", "Licensing System / PAS",
         "Real-time ready-to-sell flag enforced at point of sale; expired producers blocked", "Continuous",
         "NEW (v2.0) — point-of-sale gate", kind="control"),
    Step("13", "3", "Termination request initiated", "Sales Manager / Compliance",
         "Reason code; final commission run; open cases reviewed", "Day 0", "Standard", kind="trigger"),
    Step("14", "3", "Distribution agreement terminated", "Document Manager",
         "Termination notice executed; filed in DMS", "Day 1–3", "Standard"),
    Step("15", "3", "Automated termination filing", "Licensing Specialist / System",
         "Appointment withdrawal filed via regulator integration within 30 days", "≤30 days",
         "ENHANCED (v2.0)"),
    Step("16", "3", "Agent record deactivated; book transferred", "Licensing Specialist",
         "Access revoked; book transferred to replacement agent", "Day 3–5", "Standard", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "Appointment & monitoring", "Steps 1–8 · v2.0 adds continuous monitoring",
        ["Sales / Rep", "Licensing Specialist", "Compliance", "DMS"],
        [SwimNode("o1", "Sales / Rep", 0, "Onboarding request", "Regional Sales Mgr"),
         SwimNode("o2", "Licensing Specialist", 1, "Continuous licence sync", "regulator (PDB/NIPR)", kind="enhanced"),
         SwimNode("o3", "Compliance", 1, "Background check", "criminal · credit · conduct"),
         SwimNode("o4", "Compliance", 2, "Enrol continuous monitoring", "adverse-action feeds", kind="new"),
         SwimNode("o5", "Licensing Specialist", 2, "Pre-appointment training", "AML · conduct"),
         SwimNode("o6", "DMS", 3, "Execute agreement", "DocuSign"),
         SwimNode("o7", "Licensing Specialist", 4, "Automated appointment filing", "NIPR/PDB", kind="enhanced")],
        [SwimEdge("o1", "o2", dashed=True), SwimEdge("o2", "o3"),
         SwimEdge("o3", "o4", dashed=True, kind="new", label="monitor"), SwimEdge("o3", "o5"),
         SwimEdge("o5", "o6"), SwimEdge("o6", "o7")],
        "v2.0 adds continuous licence sync and ongoing compliance monitoring, and automates appointment filing via regulator integration."),
    SwimPhase("2", "Renewal & readiness", "Steps 9–12 · v2.0 adds CE sync & ready-to-sell",
        ["Licensing System", "Licensing Specialist", "PAS / Point of sale"],
        [SwimNode("p1", "Licensing System", 0, "Renewal alert (90 days)", "auto email"),
         SwimNode("p2", "Licensing System", 1, "Automated CE sync", "providers", kind="new"),
         SwimNode("p3", "Licensing Specialist", 2, "Automated renewal filing", "≥30 days", kind="enhanced"),
         SwimNode("p4", "PAS / Point of sale", 3, "Ready-to-sell gate", "block expired", kind="new")],
        [SwimEdge("p1", "p2", dashed=True, kind="new"), SwimEdge("p2", "p3"),
         SwimEdge("p3", "p4", dashed=True, kind="new", label="RTS")],
        "v2.0 auto-syncs CE, files renewals via regulator integration, and publishes a ready-to-sell flag enforced at point of sale."),
    SwimPhase("3", "Termination", "Steps 13–16 · automated withdrawal filing",
        ["Sales / Compliance", "Document Manager", "Licensing Specialist"],
        [SwimNode("q1", "Sales / Compliance", 0, "Termination request", "voluntary / for cause"),
         SwimNode("q2", "Document Manager", 1, "Terminate agreement", "DMS filed"),
         SwimNode("q3", "Licensing Specialist", 2, "Automated termination filing", "NIPR/PDB", kind="enhanced"),
         SwimNode("q4", "Licensing Specialist", 3, "Deactivate agent", "book transfer", kind="terminal")],
        [SwimEdge("q1", "q2"), SwimEdge("q2", "q3"), SwimEdge("q3", "q4")],
        "Termination withdrawal filings are now automated via regulator integration within the 30-day window."),
]

optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Sircon Producer Lifecycle Management Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-005"),
                ("Version", "2.0 (Optimised)"),
                ("Effective Date", "01 October 2026"),
                ("Supersedes", "v1.4 dated 01 February 2025"),
                ("Owner", "Distribution & Licensing"),
                ("Approved By", "Chief Distribution Officer"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-005 dated 18 June 2026"),
                ("Catalog Alignment Score", "92% (up from 72% in v1.4)"),
                ("Classification", "Internal Use Only"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v2.0",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-005. Alignment to the "
              "Sircon producer lifecycle catalog increased from 72% to 92%. Critical additions: continuous compliance "
              "monitoring, a real-time ready-to-sell gate at point of sale, automated regulator filing (NIPR/PDB), "
              "automated CE synchronisation, and continuous licence verification."],
             ["NEW STEP (green) — step added to close a gap vs the Sircon catalog",
              "ENHANCED (amber) — existing step updated with additional automation or controls"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines the process for licensing, renewing, amending and "
             "terminating insurance distribution agreements with agents and brokers. Version 2.0 incorporates "
             "optimisations from fit-gap analysis against the Sircon Producer Lifecycle Management Best-Practice "
             "Catalog, achieving 92% alignment (up from 72% in v1.4)."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to new agent/broker appointment and licensing, annual renewals and CE "
             "compliance, licence amendments, and voluntary or for-cause terminations."),
            ("banner", "new", "Scope extended: continuous compliance monitoring and a real-time ready-to-sell gate "
             "now apply to every active producer at all times."),
            ("para", "This procedure does NOT cover in-house staff licensing (HR onboarding SOP) or MGA entity "
             "licensing above the defined book threshold (SOP-INS-015)."),
        ]),
        DocSection("3. Authority Matrix", [
            ("table", ["Decision", "First Authority", "Second Authority"],
             [["Standard appointment", "Licensing Specialist", "—"],
              ["Minor adverse history", "Compliance Officer", "Licensing Specialist"],
              ["Material adverse / rejection", "Compliance Officer", "Chief Distribution Officer"],
              ["For-cause termination", "Compliance Officer", "Regional Sales Manager"],
              ["Reinstatement after lapse", "Compliance Officer", "Licensing Specialist"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Insurance Representative", "Completes application and training; maintains active licence and CE; notifies of status changes."],
              ["Licensing Specialist", "Verifies and syncs licences; files appointments/renewals/terminations; manages records."],
              ["Document Manager", "Maintains contracting files; executes agreements; manages contract version control."],
              ["Compliance Officer", "Reviews screening; owns continuous monitoring dispositions and ongoing standing."]], {}),
        ]),
        DocSection("5. Continuous Compliance (New Section — v2.0)", [
            ("banner", "crit", "New section. Required by the Sircon catalog. Continuous monitoring and a ready-to-sell "
             "gate now operate for every active producer, not only at appointment and renewal."),
            ("table", ["#", "Control", "Responsible", "Output / System", "Timeline"],
             [["M1", "Continuous licence/appointment sync", "Licensing Specialist", "Real-time PDB/NIPR data sync", "Continuous"],
              ["M2", "Adverse-action & watchlist monitoring", "Compliance", "Disqualifying events flagged between renewals", "Continuous"],
              ["M3", "Ready-to-sell gate at point of sale", "PAS", "Quote/bind blocked for unlicensed/unappointed producers", "Continuous"]],
             {0: "new", 1: "new", 2: "new"}),
        ]),
        DocSection("6. Process Steps", [
            ("h3", "6.1 Appointment & Monitoring"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "Onboarding request submitted", "Regional Sales Manager", "Candidate, products, territory", "Day 0"],
              ["2", "Continuous licence verification (sync)", "Licensing Specialist", "Real-time regulator sync", "Day 1"],
              ["3", "Background check initiated", "Licensing / Compliance", "Criminal/credit/conduct", "Day 1–4"],
              ["4", "Enrol in continuous monitoring", "Compliance", "Adverse-action/watchlist feeds", "Day 1"],
              ["5", "Pre-appointment compliance training", "Licensing Specialist", "AML/conduct/product via LMS", "Day 2–6"],
              ["6", "Distribution agreement executed", "Document Manager", "DocuSign; filed in DMS", "Day 6"],
              ["7", "Automated appointment filing (NIPR/PDB)", "Licensing Specialist", "Filed via integration", "Day 6"],
              ["8", "Appointment confirmed; agent activated", "Licensing Specialist", "Authorities/territory/tier", "Day 8"]],
             {1: "enh", 3: "new", 6: "enh"}),
            ("h3", "6.2 Renewal & Readiness"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["9", "Renewal alert (90 days before expiry)", "Licensing System", "Agent and Specialist notified", "Expiry −90"],
              ["10", "Automated CE synchronisation", "Licensing System", "CE auto-synced; shortfalls flagged", "Expiry −60"],
              ["11", "Automated renewal filing", "Licensing Specialist", "Filed ≥30 days pre-expiry via integration", "Expiry −30"],
              ["12", "Ready-to-sell status published to PAS", "Licensing System", "Point-of-sale gate enforced", "Continuous"]],
             {1: "new", 2: "enh", 3: "new"}),
            ("h3", "6.3 Termination"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["13", "Termination request initiated", "Sales Manager / Compliance", "Reason code; final commission", "Day 0"],
              ["14", "Distribution agreement terminated", "Document Manager", "Notice executed; DMS filed", "Day 1–3"],
              ["15", "Automated termination filing", "Licensing Specialist", "Withdrawal filed via integration", "≤30 days"],
              ["16", "Agent record deactivated; book transferred", "Licensing Specialist", "Access revoked; book transfer", "Day 3–5"]],
             {2: "enh"}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Adverse Background Check"),
            ("numbered", [
                "Compliance reviews specific findings; minor adverse history may be approved with documented justification.",
                "Material adverse findings (e.g. fraud conviction, prior licence revocation) result in automatic rejection.",
                "All adverse findings and decisions are logged in the Compliance tracking register."]),
            ("h3", "7.2 Licence Expiry Without Renewal (Enhanced — v2.0)"),
            ("banner", "enh", "The ready-to-sell gate now blocks sales the moment a licence lapses, rather than detecting lapse sales after the fact."),
            ("numbered_from", 4, [
                "On expiry, the producer's ready-to-sell flag is revoked and quote/bind is blocked in PAS immediately.",
                "Reinstatement is initiated; outstanding CE must be completed within 30 days.",
                "Any sales attempted during the lapse are blocked at point of sale; historical lapse exposure is eliminated."]),
            ("h3", "7.3 Continuous-Monitoring Alert (New — v2.0)"),
            ("banner", "new", "New exception. A mid-term adverse-action or watchlist hit triggers immediate Compliance review."),
            ("numbered_from", 7, [
                "Monitoring alert routes to Compliance for disposition within 1 business day.",
                "Disqualifying events trigger immediate ready-to-sell suspension pending review."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["Licensing System (AgentOS)", "Licence tracking, continuous sync, filing status", "Licensing Specialist"],
              ["Regulator Integration (NIPR/PDB)", "Automated appointment/renewal/termination filing and sync", "Licensing Specialist"],
              ["Compliance Monitoring Feed", "Adverse-action and watchlist monitoring", "Compliance"],
              ["LMS (Cornerstone)", "Pre-appointment and CE training and sync", "Licensing Specialist, Representatives"],
              ["DocuSign", "Digital execution of distribution agreements", "Document Manager, Representatives"],
              ["DMS (SharePoint)", "Signed agreements, certificates, compliance records", "Document Manager, Compliance"],
              ["PAS / CRM", "Agent record, authorities, ready-to-sell gate", "Licensing Specialist"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v2.0: continuous monitoring, ready-to-sell enforcement, automated "
             "regulator filing and CE synchronisation."),
            ("bullets", [
                "Continuous monitoring: adverse-action and watchlist events flagged between renewals.",
                "Ready-to-sell gate: no quote/bind for unlicensed or unappointed producers.",
                "Automated filing: appointment/renewal/termination filed via regulator integration with audit trail.",
                "CE synchronisation: completions auto-synced; shortfalls flagged before renewal.",
                "Training gate: mandatory AML/conduct/product training before any appointment filing.",
                "Segregation of duties: appointment filing ≠ compliance disposition.",
                "Immutable audit trail: verification, screening, filing and monitoring events logged."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v1.4 Target", "v2.0 Target", "Measurement"],
             [["Appointment processing time", "~10 business days", "≤6 business days", "Application to confirmed appointment"],
              ["Licence renewal on-time", "100%", "100%", "Renewed before expiry"],
              ["Lapsed-licence sales", "Zero (post-review)", "Zero (blocked)", "Ready-to-sell gate enforcement"],
              ["Continuous-monitoring coverage", "N/A (new)", "100% of active producers", "Monitoring enrolment"],
              ["Filing automation", "N/A (new)", "≥95% via integration", "Automated vs manual filings"],
              ["CE shortfall detection", "Manual", "Auto before −60 days", "CE sync flags"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["1.4", "01 Feb 2025", "C. Wong, Compliance", "Aligned to revised DOA; updated DocuSign execution steps"],
              ["2.0", "01 Oct 2026", "C. Wong, Compliance",
               "OPTIMISED: continuous compliance monitoring; ready-to-sell gate; automated NIPR/PDB filing; CE "
               "synchronisation; continuous licence verification; catalog alignment 72% → 92%"]], {}),
        ]),
    ],
)

package = SopPackage(
    meta=meta, phases=phases, steps=steps, authority=authority, swim_phases=swim_phases,
    n_phases=3, n_steps=15, n_roles=5, n_gateways=2,
    fitgap=fitgap,
    opt_phases=opt_phases, opt_steps=opt_steps, opt_swim_phases=opt_swim_phases,
    opt_n_phases=3, opt_n_steps=16, opt_n_gateways=2, opt_fit=92,
    optimised_doc=optimised_doc,
    swim_cover_tags="Appointment · Screening · Renewal · Termination · Exception handling",
    hierarchy_cover_sub="Phase breakdown with producer lifecycle tracks, compliance authority, and exception paths",
)
