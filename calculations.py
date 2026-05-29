"""
calculations.py – Automated risk scoring, evidence flagging, and overdue logic.

All functions operate on SQLAlchemy model objects (no raw SQL).
"""

from datetime import date, timedelta
from models import QuestionnaireReview, Evidence, FollowUp, Vendor


# ---------------------------------------------------------------------------
# Risk Score Helpers
# ---------------------------------------------------------------------------

RISK_RATING_MAP = {
    (1, 4):   "Low",
    (5, 9):   "Medium",
    (10, 16): "High",
    (17, 25): "Critical",
}


def score_to_rating(score: int) -> str:
    """Convert a numeric risk score (1–25) to a text rating."""
    if score <= 4:
        return "Low"
    elif score <= 9:
        return "Medium"
    elif score <= 16:
        return "High"
    else:
        return "Critical"


def calculate_risk_scores(risk_assessment):
    """
    Compute inherent and residual risk scores and ratings for a RiskAssessment object.
    Modifies the object in-place and returns it.
    """
    inherent = (risk_assessment.inherent_likelihood or 1) * (risk_assessment.inherent_impact or 1)
    residual = (risk_assessment.residual_likelihood or 1) * (risk_assessment.residual_impact or 1)

    risk_assessment.inherent_risk_score = inherent
    risk_assessment.inherent_risk_rating = score_to_rating(inherent)
    risk_assessment.residual_risk_score = residual
    risk_assessment.residual_risk_rating = score_to_rating(residual)
    return risk_assessment


# ---------------------------------------------------------------------------
# Questionnaire Auto-Checks
# ---------------------------------------------------------------------------

VAGUE_PHRASES = [
    "industry standard", "as needed", "upon request", "best effort",
    "n/a", "not applicable", "standard practice", "we follow best practices",
    "where appropriate", "in line with industry norms",
]

HIGH_RISK_PHRASES = [
    "no mfa", "not encrypted", "no logging", "no incident response",
    "no backups", "no formal plan", "no documentation", "no policy",
    "no encryption", "unencrypted", "plain text", "no audit log",
    "no disaster recovery", "no backup", "no mfa enforced",
]

SENSITIVE_NO_ENCRYPT = ["sensitive", "phi", "pii", "payment", "cardholder", "hipaa"]


def auto_check_response(qr) -> None:
    """
    Apply automated quality checks to a QuestionnaireReview object.
    Sets response_quality and risk_flag. Modifies object in-place.
    """
    response = (qr.vendor_response or "").strip().lower()

    if not response or response in ("", "none", "n/a"):
        qr.response_quality = "Missing"
        qr.risk_flag = "High"
        qr.follow_up_required = True
        return

    # High-risk keyword check
    for phrase in HIGH_RISK_PHRASES:
        if phrase in response:
            qr.response_quality = "High Risk"
            qr.risk_flag = "High"
            qr.follow_up_required = True
            return

    # Vague language check
    for phrase in VAGUE_PHRASES:
        if phrase in response:
            qr.response_quality = "Vague"
            qr.risk_flag = "Medium"
            if not qr.follow_up_required:
                qr.follow_up_required = True
            return

    # Short response (<15 chars) is suspicious
    if len(response) < 15:
        qr.response_quality = "Incomplete"
        qr.risk_flag = "Medium"
        return

    # Default – acceptable
    qr.response_quality = "Acceptable"
    qr.risk_flag = "None"


# ---------------------------------------------------------------------------
# Evidence Auto-Checks
# ---------------------------------------------------------------------------

EVIDENCE_EXPIRY_MONTHS = {
    "SOC 2 Type II Report": 12,
    "ISO 27001 Certificate": 36,
    "Penetration Test Summary": 12,
    "Vulnerability Scan Report": 6,
    "Cyber Insurance Certificate": 12,
}


def auto_check_evidence(ev) -> None:
    """
    Apply automated validity checks to an Evidence object.
    Sets evidence_status and validity_status. Modifies object in-place.
    """
    today = date.today()

    # Expired: expiration date is in the past
    if ev.expiration_date and ev.expiration_date < today:
        ev.evidence_status = "Expired"
        ev.validity_status = "Expired"
        return

    # Outdated by evidence type age thresholds
    max_months = EVIDENCE_EXPIRY_MONTHS.get(ev.evidence_type)
    if max_months and ev.evidence_date:
        age_days = (today - ev.evidence_date).days
        if age_days > max_months * 30:
            ev.evidence_status = "Outdated"
            ev.validity_status = "Outdated"
            return

    if ev.evidence_status not in ("Available", "Accepted"):
        pass  # keep existing status

    ev.validity_status = "Valid"


