"""
exports.py – Excel and Markdown export logic for MANDATE.
"""

import os
import io
from datetime import date, datetime
import pandas as pd
from models import Vendor, QuestionnaireReview, Evidence, RiskAssessment, FollowUp, Remediation, Approval


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_date(d):
    return d.strftime("%Y-%m-%d") if d else ""


def _bool_str(b):
    return "Yes" if b else "No"


# ---------------------------------------------------------------------------
# Excel Export
# ---------------------------------------------------------------------------

def export_excel(app, export_dir="exports"):
    """
    Export all MANDATE data to a multi-sheet Excel workbook.
    Returns the file path of the generated .xlsx file.
    """
    os.makedirs(export_dir, exist_ok=True)
    filename = f"MANDATE_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(export_dir, filename)

    with app.app_context():
        vendors = Vendor.query.all()
        qrs = QuestionnaireReview.query.all()
        evidence = Evidence.query.all()
        risk_assessments = RiskAssessment.query.all()
        follow_ups = FollowUp.query.all()
        remediations = Remediation.query.all()
        approvals = Approval.query.all()

    # ----- Sheet 1: Vendor Inventory -----
    vendor_rows = []
    for v in vendors:
        vendor_rows.append({
            "Vendor ID": v.id,
            "Vendor Name": v.vendor_name,
            "Category": v.vendor_category,
            "Business Owner": v.business_owner,
            "Security Reviewer": v.security_reviewer,
            "Department": v.department,
            "Service Description": v.service_description,
            "System Supported": v.system_supported,
            "Data Types Processed": v.data_types_processed,
            "Sensitive Data": _bool_str(v.sensitive_data),
            "PHI Involved": _bool_str(v.phi_involved),
            "Payment Data": _bool_str(v.payment_data),
            "PII Involved": _bool_str(v.pii_involved),
            "Cloud Hosted": _bool_str(v.cloud_hosted),
            "Country/Region": v.country_region,
            "Criticality": v.criticality,
            "Inherent Risk": v.inherent_risk,
            "Residual Risk": v.residual_risk,
            "Review Status": v.review_status,
            "Approval Status": v.approval_status,
            "Onboarding Date": _fmt_date(v.onboarding_date),
            "Last Review Date": _fmt_date(v.last_review_date),
            "Next Review Date": _fmt_date(v.next_review_date),
            "Notes": v.notes,
        })
    df_vendors = pd.DataFrame(vendor_rows)

    # ----- Sheet 2: Questionnaire Reviews -----
    qr_rows = []
    for q in qrs:
        qr_rows.append({
            "QR ID": q.id,
            "Vendor ID": q.vendor_id,
            "Domain": q.domain,
            "Question Text": q.question_text,
            "Vendor Response": q.vendor_response,
            "Response Quality": q.response_quality,
            "Risk Flag": q.risk_flag,
            "Analyst Notes": q.analyst_notes,
            "Follow-Up Required": _bool_str(q.follow_up_required),
            "Follow-Up Question": q.follow_up_question,
            "Reviewer": q.reviewer,
            "Review Date": _fmt_date(q.review_date),
        })
    df_qr = pd.DataFrame(qr_rows)

    # ----- Sheet 3: Evidence Tracker -----
    ev_rows = []
    for e in evidence:
        ev_rows.append({
            "Evidence ID": e.id,
            "Vendor ID": e.vendor_id,
            "Evidence Name": e.evidence_name,
            "Evidence Type": e.evidence_type,
            "Related Domain": e.related_domain,
            "Description": e.evidence_description,
            "Evidence Status": e.evidence_status,
            "Evidence Date": _fmt_date(e.evidence_date),
            "Expiration Date": _fmt_date(e.expiration_date),
            "Evidence Owner": e.evidence_owner,
            "File/Link": e.file_path_or_link,
            "Reviewer Notes": e.reviewer_notes,
            "Validity Status": e.validity_status,
        })
    df_ev = pd.DataFrame(ev_rows)

    # ----- Sheet 4: Risk Assessments -----
    ra_rows = []
    for ra in risk_assessments:
        ra_rows.append({
            "Assessment ID": ra.id,
            "Vendor ID": ra.vendor_id,
            "Assessment Date": _fmt_date(ra.assessment_date),
            "Assessor": ra.assessor,
            "Inherent Likelihood": ra.inherent_likelihood,
            "Inherent Impact": ra.inherent_impact,
            "Inherent Risk Score": ra.inherent_risk_score,
            "Inherent Risk Rating": ra.inherent_risk_rating,
            "Key Risk Drivers": ra.key_risk_drivers,
            "Existing Controls": ra.existing_controls,
            "Control Gaps": ra.control_gaps,
            "Compensating Controls": ra.compensating_controls,
            "Residual Likelihood": ra.residual_likelihood,
            "Residual Impact": ra.residual_impact,
            "Residual Risk Score": ra.residual_risk_score,
            "Residual Risk Rating": ra.residual_risk_rating,
            "Risk Decision": ra.risk_decision,
            "Risk Owner": ra.risk_owner,
            "Approval Required": _bool_str(ra.approval_required),
            "Notes": ra.notes,
        })
    df_ra = pd.DataFrame(ra_rows)

    # ----- Sheet 5: Follow-Ups -----
    fu_rows = []
    for fu in follow_ups:
        fu_rows.append({
            "Follow-Up ID": fu.id,
            "Vendor ID": fu.vendor_id,
            "Follow-Up Question": fu.follow_up_question,
            "Requested From": fu.requested_from,
            "Owner": fu.owner,
            "Due Date": _fmt_date(fu.due_date),
            "Status": fu.status,
            "Vendor Response": fu.vendor_response,
            "Analyst Notes": fu.analyst_notes,
            "Closure Date": _fmt_date(fu.closure_date),
        })
    df_fu = pd.DataFrame(fu_rows)

    # ----- Sheet 6: Remediation Conditions -----
    rem_rows = []
    for rem in remediations:
        rem_rows.append({
            "Remediation ID": rem.id,
            "Vendor ID": rem.vendor_id,
            "Risk Assessment ID": rem.risk_assessment_id,
            "Title": rem.title,
            "Description": rem.description,
            "Required Action": rem.required_action,
            "Owner": rem.owner,
            "Due Date": _fmt_date(rem.due_date),
            "Status": rem.status,
            "Validation Method": rem.validation_method,
            "Closure Evidence": rem.closure_evidence,
            "Closure Notes": rem.closure_notes,
        })
    df_rem = pd.DataFrame(rem_rows)

    # ----- Sheet 7: Approvals & Exceptions -----
    ap_rows = []
    for ap in approvals:
        ap_rows.append({
            "Approval ID": ap.id,
            "Vendor ID": ap.vendor_id,
            "Risk Decision": ap.risk_decision,
            "Exception Required": _bool_str(ap.exception_required),
            "Exception Reason": ap.exception_reason,
            "Business Justification": ap.business_justification,
            "Compensating Controls": ap.compensating_controls,
            "Risk Acceptance Owner": ap.risk_acceptance_owner,
            "Approval Status": ap.approval_status,
            "Approval Date": _fmt_date(ap.approval_date),
            "Expiration Date": _fmt_date(ap.expiration_date),
            "Review Date": _fmt_date(ap.review_date),
            "Notes": ap.notes,
        })
    df_ap = pd.DataFrame(ap_rows)

    # ----- Sheet 8: Dashboard Summary -----
    summary_rows = [
        {"Metric": "Total Vendors", "Value": len(vendors)},
        {"Metric": "Vendors – Sensitive Data", "Value": sum(1 for v in vendors if v.sensitive_data)},
        {"Metric": "Vendors – PHI", "Value": sum(1 for v in vendors if v.phi_involved)},
        {"Metric": "Vendors – Payment Data", "Value": sum(1 for v in vendors if v.payment_data)},
        {"Metric": "High/Critical Risk Vendors", "Value": sum(1 for v in vendors if v.residual_risk in ("High", "Critical"))},
        {"Metric": "Missing Evidence Records", "Value": sum(1 for e in evidence if e.evidence_status == "Missing")},
        {"Metric": "Outdated/Expired Evidence", "Value": sum(1 for e in evidence if e.evidence_status in ("Outdated", "Expired"))},
        {"Metric": "High-Risk QR Responses", "Value": sum(1 for q in qrs if q.risk_flag in ("High", "Critical"))},
        {"Metric": "Overdue Follow-Ups", "Value": sum(1 for fu in follow_ups if fu.status == "Overdue")},
        {"Metric": "Open Follow-Ups", "Value": sum(1 for fu in follow_ups if fu.status in ("Open", "Sent to Vendor"))},
        {"Metric": "Approved Vendors", "Value": sum(1 for ap in approvals if ap.approval_status in ("Approved", "Approved with Exception"))},
        {"Metric": "Rejected Vendors", "Value": sum(1 for ap in approvals if ap.approval_status == "Rejected")},
        {"Metric": "Pending Approvals", "Value": sum(1 for ap in approvals if ap.approval_status == "Pending Approval")},
        {"Metric": "Open Exceptions", "Value": sum(1 for ap in approvals if ap.exception_required and ap.approval_status not in ("Rejected", "Expired"))},
        {"Metric": "Report Generated", "Value": datetime.now().strftime("%Y-%m-%d %H:%M")},
    ]
    df_summary = pd.DataFrame(summary_rows)

    # ----- Write to Excel -----
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df_vendors.to_excel(writer, sheet_name="Vendor Inventory", index=False)
        df_qr.to_excel(writer, sheet_name="Questionnaire Reviews", index=False)
        df_ev.to_excel(writer, sheet_name="Evidence Tracker", index=False)
        df_ra.to_excel(writer, sheet_name="Risk Assessments", index=False)
        df_fu.to_excel(writer, sheet_name="Follow-Ups", index=False)
        df_rem.to_excel(writer, sheet_name="Remediation Conditions", index=False)
        df_ap.to_excel(writer, sheet_name="Approvals and Exceptions", index=False)
        df_summary.to_excel(writer, sheet_name="Dashboard Summary", index=False)

    return filepath


