"""SOP-INS-011 — Medical Claims Processing (Meridian Insurance Group).

FlowAgent analysis: process model, fit-gap vs the Guidewire ClaimCenter
health-claims best-practice catalog, and the optimised v3.0 SOP.
"""
from __future__ import annotations

from generator.model import (
    Meta, Phase, Step, AuthorityRow, SwimNode, SwimEdge, SwimPhase,
    FitItem, FitPhaseBar, PhaseScoreCard, CriticalGap, ControlBar,
    Remediation, FitGap, DocSection, OptimisedDoc, SopPackage,
)

CATALOG = "Guidewire ClaimCenter — Health Claims Best-Practice Catalog"
CATALOG_SHORT = "Guidewire ClaimCenter"

meta = Meta(
    sop_id="SOP-INS-011", slug="Medical_Claims",
    title="Medical Claims Processing", short_title="Medical claims processing",
    version="2.3", owner="Medical Claims — Claims Operations",
    org="Meridian Insurance Group", catalog=CATALOG, catalog_short=CATALOG_SHORT,
    new_version="3.0", effective_date="01 September 2026",
    supersedes="v2.3 dated 01 March 2025", approved_by="Chief Claims Officer",
    classification="Internal Use Only — Claims Restricted",
)

# ---- Baseline phases & steps --------------------------------------------
phases = [
    Phase("1", "Receipt & registration", "All claims entering Claims Operations",
          "blue", "Claimant · Claims Processor · PAS", "Steps 1–4", "4 steps + 1 decision"),
    Phase("2", "Assessment", "Eligibility, clinical review, fraud screening",
          "green", "Processor · Adjuster · Medical Advisor · SIU", "Steps 5–8", "4 steps"),
    Phase("3", "Decision & settlement", "Decision, payment and closure",
          "amber", "Adjuster · Manager · Finance", "Steps 9–12", "4 steps + 1 decision"),
]

steps = [
    Step("1", "1", "Claim received via portal, app, email, or post",
         "Claims Processor / System",
         "Claim ID assigned; date of receipt recorded; acknowledgement sent to claimant",
         "T+1 day", "Acknowledgement SLA: 1 business day", kind="trigger"),
    Step("2", "1", "Eligibility verification", "Claims Processor / PAS",
         "Policy active at date of loss/treatment; claimant a covered member; waiting periods checked",
         "T+1 day", "Coverage confirmed before assessment"),
    Step("3", "1", "Document completeness check", "Claims Processor",
         "Claim form, medical reports, itemised bills, referral letters and receipts reviewed",
         "T+2 days", "Missing items: 7-day request deadline"),
    Step("4", "1", "Claim type determination and routing", "Claims Processor",
         "Categorised: routine (auto-assess), complex (adjuster), high-value (manager), suspicious (SIU)",
         "T+2 days", "Determines assessment track"),
    Step("", "1", "", "", "", "", "Routing rules per claim category", kind="decision",
         decision="Claim category?",
         branches=["Routine → auto-assessment", "Complex / high-value → adjuster review",
                   "Suspicious → SIU flag (Sec 6.2)"]),
    Step("5", "2", "Policy coverage and benefit limit verification",
         "Claims Processor / Adjuster",
         "Applicable benefit, sub-limit, excess and co-payment calculated; exclusions checked",
         "T+3 days", "PAS benefit configuration applied"),
    Step("6", "2", "Clinical review (complex claims)", "Adjuster / Medical Advisor",
         "Medical necessity, standard of care and reasonableness of charges assessed",
         "T+5 days", "Medical Advisor opinion for high-value/contested"),
    Step("7", "2", "Fraud screening", "Claims System / SIU",
         "Automated scoring; flagged claims reviewed by SIU within 3 business days",
         "Parallel", "Key control: SIU review ≥2% of submissions", kind="control"),
    Step("8", "2", "Settlement amount calculated", "Claims Adjuster / System",
         "Approved amount: covered charges less excess and co-payment; itemised breakdown",
         "T+5 days", "Benefit accumulators updated"),
    Step("9", "3", "Claims decision made and documented", "Adjuster / Claims Manager",
         "Approve, partial approve, or reject; rationale documented in Claims System",
         "T+6 days", "Manager approval above adjuster authority"),
    Step("", "3", "", "", "", "", "Per authority matrix", kind="decision",
         decision="Decision outcome?",
         branches=["Approve / partial → settlement",
                   "Reject → rejection notice + 30-day appeal (Sec 6.1)"]),
    Step("10", "3", "Claimant notified of decision", "Claims Processor",
         "Settlement letter or rejection notice within 1 business day; amount and timeline stated",
         "T+7 days", "Notification SLA: 1 business day"),
    Step("11", "3", "Payment processed", "Finance / Claims System",
         "Direct bank transfer or cheque within 5 business days of approval; remittance advice sent",
         "T+10 days", "SAP payment run"),
    Step("12", "3", "Claim closed and GL updated", "Claims Processor / Finance",
         "Status set to Settled or Rejected; loss reserve released or adjusted; GL journal posted",
         "T+10 days", "Reserve adjustment; immutable audit trail", kind="complete"),
]

authority = [
    AuthorityRow("Up to SGD 5,000", "Claims Processor", "—"),
    AuthorityRow("SGD 5,001–25,000", "Claims Adjuster", "—"),
    AuthorityRow("SGD 25,001–100,000", "Claims Manager", "Adjuster recommendation"),
    AuthorityRow("SGD 100,001–250,000", "Claims Manager", "Medical Advisor sign-off"),
    AuthorityRow("Above SGD 250,000", "Chief Claims Officer", "Claims Manager"),
]

# ---- Baseline swimlanes --------------------------------------------------
swim_phases = [
    SwimPhase("1", "Claim receipt & registration", "Steps 1–4 · all claim types",
        ["Claimant", "Claims Processor", "Claims System / PAS"],
        [SwimNode("s1", "Claimant", 0, "Submit claim", "Portal · app · hotline"),
         SwimNode("s2", "Claims Processor", 1, "Register & assign Claim ID", "Claims Processor"),
         SwimNode("s3", "Claims Processor", 2, "Eligibility verification", "via PAS"),
         SwimNode("s4", "Claims Processor", 3, "Document completeness", "Claims Processor"),
         SwimNode("s5", "Claims Processor", 4, "Determine type & route", "routine / complex / SIU", kind="decision"),
         SwimNode("s6", "Claims System / PAS", 1, "Auto-acknowledge claimant", "Majesco"),
         SwimNode("s7", "Claims System / PAS", 3, "Request missing docs", "7-day deadline", kind="exception")],
        [SwimEdge("s1", "s2", dashed=True),
         SwimEdge("s2", "s6", dashed=True),
         SwimEdge("s2", "s3"), SwimEdge("s3", "s4"), SwimEdge("s4", "s5"),
         SwimEdge("s4", "s7", dashed=True, kind="exception", label="gap")],
        "Claims arrive via portal, app, hotline or post. Incomplete claims trigger a 7-day document request."),
    SwimPhase("2", "Assessment", "Steps 5–8 · eligibility, clinical, fraud",
        ["Claims Processor", "Claims Adjuster", "Medical Advisor / SIU"],
        [SwimNode("a1", "Claims Processor", 0, "Coverage & benefit check", "via PAS"),
         SwimNode("a2", "Claims Adjuster", 1, "Clinical review", "complex claims"),
         SwimNode("a3", "Medical Advisor / SIU", 2, "Medical Advisor opinion", "high-value / contested"),
         SwimNode("a4", "Medical Advisor / SIU", 1, "Fraud screening", "auto-score · SIU"),
         SwimNode("a5", "Claims Adjuster", 3, "Calculate settlement", "less excess & co-pay")],
        [SwimEdge("a1", "a2"), SwimEdge("a2", "a3", label="cx"), SwimEdge("a3", "a5"),
         SwimEdge("a2", "a5"), SwimEdge("a1", "a4", dashed=True), SwimEdge("a4", "a5", dashed=True)],
        "Routine claims auto-assess against PAS benefit configuration; complex claims get Medical Advisor review. All claims are fraud-screened in parallel."),
    SwimPhase("3", "Decision & settlement", "Steps 9–12 · decision, payment, close",
        ["Manager / Adjuster", "Claims Processor", "Finance / System"],
        [SwimNode("d1", "Manager / Adjuster", 0, "Claims decision", "approve / partial / reject", kind="decision"),
         SwimNode("d2", "Claims Processor", 1, "Notify claimant", "letter / notice"),
         SwimNode("d3", "Manager / Adjuster", 1, "Reject → 30-day appeal", "Claims Manager", kind="exception"),
         SwimNode("d4", "Finance / System", 2, "Payment processed", "SAP · ≤5 days"),
         SwimNode("d5", "Claims Processor", 3, "Close & GL update", "reserve adjusted")],
        [SwimEdge("d1", "d2", label="ok"), SwimEdge("d1", "d3", dashed=True, kind="exception", label="rej"),
         SwimEdge("d2", "d4"), SwimEdge("d4", "d5")],
        "Approved claims are paid within 5 business days. Rejections cite the specific policy clause and open a 30-day appeal to the Claims Manager."),
]

