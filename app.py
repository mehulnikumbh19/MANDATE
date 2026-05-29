"""
app.py – MANDATE Flask application entry point.

Run:
    pip install -r requirements.txt
    python app.py

Reset & reseed:
    flask seed
"""

import os
from datetime import date
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_file, abort,
)
from database import db, init_db
from models import (
    Vendor, QuestionnaireReview, Evidence,
    RiskAssessment, FollowUp, Remediation, Approval,
)
from calculations import (
    auto_check_response, auto_check_evidence,
    calculate_risk_scores, mark_overdue_followups,
    mark_expired_approvals, build_dashboard_stats,
)
from reports import build_management_report
from imports import import_vendors_csv, import_questionnaires_csv, import_evidence_csv
from exports import export_excel, export_markdown_report
from seed_data import seed_all

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/mandate.db"
else:
    DB_PATH = os.path.join(BASE_DIR, "data", "mandate.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "mandate-secret-key-2025"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit

if os.environ.get("VERCEL"):
    EXPORTS_DIR = "/tmp/exports"
    os.makedirs(EXPORTS_DIR, exist_ok=True)
else:
    EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    os.makedirs(EXPORTS_DIR, exist_ok=True)

init_db(app)

# ---------------------------------------------------------------------------
# CLI: flask seed
# ---------------------------------------------------------------------------

@app.cli.command("seed")
def seed_command():
    """Drop all data and reload sample seed data."""
    seed_all(app)


# ---------------------------------------------------------------------------
# Context helpers
# ---------------------------------------------------------------------------

RISK_BADGE = {
    "Critical": "danger",
    "High":     "warning",
    "Medium":   "info",
    "Low":      "success",
    "Unknown":  "secondary",
}

STATUS_BADGE = {
    "Approved":              "success",
    "Approved with Exception": "warning",
    "Rejected":              "danger",
    "Pending Approval":      "primary",
    "Draft":                 "secondary",
    "Expired":               "dark",
    "Not Started":           "secondary",
    "In Review":             "info",
    "Pending Evidence":      "warning",
    "Pending Vendor Response": "warning",
    "Pending Risk Decision": "primary",
    "Approved with Conditions": "warning",
    "Reassessment Required": "danger",
}


@app.context_processor
def inject_globals():
    return dict(risk_badge=RISK_BADGE, status_badge=STATUS_BADGE, today=date.today())


# ---------------------------------------------------------------------------
# Auto-refresh logic (run on each request)
# ---------------------------------------------------------------------------

def refresh_statuses():
    """Mark overdue follow-ups and expired approvals on every request."""
    follow_ups = FollowUp.query.all()
    mark_overdue_followups(follow_ups)
    approvals = Approval.query.all()
    mark_expired_approvals(approvals)
    db.session.commit()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    refresh_statuses()
    vendors = Vendor.query.all()
    qrs = QuestionnaireReview.query.all()
    evidence = Evidence.query.all()
    follow_ups = FollowUp.query.all()
    approvals = Approval.query.all()
    stats = build_dashboard_stats(vendors, qrs, evidence, follow_ups, approvals)
    return render_template("dashboard.html", stats=stats)


# ---------------------------------------------------------------------------
# Vendors
# ---------------------------------------------------------------------------

@app.route("/vendors")
def vendors():
    refresh_statuses()
    # Filters
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    criticality = request.args.get("criticality", "")
    review_status = request.args.get("review_status", "")
    approval_status = request.args.get("approval_status", "")
    risk = request.args.get("risk", "")
    phi = request.args.get("phi", "")
    payment = request.args.get("payment", "")

    query = Vendor.query
    if q:
        query = query.filter(
            Vendor.vendor_name.ilike(f"%{q}%") |
            Vendor.business_owner.ilike(f"%{q}%") |
            Vendor.service_description.ilike(f"%{q}%")
        )
    if category:
        query = query.filter(Vendor.vendor_category == category)
    if criticality:
        query = query.filter(Vendor.criticality == criticality)
    if review_status:
        query = query.filter(Vendor.review_status == review_status)
    if approval_status:
        query = query.filter(Vendor.approval_status == approval_status)
    if risk:
        query = query.filter(Vendor.residual_risk == risk)
    if phi == "yes":
        query = query.filter(Vendor.phi_involved == True)
    if payment == "yes":
        query = query.filter(Vendor.payment_data == True)

    vendor_list = query.order_by(Vendor.vendor_name).all()

    categories = sorted({v.vendor_category for v in Vendor.query.all() if v.vendor_category})
    return render_template(
        "vendors.html",
        vendors=vendor_list,
        categories=categories,
        filters=request.args,
    )


@app.route("/vendors/new", methods=["GET", "POST"])
def vendor_new():
    if request.method == "POST":
        f = request.form
        vendor = Vendor(
            vendor_name=f.get("vendor_name", "").strip(),
            vendor_category=f.get("vendor_category", ""),
            business_owner=f.get("business_owner", ""),
            security_reviewer=f.get("security_reviewer", ""),
            department=f.get("department", ""),
            service_description=f.get("service_description", ""),
            system_supported=f.get("system_supported", ""),
            data_types_processed=f.get("data_types_processed", ""),
            sensitive_data="sensitive_data" in f,
            phi_involved="phi_involved" in f,
            payment_data="payment_data" in f,
            pii_involved="pii_involved" in f,
            cloud_hosted="cloud_hosted" in f,
            country_region=f.get("country_region", ""),
            criticality=f.get("criticality", "Medium"),
            inherent_risk=f.get("inherent_risk", ""),
            residual_risk=f.get("residual_risk", ""),
            review_status=f.get("review_status", "Not Started"),
            approval_status=f.get("approval_status", "Draft"),
            onboarding_date=_parse_form_date(f.get("onboarding_date")),
            next_review_date=_parse_form_date(f.get("next_review_date")),
            notes=f.get("notes", ""),
        )
        db.session.add(vendor)
        db.session.commit()
        flash(f"Vendor '{vendor.vendor_name}' created.", "success")
        return redirect(url_for("vendor_detail", vendor_id=vendor.id))
    return render_template("vendor_form.html", vendor=None)


@app.route("/vendors/<int:vendor_id>")
def vendor_detail(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    qrs = QuestionnaireReview.query.filter_by(vendor_id=vendor_id).all()
    evidence = Evidence.query.filter_by(vendor_id=vendor_id).all()
    risk_assessments = RiskAssessment.query.filter_by(vendor_id=vendor_id).all()
    follow_ups = FollowUp.query.filter_by(vendor_id=vendor_id).all()
    remediations = Remediation.query.filter_by(vendor_id=vendor_id).all()
    approvals = Approval.query.filter_by(vendor_id=vendor_id).all()

    from calculations import check_evidence_gaps
    evidence_gaps = check_evidence_gaps(vendor, evidence)

    return render_template(
        "vendor_detail.html",
        vendor=vendor,
        qrs=qrs,
        evidence=evidence,
        risk_assessments=risk_assessments,
        follow_ups=follow_ups,
        remediations=remediations,
        approvals=approvals,
        evidence_gaps=evidence_gaps,
        risk_badge=RISK_BADGE,
        status_badge=STATUS_BADGE,
    )


@app.route("/vendors/<int:vendor_id>/edit", methods=["GET", "POST"])
def vendor_edit(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    if request.method == "POST":
        f = request.form
        vendor.vendor_name = f.get("vendor_name", vendor.vendor_name)
        vendor.vendor_category = f.get("vendor_category", vendor.vendor_category)
        vendor.business_owner = f.get("business_owner", vendor.business_owner)
        vendor.security_reviewer = f.get("security_reviewer", vendor.security_reviewer)
        vendor.department = f.get("department", vendor.department)
        vendor.service_description = f.get("service_description", vendor.service_description)
        vendor.system_supported = f.get("system_supported", vendor.system_supported)
        vendor.data_types_processed = f.get("data_types_processed", vendor.data_types_processed)
        vendor.sensitive_data = "sensitive_data" in f
        vendor.phi_involved = "phi_involved" in f
        vendor.payment_data = "payment_data" in f
        vendor.pii_involved = "pii_involved" in f
        vendor.cloud_hosted = "cloud_hosted" in f
        vendor.country_region = f.get("country_region", vendor.country_region)
        vendor.criticality = f.get("criticality", vendor.criticality)
        vendor.inherent_risk = f.get("inherent_risk", vendor.inherent_risk)
        vendor.residual_risk = f.get("residual_risk", vendor.residual_risk)
        vendor.review_status = f.get("review_status", vendor.review_status)
        vendor.approval_status = f.get("approval_status", vendor.approval_status)
        vendor.next_review_date = _parse_form_date(f.get("next_review_date"))
        vendor.notes = f.get("notes", vendor.notes)
        db.session.commit()
        flash("Vendor updated.", "success")
        return redirect(url_for("vendor_detail", vendor_id=vendor.id))
    return render_template("vendor_form.html", vendor=vendor)


# ---------------------------------------------------------------------------
# Questionnaire Reviews
# ---------------------------------------------------------------------------

@app.route("/questionnaires")
def questionnaires():
    q = request.args.get("q", "").strip()
    domain = request.args.get("domain", "")
    risk_flag = request.args.get("risk_flag", "")
    vendor_id = request.args.get("vendor_id", "")

    query = QuestionnaireReview.query.join(Vendor)
    if q:
        query = query.filter(
            QuestionnaireReview.question_text.ilike(f"%{q}%") |
            QuestionnaireReview.vendor_response.ilike(f"%{q}%") |
            Vendor.vendor_name.ilike(f"%{q}%")
        )
    if domain:
        query = query.filter(QuestionnaireReview.domain == domain)
    if risk_flag:
        query = query.filter(QuestionnaireReview.risk_flag == risk_flag)
    if vendor_id:
        query = query.filter(QuestionnaireReview.vendor_id == int(vendor_id))

    qrs = query.order_by(QuestionnaireReview.vendor_id).all()
    domains = sorted({q.domain for q in QuestionnaireReview.query.all() if q.domain})
    vendor_list = Vendor.query.order_by(Vendor.vendor_name).all()

    return render_template(
        "questionnaire.html",
        qrs=qrs,
        domains=domains,
        vendors=vendor_list,
        filters=request.args,
    )


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

@app.route("/evidence")
def evidence_list():
    q = request.args.get("q", "").strip()
    ev_status = request.args.get("ev_status", "")
    ev_type = request.args.get("ev_type", "")
    vendor_id = request.args.get("vendor_id", "")

    query = Evidence.query.join(Vendor)
    if q:
        query = query.filter(
            Evidence.evidence_name.ilike(f"%{q}%") |
            Vendor.vendor_name.ilike(f"%{q}%")
        )
    if ev_status:
        query = query.filter(Evidence.evidence_status == ev_status)
    if ev_type:
        query = query.filter(Evidence.evidence_type == ev_type)
    if vendor_id:
        query = query.filter(Evidence.vendor_id == int(vendor_id))

    ev_records = query.order_by(Evidence.vendor_id).all()
    ev_types = sorted({e.evidence_type for e in Evidence.query.all() if e.evidence_type})
    vendor_list = Vendor.query.order_by(Vendor.vendor_name).all()

    return render_template(
        "evidence.html",
        evidence=ev_records,
        ev_types=ev_types,
        vendors=vendor_list,
        filters=request.args,
    )


# ---------------------------------------------------------------------------
# Risk Assessments
# ---------------------------------------------------------------------------

@app.route("/risk-assessments")
def risk_assessments():
    ras = RiskAssessment.query.join(Vendor).order_by(
        RiskAssessment.residual_risk_score.desc()
    ).all()
    return render_template("risk_assessments.html", risk_assessments=ras)


@app.route("/risk-assessments/new", methods=["GET", "POST"])
def risk_assessment_new():
    vendors_list = Vendor.query.order_by(Vendor.vendor_name).all()
    if request.method == "POST":
        f = request.form
        ra = RiskAssessment(
            vendor_id=int(f.get("vendor_id")),
            assessment_date=_parse_form_date(f.get("assessment_date")) or date.today(),
            assessor=f.get("assessor", ""),
            inherent_likelihood=int(f.get("inherent_likelihood", 1)),
            inherent_impact=int(f.get("inherent_impact", 1)),
            key_risk_drivers=f.get("key_risk_drivers", ""),
            existing_controls=f.get("existing_controls", ""),
            control_gaps=f.get("control_gaps", ""),
            compensating_controls=f.get("compensating_controls", ""),
            residual_likelihood=int(f.get("residual_likelihood", 1)),
            residual_impact=int(f.get("residual_impact", 1)),
            risk_decision=f.get("risk_decision", ""),
            risk_owner=f.get("risk_owner", ""),
            approval_required="approval_required" in f,
            notes=f.get("notes", ""),
        )
        calculate_risk_scores(ra)
        # Sync residual risk back to vendor
        vendor = Vendor.query.get(ra.vendor_id)
        if vendor:
            vendor.residual_risk = ra.residual_risk_rating
        db.session.add(ra)
        db.session.commit()
        flash("Risk assessment saved.", "success")
        return redirect(url_for("risk_assessments"))
    return render_template("risk_assessment_form.html", vendors=vendors_list, ra=None)


# ---------------------------------------------------------------------------
# Follow-Ups
# ---------------------------------------------------------------------------

@app.route("/follow-ups")
def follow_ups():
    refresh_statuses()
    status_filter = request.args.get("status", "")
    vendor_id = request.args.get("vendor_id", "")
    q = request.args.get("q", "").strip()

    query = FollowUp.query.join(Vendor)
    if status_filter:
        query = query.filter(FollowUp.status == status_filter)
    if vendor_id:
        query = query.filter(FollowUp.vendor_id == int(vendor_id))
    if q:
        query = query.filter(FollowUp.follow_up_question.ilike(f"%{q}%"))

    fus = query.order_by(FollowUp.due_date).all()
    vendor_list = Vendor.query.order_by(Vendor.vendor_name).all()
    return render_template(
        "followups.html",
        follow_ups=fus,
        vendors=vendor_list,
        filters=request.args,
    )


# ---------------------------------------------------------------------------
# Remediation
# ---------------------------------------------------------------------------

@app.route("/remediation")
def remediation():
    status_filter = request.args.get("status", "")
    vendor_id = request.args.get("vendor_id", "")
    query = Remediation.query.join(Vendor)
    if status_filter:
        query = query.filter(Remediation.status == status_filter)
    if vendor_id:
        query = query.filter(Remediation.vendor_id == int(vendor_id))
    rems = query.order_by(Remediation.due_date).all()
    vendor_list = Vendor.query.order_by(Vendor.vendor_name).all()
    return render_template(
        "remediation.html",
        remediations=rems,
        vendors=vendor_list,
        filters=request.args,
    )


# ---------------------------------------------------------------------------
# Approvals
# ---------------------------------------------------------------------------

@app.route("/approvals")
def approvals():
    refresh_statuses()
    status_filter = request.args.get("status", "")
    query = Approval.query.join(Vendor)
    if status_filter:
        query = query.filter(Approval.approval_status == status_filter)
    aps = query.order_by(Approval.approval_date.desc()).all()
    return render_template("approvals.html", approvals=aps, filters=request.args)


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

@app.route("/reports")
def reports():
    report = build_management_report(app)
    return render_template("reports.html", report=report)


@app.route("/assessor-guide")
def assessor_guide():
    return render_template("assessor_guide.html")


@app.route("/reports/export/excel")
def export_report_excel():
    filepath = export_excel(app, export_dir=EXPORTS_DIR)
    return send_file(filepath, as_attachment=True)


@app.route("/reports/export/markdown")
def export_report_markdown():
    report = build_management_report(app)
    filepath = export_markdown_report(report, export_dir=EXPORTS_DIR)
    return send_file(filepath, as_attachment=True)


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

@app.route("/import", methods=["GET", "POST"])
def import_data():
    if request.method == "POST":
        import_type = request.form.get("import_type")
        file = request.files.get("file")
        if not file or file.filename == "":
            flash("No file selected.", "danger")
            return redirect(url_for("import_data"))

        if import_type == "vendors":
            count, errors = import_vendors_csv(file.stream)
        elif import_type == "questionnaires":
            count, errors = import_questionnaires_csv(file.stream)
        elif import_type == "evidence":
            count, errors = import_evidence_csv(file.stream)
        else:
            flash("Unknown import type.", "danger")
            return redirect(url_for("import_data"))

        if errors:
            for e in errors[:10]:
                flash(e, "warning")
        flash(f"Successfully imported {count} record(s).", "success")
        return redirect(url_for("import_data"))

    return render_template("import.html")


# ---------------------------------------------------------------------------
# Export (full Excel)
# ---------------------------------------------------------------------------

@app.route("/export")
def export_data():
    filepath = export_excel(app, export_dir=EXPORTS_DIR)
    return send_file(filepath, as_attachment=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_form_date(val):
    from datetime import datetime
    if not val or val.strip() == "":
        return None
    try:
        return datetime.strptime(val.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Auto-seed on first run
# ---------------------------------------------------------------------------

with app.app_context():
    db.create_all()
    # Seed only if the database is empty
    if Vendor.query.count() == 0:
        print("[SEED] No data found - loading seed data...")
        seed_all(app)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
