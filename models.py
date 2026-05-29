"""
models.py – SQLAlchemy ORM models for MANDATE.

Tables:
  - Vendor
  - QuestionnaireReview
  - Evidence
  - RiskAssessment
  - FollowUp
  - Remediation
  - Approval
"""

from datetime import date, datetime
from database import db


# ---------------------------------------------------------------------------
# Vendor
# ---------------------------------------------------------------------------
class Vendor(db.Model):
    __tablename__ = "vendor"

    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(200), nullable=False)
    vendor_category = db.Column(db.String(100))
    business_owner = db.Column(db.String(100))
    security_reviewer = db.Column(db.String(100))
    department = db.Column(db.String(100))
    service_description = db.Column(db.Text)
    system_supported = db.Column(db.String(200))
    data_types_processed = db.Column(db.String(500))   # comma-separated list
    sensitive_data = db.Column(db.Boolean, default=False)
    phi_involved = db.Column(db.Boolean, default=False)
    payment_data = db.Column(db.Boolean, default=False)
    pii_involved = db.Column(db.Boolean, default=False)
    cloud_hosted = db.Column(db.Boolean, default=False)
    country_region = db.Column(db.String(100))
    criticality = db.Column(db.String(50))             # Critical / High / Medium / Low
    inherent_risk = db.Column(db.String(50))
    residual_risk = db.Column(db.String(50))
    review_status = db.Column(db.String(100), default="Not Started")
    approval_status = db.Column(db.String(100), default="Draft")
    onboarding_date = db.Column(db.Date)
    last_review_date = db.Column(db.Date)
    next_review_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    # relationships
    questionnaire_reviews = db.relationship(
        "QuestionnaireReview", back_populates="vendor", cascade="all, delete-orphan"
    )
    evidence_records = db.relationship(
        "Evidence", back_populates="vendor", cascade="all, delete-orphan"
    )
    risk_assessments = db.relationship(
        "RiskAssessment", back_populates="vendor", cascade="all, delete-orphan"
    )
    follow_ups = db.relationship(
        "FollowUp", back_populates="vendor", cascade="all, delete-orphan"
    )
    remediations = db.relationship(
        "Remediation", back_populates="vendor", cascade="all, delete-orphan"
    )
    approvals = db.relationship(
        "Approval", back_populates="vendor", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Vendor {self.vendor_name}>"


# ---------------------------------------------------------------------------
# Questionnaire Review
# ---------------------------------------------------------------------------
class QuestionnaireReview(db.Model):
    __tablename__ = "questionnaire_review"

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    domain = db.Column(db.String(100))
    question_text = db.Column(db.Text)
    vendor_response = db.Column(db.Text)
    response_quality = db.Column(db.String(50))  # Acceptable / Incomplete / Vague / Missing / High Risk …
    risk_flag = db.Column(db.String(50), default="None")  # None / Low / Medium / High / Critical
    analyst_notes = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_question = db.Column(db.Text)
    reviewer = db.Column(db.String(100))
    review_date = db.Column(db.Date)

    vendor = db.relationship("Vendor", back_populates="questionnaire_reviews")

    def __repr__(self):
        return f"<QR vendor={self.vendor_id} domain={self.domain}>"


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------
class Evidence(db.Model):
    __tablename__ = "evidence"

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    evidence_name = db.Column(db.String(200))
    evidence_type = db.Column(db.String(100))
    related_domain = db.Column(db.String(100))
    evidence_description = db.Column(db.Text)
    evidence_status = db.Column(db.String(50), default="Available")
    evidence_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    evidence_owner = db.Column(db.String(100))
    file_path_or_link = db.Column(db.String(500))
    reviewer_notes = db.Column(db.Text)
    validity_status = db.Column(db.String(50), default="Valid")

    vendor = db.relationship("Vendor", back_populates="evidence_records")

    def __repr__(self):
        return f"<Evidence {self.evidence_name}>"


# ---------------------------------------------------------------------------
# Risk Assessment
# ---------------------------------------------------------------------------
class RiskAssessment(db.Model):
    __tablename__ = "risk_assessment"

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    assessment_date = db.Column(db.Date)
    assessor = db.Column(db.String(100))

    # Inherent risk
    inherent_likelihood = db.Column(db.Integer, default=1)  # 1–5
    inherent_impact = db.Column(db.Integer, default=1)      # 1–5
    inherent_risk_score = db.Column(db.Integer)             # likelihood × impact
    inherent_risk_rating = db.Column(db.String(50))         # Low / Medium / High / Critical

    key_risk_drivers = db.Column(db.Text)  # comma-separated
    existing_controls = db.Column(db.Text)
    control_gaps = db.Column(db.Text)
    compensating_controls = db.Column(db.Text)

    # Residual risk
    residual_likelihood = db.Column(db.Integer, default=1)
    residual_impact = db.Column(db.Integer, default=1)
    residual_risk_score = db.Column(db.Integer)
    residual_risk_rating = db.Column(db.String(50))

    risk_decision = db.Column(db.String(100))  # Approve / Reject / …
    risk_owner = db.Column(db.String(100))
    approval_required = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

    vendor = db.relationship("Vendor", back_populates="risk_assessments")
    remediations = db.relationship(
        "Remediation", back_populates="risk_assessment", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<RiskAssessment vendor={self.vendor_id} rating={self.residual_risk_rating}>"


# ---------------------------------------------------------------------------
# Follow-Up
# ---------------------------------------------------------------------------
class FollowUp(db.Model):
    __tablename__ = "follow_up"

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    related_question_id = db.Column(db.Integer, db.ForeignKey("questionnaire_review.id"))
    related_evidence_id = db.Column(db.Integer, db.ForeignKey("evidence.id"))
    follow_up_question = db.Column(db.Text)
    requested_from = db.Column(db.String(100))
    owner = db.Column(db.String(100))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Open")
    vendor_response = db.Column(db.Text)
    analyst_notes = db.Column(db.Text)
    closure_date = db.Column(db.Date)

    vendor = db.relationship("Vendor", back_populates="follow_ups")

    def __repr__(self):
        return f"<FollowUp vendor={self.vendor_id} status={self.status}>"


# ---------------------------------------------------------------------------
# Remediation / Conditions
# ---------------------------------------------------------------------------
class Remediation(db.Model):
    __tablename__ = "remediation"

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    risk_assessment_id = db.Column(db.Integer, db.ForeignKey("risk_assessment.id"))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    required_action = db.Column(db.Text)
    owner = db.Column(db.String(100))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Open")
    validation_method = db.Column(db.String(200))
    closure_evidence = db.Column(db.String(500))
    closure_notes = db.Column(db.Text)

    vendor = db.relationship("Vendor", back_populates="remediations")
    risk_assessment = db.relationship("RiskAssessment", back_populates="remediations")

    def __repr__(self):
        return f"<Remediation {self.title}>"


# ---------------------------------------------------------------------------
# Approval / Exception
# ---------------------------------------------------------------------------
class Approval(db.Model):
    __tablename__ = "approval"

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    risk_decision = db.Column(db.String(100))
    exception_required = db.Column(db.Boolean, default=False)
    exception_reason = db.Column(db.Text)
    business_justification = db.Column(db.Text)
    compensating_controls = db.Column(db.Text)
    risk_acceptance_owner = db.Column(db.String(100))
    approval_status = db.Column(db.String(100), default="Draft")
    approval_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    review_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    vendor = db.relationship("Vendor", back_populates="approvals")

    def __repr__(self):
        return f"<Approval vendor={self.vendor_id} status={self.approval_status}>"