# ---- Fit-gap -------------------------------------------------------------
fg_items = [
    FitItem("1", "Multi-channel claim intake", "FIT",
        "Portal, app, hotline and post intake aligns with ClaimCenter FNOL multi-channel capture.",
        "Claims Processor", "GW-CC-FNOL-01", "p1"),
    FitItem("2", "Claim registration & ID", "FIT",
        "Same-day registration with a unique Claim ID and dated audit aligns with ClaimCenter claim setup.",
        "Claims Processor", "GW-CC-FNOL-02", "p1"),
    FitItem("3", "Eligibility verification", "FIT",
        "Policy-active and covered-member checks via PAS align with ClaimCenter policy verification.",
        "Claims Processor / PAS", "GW-CC-FNOL-03", "p1"),
    FitItem("4", "Duplicate & coordination-of-benefits check", "GAP",
        "ClaimCenter requires duplicate-claim detection and a coordination-of-benefits (other-insurer) "
        "check at FNOL. SOP performs neither — risk of double payment.",
        "Claims Processor", "GW-CC-FNOL-05", "p1"),
    FitItem("5", "Case reserve at registration", "GAP",
        "ClaimCenter sets an initial case reserve when a claim is created. SOP only adjusts reserves at "
        "closure (step 12), understating outstanding-liability reporting.",
        "Claims Processor / Finance", "GW-CC-FIN-01", "p1"),
    FitItem("6", "Document completeness & follow-up", "PARTIAL",
        "Completeness check and 7-day request present, but no automated diary/escalation when documents "
        "arrive late — relies on manual follow-up.",
        "Claims Processor", "GW-CC-FNOL-04", "p1"),
    FitItem("7", "Benefit & sub-limit calculation", "FIT",
        "Benefit, sub-limit, excess, co-payment and exclusion checks via PAS align with ClaimCenter coverage evaluation.",
        "Claims Adjuster / PAS", "GW-CC-COV-01", "p2"),
    FitItem("8", "Auto-adjudication of routine claims", "PARTIAL",
        "Routine claims are routed to manual assessment. ClaimCenter recommends a straight-through "
        "auto-adjudication rules engine for low-value, in-network, rules-clear claims.",
        "Claims System", "GW-CC-ADJ-02", "p2"),
    FitItem("9", "Clinical / medical necessity review", "FIT",
        "Adjuster and Medical Advisor review of necessity, standard of care and reasonableness aligns with "
        "ClaimCenter clinical review.",
        "Adjuster / Medical Advisor", "GW-CC-ADJ-03", "p2"),
    FitItem("10", "Provider network & tariff validation", "GAP",
        "ClaimCenter validates billed charges against contracted provider tariffs/network agreements. SOP "
        "assesses 'reasonableness' subjectively with no tariff table — a key leakage driver.",
        "Claims Adjuster", "GW-CC-ADJ-05", "p2"),
    FitItem("11", "Fraud screening depth", "PARTIAL",
        "Automated scoring and SIU review present, but no provider-level fraud profiling or network/link "
        "analytics recommended by the catalog.",
        "Claims System / SIU", "GW-CC-SIU-01", "p2"),
    FitItem("12", "Concurrent / utilisation review", "GAP",
        "Pre-authorisation is point-in-time only. ClaimCenter recommends concurrent (utilisation) review "
        "for ongoing inpatient stays to control length-of-stay and cost.",
        "Claims Adjuster", "GW-CC-ADJ-06", "p2"),
    FitItem("13", "Settlement calculation & accumulators", "FIT",
        "Settlement net of excess/co-pay with itemised breakdown aligns; benefit accumulators tracked in PAS.",
        "Claims Adjuster / System", "GW-CC-COV-03", "p3"),
    FitItem("14", "Decision & authority matrix", "FIT",
        "Tiered approve/partial/reject decisioning with documented rationale and authority thresholds aligns "
        "with ClaimCenter decisioning.",
        "Adjuster / Claims Manager", "GW-CC-DEC-01", "p3"),
    FitItem("15", "Claimant notification & appeals", "FIT",
        "1-day notification, policy-clause rejection reasons and a 30-day appeal window align with the "
        "catalog communications & appeals standard.",
        "Claims Processor", "GW-CC-DEC-03", "p3"),
    FitItem("16", "Overpayment & COB recovery", "GAP",
        "No recovery process for overpayments or amounts recoverable from other insurers/third parties. "
        "ClaimCenter includes a recovery/subrogation step after settlement.",
        "Finance / Claims Manager", "GW-CC-REC-01", "p3"),
]

