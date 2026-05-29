"""
imports.py – CSV import logic for MANDATE.
Supports importing Vendors, Questionnaire Reviews, and Evidence records.
"""

import csv
import io
from datetime import date, datetime
from database import db
from models import Vendor, QuestionnaireReview, Evidence
from calculations import auto_check_response, auto_check_evidence


def _parse_date(val):
    """Parse a date string (YYYY-MM-DD) or return None."""
    if not val or val.strip() == "":
        return None
    try:
        return datetime.strptime(val.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _bool(val):
    """Convert a string like 'True', 'Yes', '1' to bool."""
    return str(val).strip().lower() in ("true", "yes", "1", "y")


def import_vendors_csv(file_stream):
    """
    Import vendors from a CSV file stream.
    Returns (success_count, errors list).
    """
    reader = csv.DictReader(io.TextIOWrapper(file_stream, encoding="utf-8-sig"))
    success, errors = 0, []
    for i, row in enumerate(reader, start=2):
        try:
            v = Vendor(
                vendor_name=row.get("vendor_name", "").strip(),
                vendor_category=row.get("vendor_category", "").strip(),
                business_owner=row.get("business_owner", "").strip(),
                security_reviewer=row.get("security_reviewer", "").strip(),
                department=row.get("department", "").strip(),
                service_description=row.get("service_description", "").strip(),
                system_supported=row.get("system_supported", "").strip(),
                data_types_processed=row.get("data_types_processed", "").strip(),
                sensitive_data=_bool(row.get("sensitive_data", "False")),
                phi_involved=_bool(row.get("phi_involved", "False")),
                payment_data=_bool(row.get("payment_data", "False")),
                pii_involved=_bool(row.get("pii_involved", "False")),
                cloud_hosted=_bool(row.get("cloud_hosted", "False")),
                country_region=row.get("country_region", "").strip(),
                criticality=row.get("criticality", "Medium").strip(),
                inherent_risk=row.get("inherent_risk", "").strip(),
                residual_risk=row.get("residual_risk", "").strip(),
                review_status=row.get("review_status", "Not Started").strip(),
                approval_status=row.get("approval_status", "Draft").strip(),
                onboarding_date=_parse_date(row.get("onboarding_date")),
                last_review_date=_parse_date(row.get("last_review_date")),
                next_review_date=_parse_date(row.get("next_review_date")),
                notes=row.get("notes", "").strip(),
            )
            if not v.vendor_name:
                errors.append(f"Row {i}: vendor_name is required.")
                continue
            db.session.add(v)
            success += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
    db.session.commit()
    return success, errors


def import_questionnaires_csv(file_stream):
    """
    Import questionnaire reviews from CSV.
    CSV must include a vendor_id column matching an existing Vendor.id.
    Returns (success_count, errors list).
    """
    reader = csv.DictReader(io.TextIOWrapper(file_stream, encoding="utf-8-sig"))
    success, errors = 0, []
    for i, row in enumerate(reader, start=2):
        try:
            vendor_id = int(row.get("vendor_id", 0))
            vendor = Vendor.query.get(vendor_id)
            if not vendor:
                errors.append(f"Row {i}: vendor_id {vendor_id} not found.")
                continue
            qr = QuestionnaireReview(
                vendor_id=vendor_id,
                domain=row.get("domain", "").strip(),
                question_text=row.get("question_text", "").strip(),
                vendor_response=row.get("vendor_response", "").strip(),
                analyst_notes=row.get("analyst_notes", "").strip(),
                reviewer=row.get("reviewer", "").strip(),
                review_date=_parse_date(row.get("review_date")),
            )
            auto_check_response(qr)
            db.session.add(qr)
            success += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
    db.session.commit()
    return success, errors


def import_evidence_csv(file_stream):
    """
    Import evidence records from CSV.
    CSV must include a vendor_id column matching an existing Vendor.id.
    Returns (success_count, errors list).
    """
    reader = csv.DictReader(io.TextIOWrapper(file_stream, encoding="utf-8-sig"))
    success, errors = 0, []
    for i, row in enumerate(reader, start=2):
        try:
            vendor_id = int(row.get("vendor_id", 0))
            vendor = Vendor.query.get(vendor_id)
            if not vendor:
                errors.append(f"Row {i}: vendor_id {vendor_id} not found.")
                continue
            ev = Evidence(
                vendor_id=vendor_id,
                evidence_name=row.get("evidence_name", "").strip(),
                evidence_type=row.get("evidence_type", "").strip(),
                related_domain=row.get("related_domain", "").strip(),
                evidence_description=row.get("evidence_description", "").strip(),
                evidence_status=row.get("evidence_status", "Available").strip(),
                evidence_date=_parse_date(row.get("evidence_date")),
                expiration_date=_parse_date(row.get("expiration_date")),
                evidence_owner=row.get("evidence_owner", "").strip(),
                file_path_or_link=row.get("file_path_or_link", "").strip(),
                reviewer_notes=row.get("reviewer_notes", "").strip(),
            )
            auto_check_evidence(ev)
            db.session.add(ev)
            success += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
    db.session.commit()
    return success, errors
