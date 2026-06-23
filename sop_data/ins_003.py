"""SOP-INS-003 — Bill Collection (Insurance Premiums) (Meridian Insurance Group).

Fit-gap vs the Guidewire BillingCenter collections & delinquency catalog.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Guidewire BillingCenter — Collections & Delinquency Best-Practice Catalog"
CATALOG_SHORT = "Guidewire BillingCenter"

meta = Meta(
    sop_id="SOP-INS-003", slug="Bill_Collection",
    title="Bill Collection (Insurance Premiums)", short_title="Premium bill collection",
    version="1.3", owner="Collections — Finance Department",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="2.0", effective_date="01 October 2026",
    supersedes="v1.3 dated 01 March 2025", approved_by="Finance Director",
    classification="Internal Use Only",
)

phases = [
    Phase("1", "Initial arrears", "T+1 to T+7 days", "blue",
          "Billing System · Collections Analyst", "Steps 1–4", "4 steps"),
    Phase("2", "Escalated arrears", "T+8 to T+30 days", "amber",
          "Collections Analyst · Investigator · Credit", "Steps 5–8", "4 steps + 1 decision"),
    Phase("3", "Resolution or write-off", "T+31 onwards", "green",
          "Collections · Credit Investigator · Finance", "Steps 9–12", "4 steps + 1 decision"),
]

steps = [
    Step("1", "1", "Billing system flags overdue account", "Billing System (auto)",
         "Arrears record created; queue updated; policy status 'Overdue'", "T+1 day", "Automated arrears trigger", kind="trigger"),
    Step("2", "1", "Automated payment reminder sent", "CRM / Email Engine",
         "Email and SMS reminder with amount, due date and payment link", "T+1 day", "Multi-channel reminder"),
    Step("3", "1", "Collections Analyst reviews arrears queue", "Collections Analyst",
         "Outstanding balance, history and contact preferences verified", "T+2 days", "Queue review"),
    Step("4", "1", "Outbound call attempt (if no response by T+5)", "Collections Analyst",
         "Max 2 call attempts/day; outcome recorded in CRM", "T+5 days", "Dialler compliance logging"),
    Step("5", "2", "Formal written notice of arrears issued", "Collections Analyst",
         "Letter and email: amount, consequences, 14-day cure period", "T+8 days", "Cure period stated"),
    Step("6", "2", "Payment-plan offer (if hardship indicated)", "Collections Analyst",
         "Instalment plan for balances above SGD 500; approved by Credit Investigator", "T+8–21 days", "Hardship plan control"),
    Step("7", "2", "Escalate to Collections Investigator (no response)", "Collections Analyst",
         "Escalation at T+21; investigator intensifies outreach", "T+21 days", "Escalation trigger"),
    Step("8", "2", "Lapse notice issued (T+30 if unresolved)", "Collections Investigator",
         "Formal lapse notice per SOP-INS-011; 7-day final cure period", "T+30 days", "Final cure period"),
    Step("", "2", "", "", "", "", "Escalation decision", kind="decision", decision="Resolved by T+30?",
         branches=["Paid / plan agreed → reinstate", "Unresolved → lapse notice + Phase 3"]),
    Step("9", "3", "Payment received — policy reinstated", "Collections / Billing",
         "Payment applied; status reset 'Active'; reinstatement endorsement if lapsed", "T+31+", "Reinstatement"),
    Step("10", "3", "No payment — policy lapsed, coverage ceased", "Collections Investigator",
         "Policy lapsed per SOP-INS-011; policyholder notified; balance referred to Credit", "T+31+", "Lapse processing"),
    Step("11", "3", "External agency referral (>SGD 1,000 at T+60)", "Credit Investigator",
         "Debt file passed to approved external agency; internal case closed", "T+60", "Agency referral threshold"),
    Step("12", "3", "Write-off recommendation (T+90 if uncollected)", "Credit Investigator",
         "Write-off request to Finance Director; GL adjustment processed", "T+90", "Write-off to DOA matrix", kind="complete"),
]

authority = [
    AuthorityRow("Payment plan ≤ SGD 5,000", "Credit Investigator", "—"),
    AuthorityRow("Payment plan > SGD 5,000", "Collections Manager", "Credit Investigator"),
    AuthorityRow("External agency referral", "Credit Investigator", "—"),
    AuthorityRow("Write-off ≤ SGD 2,000", "Finance Director", "Credit Investigator"),
    AuthorityRow("Write-off > SGD 2,000", "CFO", "Finance Director"),
]

swim_phases = [
    SwimPhase("1", "Initial arrears", "Steps 1–4 · T+1 to T+7",
        ["Billing System", "CRM / Dialler", "Collections Analyst"],
        [SwimNode("s1", "Billing System", 0, "Flag overdue account", "status 'Overdue'"),
         SwimNode("s2", "CRM / Dialler", 1, "Automated reminder", "email + SMS"),
         SwimNode("s3", "Collections Analyst", 2, "Review arrears queue", "balance + history"),
         SwimNode("s4", "Collections Analyst", 3, "Outbound call attempt", "max 2/day")],
        [SwimEdge("s1", "s2", dashed=True), SwimEdge("s2", "s3"), SwimEdge("s3", "s4")],
        "Missed payments are flagged automatically; reminders precede analyst review and outbound calls."),
    SwimPhase("2", "Escalated arrears", "Steps 5–8 · T+8 to T+30",
        ["Collections Analyst", "Credit Investigator", "Collections Investigator"],
        [SwimNode("a1", "Collections Analyst", 0, "Formal arrears notice", "14-day cure"),
         SwimNode("a2", "Credit Investigator", 1, "Approve payment plan", "if hardship", kind="standard"),
         SwimNode("a3", "Collections Analyst", 2, "Escalate (no response)", "T+21"),
         SwimNode("a4", "Collections Investigator", 3, "Lapse notice", "7-day final", kind="decision")],
        [SwimEdge("a1", "a2", label="hsh"), SwimEdge("a1", "a3"), SwimEdge("a3", "a4")],
        "Unresolved arrears escalate to formal notice, hardship plans, and a final lapse notice at T+30."),
    SwimPhase("3", "Resolution or write-off", "Steps 9–12 · T+31 onwards",
        ["Collections / Billing", "Credit Investigator", "Finance"],
        [SwimNode("d0", "Credit Investigator", 0, "Outcome at T+30?", "paid / unpaid", kind="decision"),
         SwimNode("d1", "Collections / Billing", 1, "Payment received → reinstate", "status 'Active'", kind="terminal"),
         SwimNode("d2", "Credit Investigator", 1, "No payment → lapse", "SOP-INS-011", kind="exception"),
         SwimNode("d3", "Credit Investigator", 2, "External agency referral", ">SGD 1,000 · T+60"),
         SwimNode("d4", "Finance", 3, "Write-off recommendation", "T+90 · DOA")],
        [SwimEdge("d0", "d1", label="paid"), SwimEdge("d0", "d2", dashed=True, kind="exception", label="unpaid"),
         SwimEdge("d2", "d3", dashed=True, kind="exception"), SwimEdge("d3", "d4")],
        "Paid cases are reinstated; unpaid balances lapse, route to an external agency, and are written off at T+90."),
]

fg_items = [
    FitItem("1", "Automated arrears identification", "FIT",
        "Billing-system arrears flag with status update aligns with BillingCenter delinquency-plan entry.",
        "Billing System", "GW-BC-DLQ-01", "p1"),
    FitItem("2", "Multi-channel reminders", "FIT",
        "Automated email and SMS reminders with a payment link align with BillingCenter notification templates.",
        "CRM", "GW-BC-DLQ-03", "p1"),
    FitItem("3", "Proactive pre-due reminders", "GAP",
        "Reminders only start T+1 after a miss. BillingCenter recommends pre-due nudges to prevent arrears entirely.",
        "CRM", "GW-BC-DLQ-02", "p1"),
    FitItem("4", "Risk-based collections segmentation", "GAP",
        "Every account follows the same T+1/T+5/T+8 milestones. BillingCenter prioritises treatment by "
        "propensity-to-pay and balance, focusing effort where recovery is likely.",
        "Collections Analyst", "GW-BC-DLQ-05", "p1"),
    FitItem("5", "Formal arrears notice & cure period", "FIT",
        "Written notice with a 14-day cure period aligns with BillingCenter dunning-letter cadence.",
        "Collections Analyst", "GW-BC-DLQ-04", "p2"),
    FitItem("6", "Payment-plan / arrangement", "PARTIAL",
        "Instalment plans are offered but only via an analyst. BillingCenter supports self-service arrangements and "
        "automated promise-to-pay tracking with break-detection.",
        "Collections Analyst / Credit", "GW-BC-ARR-01", "p2"),
    FitItem("7", "Escalation thresholds", "FIT",
        "T+21 escalation to an investigator aligns with BillingCenter delinquency-stage transitions.",
        "Collections Analyst", "GW-BC-DLQ-06", "p2"),
    FitItem("8", "Hardship & forbearance", "PARTIAL",
        "Hardship plans exist but without a documented forbearance/affordability framework or regulatory hardship "
        "evidence capture recommended by the catalog.",
        "Credit Investigator", "GW-BC-ARR-03", "p2"),
    FitItem("9", "Lapse / reinstatement", "FIT",
        "Lapse notice and reinstatement endorsement align with BillingCenter cancellation-for-non-payment handling.",
        "Collections Investigator", "GW-BC-CAN-01", "p3"),
    FitItem("10", "Partial-payment allocation", "PARTIAL",
        "No documented allocation of partial payments to oldest arrears. BillingCenter applies a configurable "
        "allocation hierarchy automatically.",
        "Collections / Billing", "GW-BC-CSH-03", "p3"),
    FitItem("11", "External agency referral", "FIT",
        "Threshold-based external referral with file hand-off aligns with BillingCenter agency-placement.",
        "Credit Investigator", "GW-BC-AGY-01", "p3"),
    FitItem("12", "Bad-debt provisioning (ECL)", "GAP",
        "Write-off is manual at T+90 with no automated IFRS 9 expected-credit-loss provisioning through the ageing. "
        "BillingCenter feeds provisioning models from delinquency stage.",
        "Finance / Credit", "GW-BC-WO-02", "p3"),
    FitItem("13", "Write-off governance", "FIT",
        "Write-off approval to the DOA matrix with GL adjustment aligns with BillingCenter write-off controls.",
        "Finance Director", "GW-BC-WO-01", "p3"),
]

fitgap = FitGap(
    overall_fit=68, partial_pct=15, fits=7, gaps=3, partials=3,
    steps_analysed=13, phases_count=3,
    summary_line="Overall alignment of SOP-INS-003 against the Guidewire BillingCenter collections catalog",
    metrics=[
        ("Steps analysed", "13 steps across 3 phases"),
        ("Fits confirmed", "7 steps aligned to catalog"),
        ("Gaps identified", "3 steps — remediation required"),
        ("Partial fits", "3 steps — enhancement recommended"),
        ("Highest risk area", "Risk-based segmentation (missing)"),
        ("Provisioning gap", "No automated IFRS 9 ECL provisioning"),
        ("Ref standard", "Guidewire BillingCenter Collections Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Initial", 64, ""),
        FitPhaseBar("Phase 2", "Escalated", 72, ""),
        FitPhaseBar("Phase 3", "Resolution", 70, ""),
        FitPhaseBar("Digital /", "model", 48, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 64, "Initial arrears"),
        PhaseScoreCard("Phase 2", 72, "Escalated arrears"),
        PhaseScoreCard("Phase 3", 70, "Resolution / write-off"),
        PhaseScoreCard("Digital", 48, "Self-service & models"),
    ],
    detail_slides=[
        ("Phase 1 — Initial arrears", "Steps 1–4 vs Guidewire BillingCenter catalog", ["p1"]),
        ("Phase 2 — Escalated arrears", "Steps 5–8 vs Guidewire BillingCenter catalog", ["p2"]),
        ("Phase 3 — Resolution or write-off", "Steps 9–13 vs Guidewire BillingCenter catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — INITIAL ARREARS"),
            ("p2", "PHASE 2 — ESCALATED ARREARS"),
            ("p3", "PHASE 3 — RESOLUTION OR WRITE-OFF")],
    critical_missing=[
        CriticalGap("Risk-based collections segmentation",
            "All accounts follow identical milestones regardless of balance or propensity-to-pay. The catalog "
            "prioritises treatment by recovery likelihood, improving yield and cutting cost-to-collect."),
        CriticalGap("Proactive pre-due reminders",
            "Outreach starts only after a missed payment. Pre-due nudges in the catalog prevent avoidable arrears."),
        CriticalGap("Self-service arrangements & promise-to-pay",
            "Payment plans require an analyst; there is no digital self-service arrangement or automated "
            "promise-to-pay tracking with break detection."),
        CriticalGap("Automated bad-debt provisioning (IFRS 9 ECL)",
            "Provisioning is manual at write-off; the catalog feeds expected-credit-loss provisioning from "
            "delinquency stage for accurate, timely reserves."),
    ],
    radar=[("Arrears detection", 80), ("Reminders", 72), ("Segmentation", 38), ("Arrangements", 55),
           ("Lapse / reinstate", 78), ("Provisioning", 40), ("Write-off", 80)],
    control_bars=[
        ControlBar("Arrears detection", 80, "Automated overdue flag and status update"),
        ControlBar("Reminders", 72, "Email/SMS post-miss; no pre-due nudges"),
        ControlBar("Risk segmentation", 38, "Same milestones for every account"),
        ControlBar("Arrangements", 55, "Analyst-only; no self-service or PTP tracking"),
        ControlBar("Lapse / reinstatement", 78, "Lapse notice and reinstatement well defined"),
        ControlBar("Provisioning", 40, "Manual at write-off; no ECL feed"),
        ControlBar("Write-off governance", 80, "DOA approval and GL posting solid"),
    ],
    remediations=[
        Remediation(1, "Introduce risk-based collections segmentation",
            "Score arrears by propensity-to-pay and balance; assign differentiated treatment paths so effort "
            "concentrates where recovery is likely. Effort: 5 weeks (model + workflow).", "High"),
        Remediation(2, "Add proactive pre-due reminders",
            "Send pre-due nudges (T-5/T-2) via SMS and email to prevent avoidable arrears. Effort: 2 weeks.", "High"),
        Remediation(3, "Launch self-service arrangements & promise-to-pay",
            "Let policyholders self-serve a payment arrangement online with automated promise-to-pay tracking and "
            "break detection. Effort: 6 weeks (portal).", "High"),
        Remediation(4, "Automate IFRS 9 ECL provisioning",
            "Feed expected-credit-loss provisioning from delinquency stage and ageing, replacing manual write-off-only "
            "provisioning. Effort: 4 weeks (Finance + Sapiens).", "Medium"),
        Remediation(5, "Add partial-payment allocation & forbearance framework",
            "Apply a configurable allocation hierarchy to partial payments and document a regulatory forbearance/"
            "affordability framework for hardship. Effort: 3 weeks.", "Medium"),
    ],
    risk_impact=[("Risk segmentation", 85), ("Self-service arrangements", 78), ("Pre-due reminders", 70),
                 ("ECL provisioning", 65), ("Partial allocation", 52), ("Forbearance framework", 48)],
    projected_fit=90,
)

opt_phases = [
    Phase("1", "Prevent & detect arrears", "Pre-due nudges; risk segmentation", "blue",
          "Billing · CRM · Collections Analyst", "Steps 1–5", "5 steps"),
    Phase("2", "Escalated arrears", "Notice, self-service plans, escalation", "amber",
          "Collections · Credit · Investigator", "Steps 6–9", "4 steps + 1 decision"),
    Phase("3", "Resolution, write-off & provisioning", "Reinstate, agency, ECL, write-off", "green",
          "Collections · Credit · Finance", "Steps 10–14", "5 steps + 1 decision"),
]

opt_steps = [
    Step("1", "1", "Proactive pre-due reminders", "CRM / Billing",
         "Pre-due nudges (T-5/T-2) by SMS and email to prevent arrears", "Pre-due",
         "NEW (v2.0) — prevention", kind="trigger"),
    Step("2", "1", "Billing system flags overdue account", "Billing System",
         "Arrears record; status 'Overdue'", "T+1 day", "Standard"),
    Step("3", "1", "Risk-based segmentation & treatment path", "Collections / Model",
         "Account scored by propensity-to-pay and balance; differentiated path assigned", "T+1 day",
         "NEW (v2.0) — prioritised effort"),
    Step("4", "1", "Automated reminder per segment", "CRM",
         "Channel and cadence tailored to the assigned segment", "T+1 day", "ENHANCED (v2.0)"),
    Step("5", "1", "Collections Analyst reviews high-value queue", "Collections Analyst",
         "Effort concentrated on high-recovery accounts", "T+2 days", "Standard"),
    Step("6", "2", "Formal written notice of arrears", "Collections Analyst",
         "Letter/email: amount, consequences, 14-day cure", "T+8 days", "Standard"),
    Step("7", "2", "Self-service payment arrangement & promise-to-pay", "Policyholder / Portal",
         "Online arrangement with automated promise-to-pay tracking and break detection", "T+8–21 days",
         "NEW (v2.0) — digital self-cure"),
    Step("8", "2", "Escalate to Collections Investigator", "Collections Analyst",
         "Escalation at T+21; intensified outreach", "T+21 days", "Standard"),
    Step("9", "2", "Lapse notice (T+30 if unresolved)", "Collections Investigator",
         "Lapse notice per SOP-INS-011; 7-day final cure", "T+30 days", "Standard"),
    Step("", "2", "", "", "", "", "Escalation decision", kind="decision", decision="Resolved by T+30?",
         branches=["Paid / plan kept → reinstate", "Unresolved → lapse + Phase 3"]),
    Step("10", "3", "Payment received — policy reinstated", "Collections / Billing",
         "Payment applied (oldest-arrears allocation); status 'Active'", "T+31+", "ENHANCED (v2.0)"),
    Step("11", "3", "No payment — policy lapsed", "Collections Investigator",
         "Policy lapsed; balance referred to Credit", "T+31+", "Standard"),
    Step("12", "3", "Automated ECL bad-debt provisioning", "Finance / System",
         "Expected-credit-loss provision updated from delinquency stage and ageing", "Ongoing",
         "NEW (v2.0) — IFRS 9", kind="control"),
    Step("13", "3", "External agency referral (>SGD 1,000)", "Credit Investigator",
         "Debt file to external agency; internal case closed", "T+60", "Standard"),
    Step("14", "3", "Write-off recommendation (T+90)", "Credit Investigator",
         "Write-off to Finance Director per DOA; GL adjustment", "T+90", "Standard", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "Prevent & detect arrears", "Steps 1–5 · v2.0 adds prevention & segmentation",
        ["Billing / CRM", "Collections / Model", "Collections Analyst"],
        [SwimNode("o1", "Billing / CRM", 0, "Pre-due reminders", "T-5 / T-2", kind="new"),
         SwimNode("o2", "Billing / CRM", 1, "Flag overdue account", "status 'Overdue'"),
         SwimNode("o3", "Collections / Model", 2, "Risk-based segmentation", "propensity score", kind="new"),
         SwimNode("o4", "Billing / CRM", 3, "Reminder per segment", "tailored cadence", kind="enhanced"),
         SwimNode("o5", "Collections Analyst", 4, "Review high-value queue", "prioritised")],
        [SwimEdge("o1", "o2", dashed=True, kind="new"), SwimEdge("o2", "o3"),
         SwimEdge("o3", "o4", dashed=True), SwimEdge("o4", "o5")],
        "v2.0 adds pre-due reminders and risk-based segmentation so collection effort is prioritised by recovery likelihood."),
    SwimPhase("2", "Escalated arrears", "Steps 6–9 · self-service arrangements",
        ["Collections Analyst", "Policyholder / Portal", "Collections Investigator"],
        [SwimNode("p1", "Collections Analyst", 0, "Formal arrears notice", "14-day cure"),
         SwimNode("p2", "Policyholder / Portal", 1, "Self-service arrangement", "promise-to-pay", kind="new"),
         SwimNode("p3", "Collections Analyst", 2, "Escalate (no response)", "T+21"),
         SwimNode("p4", "Collections Investigator", 3, "Lapse notice", "7-day final", kind="decision")],
        [SwimEdge("p1", "p2", dashed=True, kind="new", label="plan"), SwimEdge("p1", "p3"),
         SwimEdge("p3", "p4")],
        "Policyholders can self-serve a payment arrangement online; promise-to-pay is tracked automatically with break detection."),
    SwimPhase("3", "Resolution, write-off & provisioning", "Steps 10–14 · v2.0 adds ECL provisioning",
        ["Collections / Billing", "Finance", "Credit Investigator"],
        [SwimNode("q0", "Credit Investigator", 0, "Outcome at T+30?", "paid / unpaid", kind="decision"),
         SwimNode("q1", "Collections / Billing", 1, "Payment → reinstate", "oldest-arrears alloc", kind="terminal"),
         SwimNode("q2", "Credit Investigator", 1, "No payment → lapse", "SOP-INS-011", kind="exception"),
         SwimNode("q3", "Finance", 2, "Automated ECL provisioning", "IFRS 9", kind="new"),
         SwimNode("q4", "Credit Investigator", 2, "External agency referral", ">SGD 1,000"),
         SwimNode("q5", "Credit Investigator", 3, "Write-off recommendation", "T+90 · DOA")],
        [SwimEdge("q0", "q1", label="paid"), SwimEdge("q0", "q2", dashed=True, kind="exception", label="unpaid"),
         SwimEdge("q2", "q3", dashed=True, kind="new"), SwimEdge("q2", "q4", dashed=True, kind="exception"),
         SwimEdge("q4", "q5")],
        "v2.0 feeds expected-credit-loss provisioning from delinquency stage so reserves stay accurate ahead of any write-off."),
]

optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Guidewire BillingCenter Collections & Delinquency Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-003"),
                ("Version", "2.0 (Optimised)"),
                ("Effective Date", "01 October 2026"),
                ("Supersedes", "v1.3 dated 01 March 2025"),
                ("Owner", "Collections — Finance Department"),
                ("Approved By", "Finance Director"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-003 dated 18 June 2026"),
                ("Catalog Alignment Score", "90% (up from 68% in v1.3)"),
                ("Classification", "Internal Use Only"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v2.0",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-003. Alignment to the "
              "Guidewire BillingCenter collections catalog increased from 68% to 90%. Critical additions: proactive "
              "pre-due reminders, risk-based collections segmentation, self-service payment arrangements with "
              "promise-to-pay tracking, automated IFRS 9 ECL provisioning, and partial-payment allocation."],
             ["NEW STEP (green) — step added to close a gap vs the BillingCenter catalog",
              "ENHANCED (amber) — existing step updated with additional controls or automation"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines the process for collecting outstanding premiums from "
             "individual and commercial policyholders. Version 2.0 incorporates optimisations from fit-gap analysis "
             "against the Guidewire BillingCenter Collections & Delinquency Best-Practice Catalog, achieving 90% "
             "alignment (up from 68% in v1.3)."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to overdue instalments (30/60/90-day arrears), dishonoured direct "
             "debits and returned cheques, and reinstatement premium collection following a lapse notice."),
            ("banner", "new", "Scope extended: pre-due reminders and risk-based segmentation now apply to every "
             "billed account before it falls into arrears."),
            ("para", "This procedure does NOT cover employee expense reimbursements, reinsurance premium disputes, "
             "or broker commission clawbacks."),
        ]),
        DocSection("3. Authority Matrix", [
            ("table", ["Item", "First Authority", "Second Authority"],
             [["Payment plan ≤ SGD 5,000", "Credit Investigator", "—"],
              ["Payment plan > SGD 5,000", "Collections Manager", "Credit Investigator"],
              ["External agency referral", "Credit Investigator", "—"],
              ["Write-off ≤ SGD 2,000", "Finance Director", "Credit Investigator"],
              ["Write-off > SGD 2,000", "CFO", "Finance Director"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Collections Analyst", "Works the segmented arrears queue; outbound contact; records outcomes; processes inbound payments."],
              ["Collections Investigator", "Handles complex/high-value arrears; disputes; reinstatement coordination."],
              ["Credit Investigator", "Approves arrangements; owns ECL provisioning inputs, agency referral and write-off recommendations."],
              ["Agent / Broker", "Supports outreach for their book; flags hardship; facilitates arrangements."]], {}),
        ]),
        DocSection("5. Prevention & Segmentation (New Section — v2.0)", [
            ("banner", "crit", "New section. Required by the BillingCenter catalog. Pre-due reminders and "
             "propensity-based segmentation now precede any arrears milestone."),
            ("table", ["#", "Control", "Responsible", "Output / System", "Timeline"],
             [["P1", "Pre-due reminders", "CRM / Billing", "T-5/T-2 SMS and email nudges", "Pre-due"],
              ["P2", "Propensity-to-pay scoring", "Collections / Model", "Account scored; treatment path assigned", "T+1 day"],
              ["P3", "Segmented treatment routing", "Collections Analyst", "Effort prioritised to high-recovery accounts", "T+1 day"]],
             {0: "new", 1: "new", 2: "new"}),
        ]),
        DocSection("6. Process Steps", [
            ("h3", "6.1 Prevent & Detect Arrears"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "Proactive pre-due reminders", "CRM / Billing", "T-5/T-2 nudges", "Pre-due"],
              ["2", "Billing system flags overdue account", "Billing System", "Status 'Overdue'", "T+1 day"],
              ["3", "Risk-based segmentation & treatment path", "Collections / Model", "Propensity score; path assigned", "T+1 day"],
              ["4", "Automated reminder per segment", "CRM", "Tailored channel and cadence", "T+1 day"],
              ["5", "Analyst reviews high-value queue", "Collections Analyst", "Prioritised effort", "T+2 days"]],
             {0: "new", 2: "new", 3: "enh"}),
            ("h3", "6.2 Escalated Arrears"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["6", "Formal written notice of arrears", "Collections Analyst", "14-day cure period", "T+8 days"],
              ["7", "Self-service arrangement & promise-to-pay", "Policyholder / Portal", "Online plan; PTP tracking", "T+8–21 days"],
              ["8", "Escalate to Collections Investigator", "Collections Analyst", "T+21 escalation", "T+21 days"],
              ["9", "Lapse notice (T+30 if unresolved)", "Collections Investigator", "7-day final cure", "T+30 days"]],
             {1: "new"}),
            ("h3", "6.3 Resolution, Write-off & Provisioning"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["10", "Payment received — reinstate", "Collections / Billing", "Oldest-arrears allocation; status 'Active'", "T+31+"],
              ["11", "No payment — policy lapsed", "Collections Investigator", "Balance referred to Credit", "T+31+"],
              ["12", "Automated ECL provisioning", "Finance", "IFRS 9 provision from delinquency stage", "Ongoing"],
              ["13", "External agency referral (>SGD 1,000)", "Credit Investigator", "Debt file to agency", "T+60"],
              ["14", "Write-off recommendation (T+90)", "Credit Investigator", "DOA approval; GL adjustment", "T+90"]],
             {0: "enh", 2: "new"}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Disputed Balance"),
            ("numbered", [
                "Analyst escalates the dispute to a Collections Investigator within 1 business day.",
                "Investigator reviews records and responds within 5 business days; collections suspended pending resolution.",
                "Valid disputes: billing corrected and an adjusted statement issued."]),
            ("h3", "7.2 Financial Hardship & Forbearance (Enhanced — v2.0)"),
            ("banner", "enh", "Hardship now follows a documented forbearance/affordability framework with evidence capture."),
            ("numbered_from", 4, [
                "Policyholder submits a hardship application; Credit Investigator assesses within 3 business days.",
                "Extended plan up to 6 months approved; only timing is adjusted — total premium is not reduced.",
                "Forbearance terms and affordability evidence are recorded for regulatory audit."]),
            ("h3", "7.3 Deceased Policyholder"),
            ("numbered_from", 7, [
                "Collections activity suspended immediately on notification of death.",
                "Case transferred to Claims (estate recovery) and Legal; no external agency referral."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["Billing System (Sapiens)", "Arrears, allocation, lapse, provisioning feed", "Collections, Finance"],
              ["CRM (Salesforce)", "Contact history, segmentation, outreach", "Collections Analyst, Investigator"],
              ["Self-Service Portal", "Online arrangements and promise-to-pay", "Policyholders, Collections"],
              ["Dialler (NICE CXone)", "Outbound call management and compliance logging", "Collections Analyst"],
              ["Propensity Model", "Propensity-to-pay scoring and segmentation", "Collections, Credit"],
              ["SAP S/4HANA", "ECL provisioning, write-off postings, bad-debt provisions", "Finance, Credit"],
              ["External Agency Portal", "Debt file upload and status tracking", "Credit Investigator"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v2.0: pre-due prevention, propensity segmentation, self-service "
             "arrangements, and automated ECL provisioning."),
            ("bullets", [
                "Prevention: pre-due reminders reduce avoidable arrears entry.",
                "Segmentation: treatment prioritised by propensity-to-pay and balance.",
                "Promise-to-pay: arrangements tracked automatically with break detection.",
                "Provisioning: IFRS 9 ECL updated from delinquency stage, not only at write-off.",
                "Allocation: partial payments applied to oldest arrears by a configurable hierarchy.",
                "Forbearance: hardship terms and affordability evidence documented.",
                "Write-off governance: DOA approval with GL posting and immutable audit trail."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v1.3 Target", "v2.0 Target", "Measurement"],
             [["30-day collection rate", "≥80%", "≥86%", "Resolved within 30 days"],
              ["Lapse rate (non-payment)", "<2.5%/month", "<2.0%/month", "Lapsed / active portfolio"],
              ["Self-service adoption", "N/A (new)", "≥40% of arrangements", "Portal vs analyst plans"],
              ["Promise-to-pay kept", "N/A (new)", "≥85%", "PTP honoured / agreed"],
              ["Provision accuracy", "N/A (new)", "ECL within ±10%", "Provision vs actual loss"],
              ["Write-off rate", "<0.3%", "<0.25%", "Write-off / annual premium"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["1.3", "01 Mar 2025", "K. Sharma, Finance", "Added deceased policyholder exception; aligned write-off to DOA matrix"],
              ["2.0", "01 Oct 2026", "K. Sharma, Finance",
               "OPTIMISED: pre-due reminders; risk-based segmentation; self-service arrangements & promise-to-pay; "
               "IFRS 9 ECL provisioning; partial-payment allocation; catalog alignment 68% → 90%"]], {}),
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
    swim_cover_tags="Arrears · Escalation · Lapse · Reinstatement · Write-off",
    hierarchy_cover_sub="Phase breakdown with arrears milestones, escalation authority, and exception paths",
)