fitgap = FitGap(
    overall_fit=71, partial_pct=13, fits=8, gaps=5, partials=3,
    steps_analysed=16, phases_count=3,
    summary_line="Overall alignment of SOP-INS-011 against the Guidewire ClaimCenter health-claims catalog",
    metrics=[
        ("Steps analysed", "16 steps across 3 phases"),
        ("Fits confirmed", "8 steps aligned to catalog"),
        ("Gaps identified", "5 steps — remediation required"),
        ("Partial fits", "3 steps — enhancement recommended"),
        ("Highest risk area", "Coordination of benefits (missing)"),
        ("Reserving", "No case reserve set at FNOL"),
        ("Ref standard", "Guidewire ClaimCenter Health Catalog"),
    ],
    phase_bars=[
        FitPhaseBar("Phase 1", "Receipt", 80, ""),
        FitPhaseBar("Phase 2", "Assessment", 66, ""),
        FitPhaseBar("Fraud /", "SIU", 64, ""),
        FitPhaseBar("Phase 3", "Settlement", 72, ""),
    ],
    phase_cards=[
        PhaseScoreCard("Phase 1", 80, "Receipt & registration"),
        PhaseScoreCard("Phase 2", 66, "Assessment"),
        PhaseScoreCard("Fraud", 64, "Screening & SIU"),
        PhaseScoreCard("Phase 3", 72, "Decision & settlement"),
    ],
    detail_slides=[
        ("Phase 1 — Receipt & registration",
         "Steps 1–6 vs Guidewire ClaimCenter health-claims catalog", ["p1"]),
        ("Phase 2 — Assessment & adjudication",
         "Steps 7–12 vs Guidewire ClaimCenter health-claims catalog", ["p2"]),
        ("Phase 3 — Decision, settlement & recovery",
         "Steps 13–16 vs Guidewire ClaimCenter health-claims catalog", ["p3"]),
    ],
    items=fg_items,
    groups=[("p1", "PHASE 1 — RECEIPT & REGISTRATION"),
            ("p2", "PHASE 2 — ASSESSMENT & ADJUDICATION"),
            ("p3", "PHASE 3 — DECISION, SETTLEMENT & RECOVERY")],
    critical_missing=[
        CriticalGap("Coordination of benefits (COB)",
            "ClaimCenter requires an other-insurance / COB check at FNOL and recovery of amounts payable by "
            "other insurers. SOP-INS-011 has neither, creating double-payment and leakage exposure."),
        CriticalGap("Case reserving at FNOL",
            "No initial case reserve is set when a claim is registered; reserves are only touched at closure. "
            "Outstanding-claim liability and IBNR inputs are understated between registration and settlement."),
        CriticalGap("Provider tariff / network pricing",
            "Billed charges are assessed for 'reasonableness' with no contracted-tariff reference table — a "
            "primary source of claims leakage versus the catalog's network-pricing control."),
        CriticalGap("Recovery & subrogation",
            "No post-settlement recovery process for overpayments, third-party liability or COB amounts."),
    ],
    radar=[("Intake / FNOL", 85), ("Coverage eval", 80), ("Adjudication", 60),
           ("Clinical review", 78), ("Fraud / SIU", 64), ("Reserving", 30), ("Recovery / COB", 25)],
    control_bars=[
        ControlBar("Intake controls", 85, "Strong multi-channel FNOL with dated audit"),
        ControlBar("Coverage evaluation", 80, "Benefit/sub-limit checks solid; accumulators tracked"),
        ControlBar("Auto-adjudication", 55, "Routine claims manually assessed; no STP engine"),
        ControlBar("Clinical review", 78, "Adjuster + Medical Advisor for complex claims"),
        ControlBar("Fraud & SIU", 64, "Scoring present; no provider/network analytics"),
        ControlBar("Reserving", 30, "No FNOL reserve; closure-only adjustment"),
        ControlBar("Recovery / COB", 25, "No COB or subrogation recovery process"),
    ],
    remediations=[
        Remediation(1, "Add duplicate & coordination-of-benefits check at FNOL",
            "Insert a duplicate-claim and other-insurer (COB) check at registration; query prior claims and "
            "declared other cover before assessment and route COB-eligible claims for apportionment. "
            "Effort: 3 weeks (Majesco config + PAS link).", "High"),
        Remediation(2, "Introduce case reserving at registration",
            "Set an initial case reserve when each claim is created, derived from benefit type and claimed "
            "amount; adjust through the lifecycle. Aligns outstanding-liability and IBNR reporting. "
            "Effort: 4 weeks (Majesco + SAP).", "High"),
        Remediation(3, "Validate charges against provider tariffs / network",
            "Add a contracted-tariff / network-pricing reference table; flag charges above tariff for adjuster "
            "review. Primary leakage control. Effort: 5 weeks (tariff data + rules).", "High"),
        Remediation(4, "Add concurrent / utilisation review for inpatient stays",
            "Extend pre-authorisation into concurrent review for stays beyond a threshold length, with periodic "
            "clinical updates. Effort: 3 weeks.", "Medium"),
        Remediation(5, "Stand up auto-adjudication for routine claims",
            "Configure a straight-through rules engine to auto-settle low-value, in-network, rules-clear claims, "
            "routing only exceptions to adjusters. Effort: 6 weeks.", "Medium"),
    ],
    risk_impact=[("Coordination of benefits", 95), ("Reserving accuracy", 80),
                 ("Provider tariff leakage", 78), ("Auto-adjudication", 60),
                 ("Utilisation review", 58), ("Fraud analytics", 55)],
    projected_fit=92,
)

# ---- Optimised process ---------------------------------------------------
opt_phases = [
    Phase("1", "Receipt, registration & reserving", "Duplicate/COB check; case reserve set",
          "blue", "Claimant · Processor · PAS", "Steps 1–6", "6 steps + 1 decision"),
    Phase("2", "Assessment & adjudication", "Auto-adjudication; tariff; concurrent; fraud",
          "green", "Processor · Adjuster · Advisor · SIU", "Steps 7–13", "7 steps"),
    Phase("3", "Decision, settlement & recovery", "Decision, payment, recovery, close",
          "amber", "Adjuster · Manager · Finance", "Steps 14–18", "5 steps + 1 decision"),
]