# ---------------------------------------------------------------------------
# Markdown Report Export
# ---------------------------------------------------------------------------

def export_markdown_report(report_data, export_dir="exports"):
    """
    Write the management report as a Markdown file.
    report_data is the dict returned by reports.build_management_report().
    Returns the file path.
    """
    os.makedirs(export_dir, exist_ok=True)
    filename = f"MANDATE_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(export_dir, filename)

    lines = [
        "# MANDATE – Third-Party Security & Data Handling Review",
        f"**Report Date:** {report_data['report_date']}  ",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Vendors Reviewed | {report_data['total_vendors']} |",
        f"| Vendors Handling Sensitive Data | {report_data['sensitive_vendors']} |",
        f"| Vendors Handling PHI | {report_data['phi_vendors']} |",
        f"| Vendors Handling Payment Data | {report_data['payment_vendors']} |",
        f"| High / Critical Risk Vendors | {report_data['high_risk_vendors']} |",
        f"| Vendors Pending Evidence | {report_data['pending_evidence_vendors']} |",
        f"| Overdue Follow-Ups | {report_data['overdue_followups']} |",
        f"| Open Follow-Ups | {report_data['open_followups']} |",
        f"| Approved with Conditions | {report_data['approved_with_conditions']} |",
        f"| Open Exceptions | {report_data['open_exceptions']} |",
        "",
        "---",
        "",
        "## Review Scope",
        "",
        f"Vendor categories reviewed: {report_data['review_scope']}",
        "",
        "---",
        "",
        "## Top Control Domain Weaknesses",
        "",
        "| Domain | High/Critical Flags |",
        "|--------|---------------------|",
    ]
    for domain, count in report_data["top_missing_domains"]:
        lines.append(f"| {domain} | {count} |")

    lines += [
        "",
        "---",
        "",
        "## Top 5 High-Risk Vendors",
        "",
        "| Vendor | Residual Risk | Residual Score | Risk Decision | Review Status |",
        "|--------|--------------|----------------|---------------|---------------|",
    ]
    for v in report_data["top5_risky"]:
        lines.append(
            f"| {v['vendor_name']} | {v['residual_risk']} | {v['residual_score']} "
            f"| {v['risk_decision']} | {v['review_status']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Recommended Next Steps",
        "",
    ]
    for step in report_data["next_steps"]:
        lines.append(f"- {step}")

    lines += ["", "---", "", "*Generated by MANDATE – Third-Party Security & Data Handling Review Tracker*", ""]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath
