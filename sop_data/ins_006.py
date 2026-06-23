"""SOP-INS-006 — Group Benefits Administration (Meridian Insurance Group).

Fit-gap vs the Majesco Group & Voluntary Benefits administration catalog.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Majesco Group & Voluntary Benefits — Administration Best-Practice Catalog"
CATALOG_SHORT = "Majesco GBA"

meta = Meta(
    sop_id="SOP-INS-006", slug="Group_Benefits_Administration",
    title="Group Benefits Administration", short_title="Group benefits administration",
    version="1.2", owner="Group Business — Policy Operations",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="2.0", effective_date="01 October 2026",
    supersedes="v1.2 dated 01 April 2025", approved_by="Head of Group Insurance",
    classification="Internal Use Only",
)

phases = [
    Phase("1", "New programme setup", "Structure, master policy, onboarding", "blue",
          "Account Mgr · New Business · Compliance", "Steps 1–6", "6 steps"),
    Phase("2", "Ongoing member administration", "Enrolment, billing, reconciliation", "green",
          "Group Admin · Application Processor · Finance", "Steps 7–11", "5 steps + 1 decision"),
    Phase("3", "Annual renewal", "Analysis, presentation, acceptance", "amber",
          "Account Mgr · Actuarial · Compliance", "Steps 12–14", "3 steps + 1 decision"),
]

steps = [
    Step("1", "1", "Signed proposal received from group client", "Group Account Manager",
         "Proposal filed; implementation timeline agreed; kickoff scheduled", "Day 0", "Programme trigger", kind="trigger"),
    Step("2", "1", "Group programme structured and underwritten", "New Business Specialist / Underwriting",
         "Benefits schedule, eligibility rules and pricing confirmed; subgroups defined", "Day 1–5", "Group underwriting"),
    Step("3", "1", "Master policy drafted and reviewed by Compliance", "New Business Specialist / Compliance",
         "Wording approved; benefits schedule attached; executed via DocuSign", "Day 5–8", "Compliance review"),
    Step("4", "1", "Group configured in PAS and billing system", "New Business Specialist",
         "Master policy number; benefit codes, eligibility rules and billing cycle loaded", "Day 8–10", "System configuration"),
    Step("5", "1", "Group administrator onboarding", "Group Account Manager",
         "Training on data submission format and portal access; admin guide distributed", "Day 10–12", "Admin onboarding"),
    Step("6", "1", "Initial member data file received and processed", "Application Processor",
         "Member records loaded; certificates generated and dispatched to group admin", "Day 12–15", "Initial enrolment", kind="complete"),
    Step("7", "2", "Monthly member data file received from group admin", "Application Processor",
         "File received by 5th; format validated against agreed template", "Monthly", "Data file SLA", kind="trigger"),
    Step("8", "2", "Data file processed: additions, deletions, amendments", "Application Processor",
         "Changes effective per file date; PAS updated; billing adjusted", "Monthly", "Enrolment processing"),
    Step("9", "2", "Discrepancy resolution", "Application Processor",
         "Errors returned to group admin within 2 days; corrected file within 5 days", "Monthly", "Discrepancy control"),
    Step("", "2", "", "", "", "", "Data file status", kind="decision", decision="File received & clean?",
         branches=["Clean → process & invoice", "Missing/errors → escalate (Sec 6.1)"]),
    Step("10", "2", "Monthly group invoice generated and dispatched", "New Business Specialist / Finance",
         "Invoice reflects current member count and benefit level; sent by 10th", "Monthly", "List-bill invoicing"),
    Step("11", "2", "Premium payment received and reconciled", "Finance / Application Processor",
         "Payment matched to invoice; exceptions resolved; GL posted in SAP", "Monthly", "Reconciliation"),
    Step("12", "3", "Renewal analysis prepared", "Group Account Manager / Actuarial",
         "Loss ratio, claims experience and membership trend; pricing recommendation", "Anniv −90", "Experience analysis"),
    Step("13", "3", "Renewal terms presented to group client", "Group Account Manager",
         "Renewal meeting; revised benefits schedule and premium presented", "Anniv −45", "Renewal presentation"),
    Step("14", "3", "Renewal accepted and documented", "Group Account Manager / Compliance",
         "Master policy endorsed or reissued; new anniversary confirmed in PAS", "Anniv −15", "Renewal completion", kind="complete"),
]

authority = [
    AuthorityRow("Standard group setup", "New Business Specialist", "—"),
    AuthorityRow("Non-standard benefit design", "Head of Group Insurance", "Underwriting"),
    AuthorityRow("Renewal re-pricing", "Group Account Manager", "Actuarial sign-off"),
    AuthorityRow("Arrears payment plan", "Finance Director", "Group Account Manager"),
    AuthorityRow("Programme suspension (90-day)", "Head of Group Insurance", "Finance Director"),
]

swim_phases = [
    SwimPhase("1", "New programme setup", "Steps 1–6 · structure to enrolment",
        ["Group Account Mgr", "New Business / Compliance", "Application Processor"],
        [SwimNode("s1", "Group Account Mgr", 0, "Signed proposal", "kickoff scheduled"),
         SwimNode("s2", "New Business / Compliance", 1, "Structure & underwrite", "benefits schedule"),
         SwimNode("s3", "New Business / Compliance", 2, "Master policy + compliance", "DocuSign"),
         SwimNode("s4", "New Business / Compliance", 3, "Configure PAS & billing", "benefit codes"),
         SwimNode("s5", "Group Account Mgr", 3, "Group admin onboarding", "portal training"),
         SwimNode("s6", "Application Processor", 4, "Initial member load", "certificates", kind="terminal")],
        [SwimEdge("s1", "s2"), SwimEdge("s2", "s3"), SwimEdge("s3", "s4"),
         SwimEdge("s4", "s5"), SwimEdge("s5", "s6")],
        "New programmes are underwritten, documented and configured before the group administrator is onboarded and members are loaded."),
    SwimPhase("2", "Ongoing member administration", "Steps 7–11 · enrolment & billing",
        ["Group Admin", "Application Processor", "Finance"],
        [SwimNode("a1", "Group Admin", 0, "Monthly data file", "by 5th"),
         SwimNode("a2", "Application Processor", 1, "Process add/del/amend", "PAS updated"),
         SwimNode("a3", "Application Processor", 2, "Discrepancy resolution", "5-day correction", kind="exception"),
         SwimNode("a4", "Finance", 3, "Monthly invoice", "by 10th"),
         SwimNode("a5", "Finance", 4, "Reconcile payment", "GL posted", kind="terminal")],
        [SwimEdge("a1", "a2", dashed=True), SwimEdge("a2", "a3", dashed=True, kind="exception", label="err"),
         SwimEdge("a2", "a4"), SwimEdge("a4", "a5")],
        "A monthly flat file drives enrolment changes and list-bill invoicing; discrepancies are returned for correction within five days."),
    SwimPhase("3", "Annual renewal", "Steps 12–14 · analysis to acceptance",
        ["Group Account Mgr", "Actuarial", "Compliance"],
        [SwimNode("d1", "Actuarial", 0, "Renewal analysis", "loss ratio · trend"),
         SwimNode("d2", "Group Account Mgr", 1, "Present renewal terms", "revised schedule"),
         SwimNode("d3", "Compliance", 2, "Accept & document", "endorse / reissue", kind="terminal"),
         SwimNode("d4", "Compliance", 1, "Declined → run-off", "Sec 6.3", kind="exception")],
        [SwimEdge("d1", "d2"), SwimEdge("d2", "d3"),
         SwimEdge("d2", "d4", dashed=True, kind="exception", label="dec")],
        "Renewals are priced on experience, presented to the client, and documented; declines invoke master-policy run-off."),
]

fg_items = [
    FitItem("1", "Group programme intake", "FIT",
        "Signed-proposal intake with implementation timeline aligns with Majesco group case setup.",
        "Group Account Manager", "MJ-GB-CASE-01", "p1"),
    FitItem("2", "Group underwriting & benefit design", "FIT",
        "Benefits schedule, eligibility rules and subgroup structure align with Majesco plan configuration.",
        "New Business / Underwriting", "MJ-GB-PLN-01", "p1"),
    FitItem("3", "Master policy & compliance", "FIT",
        "Compliance-reviewed master wording executed via DocuSign aligns with Majesco contract management.",
        "New Business / Compliance", "MJ-GB-CON-01", "p1"),
    FitItem("4", "Employee self-service enrolment", "GAP",
        "Enrolment is administrator-mediated only. Majesco provides employee self-service enrolment with real-time "
        "eligibility — without it, member experience and data quality suffer.",
        "Group Administrator", "MJ-GB-ENR-02", "p1"),
    FitItem("5", "Group administrator onboarding", "FIT",
        "Portal training and admin guide for data submission align with Majesco group-admin onboarding.",
        "Group Account Manager", "MJ-GB-ADM-01", "p1"),
    FitItem("6", "Member data integration (EDI/API)", "GAP",
        "Member changes arrive as a monthly flat file. Majesco ingests EDI 834 / API feeds for near-real-time, "
        "validated enrolment — the flat file delays changes and increases error.",
        "Application Processor", "MJ-GB-ENR-01", "p2"),
    FitItem("7", "Eligibility & dependent verification", "PARTIAL",
        "Format is validated but eligibility and dependent records are not systematically verified at ingest, as "
        "the catalog requires to prevent ineligible coverage.",
        "Application Processor", "MJ-GB-ELG-01", "p2"),
    FitItem("8", "Discrepancy resolution", "PARTIAL",
        "Discrepancies are worked manually with the group admin. Majesco auto-validates files and routes only "
        "true exceptions with a self-correct portal.",
        "Application Processor", "MJ-GB-ENR-03", "p2"),
    FitItem("9", "List-bill invoicing", "FIT",
        "Member-level list-bill invoicing reflecting current count and benefit aligns with Majesco group billing.",
        "New Business / Finance", "MJ-GB-BIL-01", "p2"),
    FitItem("10", "Reconciliation & retro adjustments", "PARTIAL",
        "Payments are reconciled to invoice, but retroactive add/term adjustments are manual. Majesco automates "
        "retro premium and self-bill/list-bill reconciliation.",
        "Finance / Application Processor", "MJ-GB-BIL-03", "p2"),
    FitItem("11", "Evidence of insurability (EOI)", "GAP",
        "No EOI workflow for voluntary/over-guarantee benefit elections. Majesco routes EOI to underwriting and "
        "gates coverage until approved — a leakage and compliance gap.",
        "Underwriting", "MJ-GB-EOI-01", "p2"),
    FitItem("12", "Experience-based renewal", "FIT",
        "Loss-ratio, claims-experience and trend analysis with actuarial pricing align with Majesco renewal analytics.",
        "Group Account Manager / Actuarial", "MJ-GB-REN-01", "p3"),
    FitItem("13", "Renewal documentation", "FIT",
        "Endorsed/reissued master policy with new anniversary aligns with Majesco renewal processing.",
        "Group Account Manager / Compliance", "MJ-GB-REN-03", "p3"),
]

fitgap = FitGap(
    overall_fit=67, partial_pct=18, fits=7, gaps=3, partials=3,
    steps_analysed=13, phases_count=3,
    summary_line="Overall alignment of SOP-INS-006 against the Majesco group benefits catalog",
    metrics=[
        ("Steps analysed", "13 steps across 3 phases"),
        ("Fits confirmed", "7 steps aligned to catalog"),
        ("Gaps identified", "3 steps — remediation required"),
        ("Partial fits", "3 steps — enhancement recommended"),
        ("Highest risk area", "Flat-file enrolment (no EDI/API)"),
        ("Coverage gap", "No evidence-of-insurability workflow"),
        ("Ref standard", "Majesco Group Benefits Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Setup", 76, ""),
        FitPhaseBar("Phase 2", "Member admin", 58, ""),
        FitPhaseBar("Phase 3", "Renewal", 80, ""),
        FitPhaseBar("Enrolment /", "EOI", 46, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 76, "Programme setup"),
        PhaseScoreCard("Phase 2", 58, "Member admin"),
        PhaseScoreCard("Phase 3", 80, "Renewal"),
        PhaseScoreCard("Enrol", 46, "Self-service & EOI"),
    ],
    detail_slides=[
        ("Phase 1 — New programme setup", "Steps 1–6 vs Majesco group benefits catalog", ["p1"]),
        ("Phase 2 — Ongoing member administration", "Steps 7–11 vs Majesco group benefits catalog", ["p2"]),
        ("Phase 3 — Annual renewal", "Steps 12–13 vs Majesco group benefits catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — NEW PROGRAMME SETUP"),
            ("p2", "PHASE 2 — ONGOING MEMBER ADMINISTRATION"),
            ("p3", "PHASE 3 — ANNUAL RENEWAL")],
    critical_missing=[
        CriticalGap("EDI/API member data integration",
            "Enrolment changes arrive as a monthly flat file, delaying coverage updates and increasing error. The "
            "catalog ingests EDI 834 / API feeds with validation for near-real-time enrolment."),
        CriticalGap("Employee self-service enrolment",
            "Enrolment is administrator-mediated; there is no employee self-service with real-time eligibility, "
            "hurting member experience and data quality."),
        CriticalGap("Evidence of insurability (EOI)",
            "No EOI workflow for voluntary/over-guarantee elections; coverage is not gated on underwriting approval, "
            "a leakage and compliance gap."),
        CriticalGap("Eligibility & dependent verification",
            "Files are format-checked but eligibility and dependents are not systematically verified at ingest, "
            "risking ineligible coverage and claims leakage."),
    ],
    radar=[("Case setup", 80), ("Enrolment", 45), ("Eligibility", 52), ("Billing", 74),
           ("EOI", 35), ("Reconciliation", 58), ("Renewal", 82)],
    control_bars=[
        ControlBar("Case setup", 80, "Underwriting, contracting and configuration solid"),
        ControlBar("Enrolment integration", 45, "Monthly flat file; no EDI/API or self-service"),
        ControlBar("Eligibility verification", 52, "Format checked; no systematic eligibility check"),
        ControlBar("List-bill invoicing", 74, "Member-level invoicing accurate"),
        ControlBar("Evidence of insurability", 35, "No EOI workflow for voluntary elections"),
        ControlBar("Reconciliation", 58, "Manual retro adjustments"),
        ControlBar("Renewal", 82, "Experience-based pricing and documentation"),
    ],
    remediations=[
        Remediation(1, "Implement EDI 834 / API member integration",
            "Replace the monthly flat file with EDI 834 / API feeds and validation for near-real-time, accurate "
            "enrolment. Effort: 6 weeks (integration).", "High"),
        Remediation(2, "Launch employee self-service enrolment",
            "Provide an employee self-service portal with real-time eligibility, open-enrolment windows and "
            "life-event changes. Effort: 7 weeks.", "High"),
        Remediation(3, "Add evidence-of-insurability (EOI) workflow",
            "Route voluntary/over-guarantee elections to underwriting and gate coverage until EOI approval. "
            "Effort: 4 weeks.", "High"),
        Remediation(4, "Automate eligibility & dependent verification",
            "Verify eligibility and dependents at ingest against rules and source data, blocking ineligible coverage. "
            "Effort: 4 weeks.", "Medium"),
        Remediation(5, "Automate retro adjustments & reconciliation",
            "Automate retroactive premium add/term adjustments and self-bill/list-bill reconciliation. "
            "Effort: 4 weeks.", "Medium"),
    ],
    risk_impact=[("Flat-file enrolment", 85), ("Self-service enrolment", 78), ("Evidence of insurability", 75),
                 ("Eligibility verification", 62), ("Retro reconciliation", 52), ("Data quality", 58)],
    projected_fit=90,
)

opt_phases = [
    Phase("1", "New programme setup", "Structure, master policy, self-service", "blue",
          "Account Mgr · New Business · Compliance", "Steps 1–6", "6 steps"),
    Phase("2", "Member administration & EOI", "EDI enrolment, eligibility, EOI, billing", "green",
          "Group Admin · Processor · Underwriting · Finance", "Steps 7–12", "6 steps + 1 decision"),
    Phase("3", "Annual renewal", "Analysis, presentation, acceptance", "amber",
          "Account Mgr · Actuarial · Compliance", "Steps 13–15", "3 steps + 1 decision"),
]

opt_steps = [
    Step("1", "1", "Signed proposal received from group client", "Group Account Manager",
         "Proposal filed; timeline agreed; kickoff scheduled", "Day 0", "Standard", kind="trigger"),
    Step("2", "1", "Group programme structured and underwritten", "New Business / Underwriting",
         "Benefits schedule, eligibility rules and pricing confirmed", "Day 1–5", "Standard"),
    Step("3", "1", "Master policy drafted and reviewed by Compliance", "New Business / Compliance",
         "Wording approved; executed via DocuSign", "Day 5–8", "Standard"),
    Step("4", "1", "Group configured in PAS and billing system", "New Business Specialist",
         "Master policy number; benefit codes and billing cycle loaded", "Day 8–10", "Standard"),
    Step("5", "1", "Enable employee self-service enrolment", "Group Account Manager / System",
         "Self-service portal with real-time eligibility and open-enrolment windows", "Day 10–12",
         "NEW (v2.0) — member experience"),
    Step("6", "1", "Initial enrolment via EDI / self-service", "Application Processor",
         "Members enrolled via EDI 834 / self-service; certificates issued", "Day 12–15", "ENHANCED (v2.0)", kind="complete"),
    Step("7", "2", "EDI / API member data feed received", "Application Processor / System",
         "Near-real-time EDI 834 / API enrolment changes ingested", "Continuous",
         "NEW (v2.0) — replaces flat file", kind="trigger"),
    Step("8", "2", "Automated eligibility & dependent verification", "Application Processor / System",
         "Eligibility and dependents verified at ingest; ineligible coverage blocked", "Continuous",
         "NEW (v2.0) — leakage control"),
    Step("9", "2", "Evidence of insurability (EOI) workflow", "Underwriting",
         "Voluntary/over-guarantee elections routed to UW; coverage gated until approval", "On election",
         "NEW (v2.0) — coverage gate"),
    Step("10", "2", "Discrepancy auto-resolution", "Application Processor",
         "Files auto-validated; only true exceptions routed; self-correct portal", "Continuous", "ENHANCED (v2.0)"),
    Step("", "2", "", "", "", "", "Enrolment status", kind="decision", decision="Eligible & EOI clear?",
         branches=["Yes → activate & invoice", "No → exception / EOI pending"]),
    Step("11", "2", "List-bill invoice with retro adjustments", "New Business / Finance",
         "Member-level invoice with automated retro add/term adjustments", "Monthly", "ENHANCED (v2.0)"),
    Step("12", "2", "Premium payment received and reconciled", "Finance / Application Processor",
         "Payment matched; self-bill/list-bill reconciled; GL posted", "Monthly", "Standard"),
    Step("13", "3", "Renewal analysis prepared", "Group Account Manager / Actuarial",
         "Loss ratio, experience and trend; pricing recommendation", "Anniv −90", "Standard"),
    Step("14", "3", "Renewal terms presented to group client", "Group Account Manager",
         "Revised benefits schedule and premium presented", "Anniv −45", "Standard"),
    Step("15", "3", "Renewal accepted and documented", "Group Account Manager / Compliance",
         "Master policy endorsed/reissued; new anniversary confirmed", "Anniv −15", "Standard", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "New programme setup", "Steps 1–6 · v2.0 adds self-service",
        ["Group Account Mgr", "New Business / Compliance", "Application Processor"],
        [SwimNode("o1", "Group Account Mgr", 0, "Signed proposal", "kickoff"),
         SwimNode("o2", "New Business / Compliance", 1, "Structure & underwrite", "benefits schedule"),
         SwimNode("o3", "New Business / Compliance", 2, "Master policy + compliance", "DocuSign"),
         SwimNode("o4", "New Business / Compliance", 3, "Configure PAS & billing", "benefit codes"),
         SwimNode("o5", "Group Account Mgr", 3, "Enable self-service enrolment", "real-time eligibility", kind="new"),
         SwimNode("o6", "Application Processor", 4, "Initial enrolment (EDI/self-serve)", "certificates", kind="enhanced")],
        [SwimEdge("o1", "o2"), SwimEdge("o2", "o3"), SwimEdge("o3", "o4"),
         SwimEdge("o4", "o5", dashed=True, kind="new"), SwimEdge("o5", "o6")],
        "v2.0 turns on employee self-service enrolment with real-time eligibility for initial member loading."),
    SwimPhase("2", "Member administration & EOI", "Steps 7–12 · EDI, eligibility, EOI",
        ["Group Admin / EDI", "Application Processor", "Underwriting / Finance"],
        [SwimNode("p1", "Group Admin / EDI", 0, "EDI / API member feed", "near-real-time", kind="new"),
         SwimNode("p2", "Application Processor", 1, "Eligibility & dependent check", "blocked if ineligible", kind="new"),
         SwimNode("p3", "Underwriting / Finance", 1, "EOI workflow", "voluntary elections", kind="new"),
         SwimNode("p4", "Application Processor", 2, "Discrepancy auto-resolution", "self-correct", kind="enhanced"),
         SwimNode("p5", "Underwriting / Finance", 2, "List-bill + retro adjust", "automated retro", kind="enhanced"),
         SwimNode("p6", "Application Processor", 3, "Reconcile payment", "GL posted", kind="terminal")],
        [SwimEdge("p1", "p2"), SwimEdge("p2", "p3", dashed=True, kind="new", label="EOI"),
         SwimEdge("p2", "p4"), SwimEdge("p4", "p5"), SwimEdge("p5", "p6")],
        "v2.0 ingests EDI/API feeds, verifies eligibility and dependents, gates voluntary elections on EOI, and automates retro billing."),
    SwimPhase("3", "Annual renewal", "Steps 13–15 · experience-based renewal",
        ["Group Account Mgr", "Actuarial", "Compliance"],
        [SwimNode("q1", "Actuarial", 0, "Renewal analysis", "loss ratio · trend"),
         SwimNode("q2", "Group Account Mgr", 1, "Present renewal terms", "revised schedule"),
         SwimNode("q3", "Compliance", 2, "Accept & document", "endorse / reissue", kind="terminal"),
         SwimNode("q4", "Compliance", 1, "Declined → run-off", "Sec 6.3", kind="exception")],
        [SwimEdge("q1", "q2"), SwimEdge("q2", "q3"),
         SwimEdge("q2", "q4", dashed=True, kind="exception", label="dec")],
        "Renewal continues to be priced on experience and documented; the unchanged flow now benefits from cleaner enrolment data."),
]

optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Majesco Group & Voluntary Benefits Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-006"),
                ("Version", "2.0 (Optimised)"),
                ("Effective Date", "01 October 2026"),
                ("Supersedes", "v1.2 dated 01 April 2025"),
                ("Owner", "Group Business — Policy Operations"),
                ("Approved By", "Head of Group Insurance"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-006 dated 18 June 2026"),
                ("Catalog Alignment Score", "90% (up from 67% in v1.2)"),
                ("Classification", "Internal Use Only"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v2.0",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-006. Alignment to the "
              "Majesco group benefits catalog increased from 67% to 90%. Critical additions: EDI 834 / API member "
              "integration, employee self-service enrolment, an evidence-of-insurability (EOI) workflow, automated "
              "eligibility/dependent verification, and automated retro adjustments."],
             ["NEW STEP (green) — step added to close a gap vs the Majesco catalog",
              "ENHANCED (amber) — existing step updated with additional automation or controls"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines the process for developing, onboarding, administering "
             "and renewing group insurance programmes. Version 2.0 incorporates optimisations from fit-gap analysis "
             "against the Majesco Group & Voluntary Benefits Administration Best-Practice Catalog, achieving 90% "
             "alignment (up from 67% in v1.2)."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to new group programme setup, member enrolment changes throughout the "
             "year, annual renewal and premium renegotiation, and group billing reconciliation."),
            ("banner", "new", "Scope extended: EDI/API member integration, self-service enrolment and EOI now apply "
             "to every member change."),
            ("para", "This procedure does NOT cover voluntary individual policies under a group master (SOP-INS-004) "
             "or reinsurance treaty administration."),
        ]),
        DocSection("3. Authority Matrix", [
            ("table", ["Item", "First Authority", "Second Authority"],
             [["Standard group setup", "New Business Specialist", "—"],
              ["Non-standard benefit design", "Head of Group Insurance", "Underwriting"],
              ["Renewal re-pricing", "Group Account Manager", "Actuarial sign-off"],
              ["Arrears payment plan", "Finance Director", "Group Account Manager"],
              ["Programme suspension (90-day)", "Head of Group Insurance", "Finance Director"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Group Account Manager", "Owns the client relationship; leads design and renewal; coordinates internal teams."],
              ["Application Processor", "Ingests EDI/self-service enrolment; verifies eligibility; resolves exceptions; reconciles billing."],
              ["New Business Specialist", "Configures the programme; issues the master policy; sets billing with Finance."],
              ["Underwriting", "Owns EOI dispositions and non-standard benefit design."],
              ["Compliance Officer", "Reviews master wording and regulatory requirements."]], {}),
        ]),
        DocSection("5. Enrolment & EOI Controls (New Section — v2.0)", [
            ("banner", "crit", "New section. Required by the Majesco catalog. EDI/API enrolment, eligibility "
             "verification and EOI now gate member coverage."),
            ("table", ["#", "Control", "Responsible", "Output / System", "Timeline"],
             [["E1", "EDI 834 / API member feed", "Application Processor", "Near-real-time validated enrolment", "Continuous"],
              ["E2", "Eligibility & dependent verification", "Application Processor", "Ineligible coverage blocked at ingest", "Continuous"],
              ["E3", "Evidence of insurability (EOI)", "Underwriting", "Voluntary elections gated on UW approval", "On election"]],
             {0: "new", 1: "new", 2: "new"}),
        ]),
        DocSection("6. Process Steps", [
            ("h3", "6.1 New Programme Setup"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "Signed proposal received", "Group Account Manager", "Timeline agreed; kickoff", "Day 0"],
              ["2", "Programme structured and underwritten", "New Business / Underwriting", "Benefits schedule, eligibility", "Day 1–5"],
              ["3", "Master policy drafted & compliance review", "New Business / Compliance", "DocuSign execution", "Day 5–8"],
              ["4", "Group configured in PAS and billing", "New Business Specialist", "Benefit codes; billing cycle", "Day 8–10"],
              ["5", "Enable employee self-service enrolment", "Group Account Manager", "Self-service with real-time eligibility", "Day 10–12"],
              ["6", "Initial enrolment via EDI / self-service", "Application Processor", "Members enrolled; certificates", "Day 12–15"]],
             {4: "new", 5: "enh"}),
            ("h3", "6.2 Member Administration & EOI"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["7", "EDI / API member data feed", "Application Processor", "Near-real-time enrolment changes", "Continuous"],
              ["8", "Eligibility & dependent verification", "Application Processor", "Ineligible coverage blocked", "Continuous"],
              ["9", "Evidence of insurability (EOI)", "Underwriting", "Voluntary elections gated", "On election"],
              ["10", "Discrepancy auto-resolution", "Application Processor", "Auto-validated; self-correct portal", "Continuous"],
              ["11", "List-bill invoice with retro adjustments", "New Business / Finance", "Member-level + automated retro", "Monthly"],
              ["12", "Premium payment received and reconciled", "Finance", "Self-bill/list-bill reconciled; GL", "Monthly"]],
             {0: "new", 1: "new", 2: "new", 3: "enh", 4: "enh"}),
            ("h3", "6.3 Annual Renewal"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["13", "Renewal analysis prepared", "Group Account Manager / Actuarial", "Loss ratio; trend; pricing", "Anniv −90"],
              ["14", "Renewal terms presented to client", "Group Account Manager", "Revised schedule and premium", "Anniv −45"],
              ["15", "Renewal accepted and documented", "Group Account Manager / Compliance", "Endorsed/reissued; new anniversary", "Anniv −15"]],
             {}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Member Data Not Received (Enhanced — v2.0)"),
            ("banner", "enh", "With EDI/API feeds, missing-file risk is largely eliminated; residual gaps are flagged automatically."),
            ("numbered", [
                "If a feed gap is detected, the system alerts the Application Processor the same day.",
                "Unresolved by the 10th: Group Account Manager escalates to the client HR contact.",
                "Billing uses prior-period membership provisionally, subject to retroactive adjustment."]),
            ("h3", "7.2 Group Premium Arrears"),
            ("numbered_from", 4, [
                "30-day arrears: formal written notice to the group administrator.",
                "60-day arrears: Account Manager engages the client; payment plan with Finance Director approval.",
                "90-day arrears: programme suspended; members notified that coverage is under review."]),
            ("h3", "7.3 Renewal Declined by Client"),
            ("numbered_from", 7, [
                "Master-policy run-off provisions apply; claims incurred before expiry honoured to the run-off period.",
                "Member data archived per retention policy; group-admin portal access revoked."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["Policy Administration System (PAS)", "Master policy, member records, certificates", "All roles"],
              ["Group Billing System (Sapiens)", "List-bill invoicing, retro adjustments, reconciliation", "Application Processor, Finance"],
              ["EDI / API Gateway", "EDI 834 / API member data integration", "Application Processor"],
              ["Self-Service Enrolment Portal", "Employee enrolment and life-event changes", "Members, Group Admin"],
              ["EOI / Underwriting Workbench", "Evidence-of-insurability dispositions", "Underwriting"],
              ["SAP S/4HANA", "Premium GL posting and accounts receivable", "Finance"],
              ["CRM (Salesforce)", "Group account management and renewal tracking", "Group Account Manager"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v2.0: EDI/API enrolment, eligibility verification, EOI gating, "
             "and automated retro reconciliation."),
            ("bullets", [
                "Enrolment integration: validated EDI/API feeds replace the monthly flat file.",
                "Eligibility gate: ineligible members and dependents blocked at ingest.",
                "EOI gate: voluntary/over-guarantee coverage withheld until underwriting approval.",
                "Self-service: members manage elections with real-time eligibility.",
                "Retro reconciliation: retroactive add/term premium adjusted automatically.",
                "Segregation of duties: enrolment ≠ EOI disposition ≠ billing reconciliation.",
                "Immutable audit trail: enrolment, EOI, billing and renewal events logged."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v1.2 Target", "v2.0 Target", "Measurement"],
             [["New group setup cycle time", "≤15 business days", "≤12 business days", "Proposal to master policy"],
              ["Enrolment processing", "By 15th monthly", "Near-real-time", "Feed-to-effective lag"],
              ["Billing accuracy", "≥97%", "≥99%", "Invoices without amendment"],
              ["Ineligible coverage incidents", "N/A (new)", "Zero (blocked)", "Eligibility gate"],
              ["EOI compliance", "N/A (new)", "100% gated", "Voluntary elections vs EOI approval"],
              ["Annual renewal retention", "≥88%", "≥90%", "Clients renewed at anniversary"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["1.2", "01 Apr 2025", "S. Mehta, Operations", "Added arrears escalation protocol; updated renewal steps with actuarial sign-off"],
              ["2.0", "01 Oct 2026", "S. Mehta, Operations",
               "OPTIMISED: EDI/API integration; self-service enrolment; EOI workflow; eligibility/dependent "
               "verification; automated retro adjustments; catalog alignment 67% → 90%"]], {}),
        ]),
    ],
)

package = SopPackage(
    meta=meta, phases=phases, steps=steps, authority=authority, swim_phases=swim_phases,
    n_phases=3, n_steps=14, n_roles=5, n_gateways=2,
    fitgap=fitgap,
    opt_phases=opt_phases, opt_steps=opt_steps, opt_swim_phases=opt_swim_phases,
    opt_n_phases=3, opt_n_steps=15, opt_n_gateways=2, opt_fit=90,
    optimised_doc=optimised_doc,
    swim_cover_tags="Setup · Enrolment · Billing · Renewal · Exception handling",
    hierarchy_cover_sub="Phase breakdown with group programme tracks, billing authority, and exception paths",
)