def check_evidence_gaps(vendor, evidence_list: list) -> list[str]:
    """
    Return a list of evidence gap strings for a given vendor.
    evidence_list: list of Evidence objects for this vendor.
    """
    gaps = []
    types_present = {e.evidence_type for e in evidence_list
                     if e.evidence_status in ("Available", "Accepted")}

    if vendor.phi_involved:
        hipaa_types = {"HIPAA BAA", "HITRUST Certificate", "SOC 2 Type II Report"}
        if not types_present.intersection(hipaa_types):
            gaps.append("PHI handled but no HIPAA/HITRUST/SOC 2 evidence found")

    if vendor.payment_data:
        pci_types = {"PCI DSS Certificate", "PCI SAQ", "SOC 2 Type II Report"}
        if not types_present.intersection(pci_types):
            gaps.append("Payment data handled but no PCI-related evidence found")

    if vendor.sensitive_data:
        if "Encryption Policy" not in types_present:
            gaps.append("Sensitive data handled but no Encryption Policy on file")

    return gaps


# ---------------------------------------------------------------------------
# Follow-Up Overdue Logic
# ---------------------------------------------------------------------------

def mark_overdue_followups(follow_ups: list) -> None:
    """
    Mark any follow-up past its due date (and not Closed) as Overdue.
    Modifies objects in-place.
    """
    today = date.today()
    for fu in follow_ups:
        if fu.status not in ("Closed",) and fu.due_date and fu.due_date < today:
            fu.status = "Overdue"


# ---------------------------------------------------------------------------
# Approval Expiry Logic
# ---------------------------------------------------------------------------

def mark_expired_approvals(approvals: list) -> None:
    """
    Mark any approval whose expiration_date is in the past as Expired.
    Modifies objects in-place.
    """
    today = date.today()
    for ap in approvals:
        if ap.expiration_date and ap.expiration_date < today:
            if ap.approval_status not in ("Rejected",):
                ap.approval_status = "Expired"


# ---------------------------------------------------------------------------
# Dashboard Summary Stats
# ---------------------------------------------------------------------------

def build_dashboard_stats(vendors, questionnaire_reviews, evidence_records,
                           follow_ups, approvals):
    """
    Return a dictionary of dashboard KPI numbers used by the dashboard template.
    """
    today = date.today()

    total_vendors = len(vendors)

    # Risk distribution
    risk_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0, "Unknown": 0}
    for v in vendors:
        rating = v.residual_risk or "Unknown"
        risk_counts[rating] = risk_counts.get(rating, 0) + 1

    # Review status distribution
    status_counts = {}
    for v in vendors:
        s = v.review_status or "Not Started"
        status_counts[s] = status_counts.get(s, 0) + 1

    # Evidence issues
    missing_evidence = sum(1 for e in evidence_records if e.evidence_status == "Missing")
    outdated_evidence = sum(1 for e in evidence_records if e.evidence_status in ("Outdated", "Expired"))

    # High-risk responses
    high_risk_responses = sum(
        1 for q in questionnaire_reviews if q.risk_flag in ("High", "Critical")
    )

    # Sensitive data vendors
    vendors_phi = sum(1 for v in vendors if v.phi_involved)
    vendors_payment = sum(1 for v in vendors if v.payment_data)
    vendors_sensitive = sum(1 for v in vendors if v.sensitive_data)

    # Follow-ups
    open_followups = sum(1 for fu in follow_ups if fu.status in ("Open", "Sent to Vendor", "Vendor Responded", "Pending Review"))
    overdue_followups = sum(1 for fu in follow_ups if fu.status == "Overdue")

    # Approvals
    pending_approvals = sum(1 for ap in approvals if ap.approval_status == "Pending Approval")
    approved_count = sum(1 for ap in approvals if ap.approval_status in ("Approved", "Approved with Exception"))
    rejected_count = sum(1 for ap in approvals if ap.approval_status == "Rejected")
    expired_exceptions = sum(1 for ap in approvals if ap.approval_status == "Expired")

    # Domain weakness (count High/Critical flags per domain)
    domain_flags = {}
    for q in questionnaire_reviews:
        if q.risk_flag in ("High", "Critical"):
            d = q.domain or "Unknown"
            domain_flags[d] = domain_flags.get(d, 0) + 1

    return {
        "total_vendors": total_vendors,
        "risk_counts": risk_counts,
        "status_counts": status_counts,
        "missing_evidence": missing_evidence,
        "outdated_evidence": outdated_evidence,
        "high_risk_responses": high_risk_responses,
        "vendors_phi": vendors_phi,
        "vendors_payment": vendors_payment,
        "vendors_sensitive": vendors_sensitive,
        "open_followups": open_followups,
        "overdue_followups": overdue_followups,
        "pending_approvals": pending_approvals,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "expired_exceptions": expired_exceptions,
        "domain_flags": domain_flags,
    }