opt_steps = [
    Step("1", "1", "Claim received via portal, app, email, or post", "Claims Processor / System",
         "Claim ID assigned; acknowledgement sent within 1 business day", "T+1 day", "Standard", kind="trigger"),
    Step("2", "1", "Eligibility verification", "Claims Processor / PAS",
         "Policy active; covered member; waiting periods checked", "T+1 day", "Standard"),
    Step("3", "1", "Duplicate & coordination-of-benefits (COB) check", "Claims Processor / System",
         "Prior-claim and other-insurer check; COB-eligible claims routed for apportionment", "T+1 day",
         "NEW (v3.0) — prevents double payment"),
    Step("4", "1", "Set initial case reserve", "Claims Processor / Finance",
         "Case reserve raised in Majesco/SAP from benefit type and claimed amount", "T+1 day",
         "NEW (v3.0) — aligns outstanding liability"),
    Step("5", "1", "Document completeness check with automated diary", "Claims Processor",
         "Completeness check; missing-item request with automated 7/14/28-day diary and escalation", "T+2 days",
         "ENHANCED (v3.0)"),
    Step("6", "1", "Claim type determination and routing", "Claims Processor",
         "Categorised: routine (auto-adjudicate), complex, high-value, suspicious (SIU)", "T+2 days", "Standard"),
    Step("", "1", "", "", "", "", "Routing rules", kind="decision", decision="Claim category?",
         branches=["Routine → auto-adjudication", "Complex / high-value → adjuster", "Suspicious → SIU"]),
    Step("7", "2", "Policy coverage and benefit limit verification", "Adjuster / PAS",
         "Benefit, sub-limit, excess, co-payment and exclusions calculated", "T+3 days", "Standard"),
    Step("8", "2", "Auto-adjudication of routine claims", "Claims System",
         "Straight-through rules engine settles low-value, in-network, rules-clear claims", "Same day",
         "ENHANCED (v3.0) — STP engine"),
    Step("9", "2", "Clinical / medical necessity review (complex)", "Adjuster / Medical Advisor",
         "Necessity, standard of care and reasonableness assessed", "T+5 days", "Standard"),
    Step("10", "2", "Provider network & tariff validation", "Claims Adjuster",
         "Billed charges validated against contracted tariffs; above-tariff items flagged", "T+5 days",
         "NEW (v3.0) — leakage control"),
    Step("11", "2", "Fraud screening with provider & network analytics", "Claims System / SIU",
         "Claim scoring plus provider-profiling and link analytics; SIU review within 3 days", "Parallel",
         "ENHANCED (v3.0)"),
    Step("12", "2", "Concurrent / utilisation review (inpatient)", "Claims Adjuster",
         "Ongoing inpatient stays reviewed periodically against length-of-stay norms", "Ongoing",
         "NEW (v3.0)"),
    Step("13", "2", "Settlement amount calculated", "Claims Adjuster / System",
         "Covered charges less excess and co-payment; itemised breakdown; accumulators updated", "T+5 days", "Standard"),
    Step("14", "3", "Claims decision made and documented", "Adjuster / Claims Manager",
         "Approve, partial or reject; rationale documented; per authority matrix", "T+6 days", "Standard"),
    Step("", "3", "", "", "", "", "Authority matrix", kind="decision", decision="Decision outcome?",
         branches=["Approve / partial → settlement", "Reject → notice + 30-day appeal"]),
    Step("15", "3", "Claimant notified of decision", "Claims Processor",
         "Settlement letter or rejection notice within 1 business day", "T+7 days", "Standard"),
    Step("16", "3", "Payment processed", "Finance / Claims System",
         "Bank transfer or cheque within 5 business days; remittance advice sent", "T+10 days", "Standard"),
    Step("17", "3", "Recovery — overpayment, COB & subrogation", "Finance / Claims Manager",
         "Recoverable amounts (overpayment, other-insurer, third-party) identified and pursued", "Post-settlement",
         "NEW (v3.0) — recovers leakage", kind="control"),
    Step("18", "3", "Claim closed and GL updated", "Claims Processor / Finance",
         "Status set; case reserve released or adjusted; GL journal posted", "T+10 days",
         "Reserve true-up; immutable audit trail", kind="complete"),
]

opt_swim_phases = [
    SwimPhase("1", "Receipt, registration & reserving", "Steps 1–6 · v3.0 adds COB check & reserving",
        ["Claimant", "Claims Processor", "Claims System / PAS"],
        [SwimNode("o1", "Claimant", 0, "Submit claim", "Portal · app · hotline"),
         SwimNode("o2", "Claims Processor", 1, "Register & assign ID", "auto-acknowledge"),
         SwimNode("o3", "Claims Processor", 2, "Eligibility verification", "via PAS"),
         SwimNode("o4", "Claims Processor", 3, "Document completeness", "auto diary 7/14/28d", kind="enhanced"),
         SwimNode("o7", "Claims Processor", 4, "Determine type & route", "routine / complex / SIU", kind="decision"),
         SwimNode("o5", "Claims System / PAS", 2, "Duplicate & COB check", "Majesco · PAS", kind="new"),
         SwimNode("o6", "Claims System / PAS", 3, "Set case reserve", "Majesco · SAP", kind="new")],
        [SwimEdge("o1", "o2", dashed=True), SwimEdge("o2", "o3"), SwimEdge("o3", "o4"),
         SwimEdge("o4", "o7"), SwimEdge("o3", "o5", dashed=True, kind="new", label="COB"),
         SwimEdge("o4", "o6", dashed=True, kind="new", label="rsv")],
        "v3.0 adds duplicate/COB detection and case reserving at registration, with an automated missing-document diary."),
    SwimPhase("2", "Assessment & adjudication", "Steps 7–13 · auto-adjudication, tariff & concurrent review",
        ["Processor / System", "Claims Adjuster", "Medical Advisor / SIU"],
        [SwimNode("p1", "Processor / System", 0, "Coverage & benefit check", "via PAS"),
         SwimNode("p2", "Processor / System", 1, "Auto-adjudication", "STP rules engine", kind="enhanced"),
         SwimNode("p3", "Claims Adjuster", 1, "Clinical review", "complex claims"),
         SwimNode("p4", "Claims Adjuster", 2, "Provider tariff validation", "contracted tariffs", kind="new"),
         SwimNode("p5", "Claims Adjuster", 3, "Concurrent / utilisation review", "inpatient", kind="new"),
         SwimNode("p7", "Medical Advisor / SIU", 1, "Fraud screening + analytics", "provider profiling", kind="enhanced"),
         SwimNode("p8", "Claims Adjuster", 4, "Calculate settlement", "less excess & co-pay")],
        [SwimEdge("p1", "p2", label="rtn"), SwimEdge("p1", "p3", label="cx"), SwimEdge("p3", "p4"),
         SwimEdge("p4", "p5"), SwimEdge("p5", "p8"), SwimEdge("p2", "p8", dashed=True),
         SwimEdge("p1", "p7", dashed=True), SwimEdge("p7", "p8", dashed=True)],
        "Routine claims auto-adjudicate (STP). Complex claims add provider-tariff validation and concurrent review; enhanced fraud analytics run in parallel."),
    SwimPhase("3", "Decision, settlement & recovery", "Steps 14–18 · v3.0 adds recovery step",
        ["Manager / Adjuster", "Claims Processor", "Finance / System"],
        [SwimNode("q1", "Manager / Adjuster", 0, "Claims decision", "approve / partial / reject", kind="decision"),
         SwimNode("q2", "Claims Processor", 1, "Notify claimant", "letter / notice"),
         SwimNode("q3", "Manager / Adjuster", 1, "Reject → 30-day appeal", "Claims Manager", kind="exception"),
         SwimNode("q4", "Finance / System", 2, "Payment processed", "SAP · ≤5 days"),
         SwimNode("q5", "Finance / System", 3, "Recovery: overpayment / COB", "subrogation", kind="new"),
         SwimNode("q6", "Claims Processor", 4, "Close & GL update", "reserve true-up", kind="terminal")],
        [SwimEdge("q1", "q2", label="ok"), SwimEdge("q1", "q3", dashed=True, kind="exception", label="rej"),
         SwimEdge("q2", "q4"), SwimEdge("q4", "q5", dashed=True, kind="new", label="rec"),
         SwimEdge("q4", "q6"), SwimEdge("q5", "q6", dashed=True, kind="new")],
        "v3.0 adds a post-settlement recovery step for overpayments, coordination-of-benefits and subrogation before closure."),
]

