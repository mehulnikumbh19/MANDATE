"""
reports.py – Management report generation logic for MANDATE.
Produces summary dicts used by the reports template and export functions.
"""

from datetime import date
from models import Vendor, QuestionnaireReview, Evidence, RiskAssessment, FollowUp, Remediation, Approval
from calculations import score_to_rating


def build_management_report(app):
    """
    Build a comprehensive management-ready third-party risk summary dict.
    Returns a dict consumed by reports.html and the export functions.
    """
    with app.app_context():
        vendors = Vendor.query.all()
        qrs = QuestionnaireReview.query.all()
        evidence = Evidence.query.all()
        follow_ups = FollowUp.query.all()
        remediations = Remediation.query.all()
        approvals = Approval.query.all()
        risk_assessments = RiskAssessment.query.all()

        today = date.today()

        total_vendors = len(vendors)
        sensitive_vendors = [v for v in vendors if v.sensitive_data]
        phi_vendors = [v for v in vendors if v.phi_involved]
        payment_vendors = [v for v in vendors if v.payment_data]
        high_risk = [v for v in vendors if v.residual_risk in ("High", "Critical")]
        pending_evidence_vendors = [v for v in vendors if v.review_status == "Pending Evidence"]

        # Missing control domains (High or Critical flagged QRs grouped by domain)
        domain_flag_counts = {}
        for q in qrs:
            if q.risk_flag in ("High", "Critical"):
                d = q.domain or "Unknown"
                domain_flag_counts[d] = domain_flag_counts.get(d, 0) + 1
        top_missing_domains = sorted(domain_flag_counts.items(), key=lambda x: -x[1])[:5]

        # Top 5 high-risk vendors by residual risk score
        ra_by_vendor = {ra.vendor_id: ra for ra in risk_assessments}
        scored = []
        for v in vendors:
            ra = ra_by_vendor.get(v.id)
            score = ra.residual_risk_score if ra else 0
            scored.append((v, score, ra))
        top5_risky = sorted(scored, key=lambda x: -x[1])[:5]

        overdue_fus = [fu for fu in follow_ups if fu.status == "Overdue"]
        open_fus = [fu for fu in follow_ups if fu.status in ("Open", "Sent to Vendor", "Vendor Responded", "Pending Review")]

        approved_with_conditions = [
            v for v in vendors
            if v.review_status in ("Approved with Conditions",)
            or v.approval_status == "Approved with Exception"
        ]

        open_exceptions = [
            ap for ap in approvals
            if ap.exception_required and ap.approval_status not in ("Rejected", "Expired")
        ]

        # Recommended next steps
        next_steps = []
        if [v for v in vendors if v.phi_involved and v.review_status in ("Pending Evidence", "In Review", "Not Started")]:
            next_steps.append("Prioritize PHI vendors with outstanding evidence gaps.")
        if overdue_fus:
            next_steps.append(f"Resolve {len(overdue_fus)} overdue follow-up questions with vendors.")
        if [v for v in vendors if v.residual_risk == "Critical"]:
            next_steps.append("Escalate Critical-risk vendors to CISO for review.")
        if [ap for ap in approvals if ap.approval_status == "Expired"]:
            next_steps.append("Renew expired approval exceptions before vendor continues processing data.")
        next_steps.append("Schedule annual reassessment for vendors with next review date within 90 days.")

        return {
            "report_date": today.strftime("%B %d, %Y"),
            "total_vendors": total_vendors,
            "review_scope": ", ".join(sorted({v.vendor_category for v in vendors if v.vendor_category})),
            "sensitive_vendors": len(sensitive_vendors),
            "phi_vendors": len(phi_vendors),
            "payment_vendors": len(payment_vendors),
            "high_risk_vendors": len(high_risk),
            "pending_evidence_vendors": len(pending_evidence_vendors),
            "top_missing_domains": top_missing_domains,
            "top5_risky": [
                {
                    "vendor_name": v.vendor_name,
                    "residual_risk": v.residual_risk or "Unknown",
                    "residual_score": score,
                    "risk_decision": ra.risk_decision if ra else "N/A",
                    "review_status": v.review_status,
                }
                for v, score, ra in top5_risky
            ],
            "overdue_followups": len(overdue_fus),
            "open_followups": len(open_fus),
            "approved_with_conditions": len(approved_with_conditions),
            "open_exceptions": len(open_exceptions),
            "next_steps": next_steps,
            # Raw lists for export
            "_vendors": vendors,
            "_qrs": qrs,
            "_evidence": evidence,
            "_follow_ups": follow_ups,
            "_remediations": remediations,
            "_approvals": approvals,
            "_risk_assessments": risk_assessments,
        }
