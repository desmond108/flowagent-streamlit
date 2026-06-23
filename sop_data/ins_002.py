"""SOP-INS-002 — Premium Accounting (Meridian Insurance Group).

Fit-gap vs the Guidewire BillingCenter premium-billing best-practice catalog.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Guidewire BillingCenter — Premium Billing Best-Practice Catalog"
CATALOG_SHORT = "Guidewire BillingCenter"

meta = Meta(
    sop_id="SOP-INS-002", slug="Premium_Accounting",
    title="Premium Accounting", short_title="Premium accounting",
    version="2.0", owner="Finance — Premium Accounting",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="3.0", effective_date="01 October 2026",
    supersedes="v2.0 dated 15 February 2025", approved_by="Chief Financial Officer",
    classification="Internal Use Only",
)

phases = [
    Phase("1", "Review & premium validation", "Policy intake and premium check", "blue",
          "PAS · Premium Accounting", "Steps 1–4", "4 steps + 1 decision"),
    Phase("2", "Payment method setup", "Mandate, schedule, confirmation", "green",
          "Premium Accounting · CRM · Agent", "Steps 5–8", "4 steps"),
    Phase("3", "First payment processing", "Collection, reconciliation, activation", "amber",
          "Billing System · Premium Accounting", "Steps 9–11", "3 steps + 1 decision"),
]

steps = [
    Step("1", "1", "Home Office receives new policy notification from PAS", "PAS (automated)",
         "Email alert to Premium Accounting queue; policy accessible in billing system", "T+0", "Automated trigger", kind="trigger"),
    Step("2", "1", "Validate premium calculation against rating output", "Premium Accounting",
         "Billed premium matched to quote/schedule; variance above SGD 10 flagged", "T+1 day", "Variance threshold control"),
    Step("3", "1", "Confirm coverage period and instalment schedule", "Premium Accounting",
         "Annual/semi-annual/quarterly/monthly recorded in billing module", "T+1 day", "Schedule confirmed"),
    Step("4", "1", "Verify policyholder banking or card details", "Premium Accounting",
         "Bank/card validated via micro-deposit or card check", "T+1 day", "Account verification"),
    Step("", "1", "", "", "", "", "Variance investigation", kind="decision", decision="Premium variance?",
         branches=["Within SGD 10 → proceed to setup", "Above SGD 10 → hold + investigate (Sec 6.1)"]),
    Step("5", "2", "Configure direct debit mandate in billing system", "Premium Accounting",
         "GIRO/direct debit mandate activated; reference recorded in PAS", "T+2 days", "Mandate control"),
    Step("6", "2", "Set up payment schedule in billing module", "Premium Accounting",
         "Due dates, amounts and instalment plan loaded; first due date confirmed", "T+2 days", "Schedule loaded"),
    Step("7", "2", "Send first-payment confirmation to policyholder", "Premium Accounting / CRM",
         "Written confirmation by email/post; amount, due date and payment reference", "T+2 days", "Confirmation SLA: 1 day"),
    Step("8", "2", "Notify agent or branch of billing setup completion", "Premium Accounting",
         "Agent notified; confirmation logged in CRM", "T+2 days", "Agent notification"),
    Step("9", "3", "First premium collected on due date", "Billing System (automated)",
         "Payment deducted; receipt generated and emailed", "Due date", "Automated collection"),
    Step("10", "3", "Payment reconciled against policy record", "Premium Accounting",
         "Receipt matched to policy; GL entry posted in SAP", "Due date +1", "Reconciliation to GL"),
    Step("11", "3", "Update billing status in PAS to 'Active – Current'", "Premium Accounting",
         "Policy confirmed fully in-force; agent notified", "Due date +1", "Status activation", kind="complete"),
]

authority = [
    AuthorityRow("Variance ≤ SGD 10", "Premium Accounting", "—"),
    AuthorityRow("Variance SGD 11–500", "Premium Accounting", "Underwriting sign-off"),
    AuthorityRow("Variance above SGD 500", "Finance Manager", "Underwriting Manager"),
    AuthorityRow("Write-off / small balance", "Finance Manager", "—"),
    AuthorityRow("Refund authorisation", "Finance Manager", "CFO above SGD 25,000"),
]

swim_phases = [
    SwimPhase("1", "Review & premium validation", "Steps 1–4 · intake and premium check",
        ["PAS / System", "Premium Accounting", "Underwriting"],
        [SwimNode("s1", "PAS / System", 0, "New policy notification", "auto alert"),
         SwimNode("s2", "Premium Accounting", 1, "Validate premium vs rating", "variance > SGD 10 flagged"),
         SwimNode("s3", "Premium Accounting", 2, "Confirm instalment schedule", "billing module"),
         SwimNode("s4", "Premium Accounting", 3, "Verify bank / card details", "micro-deposit"),
         SwimNode("s5", "Underwriting", 2, "Variance hold & sign-off", "Sec 6.1", kind="exception")],
        [SwimEdge("s1", "s2", dashed=True), SwimEdge("s2", "s3"), SwimEdge("s3", "s4"),
         SwimEdge("s2", "s5", dashed=True, kind="exception", label="var")],
        "Policy issuance triggers premium validation; variances above SGD 10 are held for underwriting sign-off."),
    SwimPhase("2", "Payment method setup", "Steps 5–8 · mandate, schedule, confirmation",
        ["Premium Accounting", "Billing System", "CRM / Agent"],
        [SwimNode("a1", "Premium Accounting", 0, "Configure DD mandate", "GIRO"),
         SwimNode("a2", "Billing System", 1, "Load payment schedule", "due dates"),
         SwimNode("a3", "Premium Accounting", 2, "Send first-payment confirmation", "email / post"),
         SwimNode("a4", "CRM / Agent", 3, "Notify agent / branch", "logged in CRM", kind="terminal")],
        [SwimEdge("a1", "a2"), SwimEdge("a2", "a3"), SwimEdge("a3", "a4")],
        "The mandate and payment schedule are configured in Sapiens; the policyholder and agent receive written confirmation."),
    SwimPhase("3", "First payment processing", "Steps 9–11 · collection, reconciliation, activation",
        ["Billing System", "Premium Accounting", "Finance / SAP"],
        [SwimNode("d1", "Billing System", 0, "Collect first premium", "auto deduct"),
         SwimNode("d2", "Premium Accounting", 1, "Reconcile to policy", "match receipt"),
         SwimNode("d3", "Finance / SAP", 2, "Post GL entry", "SAP S/4HANA"),
         SwimNode("d4", "Premium Accounting", 3, "Activate billing status", "Active – Current", kind="terminal"),
         SwimNode("d5", "Premium Accounting", 0, "Failed payment → Collections", "Sec 6.2", kind="exception")],
        [SwimEdge("d1", "d2"), SwimEdge("d2", "d3"), SwimEdge("d3", "d4"),
         SwimEdge("d1", "d5", dashed=True, kind="exception", label="fail")],
        "On the due date the first premium is collected, reconciled and posted to the GL; failed payments route to Collections."),
]

fg_items = [
    FitItem("1", "Automated policy intake", "FIT",
        "PAS-triggered notification into the billing queue aligns with BillingCenter policy-to-billing integration.",
        "PAS / Premium Accounting", "GW-BC-INT-01", "p1"),
    FitItem("2", "Premium validation vs rating", "PARTIAL",
        "Premium is validated manually against the schedule with a fixed SGD 10 flag. BillingCenter auto-reconciles "
        "billed-to-rated premium and raises variance exceptions systematically.",
        "Premium Accounting", "GW-BC-INV-02", "p1"),
    FitItem("3", "Instalment schedule configuration", "FIT",
        "Annual to monthly instalment options recorded in the billing module align with BillingCenter payment plans.",
        "Premium Accounting", "GW-BC-PLN-01", "p1"),
    FitItem("4", "Bank / card verification", "FIT",
        "Micro-deposit / card verification before mandate setup aligns with BillingCenter payment-instrument validation.",
        "Premium Accounting", "GW-BC-PAY-03", "p1"),
    FitItem("5", "Direct debit mandate setup", "FIT",
        "GIRO/direct-debit mandate activation with reference recorded in PAS aligns with BillingCenter mandate management.",
        "Premium Accounting", "GW-BC-PAY-01", "p2"),
    FitItem("6", "Instalment fees & partial payments", "GAP",
        "No instalment-fee logic or handling of partial/short payments. BillingCenter applies plan fees and an "
        "allocation hierarchy for partial receipts.",
        "Premium Accounting", "GW-BC-PLN-04", "p2"),
    FitItem("7", "First-payment confirmation", "FIT",
        "Written confirmation with amount, due date and reference aligns with BillingCenter billing communications.",
        "Premium Accounting / CRM", "GW-BC-COM-01", "p2"),
    FitItem("8", "GST / premium tax handling", "GAP",
        "No explicit GST/premium-tax computation, posting or reporting step. BillingCenter itemises and posts "
        "premium tax separately for regulatory reporting.",
        "Premium Accounting / Finance", "GW-BC-TAX-01", "p2"),
    FitItem("9", "Automated collection", "FIT",
        "Scheduled auto-collection with receipt issuance aligns with BillingCenter direct-debit processing.",
        "Billing System", "GW-BC-COL-01", "p3"),
    FitItem("10", "Unapplied / suspense cash", "GAP",
        "Receipts are matched manually; there is no suspense/unapplied-cash account for unmatched payments. "
        "BillingCenter posts unmatched cash to suspense and works it off systematically.",
        "Premium Accounting", "GW-BC-CSH-02", "p3"),
    FitItem("11", "Reconciliation to GL", "PARTIAL",
        "GL posting to SAP is performed per policy. BillingCenter posts an automated subledger with daily "
        "reconciliation and an exceptions dashboard rather than manual matching.",
        "Premium Accounting / Finance", "GW-BC-GL-01", "p3"),
    FitItem("12", "Delinquency / dunning", "GAP",
        "Failed first payment is handled manually by Collections. BillingCenter runs an automated delinquency/dunning "
        "workflow with staged notices and lapse triggers.",
        "Collections", "GW-BC-DLQ-01", "p3"),
    FitItem("13", "Write-off / small-balance tolerance", "PARTIAL",
        "No documented small-balance write-off tolerance. BillingCenter auto-writes-off balances below a threshold "
        "to avoid uneconomic collection.",
        "Finance", "GW-BC-WO-01", "p3"),
    FitItem("14", "Billing status activation", "FIT",
        "Status set to 'Active – Current' with agent notification aligns with BillingCenter account status management.",
        "Premium Accounting", "GW-BC-ACC-01", "p3"),
]

fitgap = FitGap(
    overall_fit=66, partial_pct=16, fits=7, gaps=4, partials=3,
    steps_analysed=14, phases_count=3,
    summary_line="Overall alignment of SOP-INS-002 against the Guidewire BillingCenter billing catalog",
    metrics=[
        ("Steps analysed", "14 steps across 3 phases"),
        ("Fits confirmed", "7 steps aligned to catalog"),
        ("Gaps identified", "4 steps — remediation required"),
        ("Partial fits", "3 steps — enhancement recommended"),
        ("Highest risk area", "Unapplied/suspense cash (missing)"),
        ("Compliance gap", "No GST / premium-tax handling"),
        ("Ref standard", "Guidewire BillingCenter Billing Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Validation", 74, ""),
        FitPhaseBar("Phase 2", "Setup", 62, ""),
        FitPhaseBar("Phase 3", "Collection", 60, ""),
        FitPhaseBar("Cash /", "GL", 52, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 74, "Review & validation"),
        PhaseScoreCard("Phase 2", 62, "Payment setup"),
        PhaseScoreCard("Phase 3", 60, "First payment"),
        PhaseScoreCard("Cash/GL", 52, "Reconciliation"),
    ],
    detail_slides=[
        ("Phase 1 — Review & premium validation", "Steps 1–4 vs Guidewire BillingCenter catalog", ["p1"]),
        ("Phase 2 — Payment method setup", "Steps 5–8 vs Guidewire BillingCenter catalog", ["p2"]),
        ("Phase 3 — First payment & reconciliation", "Steps 9–14 vs Guidewire BillingCenter catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — REVIEW & PREMIUM VALIDATION"),
            ("p2", "PHASE 2 — PAYMENT METHOD SETUP"),
            ("p3", "PHASE 3 — FIRST PAYMENT & RECONCILIATION")],
    critical_missing=[
        CriticalGap("Unapplied / suspense cash management",
            "Unmatched receipts have no suspense account; manual matching risks misallocation and reconciliation "
            "breaks. BillingCenter posts unmatched cash to suspense and works it off with an ageing report."),
        CriticalGap("Automated delinquency / dunning",
            "Failed payments are worked manually by Collections with no staged dunning. BillingCenter automates "
            "delinquency notices, grace periods and lapse triggers."),
        CriticalGap("GST / premium-tax handling",
            "No explicit premium-tax computation, posting or reporting, a regulatory gap versus the catalog's "
            "tax itemisation."),
        CriticalGap("Write-off & small-balance tolerance",
            "No documented tolerance for uneconomic small balances, leading to manual effort and stale receivables."),
    ],
    radar=[("Policy intake", 82), ("Premium validation", 70), ("Mandate setup", 80), ("Cash application", 45),
           ("Delinquency", 40), ("Tax handling", 35), ("GL reconciliation", 60)],
    control_bars=[
        ControlBar("Policy intake", 82, "Automated PAS-to-billing trigger"),
        ControlBar("Premium validation", 70, "Manual check; fixed variance threshold"),
        ControlBar("Mandate & schedule", 80, "GIRO mandate and plan setup solid"),
        ControlBar("Cash application", 45, "Manual matching; no suspense account"),
        ControlBar("Delinquency / dunning", 40, "Manual collections; no staged dunning"),
        ControlBar("Tax handling", 35, "No GST/premium-tax itemisation"),
        ControlBar("GL reconciliation", 60, "Per-policy posting; no daily auto-recon"),
    ],
    remediations=[
        Remediation(1, "Introduce suspense / unapplied-cash management",
            "Post unmatched receipts to a suspense account with an ageing report; auto-match on payment reference "
            "and work off exceptions daily. Effort: 4 weeks (Sapiens + SAP).", "High"),
        Remediation(2, "Automate delinquency / dunning workflow",
            "Configure staged dunning notices, grace periods and lapse triggers for failed and overdue payments, "
            "replacing manual collections handling. Effort: 5 weeks.", "High"),
        Remediation(3, "Add GST / premium-tax handling",
            "Compute, itemise and post premium tax separately for regulatory reporting at billing setup. "
            "Effort: 3 weeks (Finance + Sapiens).", "High"),
        Remediation(4, "Automate billed-to-rated reconciliation",
            "Replace manual premium validation with an automated billed-vs-rated reconciliation that raises only "
            "variance exceptions. Effort: 3 weeks.", "Medium"),
        Remediation(5, "Define instalment fees & small-balance write-off",
            "Add instalment-fee logic, a partial-payment allocation hierarchy, and an auto-write-off tolerance for "
            "uneconomic balances. Effort: 3 weeks.", "Medium"),
    ],
    risk_impact=[("Unapplied cash", 88), ("Delinquency automation", 80), ("Tax handling", 72),
                 ("Auto reconciliation", 60), ("Instalment fees", 50), ("Write-off tolerance", 45)],
    projected_fit=90,
)

opt_phases = [
    Phase("1", "Review & premium validation", "Auto-reconciliation; tax setup", "blue",
          "PAS · Premium Accounting", "Steps 1–5", "5 steps + 1 decision"),
    Phase("2", "Payment method setup", "Mandate, plan, fees, confirmation", "green",
          "Premium Accounting · Billing · CRM", "Steps 6–9", "4 steps"),
    Phase("3", "Collection, cash & reconciliation", "Collection, suspense, dunning, GL", "amber",
          "Billing System · Premium Accounting · Finance", "Steps 10–14", "5 steps + 1 decision"),
]

opt_steps = [
    Step("1", "1", "New policy notification from PAS", "PAS (automated)",
         "Alert to billing queue", "T+0", "Standard", kind="trigger"),
    Step("2", "1", "Automated billed-to-rated reconciliation", "Premium Accounting / System",
         "Billed premium auto-reconciled to rating; only variances raised as exceptions", "T+0",
         "ENHANCED (v3.0)"),
    Step("3", "1", "Confirm coverage period and instalment schedule", "Premium Accounting",
         "Schedule recorded in billing module", "T+1 day", "Standard"),
    Step("4", "1", "Compute GST / premium tax", "Premium Accounting / Finance",
         "Premium tax itemised and posted separately for reporting", "T+1 day",
         "NEW (v3.0) — regulatory"),
    Step("5", "1", "Verify policyholder banking or card details", "Premium Accounting",
         "Bank/card validated via micro-deposit or card check", "T+1 day", "Standard"),
    Step("", "1", "", "", "", "", "Variance exception", kind="decision", decision="Premium variance?",
         branches=["Within tolerance → setup", "Exception → underwriting sign-off (Sec 6.1)"]),
    Step("6", "2", "Configure direct debit mandate", "Premium Accounting",
         "GIRO/direct-debit mandate activated", "T+2 days", "Standard"),
    Step("7", "2", "Set up payment schedule with instalment fees", "Premium Accounting",
         "Plan loaded with instalment-fee logic and partial-payment allocation", "T+2 days",
         "ENHANCED (v3.0)"),
    Step("8", "2", "Send first-payment confirmation", "Premium Accounting / CRM",
         "Written confirmation; amount, due date, reference", "T+2 days", "Standard"),
    Step("9", "2", "Notify agent or branch", "Premium Accounting",
         "Agent notified; logged in CRM", "T+2 days", "Standard"),
    Step("10", "3", "First premium collected on due date", "Billing System (automated)",
         "Payment deducted; receipt issued", "Due date", "Standard"),
    Step("11", "3", "Cash application with suspense handling", "Premium Accounting / System",
         "Receipts auto-matched; unmatched cash posted to suspense and aged", "Due date",
         "NEW (v3.0) — cash control", kind="control"),
    Step("12", "3", "Automated subledger reconciliation to GL", "Premium Accounting / Finance",
         "Daily subledger posted to SAP; exceptions dashboard worked", "Due date +1",
         "ENHANCED (v3.0)"),
    Step("13", "3", "Delinquency / dunning on failed or overdue", "Collections / System",
         "Staged dunning notices, grace periods and lapse triggers", "On failure",
         "NEW (v3.0) — automated collections", kind="control"),
    Step("14", "3", "Activate billing status / small-balance write-off", "Premium Accounting",
         "Status set Active – Current; uneconomic balances auto-written-off within tolerance", "Due date +1",
         "ENHANCED (v3.0)", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "Review & premium validation", "Steps 1–5 · v3.0 adds auto-recon & tax",
        ["PAS / System", "Premium Accounting", "Finance"],
        [SwimNode("o1", "PAS / System", 0, "New policy notification", "auto alert"),
         SwimNode("o2", "Premium Accounting", 1, "Auto billed-vs-rated recon", "exceptions only", kind="enhanced"),
         SwimNode("o3", "Premium Accounting", 2, "Confirm instalment schedule", "billing module"),
         SwimNode("o4", "Finance", 2, "Compute GST / premium tax", "itemised", kind="new"),
         SwimNode("o5", "Premium Accounting", 3, "Verify bank / card details", "micro-deposit")],
        [SwimEdge("o1", "o2", dashed=True), SwimEdge("o2", "o3"), SwimEdge("o3", "o5"),
         SwimEdge("o3", "o4", dashed=True, kind="new", label="tax")],
        "v3.0 automates billed-to-rated reconciliation and adds a GST/premium-tax computation and posting step."),
    SwimPhase("2", "Payment method setup", "Steps 6–9 · mandate, plan & fees",
        ["Premium Accounting", "Billing System", "CRM / Agent"],
        [SwimNode("p1", "Premium Accounting", 0, "Configure DD mandate", "GIRO"),
         SwimNode("p2", "Billing System", 1, "Load plan with fees", "instalment fees", kind="enhanced"),
         SwimNode("p3", "Premium Accounting", 2, "First-payment confirmation", "email / post"),
         SwimNode("p4", "CRM / Agent", 3, "Notify agent / branch", "logged", kind="terminal")],
        [SwimEdge("p1", "p2"), SwimEdge("p2", "p3"), SwimEdge("p3", "p4")],
        "Plans now carry instalment-fee logic and a partial-payment allocation hierarchy."),
    SwimPhase("3", "Collection, cash & reconciliation", "Steps 10–14 · v3.0 adds suspense & dunning",
        ["Billing System", "Premium Accounting", "Finance / Collections"],
        [SwimNode("q1", "Billing System", 0, "Collect first premium", "auto deduct"),
         SwimNode("q2", "Premium Accounting", 1, "Cash application + suspense", "auto-match / age", kind="new"),
         SwimNode("q3", "Finance / Collections", 1, "Subledger recon to GL", "daily", kind="enhanced"),
         SwimNode("q4", "Premium Accounting", 2, "Activate / write-off", "tolerance", kind="terminal"),
         SwimNode("q5", "Finance / Collections", 2, "Delinquency / dunning", "staged notices", kind="new")],
        [SwimEdge("q1", "q2"), SwimEdge("q2", "q3"), SwimEdge("q3", "q4"),
         SwimEdge("q1", "q5", dashed=True, kind="new", label="fail")],
        "v3.0 introduces suspense/unapplied-cash handling, daily subledger reconciliation, and an automated delinquency/dunning workflow."),
]

optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Guidewire BillingCenter Premium Billing Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-002"),
                ("Version", "3.0 (Optimised)"),
                ("Effective Date", "01 October 2026"),
                ("Supersedes", "v2.0 dated 15 February 2025"),
                ("Owner", "Finance — Premium Accounting"),
                ("Approved By", "Chief Financial Officer"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-002 dated 18 June 2026"),
                ("Catalog Alignment Score", "90% (up from 66% in v2.0)"),
                ("Classification", "Internal Use Only"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v3.0",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-002. Alignment to the "
              "Guidewire BillingCenter billing catalog increased from 66% to 90%. Critical additions: suspense / "
              "unapplied-cash management, an automated delinquency/dunning workflow, GST/premium-tax handling, "
              "automated billed-to-rated reconciliation, and a small-balance write-off tolerance."],
             ["NEW STEP (green) — step added to close a gap vs the BillingCenter catalog",
              "ENHANCED (amber) — existing step updated with additional controls or automation"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines the process for reviewing newly onboarded policies "
             "and establishing premium payment arrangements. Version 3.0 incorporates optimisations from fit-gap "
             "analysis against the Guidewire BillingCenter Premium Billing Best-Practice Catalog, achieving 90% "
             "alignment (up from 66% in v2.0)."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to all personal and commercial lines policies newly issued by Meridian, "
             "across online, agent, broker and bancassurance channels, and to mid-term changes that alter billing."),
            ("banner", "new", "Scope extended: GST/premium-tax computation and suspense-cash handling now apply to "
             "every billing setup and receipt."),
            ("para", "This procedure does NOT cover claims payment (SOP-INS-007), refund handling (SOP-FIN-012), "
             "or reinsurance premium settlements."),
        ]),
        DocSection("3. Authority Matrix", [
            ("table", ["Item", "First Authority", "Second Authority"],
             [["Variance ≤ SGD 10", "Premium Accounting", "—"],
              ["Variance SGD 11–500", "Premium Accounting", "Underwriting sign-off"],
              ["Variance above SGD 500", "Finance Manager", "Underwriting Manager"],
              ["Write-off / small balance", "Finance Manager", "—"],
              ["Refund authorisation", "Finance Manager", "CFO above SGD 25,000"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Branch / Agent", "Confirms payment preference at point of sale; submits setup request; addresses billing queries."],
              ["Premium Accounting", "Validates premium; configures mandates and plans; applies cash; reconciles to GL; manages suspense."],
              ["Collections Specialist", "Runs delinquency/dunning; manages failed payments and reinstatement."],
              ["Finance", "Owns GST posting, GL reconciliation, write-off tolerance and refunds."]], {}),
        ]),
        DocSection("5. Cash & Tax Controls (New Section — v3.0)", [
            ("banner", "crit", "New section. Required by the BillingCenter catalog. Suspense-cash handling and "
             "premium-tax posting are now mandatory controls on every receipt and billing setup."),
            ("table", ["#", "Control", "Responsible", "Output / System", "Timeline"],
             [["X1", "GST / premium-tax computation", "Finance", "Premium tax itemised and posted separately", "At setup"],
              ["X2", "Suspense / unapplied-cash account", "Premium Accounting", "Unmatched receipts posted to suspense and aged", "Daily"],
              ["X3", "Small-balance write-off tolerance", "Finance", "Uneconomic balances auto-written-off within tolerance", "Monthly"]],
             {0: "new", 1: "new", 2: "new"}),
        ]),
        DocSection("6. Process Steps", [
            ("h3", "6.1 Review & Premium Validation"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "New policy notification from PAS", "PAS", "Alert to billing queue", "T+0"],
              ["2", "Automated billed-to-rated reconciliation", "Premium Accounting", "Variances raised as exceptions only", "T+0"],
              ["3", "Confirm coverage period and instalment schedule", "Premium Accounting", "Schedule recorded", "T+1 day"],
              ["4", "Compute GST / premium tax", "Finance", "Premium tax itemised and posted", "T+1 day"],
              ["5", "Verify banking or card details", "Premium Accounting", "Micro-deposit / card check", "T+1 day"]],
             {1: "enh", 3: "new"}),
            ("h3", "6.2 Payment Method Setup"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["6", "Configure direct debit mandate", "Premium Accounting", "GIRO mandate activated", "T+2 days"],
              ["7", "Set up payment schedule with instalment fees", "Premium Accounting", "Plan + fee logic + allocation", "T+2 days"],
              ["8", "Send first-payment confirmation", "Premium Accounting / CRM", "Amount, due date, reference", "T+2 days"],
              ["9", "Notify agent or branch", "Premium Accounting", "Logged in CRM", "T+2 days"]],
             {1: "enh"}),
            ("h3", "6.3 Collection, Cash & Reconciliation"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["10", "First premium collected on due date", "Billing System", "Payment deducted; receipt issued", "Due date"],
              ["11", "Cash application with suspense handling", "Premium Accounting", "Auto-match; unmatched to suspense", "Due date"],
              ["12", "Automated subledger reconciliation to GL", "Finance", "Daily subledger to SAP; exceptions worked", "Due date +1"],
              ["13", "Delinquency / dunning on failure", "Collections", "Staged notices; lapse triggers", "On failure"],
              ["14", "Activate status / small-balance write-off", "Premium Accounting", "Active – Current; write-off within tolerance", "Due date +1"]],
             {1: "new", 2: "enh", 3: "new", 4: "enh"}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Premium Variance"),
            ("numbered", [
                "Billing is placed on hold and the issuing agent notified within 1 business day.",
                "Agent or Underwriting confirms the correct premium within 3 business days; endorsement issued if required.",
                "Billing setup resumes only after written Underwriting sign-off on the correct amount."]),
            ("h3", "7.2 Failed Payment & Dunning (Enhanced — v3.0)"),
            ("banner", "enh", "Failed payments now enter an automated dunning workflow rather than ad-hoc manual follow-up."),
            ("numbered_from", 4, [
                "Automated dunning notice issued on payment failure; policyholder given a grace period.",
                "Collections contacts the policyholder within 2 business days; 5 business days to provide an alternate method.",
                "If unresolved, a lapse trigger issues a cancellation notice per SOP-INS-011."]),
            ("h3", "7.3 Invalid Banking Details"),
            ("numbered_from", 7, [
                "Agent notified immediately; policyholder contacted for correction within 1 business day.",
                "Corrected details submitted via secure channel; Premium Accounting re-validates and reactivates billing within 24 hours."]),
            ("h3", "7.4 Unapplied Cash (New — v3.0)"),
            ("banner", "new", "New exception. Unmatched receipts are held in suspense and worked off via an ageing report."),
            ("numbered_from", 9, [
                "Unmatched receipts posted to the suspense account and aged daily.",
                "Items unresolved after 30 days escalated to Finance for investigation or refund."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["Policy Administration System (PAS)", "Policy issuance data; payment-setup trigger", "Premium Accounting, Agent"],
              ["Billing System (Sapiens)", "Schedules, mandates, instalments, suspense, dunning", "Premium Accounting, Collections"],
              ["SAP S/4HANA", "GL subledger, premium-tax and receipt posting", "Finance"],
              ["CRM (Salesforce)", "Agent and policyholder communications", "Premium Accounting, Agent"],
              ["Banking Portal (GIRO / Direct Debit)", "Mandate registration and payment execution", "Premium Accounting"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v3.0: suspense-cash, automated dunning, premium-tax posting, "
             "automated reconciliation and write-off tolerance."),
            ("bullets", [
                "Suspense control: unmatched receipts never posted directly to policy; held and aged in suspense.",
                "Automated reconciliation: billed-vs-rated and subledger-to-GL reconciled daily with exceptions worked.",
                "Premium tax: GST itemised and posted separately for regulatory reporting.",
                "Delinquency: staged dunning with documented grace periods and lapse triggers.",
                "Write-off tolerance: uneconomic balances auto-written-off within an approved threshold.",
                "Segregation of duties: setup ≠ cash application ≠ write-off approval.",
                "Immutable audit trail: validation, setup, collection and reconciliation events logged."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v2.0 Target", "v3.0 Target", "Measurement"],
             [["Billing setup SLA", "≤2 business days", "≤2 business days", "Issuance to setup"],
              ["Premium variance rate", "<0.5%", "<0.3%", "Corrections post-issuance"],
              ["Cash applied same day", "N/A (new)", "≥98%", "Receipts matched / received"],
              ["Suspense ageing >30 days", "N/A (new)", "<1%", "Suspense ageing report"],
              ["First-payment failure rate", "<3%", "<2.5%", "Failed / monthly new business"],
              ["GL reconciliation breaks", "N/A (new)", "Zero unexplained", "Daily subledger recon"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["2.0", "15 Feb 2025", "M. Patel, Finance", "Added premium variance exception handling; aligned to SAP S/4HANA migration"],
              ["3.0", "01 Oct 2026", "M. Patel, Finance",
               "OPTIMISED: suspense/unapplied cash; automated dunning; GST handling; automated reconciliation; "
               "small-balance write-off; catalog alignment 66% → 90%"]], {}),
        ]),
    ],
)

package = SopPackage(
    meta=meta, phases=phases, steps=steps, authority=authority, swim_phases=swim_phases,
    n_phases=3, n_steps=11, n_roles=4, n_gateways=2,
    fitgap=fitgap,
    opt_phases=opt_phases, opt_steps=opt_steps, opt_swim_phases=opt_swim_phases,
    opt_n_phases=3, opt_n_steps=14, opt_n_gateways=2, opt_fit=90,
    optimised_doc=optimised_doc,
    swim_cover_tags="Validation · Mandate setup · Collection · Reconciliation · Exception handling",
    hierarchy_cover_sub="Phase breakdown with billing tracks, variance authority, and exception paths",
)