# ---- Optimised SOP document ---------------------------------------------
optimised_doc = OptimisedDoc(
    subtitle="Optimised per Fit-Gap Analysis against the Guidewire ClaimCenter Health Claims Catalog",
    sections=[
        DocSection("", [
            ("meta", [
                ("Document Reference", "SOP-INS-011"),
                ("Version", "3.0 (Optimised)"),
                ("Effective Date", "01 September 2026"),
                ("Supersedes", "v2.3 dated 01 March 2025"),
                ("Owner", "Medical Claims — Claims Operations"),
                ("Approved By", "Chief Claims Officer"),
                ("Optimisation Reference", "Fit-Gap Report FG-INS-011 dated 18 June 2026"),
                ("Catalog Alignment Score", "92% (up from 71% in v2.3)"),
                ("Classification", "Internal Use Only — Claims Restricted"),
            ]),
            ("summary", "OPTIMISATION SUMMARY — What changed in v3.0",
             ["This version incorporates 5 remediation actions from Fit-Gap Report FG-INS-011. "
              "Alignment to the Guidewire ClaimCenter health-claims catalog increased from 71% to 92%. "
              "Critical additions: duplicate & coordination-of-benefits (COB) checking, case reserving at "
              "registration, provider tariff/network validation, concurrent utilisation review, and a "
              "post-settlement recovery process. Routine claims now auto-adjudicate."],
             ["NEW STEP (green) — step added to close a gap vs the ClaimCenter catalog",
              "ENHANCED (amber) — existing step updated with additional controls or automation"]),
        ]),
        DocSection("1. Purpose", [
            ("para", "This Standard Operating Procedure defines the end-to-end process for receiving, "
             "validating, assessing, and settling medical insurance claims submitted by Meridian "
             "policyholders. Version 3.0 incorporates optimisations identified through fit-gap analysis "
             "against the Guidewire ClaimCenter Health Claims Best-Practice Catalog, achieving 92% "
             "alignment (up from 71% in v2.3)."),
            ("para", "Key additions in v3.0: duplicate and coordination-of-benefits checking at first "
             "notification, case reserving at registration, provider tariff validation, concurrent "
             "utilisation review for inpatient stays, straight-through auto-adjudication of routine claims, "
             "and a post-settlement recovery process for overpayments, COB and subrogation."),
        ]),
        DocSection("2. Scope", [
            ("para", "This procedure applies to all medical claims submitted under individual and group "
             "health, hospitalisation, and critical illness policies, including cashless treatment "
             "authorisations, reimbursement claims, pre-authorisation requests, and claim appeals."),
            ("banner", "new", "Scope extended: coordination-of-benefits (Section 5) now precedes assessment. "
             "Claims with other applicable cover are apportioned before settlement."),
            ("para", "This procedure does NOT cover property or casualty claims (SOP-INS-012), life "
             "insurance claims (SOP-INS-013), or internal employee health benefit claims processed by HR."),
        ]),
        DocSection("3. Authority Matrix", [
            ("para", "All claim settlements must be approved in accordance with the claims authority matrix. "
             "Unchanged from v2.3."),
            ("table",
             ["Settlement Value", "First Authority", "Second Authority"],
             [["Up to SGD 5,000", "Claims Processor", "—"],
              ["SGD 5,001–25,000", "Claims Adjuster", "—"],
              ["SGD 25,001–100,000", "Claims Manager", "Adjuster recommendation"],
              ["SGD 100,001–250,000", "Claims Manager", "Medical Advisor sign-off"],
              ["Above SGD 250,000", "Chief Claims Officer", "Claims Manager"]], {}),
        ]),
        DocSection("4. Roles and Responsibilities", [
            ("table", ["Role", "Responsibilities"],
             [["Claims Processor", "Registers claims; verifies eligibility; performs duplicate/COB check; "
               "sets initial reserve; checks completeness; routes claims; notifies claimants."],
              ["Claims Adjuster", "Assesses complex claims; validates provider tariffs; conducts concurrent "
               "review; calculates settlement within authority."],
              ["Claims Manager", "Approves above adjuster authority; reviews rejections; manages appeals and "
               "escalations; oversees loss ratio and recovery."],
              ["Medical Advisor (Consulting)", "Provides clinical opinion on complex, contested or high-value "
               "claims; advises on necessity and reasonable cost."],
              ["Fraud & SIU", "Reviews scored/flagged claims; runs provider-profiling and network analytics; "
               "investigates and recommends rejection, recovery or referral."],
              ["Finance", "Executes payment runs; maintains case reserves; pursues recoveries; posts GL."]], {}),
        ]),
        DocSection("5. Coordination of Benefits & Reserving (New Section — v3.0)", [
            ("banner", "crit", "New section. Required by the ClaimCenter catalog. A duplicate/COB check and an "
             "initial case reserve must be completed at registration before a claim proceeds to assessment."),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["C1", "Duplicate-claim check against Claims System", "Claims Processor",
               "Prior claims for same event/period identified; potential duplicates flagged", "T+1 day"],
              ["C2", "Coordination-of-benefits declaration check", "Claims Processor",
               "Other applicable cover (employer, government, other insurer) identified; primary/secondary payer set", "T+1 day"],
              ["C3", "Apportionment for COB-eligible claims", "Claims Adjuster",
               "Liability apportioned; secondary-payer amount calculated per policy COB clause", "T+2 days"],
              ["C4", "Set initial case reserve", "Claims Processor / Finance",
               "Case reserve raised in Majesco/SAP from benefit type and claimed amount", "T+1 day"]],
             {0: "new", 1: "new", 2: "new", 3: "new"}),
        ]),
        DocSection("6. Claim Processing Steps", [
            ("h3", "6.1 Receipt, Registration & Reserving"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["1", "Claim received (portal, app, email, post)", "Claims Processor",
               "Claim ID assigned; acknowledgement within 1 business day", "T+1 day"],
              ["2", "Eligibility verification", "Claims Processor / PAS",
               "Policy active; covered member; waiting periods checked", "T+1 day"],
              ["3", "Duplicate & COB check", "Claims Processor",
               "Per Section 5; double-payment risk removed", "T+1 day"],
              ["4", "Set initial case reserve", "Claims Processor / Finance",
               "Case reserve raised at registration", "T+1 day"],
              ["5", "Document completeness with automated diary", "Claims Processor",
               "Missing items requested; automated 7/14/28-day diary and escalation", "T+2 days"],
              ["6", "Claim type determination and routing", "Claims Processor",
               "Routine (auto-adjudicate), complex, high-value, suspicious (SIU)", "T+2 days"]],
             {2: "new", 3: "new", 4: "enh"}),
            ("h3", "6.2 Assessment & Adjudication"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["7", "Coverage & benefit limit verification", "Adjuster / PAS",
               "Benefit, sub-limit, excess, co-payment, exclusions", "T+3 days"],
              ["8", "Auto-adjudication of routine claims", "Claims System",
               "Straight-through settlement of low-value, in-network, rules-clear claims", "Same day"],
              ["9", "Clinical / medical necessity review (complex)", "Adjuster / Medical Advisor",
               "Necessity, standard of care, reasonableness assessed", "T+5 days"],
              ["10", "Provider network & tariff validation", "Claims Adjuster",
               "Charges validated against contracted tariffs; above-tariff items flagged", "T+5 days"],
              ["11", "Fraud screening with provider & network analytics", "Claims System / SIU",
               "Scoring plus provider profiling and link analytics; SIU review ≤3 days", "Parallel"],
              ["12", "Concurrent / utilisation review (inpatient)", "Claims Adjuster",
               "Ongoing stays reviewed against length-of-stay norms", "Ongoing"],
              ["13", "Settlement amount calculated", "Claims Adjuster / System",
               "Covered charges less excess and co-payment; accumulators updated", "T+5 days"]],
             {1: "enh", 3: "new", 4: "enh", 5: "new"}),
            ("h3", "6.3 Decision, Settlement & Recovery"),
            ("table", ["#", "Step / Activity", "Responsible", "Output / System", "Timeline"],
             [["14", "Claims decision made and documented", "Adjuster / Claims Manager",
               "Approve, partial, or reject; rationale recorded; per authority matrix", "T+6 days"],
              ["15", "Claimant notified of decision", "Claims Processor",
               "Settlement letter or rejection notice within 1 business day", "T+7 days"],
              ["16", "Payment processed", "Finance / Claims System",
               "Bank transfer or cheque within 5 business days; remittance advice", "T+10 days"],
              ["17", "Recovery — overpayment, COB & subrogation", "Finance / Claims Manager",
               "Recoverable amounts identified and pursued post-settlement", "Post-settlement"],
              ["18", "Claim closed and GL updated", "Claims Processor / Finance",
               "Status set; reserve released/adjusted; GL journal posted", "T+10 days"]],
             {3: "new"}),
        ]),
        DocSection("7. Exception Handling", [
            ("h3", "7.1 Claim Rejection & Appeals"),
            ("numbered", [
                "Rejection notice states the specific reason with reference to the policy wording clause; "
                "issued within 1 business day of decision.",
                "Claimant has 30 calendar days to lodge an appeal with the Claims Manager.",
                "Appeals reviewed within 10 business days; outcome communicated in writing."]),
            ("h3", "7.2 Suspected Fraud"),
            ("numbered_from", 4, [
                "SIU takes over the claim file; normal settlement is suspended.",
                "Claimant notified that additional information is required, without disclosing the investigation.",
                "SIU provides an investigation report to the Claims Manager within 20 business days; the "
                "Claims Manager determines next action including recovery or referral."]),
            ("h3", "7.3 Pre-Authorisation & Concurrent Review"),
            ("numbered_from", 7, [
                "Medical facility submits a pre-authorisation request via the provider portal at least 48 "
                "hours before scheduled admission; the Adjuster responds within 4 business hours.",
                "Approval triggers a direct-billing arrangement; no cash payment is required at point of care.",
                "For inpatient stays beyond the approved length, concurrent review (step 12) requires periodic "
                "clinical updates before further days are authorised."]),
            ("h3", "7.4 Missing Documents (Enhanced — v3.0)"),
            ("banner", "enh", "Document follow-up is now driven by an automated diary with escalation at 14 "
             "and 28 days, replacing manual tracking."),
            ("numbered_from", 10, [
                "Written request issued with an itemised list of missing items; claimant given 14 calendar days.",
                "Day 14 without response: automated follow-up notice; claim held a further 14 days.",
                "Day 28 without response: claim closed as 'Insufficient Documentation'; reopenable within 12 months."]),
        ]),
        DocSection("8. Systems and Tools", [
            ("table", ["System", "Purpose", "Primary Users"],
             [["Claims Management System (Majesco)", "Registration, reserving, adjudication workflow, "
               "settlement, recovery, reporting", "All Claims roles"],
              ["Policy Administration System (PAS)", "Eligibility, benefit limits, COB, accumulators", "Processor, Adjuster"],
              ["Provider Portal", "Pre-authorisation, concurrent review, direct billing, document submission", "Facilities, Adjuster"],
              ["Fraud Detection System", "Claim scoring, provider profiling, network/link analytics", "Automated / SIU"],
              ["Provider Tariff / Network Catalog", "Contracted tariffs and network pricing for charge validation", "Claims Adjuster"],
              ["SAP S/4HANA", "Payment, case reserves, recoveries, GL", "Finance, Claims Manager"],
              ["Medical Advisor Platform (TPA)", "Secure clinical document sharing", "Adjuster, Medical Advisor"]], {}),
        ]),
        DocSection("9. Key Controls and Audit Points", [
            ("banner", "enh", "Controls expanded in v3.0: COB/duplicate gate, FNOL reserving, tariff "
             "validation, concurrent review, and post-settlement recovery."),
            ("bullets", [
                "Duplicate & COB gate: every claim is checked for prior claims and other cover before assessment.",
                "Case reserving: an initial reserve is raised at registration and trued-up at closure.",
                "Provider tariff validation: billed charges are validated against contracted tariffs to control leakage.",
                "Segregation of duties: assessor ≠ payment approver ≠ recovery owner.",
                "Auto-adjudication audit: STP-settled claims sampled monthly by the Claims Manager.",
                "Fraud analytics: provider-profiling and network analytics supplement claim scoring; SIU review ≥2%.",
                "Recovery: overpayments, COB and subrogation amounts identified and pursued after settlement.",
                "Immutable audit trail: all registration, decision, payment and recovery actions logged with user ID and timestamp."]),
        ]),
        DocSection("10. Key Performance Indicators", [
            ("table", ["KPI", "v2.3 Target", "v3.0 Target", "Measurement"],
             [["Straight-through settlement", "N/A (new)", "≥40% of routine claims", "Majesco auto-adjudication rate"],
              ["Claims processing cycle time", "90% ≤10 business days", "90% ≤7 business days", "Receipt to settlement"],
              ["First-pass accuracy", "≥92%", "≥95%", "Claims assessed without rework"],
              ["Claims leakage vs expected", "≤3 ppts", "≤1.5 ppts", "Paid vs expected loss ratio"],
              ["Recovery capture", "N/A (new)", "≥80% of identified recoverables", "SAP recovery ledger"],
              ["Reserving accuracy", "N/A (new)", "Reserve set at FNOL on 100%", "Majesco reserve date vs registration"]], {}),
        ]),
        DocSection("11. Document Control", [
            ("table", ["Version", "Date", "Author", "Summary of Changes"],
             [["2.3", "01 Mar 2025", "R. Nair, Claims Manager", "Added cashless pre-auth sub-steps; updated KPIs for leakage control"],
              ["3.0", "01 Sep 2026", "R. Nair, Claims Manager",
               "OPTIMISED: COB & duplicate check; FNOL reserving; provider tariff validation; concurrent "
               "review; auto-adjudication; post-settlement recovery; catalog alignment 71% → 92%"]], {}),
        ]),
    ],
)

package = SopPackage(
    meta=meta, phases=phases, steps=steps, authority=authority, swim_phases=swim_phases,
    n_phases=3, n_steps=12, n_roles=6, n_gateways=3,
    fitgap=fitgap,
    opt_phases=opt_phases, opt_steps=opt_steps, opt_swim_phases=opt_swim_phases,
    opt_n_phases=3, opt_n_steps=18, opt_n_gateways=3, opt_fit=92,
    optimised_doc=optimised_doc,
    swim_cover_tags="Receipt · Assessment · Settlement · Fraud screening · Exception handling",
    hierarchy_cover_sub="Phase breakdown with claim tracks, authority thresholds, and exception paths",
)
