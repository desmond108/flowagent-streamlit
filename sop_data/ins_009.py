"""SOP-INS-009 — In-Force Customer Service (General) (Meridian Insurance Group).

Fit-gap vs the Salesforce Service Cloud insurance-servicing catalog.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Salesforce Service Cloud — Insurance Servicing Best-Practice Catalog"
CATALOG_SHORT = "Service Cloud"

meta = Meta(
    sop_id="SOP-INS-009", slug="In_Force_Customer_Service",
    title="In-Force Customer Service", short_title="In-force customer service",
    version="3.0", owner="Customer Service — Policy Servicing",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="3.1", effective_date="01 October 2026",
    supersedes="v3.0 dated 01 January 2025", approved_by="Chief Customer Officer",
    classification="Internal Use Only",
)

phases = [
    Phase("1", "Contact receipt & verification", "Intake, identity, context", "blue",
          "Policyholder · CSR · PAS", "Steps 1–4", "4 steps + 1 decision"),
    Phase("2", "Request handling", "Resolve, update, escalate", "green",
          "CSR · Policy Service · Member Care", "Steps 5–9", "5 steps + 1 decision"),
    Phase("3", "Closure & quality", "Confirm, close, survey", "amber",
          "CSR · CRM", "Steps 10–12", "3 steps"),
]

steps = [
    Step("1", "1", "Inbound contact received (phone, email, chat, portal)", "CSR / ACD System",
         "Contact logged in CRM; channel and timestamp recorded", "Real time", "Omni-channel intake", kind="trigger"),
    Step("2", "1", "Identity verification", "CSR",
         "3-point verification: policy number, DOB and postcode/email; on hold until passed", "Real time", "Key control: 3-point ID"),
    Step("3", "1", "Contact purpose identified and categorised", "CSR",
         "Contact type coded in CRM (enquiry, update, payment, document, complaint)", "Real time", "Categorisation"),
    Step("4", "1", "Policy record retrieved and reviewed", "CSR / PAS",
         "Policy status, payment standing and interaction history reviewed before engaging", "Real time", "Context review"),
    Step("", "1", "", "", "", "", "Identity gate", kind="decision", decision="Identity verified?",
         branches=["Pass → handle request", "Fail (2 attempts) → terminate + security flag (Sec 6.1)"]),
    Step("5", "2", "Standard enquiry resolved at first contact", "CSR",
         "Policy info, billing, payment dates and coverage summaries within CSR authority", "Real time", "First-contact resolution"),
    Step("6", "2", "Account update processed (address, payment, contacts)", "CSR / Policy Service Rep",
         "Update processed in PAS; confirmation emailed; change noted in CRM", "Real time", "Account update"),
    Step("7", "2", "Document request fulfilled", "CSR / PAS (auto)",
         "Certificate, schedule or receipt regenerated and emailed within 24 hours", "≤24 hours", "Document fulfilment"),
    Step("8", "2", "Payment received or arrangement set up", "CSR",
         "Payment via IVR or agent-assisted; arrangement per SOP-INS-003 authority", "Real time", "Payment handling"),
    Step("9", "2", "Complex or sensitive contact escalated to Member Care", "CSR / Member Care Rep",
         "Escalation logged; Member Care contacts policyholder within 2 hours", "≤2 hours", "Escalation control"),
    Step("10", "3", "Resolution confirmed with policyholder", "CSR",
         "Summary of actions communicated verbally or in writing", "Real time", "Resolution confirmation"),
    Step("11", "3", "Contact record closed and coded in CRM", "CSR",
         "Resolution code, handle time and CSAT prompt recorded; follow-up task if pending", "Real time", "Closure coding"),
    Step("12", "3", "Post-interaction survey sent", "CRM (auto)",
         "CSAT survey dispatched; responses captured for quality reporting", "Post-contact", "CSAT capture", kind="complete"),
]

authority = [
    AuthorityRow("Standard enquiry / document", "CSR", "—"),
    AuthorityRow("Account update (non-financial)", "CSR", "Policy Service Rep"),
    AuthorityRow("Payment arrangement", "CSR", "per SOP-INS-003 matrix"),
    AuthorityRow("Complex / VIP / sensitive", "Member Care Rep", "Team Leader"),
    AuthorityRow("Exception outside CSR authority", "Team Leader", "—"),
]

swim_phases = [
    SwimPhase("1", "Contact receipt & verification", "Steps 1–4 · intake to context",
        ["Policyholder", "CSR", "PAS / Security"],
        [SwimNode("s1", "Policyholder", 0, "Inbound contact", "phone · email · chat · portal"),
         SwimNode("s2", "CSR", 1, "Identity verification", "3-point", kind="decision"),
         SwimNode("s3", "CSR", 2, "Categorise contact", "CRM coded"),
         SwimNode("s4", "PAS / Security", 3, "Retrieve policy record", "status · standing"),
         SwimNode("s5", "PAS / Security", 2, "Failed ID → terminate", "security flag", kind="exception")],
        [SwimEdge("s1", "s2", dashed=True), SwimEdge("s2", "s3", label="pass"),
         SwimEdge("s2", "s5", dashed=True, kind="exception", label="fail"), SwimEdge("s3", "s4")],
        "Every contact passes 3-point identity verification before any account information is provided; failures trigger a security flag."),
    SwimPhase("2", "Request handling", "Steps 5–9 · resolve, update, escalate",
        ["CSR", "Policy Service / PAS", "Member Care"],
        [SwimNode("a1", "CSR", 0, "Resolve standard enquiry", "first contact"),
         SwimNode("a2", "Policy Service / PAS", 1, "Process account update", "PAS + confirmation"),
         SwimNode("a3", "Policy Service / PAS", 2, "Fulfil document request", "≤24h"),
         SwimNode("a4", "CSR", 1, "Payment / arrangement", "IVR / assisted"),
         SwimNode("a5", "Member Care", 2, "Escalate complex / sensitive", "≤2h", kind="exception")],
        [SwimEdge("a1", "a2"), SwimEdge("a2", "a3"), SwimEdge("a1", "a4"),
         SwimEdge("a1", "a5", dashed=True, kind="exception", label="esc")],
        "Standard enquiries, updates, documents and payments are handled at first contact; complex or sensitive cases escalate to Member Care."),
    SwimPhase("3", "Closure & quality", "Steps 10–12 · confirm to survey",
        ["CSR", "Policyholder", "CRM"],
        [SwimNode("d1", "CSR", 0, "Confirm resolution", "summary of actions"),
         SwimNode("d2", "CSR", 1, "Close & code contact", "resolution code · AHT"),
         SwimNode("d3", "CRM", 2, "Send CSAT survey", "quality reporting", kind="terminal")],
        [SwimEdge("d1", "d2"), SwimEdge("d2", "d3")],
        "Contacts are confirmed, coded and closed, and a CSAT survey is dispatched for quality reporting."),
]

fg_items = [
    FitItem("1", "Omni-channel intake", "FIT",
        "Phone, email, chat and portal logged in CRM with channel/timestamp align with Service Cloud omni-channel.",
        "CSR / ACD", "SF-SC-OMN-01", "p1"),
    FitItem("2", "Identity verification", "PARTIAL",
        "3-point knowledge-based verification is enforced, but the catalog recommends step-up authentication "
        "(OTP/biometric) for sensitive changes — KBA alone is increasingly bypassable.",
        "CSR", "SF-SC-IDV-01", "p1"),
    FitItem("3", "Contact categorisation", "FIT",
        "Coded contact types in CRM align with Service Cloud case classification.",
        "CSR", "SF-SC-CAS-01", "p1"),
    FitItem("4", "Unified policy context", "PARTIAL",
        "Policy context is reviewed from PAS, but the agent works across PAS and CRM without a single 360° "
        "customer view/agent desktop as the catalog recommends.",
        "CSR / PAS", "SF-SC-360-01", "p1"),
    FitItem("5", "First-contact resolution", "FIT",
        "Standard enquiries resolved within authority at first contact align with Service Cloud FCR practice.",
        "CSR", "SF-SC-FCR-01", "p2"),
    FitItem("6", "Self-service deflection", "GAP",
        "A self-service portal exists but is limited; the catalog deflects routine contacts via an AI assistant/"
        "chatbot and expanded self-service, reducing volume and AHT.",
        "Policyholder / Portal", "SF-SC-SS-01", "p2"),
    FitItem("7", "AI agent-assist & knowledge", "GAP",
        "No agent-assist, knowledge suggestions or next-best-action. The catalog surfaces knowledge and recommended "
        "actions in-flow to improve consistency and FCR.",
        "CSR", "SF-SC-AI-01", "p2"),
    FitItem("8", "Account update processing", "FIT",
        "PAS account updates with emailed confirmation align with Service Cloud service requests.",
        "CSR / Policy Service Rep", "SF-SC-REQ-01", "p2"),
    FitItem("9", "Escalation to Member Care", "FIT",
        "Logged escalation with a 2-hour callback aligns with Service Cloud escalation/queue management.",
        "Member Care Rep", "SF-SC-ESC-01", "p2"),
    FitItem("10", "Complaint & sentiment detection", "PARTIAL",
        "Complaints are spotted by manual keyword recognition. The catalog applies automated sentiment/complaint "
        "detection to flag at-risk interactions in real time.",
        "CSR", "SF-SC-SEN-01", "p2"),
    FitItem("11", "Vulnerable-customer & consent handling", "GAP",
        "No structured vulnerable-customer identification or consent capture for changes. The catalog supports "
        "vulnerability flags and consent logging — a conduct and privacy gap.",
        "Member Care / CSR", "SF-SC-VUL-01", "p2"),
    FitItem("12", "Closure coding & CSAT", "FIT",
        "Resolution coding, handle-time capture and CSAT survey align with Service Cloud closure and feedback.",
        "CSR / CRM", "SF-SC-CSAT-01", "p3"),
    FitItem("13", "Quality / interaction analytics", "PARTIAL",
        "Quality is scored manually on samples. The catalog uses interaction/speech analytics to QA at scale and "
        "coach automatically.",
        "Team Leader", "SF-SC-QA-01", "p3"),
]

fitgap = FitGap(
    overall_fit=69, partial_pct=22, fits=6, gaps=3, partials=4,
    steps_analysed=13, phases_count=3,
    summary_line="Overall alignment of SOP-INS-009 against the Salesforce Service Cloud servicing catalog",
    metrics=[
        ("Steps analysed", "13 steps across 3 phases"),
        ("Fits confirmed", "6 steps aligned to catalog"),
        ("Gaps identified", "3 steps — remediation required"),
        ("Partial fits", "4 steps — enhancement recommended"),
        ("Highest risk area", "Knowledge-based ID only"),
        ("Experience gap", "No AI assist / self-service deflection"),
        ("Ref standard", "Salesforce Service Cloud Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Receipt", 72, ""),
        FitPhaseBar("Phase 2", "Handling", 60, ""),
        FitPhaseBar("Phase 3", "Closure", 80, ""),
        FitPhaseBar("Digital /", "AI", 46, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 72, "Receipt & verification"),
        PhaseScoreCard("Phase 2", 60, "Request handling"),
        PhaseScoreCard("Phase 3", 80, "Closure & quality"),
        PhaseScoreCard("Digital", 46, "AI & self-service"),
    ],
    detail_slides=[
        ("Phase 1 — Contact receipt & verification", "Steps 1–4 vs Salesforce Service Cloud catalog", ["p1"]),
        ("Phase 2 — Request handling", "Steps 5–11 vs Salesforce Service Cloud catalog", ["p2"]),
        ("Phase 3 — Closure & quality", "Steps 12–13 vs Salesforce Service Cloud catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — CONTACT RECEIPT & VERIFICATION"),
            ("p2", "PHASE 2 — REQUEST HANDLING"),
            ("p3", "PHASE 3 — CLOSURE & QUALITY")],
    critical_missing=[
        CriticalGap("Step-up authentication",
            "Identity relies on 3-point knowledge-based verification, increasingly bypassable. The catalog adds "
            "step-up authentication (OTP/biometric) for sensitive changes to control account-takeover fraud."),
        CriticalGap("AI agent-assist & self-service deflection",
            "No agent-assist, knowledge or next-best-action, and limited self-service. The catalog deflects routine "
            "contacts via an AI assistant and surfaces knowledge in-flow, improving FCR and lowering AHT."),
        CriticalGap("Vulnerable-customer & consent handling",
            "No structured vulnerable-customer identification or consent capture for changes, a conduct and privacy gap."),
        CriticalGap("Interaction / speech analytics for QA",
            "Quality is scored on manual samples; the catalog QA's interactions at scale with speech/interaction "
            "analytics and automated coaching."),
    ],
    radar=[("Omni-channel", 80), ("Identity", 55), ("360 view", 52), ("Self-service / AI", 40),
           ("Escalation", 78), ("Vulnerability", 38), ("Quality / CSAT", 70)],
    control_bars=[
        ControlBar("Omni-channel intake", 80, "Phone, email, chat, portal logged in CRM"),
        ControlBar("Identity verification", 55, "3-point KBA; no step-up auth"),
        ControlBar("Unified 360 view", 52, "PAS + CRM not unified into one desktop"),
        ControlBar("Self-service / AI assist", 40, "Limited portal; no AI assist or chatbot"),
        ControlBar("Escalation", 78, "Logged escalation with 2-hour callback"),
        ControlBar("Vulnerable-customer handling", 38, "No vulnerability flags or consent logging"),
        ControlBar("Quality & CSAT", 70, "CSAT captured; manual QA sampling"),
    ],
    remediations=[
        Remediation(1, "Add step-up authentication for sensitive changes",
            "Require OTP or biometric step-up beyond 3-point KBA for payment, bank and contact changes to control "
            "account takeover. Effort: 4 weeks.", "High"),
        Remediation(2, "Deploy AI agent-assist & self-service deflection",
            "Add an AI assistant/chatbot for routine contacts and surface knowledge and next-best-action in the agent "
            "desktop to improve FCR and AHT. Effort: 7 weeks.", "High"),
        Remediation(3, "Add vulnerable-customer & consent handling",
            "Introduce vulnerability identification flags and consent capture/logging for account changes. "
            "Effort: 3 weeks.", "High"),
        Remediation(4, "Unify the agent desktop (360 view)",
            "Surface a single 360° customer view across PAS and CRM to cut context switching. Effort: 5 weeks.", "Medium"),
        Remediation(5, "Add interaction/speech analytics for QA",
            "QA interactions at scale with speech/interaction analytics and automated complaint/sentiment detection "
            "and coaching. Effort: 5 weeks.", "Medium"),
    ],
    risk_impact=[("Step-up authentication", 85), ("AI assist / deflection", 75), ("Vulnerable-customer", 72),
                 ("360 view", 58), ("Speech analytics", 55), ("Sentiment detection", 52)],
    projected_fit=91,
)

opt_phases = [
    Phase("1", "Receipt, verification & 360 view", "Intake, step-up ID, unified view", "blue",
          "Policyholder · CSR · PAS", "Steps 1–5", "5 steps + 1 decision"),
    Phase("2", "Request handling & assist", "Deflect, assist, resolve, escalate", "green",
          "CSR · Policy Service · Member Care · AI", "Steps 6–11", "6 steps + 1 decision"),
    Phase("3", "Closure & quality analytics", "Confirm, close, analytics", "amber",
          "CSR · CRM · Quality", "Steps 12–14", "3 steps"),
]

opt_steps = [
    Step("1", "1", "Inbound contact received (omni-channel)", "CSR / ACD System",
         "Logged in CRM with channel and timestamp", "Real time", "Standard", kind="trigger"),
    Step("2", "1", "Identity verification with step-up", "CSR / Auth Service",
         "3-point KBA plus OTP/biometric step-up for sensitive changes", "Real time",
         "ENHANCED (v3.1) — account-takeover control"),
    Step("3", "1", "Contact categorised with AI intent", "CSR / AI",
         "Intent classified automatically; type coded in CRM", "Real time", "ENHANCED (v3.1)"),
    Step("4", "1", "Unified 360 customer view retrieved", "CSR / PAS / CRM",
         "Single 360° view across PAS and CRM presented to the agent", "Real time",
         "NEW (v3.1) — agent desktop"),
    Step("5", "1", "Vulnerability check & consent capture", "CSR / Member Care",
         "Vulnerability flags applied; consent captured for any change", "Real time",
         "NEW (v3.1) — conduct & privacy"),
    Step("", "1", "", "", "", "", "Identity gate", kind="decision", decision="Identity verified?",
         branches=["Pass → handle request", "Fail → terminate + security flag (Sec 6.1)"]),
    Step("6", "2", "Self-service deflection (AI assistant)", "Policyholder / AI Assistant",
         "Routine requests deflected to chatbot/self-service before agent handling", "Real time",
         "NEW (v3.1) — volume reduction"),
    Step("7", "2", "Standard enquiry resolved with agent-assist", "CSR / AI",
         "Knowledge and next-best-action surfaced in-flow; resolved at first contact", "Real time",
         "ENHANCED (v3.1)"),
    Step("8", "2", "Account update processed", "CSR / Policy Service Rep",
         "Update in PAS with consent; confirmation emailed", "Real time", "Standard"),
    Step("9", "2", "Document request fulfilled", "CSR / PAS",
         "Certificate, schedule or receipt regenerated within 24 hours", "≤24 hours", "Standard"),
    Step("10", "2", "Payment received or arrangement set up", "CSR",
         "Payment via IVR/assisted; arrangement per SOP-INS-003", "Real time", "Standard"),
    Step("11", "2", "Complex / sensitive escalated to Member Care", "CSR / Member Care Rep",
         "Sentiment-flagged contacts escalated; 2-hour callback", "≤2 hours", "ENHANCED (v3.1)"),
    Step("12", "3", "Resolution confirmed with policyholder", "CSR",
         "Summary of actions communicated", "Real time", "Standard"),
    Step("13", "3", "Contact closed and coded in CRM", "CSR",
         "Resolution code, handle time and CSAT prompt", "Real time", "Standard"),
    Step("14", "3", "Quality via interaction analytics & CSAT", "CRM / Quality",
         "Interaction/speech analytics QA every contact; CSAT captured; coaching automated", "Post-contact",
         "NEW (v3.1) — QA at scale", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "Receipt, verification & 360 view", "Steps 1–5 · v3.1 adds step-up & 360 view",
        ["Policyholder", "CSR", "PAS / CRM"],
        [SwimNode("o1", "Policyholder", 0, "Inbound contact", "omni-channel"),
         SwimNode("o2", "CSR", 1, "Identity + step-up auth", "OTP / biometric", kind="enhanced"),
         SwimNode("o3", "CSR", 2, "AI intent categorisation", "auto-coded", kind="enhanced"),
         SwimNode("o4", "PAS / CRM", 3, "Unified 360 view", "single desktop", kind="new"),
         SwimNode("o5", "CSR", 3, "Vulnerability & consent", "flags + consent", kind="new")],
        [SwimEdge("o1", "o2", dashed=True), SwimEdge("o2", "o3"), SwimEdge("o3", "o4"),
         SwimEdge("o4", "o5", dashed=True, kind="new")],
        "v3.1 adds step-up authentication, an AI-classified intent, a unified 360 view, and vulnerability/consent capture."),
    SwimPhase("2", "Request handling & assist", "Steps 6–11 · deflection and agent-assist",
        ["Policyholder / AI", "CSR", "Policy Service / Member Care"],
        [SwimNode("p1", "Policyholder / AI", 0, "Self-service deflection", "chatbot", kind="new"),
         SwimNode("p2", "CSR", 1, "Resolve with agent-assist", "knowledge · NBA", kind="enhanced"),
         SwimNode("p3", "Policy Service / Member Care", 1, "Process account update", "PAS + consent"),
         SwimNode("p4", "Policy Service / Member Care", 2, "Fulfil document request", "≤24h"),
         SwimNode("p5", "CSR", 2, "Payment / arrangement", "IVR / assisted"),
         SwimNode("p6", "Policy Service / Member Care", 3, "Escalate (sentiment-flagged)", "≤2h", kind="exception")],
        [SwimEdge("p1", "p2", dashed=True, kind="new", label="deflect"), SwimEdge("p2", "p3"),
         SwimEdge("p3", "p4"), SwimEdge("p2", "p5"), SwimEdge("p2", "p6", dashed=True, kind="exception", label="esc")],
        "v3.1 deflects routine contacts to self-service and gives agents knowledge and next-best-action; sentiment flags drive escalation."),
    SwimPhase("3", "Closure & quality analytics", "Steps 12–14 · v3.1 adds interaction analytics",
        ["CSR", "Policyholder", "CRM / Quality"],
        [SwimNode("q1", "CSR", 0, "Confirm resolution", "summary"),
         SwimNode("q2", "CSR", 1, "Close & code contact", "resolution code"),
         SwimNode("q3", "CRM / Quality", 2, "Interaction analytics & CSAT", "QA every contact", kind="new")],
        [SwimEdge("q1", "q2"), SwimEdge("q2", "q3", dashed=True, kind="new")],
        "v3.1 QA's every interaction with speech/interaction analytics and captures CSAT for automated coaching."),
]

optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Salesforce Service Cloud Insurance Servicing Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-009"),
                ("Version", "3.1 (Optimised)"),
                ("Effective Date", "01 October 2026"),
                ("Supersedes", "v3.0 dated 01 January 2025"),
                ("Owner", "Customer Service — Policy Servicing"),
                ("Approved By", "Chief Customer Officer"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-009 dated 18 June 2026"),
                ("Catalog Alignment Score", "91% (up from 69% in v3.0)"),
                ("Classification", "Internal Use Only"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v3.1",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-009. Alignment to the "
              "Salesforce Service Cloud servicing catalog increased from 69% to 91%. Critical additions: step-up "
              "authentication, AI agent-assist with self-service deflection, vulnerable-customer and consent "
              "handling, a unified 360 view, and interaction/speech analytics for quality."],
             ["NEW STEP (green) — step added to close a gap vs the Service Cloud catalog",
              "ENHANCED (amber) — existing step updated with additional automation or controls"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines how inbound requests from current policyholders are "
             "received and resolved across all channels. Version 3.1 incorporates optimisations from fit-gap analysis "
             "against the Salesforce Service Cloud Insurance Servicing Best-Practice Catalog, achieving 91% alignment "
             "(up from 69% in v3.0)."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to inbound policyholder contacts for general enquiries, policy "
             "information, billing queries, payment processing, account updates and document requests."),
            ("banner", "new", "Scope extended: step-up authentication and vulnerable-customer/consent handling now "
             "apply to every sensitive request."),
            ("para", "This procedure does NOT cover claims notifications (SOP-INS-007/011/012), formal complaints "
             "(SOP-COMP-001), or policy cancellation (SOP-INS-011)."),
        ]),
        DocSection("3. Authority Matrix", [
            ("table", ["Item", "First Authority", "Second Authority"],
             [["Standard enquiry / document", "CSR", "—"],
              ["Account update (non-financial)", "CSR", "Policy Service Rep"],
              ["Payment arrangement", "CSR", "per SOP-INS-003 matrix"],
              ["Complex / VIP / sensitive", "Member Care Rep", "Team Leader"],
              ["Exception outside CSR authority", "Team Leader", "—"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Customer Service Representative", "Logs contacts; verifies identity; resolves standard requests with agent-assist; escalates."],
              ["Member Care Representative", "Handles complex/sensitive and VIP cases; owns vulnerable-customer handling."],
              ["Policy Service Representative", "Processes formal account changes in PAS; back-office support."],
              ["Team Leader / Supervisor", "Monitors queues; handles escalations; reviews analytics-driven quality."]], {}),
        ]),
        DocSection("5. Identity & Conduct Controls (New Section — v3.1)", [
            ("banner", "crit", "New section. Required by the Service Cloud catalog. Step-up authentication and "
             "vulnerable-customer/consent handling now gate sensitive requests."),
            ("table", ["#", "Control", "Responsible", "Output / System", "Timeline"],
             [["C1", "Step-up authentication", "CSR / Auth Service", "OTP/biometric for sensitive changes", "Real time"],
              ["C2", "Vulnerability identification", "Member Care / CSR", "Vulnerability flags applied", "Real time"],
              ["C3", "Consent capture & logging", "CSR", "Consent recorded for account changes", "Real time"]],
             {0: "new", 1: "new", 2: "new"}),
        ]),
        DocSection("6. Process Steps", [
            ("h3", "6.1 Receipt, Verification & 360 View"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "Inbound contact received (omni-channel)", "CSR / ACD", "Logged in CRM", "Real time"],
              ["2", "Identity verification with step-up", "CSR / Auth Service", "3-point + OTP/biometric", "Real time"],
              ["3", "Contact categorised with AI intent", "CSR / AI", "Intent classified; coded", "Real time"],
              ["4", "Unified 360 customer view retrieved", "CSR / PAS / CRM", "Single agent desktop", "Real time"],
              ["5", "Vulnerability check & consent capture", "CSR / Member Care", "Flags + consent", "Real time"]],
             {1: "enh", 2: "enh", 3: "new", 4: "new"}),
            ("h3", "6.2 Request Handling & Assist"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["6", "Self-service deflection (AI assistant)", "Policyholder / AI", "Routine requests deflected", "Real time"],
              ["7", "Standard enquiry resolved with agent-assist", "CSR / AI", "Knowledge + next-best-action", "Real time"],
              ["8", "Account update processed", "CSR / Policy Service Rep", "PAS update with consent", "Real time"],
              ["9", "Document request fulfilled", "CSR / PAS", "Regenerated within 24 hours", "≤24 hours"],
              ["10", "Payment received or arrangement set up", "CSR", "IVR/assisted; per SOP-INS-003", "Real time"],
              ["11", "Complex / sensitive escalated", "CSR / Member Care", "Sentiment-flagged; 2-hour callback", "≤2 hours"]],
             {0: "new", 1: "enh", 5: "enh"}),
            ("h3", "6.3 Closure & Quality Analytics"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["12", "Resolution confirmed with policyholder", "CSR", "Summary of actions", "Real time"],
              ["13", "Contact closed and coded in CRM", "CSR", "Resolution code; AHT; CSAT prompt", "Real time"],
              ["14", "Quality via interaction analytics & CSAT", "CRM / Quality", "QA every contact; coaching", "Post-contact"]],
             {2: "new"}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Failed Identity Verification (Enhanced — v3.1)"),
            ("banner", "enh", "Step-up authentication strengthens identity assurance; repeated failures still trigger a security flag."),
            ("numbered", [
                "After 2 failed attempts, the CSR terminates the contact and advises a call-back with correct information.",
                "A third failure within 24 hours triggers a security flag and Team Leader notification.",
                "No account information is provided to an unverified caller under any circumstances."]),
            ("h3", "7.2 Formal Complaint Identified"),
            ("numbered_from", 4, [
                "Automated sentiment/complaint detection or agent recognition routes the contact to Member Care immediately.",
                "Formal complaint logged in the Complaints Register within 30 minutes per SOP-COMP-001.",
                "CSR must not attempt to resolve a formal complaint without Member Care or Supervisor involvement."]),
            ("h3", "7.3 Suspected Fraud or Identity Theft"),
            ("numbered_from", 7, [
                "CSR transfers to Member Care and flags the policy as 'Security Hold' in PAS.",
                "Fraud team notified within 1 hour; no account changes processed until fraud review is complete."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["CRM (Salesforce Service Cloud)", "Contact logging, case management, 360 view, analytics", "All CSR roles"],
              ["Policy Administration System (PAS)", "Policy record, account updates, documents", "CSR, Policy Service Rep"],
              ["ACD / IVR (NICE CXone)", "Routing, IVR payment, recording", "CSR, Team Leader"],
              ["Authentication Service", "OTP/biometric step-up authentication", "CSR"],
              ["AI Assistant / Knowledge", "Self-service deflection, agent-assist, next-best-action", "Policyholders, CSR"],
              ["Interaction Analytics", "Speech/interaction QA, sentiment detection", "Team Leader, Quality"],
              ["Self-Service Portal", "Policyholder self-service and document downloads", "Policyholders"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v3.1: step-up authentication, consent logging, AI assist, and "
             "interaction analytics."),
            ("bullets", [
                "Identity assurance: 3-point verification plus step-up for sensitive changes; no service without verification.",
                "Consent: account changes captured against logged policyholder consent.",
                "Vulnerability: vulnerable customers identified and handled with appropriate care.",
                "AI assist: knowledge and next-best-action surfaced in-flow for consistency.",
                "Deflection: routine contacts handled via self-service to reduce volume.",
                "Quality: every interaction QA'd via analytics with automated coaching.",
                "Immutable audit trail: identity, consent, change and escalation events logged."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v3.0 Target", "v3.1 Target", "Measurement"],
             [["First Contact Resolution", "≥78%", "≥84%", "Resolved on first interaction"],
              ["Average Handle Time", "<5 min", "<4 min", "Standard enquiries"],
              ["Self-service deflection", "N/A (new)", "≥25% of routine", "Deflected vs total"],
              ["Step-up auth on sensitive changes", "N/A (new)", "100%", "Step-up enforcement"],
              ["CSAT", "≥4.2/5.0", "≥4.4/5.0", "Post-contact survey"],
              ["Quality coverage", "Sample-based", "100% via analytics", "Interaction analytics QA"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["3.0", "01 Jan 2025", "L. Adebayo, CS Ops", "Full rewrite aligned to Salesforce CRM migration; new FCR and AHT KPI baselines"],
              ["3.1", "01 Oct 2026", "L. Adebayo, CS Ops",
               "OPTIMISED: step-up authentication; AI agent-assist & self-service deflection; vulnerable-customer & "
               "consent handling; unified 360 view; interaction analytics; catalog alignment 69% → 91%"]], {}),
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
    swim_cover_tags="Receipt · Verification · Handling · Closure · Exception handling",
    hierarchy_cover_sub="Phase breakdown with service tracks, identity controls, and exception paths",
)
