"""
seed_data.py – Realistic fictional sample data for MANDATE.

Run via: flask seed  (or directly: python seed_data.py)

15 vendors · 75 questionnaire responses · 30 evidence records ·
12 risk assessments · 20 follow-ups · 8 remediations · 6 approvals
"""

from datetime import date, timedelta
from database import db
from models import (
    Vendor, QuestionnaireReview, Evidence,
    RiskAssessment, FollowUp, Remediation, Approval,
)
from calculations import (
    auto_check_response, auto_check_evidence, calculate_risk_scores,
    mark_overdue_followups, mark_expired_approvals,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def d(year, month, day):
    return date(year, month, day)


# ---------------------------------------------------------------------------
# VENDORS
# ---------------------------------------------------------------------------

VENDORS = [
    dict(
        vendor_name="HealthBridge Analytics",
        vendor_category="Healthcare Data Processor",
        business_owner="Dr. Lisa Nguyen",
        security_reviewer="James Okafor",
        department="Clinical Informatics",
        service_description="Processes de-identified and identifiable patient analytics data for population health reporting.",
        system_supported="PopHealth BI Platform",
        data_types_processed="PHI, PII, Clinical Records",
        sensitive_data=True, phi_involved=True, payment_data=False, pii_involved=True,
        cloud_hosted=True, country_region="United States",
        criticality="Critical",
        inherent_risk="High", residual_risk="High",
        review_status="Pending Risk Decision",
        approval_status="Pending Approval",
        onboarding_date=d(2023, 3, 1), last_review_date=d(2024, 11, 15), next_review_date=d(2025, 11, 15),
        notes="Missing current SOC 2 report. HITRUST evidence expired.",
    ),
    dict(
        vendor_name="PayFlow Gateway",
        vendor_category="Payment Processor",
        business_owner="Marcus Webb",
        security_reviewer="Sarah Lin",
        department="Finance",
        service_description="Processes credit card and ACH payments for e-commerce platform.",
        system_supported="Checkout & Billing System",
        data_types_processed="Payment Data, Cardholder Data, PII",
        sensitive_data=True, phi_involved=False, payment_data=True, pii_involved=True,
        cloud_hosted=True, country_region="United States",
        criticality="Critical",
        inherent_risk="High", residual_risk="Medium",
        review_status="Approved",
        approval_status="Approved",
        onboarding_date=d(2022, 6, 15), last_review_date=d(2025, 1, 10), next_review_date=d(2026, 1, 10),
        notes="PCI DSS Level 1 certified. Annual review completed.",
    ),
    dict(
        vendor_name="SecureID Connect",
        vendor_category="Security Tool",
        business_owner="Angela Reyes",
        security_reviewer="James Okafor",
        department="IT Security",
        service_description="Provides SSO, MFA, and identity federation for enterprise applications.",
        system_supported="Identity and Access Management",
        data_types_processed="Authentication Logs, Employee Data, PII",
        sensitive_data=True, phi_involved=False, payment_data=False, pii_involved=True,
        cloud_hosted=True, country_region="United States",
        criticality="High",
        inherent_risk="High", residual_risk="Low",
        review_status="Approved",
        approval_status="Approved",
        onboarding_date=d(2021, 9, 1), last_review_date=d(2025, 2, 20), next_review_date=d(2026, 2, 20),
        notes="SOC 2 Type II current. ISO 27001 certified.",
    ),
    dict(
        vendor_name="CloudDesk Support",
        vendor_category="Customer Support Platform",
        business_owner="Tom Harrington",
        security_reviewer="Sarah Lin",
        department="Customer Success",
        service_description="Customer ticketing and support platform with chat, email, and phone channels.",
        system_supported="Support Ticketing System",
        data_types_processed="PII, Internal Confidential",
        sensitive_data=True, phi_involved=False, payment_data=False, pii_involved=True,
        cloud_hosted=True, country_region="Ireland",
        criticality="Medium",
        inherent_risk="Medium", residual_risk="Low",
        review_status="Approved",
        approval_status="Approved",
        onboarding_date=d(2022, 1, 20), last_review_date=d(2025, 3, 5), next_review_date=d(2026, 3, 5),
        notes="GDPR DPA in place. Privacy review completed.",
    ),
    dict(
        vendor_name="PeopleCore HR",
        vendor_category="HR Platform",
        business_owner="Kim Peterson",
        security_reviewer="James Okafor",
        department="Human Resources",
        service_description="Human capital management: payroll, benefits, onboarding, and employee data.",
        system_supported="HRIS Platform",
        data_types_processed="Employee Data, PII, Payment Data",
        sensitive_data=True, phi_involved=False, payment_data=True, pii_involved=True,
        cloud_hosted=True, country_region="United States",
        criticality="High",
        inherent_risk="High", residual_risk="Medium",
        review_status="Approved with Conditions",
        approval_status="Approved with Exception",
        onboarding_date=d(2020, 8, 10), last_review_date=d(2024, 12, 1), next_review_date=d(2025, 12, 1),
        notes="Admin MFA enforcement gap identified. Compensating control accepted.",
    ),
    dict(
        vendor_name="LogStream Security",
        vendor_category="Security Tool",
        business_owner="Angela Reyes",
        security_reviewer="Sarah Lin",
        department="IT Security",
        service_description="SIEM and log aggregation platform for security event monitoring.",
        system_supported="SIEM / Log Management",
        data_types_processed="Security Event Logs, Authentication Logs",
        sensitive_data=True, phi_involved=False, payment_data=False, pii_involved=False,
        cloud_hosted=False, country_region="United States",
        criticality="High",
        inherent_risk="Medium", residual_risk="Low",
        review_status="Approved",
        approval_status="Approved",
        onboarding_date=d(2021, 5, 1), last_review_date=d(2025, 1, 15), next_review_date=d(2026, 1, 15),
        notes="On-premise deployment. Annual security review completed.",
    ),
    dict(
        vendor_name="DataLake Insights",
        vendor_category="Analytics Platform",
        business_owner="Priya Sharma",
        security_reviewer="James Okafor",
        department="Data & Analytics",
        service_description="Cloud-based data lake for business intelligence and advanced analytics workloads.",
        system_supported="Data Lake / BI Platform",
        data_types_processed="PII, Internal Confidential, Employee Data",
        sensitive_data=True, phi_involved=False, payment_data=False, pii_involved=True,
        cloud_hosted=True, country_region="United States",
        criticality="High",
        inherent_risk="High", residual_risk="Medium",
        review_status="In Review",
        approval_status="Pending Approval",
        onboarding_date=d(2023, 7, 1), last_review_date=d(2025, 4, 10), next_review_date=d(2026, 4, 10),
        notes="Encryption evidence vague. Penetration test outdated.",
    ),
    dict(
        vendor_name="MedForms Processor",
        vendor_category="Healthcare Data Processor",
        business_owner="Dr. Lisa Nguyen",
        security_reviewer="James Okafor",
        department="Clinical Operations",
        service_description="Processes patient intake forms, prior authorization, and referral documents.",
        system_supported="Patient Intake & Referral System",
        data_types_processed="PHI, PII, Clinical Records",
        sensitive_data=True, phi_involved=True, payment_data=False, pii_involved=True,
        cloud_hosted=True, country_region="United States",
        criticality="Critical",
        inherent_risk="Critical", residual_risk="High",
        review_status="Pending Evidence",
        approval_status="Pending Approval",
        onboarding_date=d(2024, 2, 1), last_review_date=d(2025, 2, 1), next_review_date=d(2025, 8, 1),
        notes="No current SOC 2. No HITRUST. No signed BAA on file.",
    ),
    dict(
        vendor_name="VendorShield Platform",
        vendor_category="SaaS Application",
        business_owner="Marcus Webb",
        security_reviewer="Sarah Lin",
        department="Procurement",
        service_description="Third-party risk management and contract repository platform.",
        system_supported="Vendor Risk Management System",
        data_types_processed="Internal Confidential",
        sensitive_data=False, phi_involved=False, payment_data=False, pii_involved=False,
        cloud_hosted=True, country_region="United States",
        criticality="Medium",
        inherent_risk="Low", residual_risk="Low",
        review_status="Approved",
        approval_status="Approved",
        onboarding_date=d(2022, 4, 1), last_review_date=d(2025, 4, 1), next_review_date=d(2026, 4, 1),
        notes="Low risk. SOC 2 Type II available.",
    ),
    dict(
        vendor_name="FinanceSync API",
        vendor_category="SaaS Application",
        business_owner="Tom Harrington",
        security_reviewer="James Okafor",
        department="Finance",
        service_description="Financial data aggregation and reporting API connecting to banking and ERP systems.",
        system_supported="Finance Reporting Platform",
        data_types_processed="Payment Data, Internal Confidential",
        sensitive_data=True, phi_involved=False, payment_data=True, pii_involved=False,
        cloud_hosted=True, country_region="United Kingdom",
        criticality="High",
        inherent_risk="High", residual_risk="Medium",
        review_status="In Review",
        approval_status="Draft",
        onboarding_date=d(2024, 9, 1), last_review_date=d(2025, 3, 20), next_review_date=d(2026, 3, 20),
        notes="Cross-border data transfer (UK). PCI evidence incomplete.",
    ),
    dict(
        vendor_name="TicketOps Cloud",
        vendor_category="SaaS Application",
        business_owner="Kim Peterson",
        security_reviewer="Sarah Lin",
        department="IT Operations",
        service_description="IT service management and ticketing platform for internal helpdesk.",
        system_supported="ITSM Platform",
        data_types_processed="Employee Data, Internal Confidential",
        sensitive_data=False, phi_involved=False, payment_data=False, pii_involved=False,
        cloud_hosted=True, country_region="United States",
        criticality="Low",
        inherent_risk="Low", residual_risk="Low",
        review_status="Approved",
        approval_status="Approved",
        onboarding_date=d(2021, 3, 1), last_review_date=d(2025, 3, 1), next_review_date=d(2026, 3, 1),
        notes="Low criticality. Standard review completed.",
    ),
    dict(
        vendor_name="AuthLayer SSO",
        vendor_category="Security Tool",
        business_owner="Angela Reyes",
        security_reviewer="James Okafor",
        department="IT Security",
        service_description="Single sign-on and adaptive MFA provider for enterprise workforce.",
        system_supported="Identity Platform",
        data_types_processed="Authentication Logs, PII",
        sensitive_data=True, phi_involved=False, payment_data=False, pii_involved=True,
        cloud_hosted=True, country_region="United States",
        criticality="High",
        inherent_risk="High", residual_risk="Low",
        review_status="Approved",
        approval_status="Approved",
        onboarding_date=d(2022, 11, 1), last_review_date=d(2025, 2, 10), next_review_date=d(2026, 2, 10),
        notes="SOC 2 Type II current. Strong MFA controls.",
    ),
    dict(
        vendor_name="BackupVault Cloud",
        vendor_category="Cloud Service Provider",
        business_owner="Priya Sharma",
        security_reviewer="Sarah Lin",
        department="IT Infrastructure",
        service_description="Cloud-based backup and disaster recovery for on-premise and cloud workloads.",
        system_supported="Backup and DR Platform",
        data_types_processed="Internal Confidential, Employee Data",
        sensitive_data=True, phi_involved=False, payment_data=False, pii_involved=False,
        cloud_hosted=True, country_region="United States",
        criticality="High",
        inherent_risk="Medium", residual_risk="Low",
        review_status="Approved",
        approval_status="Approved",
        onboarding_date=d(2021, 7, 1), last_review_date=d(2025, 1, 1), next_review_date=d(2026, 1, 1),
        notes="BCP and DR plan validated. Encryption at rest confirmed.",
    ),
    dict(
        vendor_name="MetricsPulse Analytics",
        vendor_category="Analytics Platform",
        business_owner="Tom Harrington",
        security_reviewer="James Okafor",
        department="Marketing",
        service_description="Marketing analytics and customer behavior tracking platform.",
        system_supported="Marketing Analytics Platform",
        data_types_processed="PII, Internal Confidential",
        sensitive_data=True, phi_involved=False, payment_data=False, pii_involved=True,
        cloud_hosted=True, country_region="United States",
        criticality="Medium",
        inherent_risk="Medium", residual_risk="Low",
        review_status="Approved",
        approval_status="Approved",
        onboarding_date=d(2023, 1, 1), last_review_date=d(2025, 1, 5), next_review_date=d(2026, 1, 5),
        notes="Privacy review complete. Cookie consent mechanism validated.",
    ),
    dict(
        vendor_name="DocuSafe Storage",
        vendor_category="Cloud Service Provider",
        business_owner="Marcus Webb",
        security_reviewer="Sarah Lin",
        department="Legal",
        service_description="Secure cloud document storage, e-signature, and legal document management.",
        system_supported="Document Management System",
        data_types_processed="Internal Confidential, PII",
        sensitive_data=True, phi_involved=False, payment_data=False, pii_involved=True,
        cloud_hosted=True, country_region="United States",
        criticality="Medium",
        inherent_risk="Medium", residual_risk="Low",
        review_status="Approved",
        approval_status="Approved",
        onboarding_date=d(2020, 12, 1), last_review_date=d(2025, 2, 28), next_review_date=d(2026, 2, 28),
        notes="SOC 2 Type II on file. Encryption at rest and in transit confirmed.",
    ),
]


# ---------------------------------------------------------------------------
# QUESTIONNAIRE RESPONSES  (5 per vendor × 15 = 75)
# ---------------------------------------------------------------------------
# Format: (domain, question_text, vendor_response, analyst_notes)

QR_TEMPLATE = [
    # --- HealthBridge Analytics
    ("Access Management",
     "Describe your role-based access control (RBAC) implementation.",
     "We implement RBAC based on job function. Access reviews are conducted annually.",
     ""),
    ("Authentication and MFA",
     "Is MFA enforced for all administrator accounts?",
     "MFA is enforced for most accounts. Some legacy admin accounts do not currently require MFA.",
     "Legacy accounts without MFA – flag for follow-up."),
    ("Encryption at Rest",
     "Describe encryption controls for data at rest.",
     "We use industry standard encryption for data at rest.",
     "Vague – no algorithm or key management detail provided."),
    ("Compliance Certifications",
     "Provide your current SOC 2 Type II report or certification status.",
     "Our SOC 2 report is currently being renewed. We can provide the previous report upon request.",
     "Previous report expired. No current SOC 2 available."),
    ("Data Handling and Privacy",
     "How do you handle PHI and ensure HIPAA compliance?",
     "We follow HIPAA best practices and have internal policies in place.",
     "No HITRUST or BAA evidence provided. High risk for PHI vendor."),

    # --- PayFlow Gateway
    ("Compliance Certifications",
     "Provide evidence of PCI DSS compliance.",
     "PayFlow Gateway is a PCI DSS Level 1 Service Provider. Our current AOC and SAQ are available upon request.",
     "PCI Level 1 confirmed. Evidence received."),
    ("Encryption in Transit",
     "Describe TLS/encryption controls for data in transit.",
     "All data in transit uses TLS 1.2 or higher. TLS 1.0/1.1 are disabled.",
     "Acceptable."),
    ("Incident Response",
     "Do you have a formal incident response plan?",
     "Yes. We maintain a documented incident response plan tested quarterly via tabletop exercises.",
     "Strong IR posture."),
    ("Access Management",
     "How is privileged access managed for production systems?",
     "Privileged access is managed via PAM tooling with just-in-time access and MFA required.",
     "Good control."),
    ("Logging and Monitoring",
     "Describe your security event logging and monitoring capability.",
     "We use a SIEM platform with 24/7 SOC monitoring. Logs are retained for 12 months.",
     "Acceptable."),

    # --- SecureID Connect
    ("Authentication and MFA",
     "Is MFA enforced for all user and admin accounts?",
     "Yes. MFA is enforced globally. We do not permit password-only authentication.",
     "Strong MFA posture."),
    ("Access Management",
     "How do you manage user provisioning and de-provisioning?",
     "User lifecycle is automated via SCIM integration. De-provisioning happens within 2 hours of termination.",
     "Excellent."),
    ("Logging and Monitoring",
     "Describe your audit logging for authentication events.",
     "All authentication events are logged, including failed attempts. Logs are tamper-evident.",
     "Acceptable."),
    ("Compliance Certifications",
     "Provide current SOC 2 Type II and ISO 27001 status.",
     "SOC 2 Type II completed in Q1 2025. ISO 27001 certified through 2027.",
     "Both certifications current."),
    ("Encryption at Rest",
     "Describe encryption controls for stored credential data.",
     "All credential data is hashed using bcrypt with salting. Key material is stored in HSMs.",
     "Acceptable."),

    # --- CloudDesk Support
    ("Data Handling and Privacy",
     "How do you handle PII in support tickets and chat logs?",
     "PII is masked in ticket views after 90 days. Data is retained per GDPR requirements.",
     "Acceptable with DPA in place."),
    ("Encryption in Transit",
     "Describe encryption controls for data in transit.",
     "We use TLS 1.3 for all data in transit. Older protocol versions are disabled.",
     "Acceptable."),
    ("Subprocessor Management",
     "Do you use subprocessors? Provide a current subprocessor list.",
     "Yes. We use subprocessors for cloud hosting and email. Our subprocessor list is available on our website.",
     "Subprocessor list referenced. Verify it is current."),
    ("Business Continuity and Disaster Recovery",
     "Describe your BCP and DR testing cadence.",
     "We test our DR plan annually. Last test was conducted in October 2024.",
     "Acceptable."),
    ("Incident Response",
     "How quickly do you notify customers in the event of a data breach?",
     "We notify affected customers within 72 hours per GDPR requirements.",
     "Acceptable."),

    # --- PeopleCore HR
    ("Authentication and MFA",
     "Is MFA enforced for all administrator accounts accessing employee data?",
     "MFA is enforced for end users. Some administrator accounts do not currently enforce MFA due to legacy system constraints.",
     "Admin MFA gap – critical finding for HR platform with PII and payment data."),
    ("Data Retention and Deletion",
     "Describe your data deletion process for terminated employee records.",
     "Employee records are retained for 7 years per legal requirements, then deleted upon request.",
     "Acceptable. Verify data deletion SLA."),
    ("Encryption at Rest",
     "Describe encryption of employee PII and payroll data.",
     "Payroll data is encrypted at rest using AES-256.",
     "Acceptable."),
    ("Incident Response",
     "Provide your incident response plan or summary.",
     "We have a documented IR plan. We can provide a summary upon request.",
     "Summary not yet received. Follow-up needed."),
    ("Compliance Certifications",
     "Provide SOC 2 Type II or equivalent certification.",
     "SOC 2 Type II report available. Last audit completed September 2024.",
     "Acceptable. SOC 2 received."),

    # --- LogStream Security
    ("Logging and Monitoring",
     "Describe log collection, retention, and alerting capabilities.",
     "We collect logs from 500+ sources. Retention is configurable up to 5 years. Real-time alerting is available.",
     "Strong logging platform."),
    ("Access Management",
     "How is administrative access to the SIEM platform controlled?",
     "Admin access requires MFA and is limited to the security team. Role separation is enforced.",
     "Acceptable."),
    ("Vulnerability Management",
     "Describe your vulnerability scanning and patching cadence.",
     "Weekly automated scans using a commercial scanner. Critical patches applied within 7 days.",
     "Acceptable."),
    ("Incident Response",
     "Do you provide incident response capabilities or tooling?",
     "Yes. The platform includes playbook automation and integration with ticketing systems.",
     "Acceptable."),
    ("Business Continuity and Disaster Recovery",
     "Describe your HA and failover architecture for on-premise deployments.",
     "LogStream is deployed in active-passive HA. Failover time is under 15 minutes.",
     "Acceptable."),

    # --- DataLake Insights
    ("Encryption at Rest",
     "Describe encryption of data stored in the data lake.",
     "We use encryption as needed based on data classification.",
     "Vague. No algorithm specified. No key management details."),
    ("Access Management",
     "How is access to sensitive data sets controlled?",
     "Access is managed by data owners on a best effort basis.",
     "Vague. 'Best effort' is not an acceptable access control statement."),
    ("Vulnerability Management",
     "When was your last penetration test conducted?",
     "Our last penetration test was conducted in Q3 2022.",
     "Outdated – over 2 years ago. Follow-up required."),
    ("Data Handling and Privacy",
     "How is PII segregated and protected within the data lake?",
     "PII is handled in accordance with our data classification policy.",
     "Vague. No technical controls described."),
    ("Logging and Monitoring",
     "Describe audit logging for data access events.",
     "Audit logging is enabled for most data access operations.",
     "Incomplete. 'Most' is not sufficient for PII data sets."),

    # --- MedForms Processor
    ("Compliance Certifications",
     "Provide your current SOC 2 Type II or HITRUST certification.",
     "We do not currently hold a SOC 2 Type II or HITRUST certification. We plan to pursue SOC 2 in 2026.",
     "Critical gap. Vendor handles PHI with no SOC 2 or HITRUST."),
    ("Data Handling and Privacy",
     "How do you ensure HIPAA compliance for PHI processing?",
     "We follow HIPAA best practices and train staff annually.",
     "No BAA signed. No formal HIPAA evidence. High risk."),
    ("Encryption at Rest",
     "How is PHI encrypted at rest?",
     "PHI is encrypted using industry standard methods.",
     "Vague. No specific algorithm or key management provided."),
    ("Incident Response",
     "Do you have a formal incident response plan for PHI breaches?",
     "We do not have a formal documented incident response plan at this time.",
     "Critical. No IR plan for a PHI processor."),
    ("Business Continuity and Disaster Recovery",
     "Describe your backup and recovery capability for PHI systems.",
     "We perform daily backups. Recovery has not been formally tested.",
     "No formal BCP/DR testing. Concern for PHI availability."),

    # --- VendorShield Platform
    ("Access Management",
     "How is access managed for vendor data stored on the platform?",
     "Access is role-based. Each customer's data is logically isolated.",
     "Acceptable."),
    ("Compliance Certifications",
     "Provide SOC 2 Type II status.",
     "SOC 2 Type II report available from our most recent audit, completed February 2025.",
     "Current SOC 2. Acceptable."),
    ("Encryption in Transit",
     "Describe TLS controls for data in transit.",
     "All data uses TLS 1.2+. HTTPS enforced across all endpoints.",
     "Acceptable."),
    ("Incident Response",
     "Do you have an incident response plan?",
     "Yes. Our IR plan is documented and reviewed annually.",
     "Acceptable."),
    ("Data Retention and Deletion",
     "How is vendor data deleted upon contract termination?",
     "Customer data is deleted within 30 days of contract termination and a deletion certificate is issued.",
     "Acceptable."),

    # --- FinanceSync API
    ("Compliance Certifications",
     "Provide PCI DSS compliance evidence for financial data handling.",
     "We are in the process of completing our PCI SAQ. We do not yet hold a formal PCI DSS certification.",
     "PCI evidence incomplete for a payment data vendor."),
    ("Encryption at Rest",
     "Describe encryption of financial data at rest.",
     "Financial data is encrypted using AES-256.",
     "Acceptable."),
    ("Access Management",
     "How is API access managed and controlled?",
     "API access uses OAuth 2.0 and API keys with IP allowlisting.",
     "Acceptable."),
    ("Data Handling and Privacy",
     "How is financial data handled for UK-based customers under UK GDPR?",
     "We are reviewing our UK GDPR obligations. Data processing agreements are pending update.",
     "Cross-border data transfer risk. DPA not current."),
    ("Logging and Monitoring",
     "Describe API audit logging and anomaly detection.",
     "API calls are logged. We do not currently have automated anomaly detection in place.",
     "Anomaly detection gap. Flag for follow-up."),

    # --- TicketOps Cloud
    ("Access Management",
     "Describe user access controls for the helpdesk platform.",
     "RBAC is implemented. Access is provisioned by IT administrators.",
     "Acceptable."),
    ("Incident Response",
     "Do you have an incident response process?",
     "Yes. We have a standard incident response process documented internally.",
     "Acceptable."),
    ("Data Retention and Deletion",
     "How long are helpdesk tickets retained?",
     "Tickets are retained for 3 years and then purged automatically.",
     "Acceptable."),
    ("Encryption in Transit",
     "Describe TLS controls.",
     "TLS 1.2+ enforced. Certificate management automated.",
     "Acceptable."),
    ("Compliance Certifications",
     "Provide SOC 2 or ISO 27001 status.",
     "We hold a SOC 2 Type I report. SOC 2 Type II is planned for 2025.",
     "Type I only. Note for record."),

    # --- AuthLayer SSO
    ("Authentication and MFA",
     "Describe your MFA enforcement capabilities.",
     "We support TOTP, FIDO2, push notification, and hardware token MFA. MFA is enforced by default.",
     "Excellent."),
    ("Access Management",
     "How is privileged admin access to the identity platform managed?",
     "PAM tool with session recording. Admin access requires MFA and break-glass procedures.",
     "Strong control."),
    ("Logging and Monitoring",
     "Describe audit logging for authentication and admin events.",
     "All auth and admin events are logged with tamper-evident audit trail. Logs exported to SIEM.",
     "Acceptable."),
    ("Compliance Certifications",
     "Provide SOC 2 Type II status.",
     "SOC 2 Type II completed March 2025. Report available under NDA.",
     "Current. Acceptable."),
    ("Incident Response",
     "How do you handle identity-related security incidents?",
     "Dedicated security team with 24/7 paging. Identity incidents trigger automated lockdown and notification.",
     "Strong IR posture."),

    # --- BackupVault Cloud
    ("Business Continuity and Disaster Recovery",
     "Describe your backup encryption and recovery testing.",
     "Backups are encrypted with AES-256. Recovery testing is performed monthly.",
     "Acceptable."),
    ("Encryption at Rest",
     "How are backed-up data sets encrypted?",
     "All backup data encrypted at rest using AES-256 with customer-managed keys available.",
     "Acceptable."),
    ("Access Management",
     "Who can access stored backup data?",
     "Access is restricted to authorized administrators. MFA required for management console.",
     "Acceptable."),
    ("Incident Response",
     "Describe incident response for data loss scenarios.",
     "We have a documented IR and data recovery playbook tested semi-annually.",
     "Acceptable."),
    ("Compliance Certifications",
     "Provide SOC 2 Type II status.",
     "SOC 2 Type II report available. Last audit completed November 2024.",
     "Current. Acceptable."),

    # --- MetricsPulse Analytics
    ("Data Handling and Privacy",
     "How is PII collected and processed in analytics pipelines?",
     "PII is pseudonymized at collection. Raw PII is not retained beyond 30 days.",
     "Acceptable."),
    ("Compliance Certifications",
     "Provide SOC 2 or GDPR compliance evidence.",
     "SOC 2 Type II completed January 2025. GDPR DPA available.",
     "Current. Acceptable."),
    ("Encryption at Rest",
     "Describe encryption of analytics data at rest.",
     "Analytics data encrypted using AES-256 in our cloud environment.",
     "Acceptable."),
    ("Access Management",
     "How is access to analytics dashboards and data controlled?",
     "SSO enforced. RBAC applied at dataset level. Audit log maintained.",
     "Acceptable."),
    ("Data Retention and Deletion",
     "Describe data retention and deletion policies.",
     "Data retained per customer contract. Deletion executed within 30 days of request.",
     "Acceptable."),

    # --- DocuSafe Storage
    ("Encryption at Rest",
     "Describe document encryption at rest.",
     "All documents encrypted at rest using AES-256. Key management via AWS KMS.",
     "Acceptable."),
    ("Access Management",
     "How is access to stored documents controlled?",
     "Access controlled by document owner. Folder-level permissions. MFA required for login.",
     "Acceptable."),
    ("Compliance Certifications",
     "Provide SOC 2 Type II status.",
     "SOC 2 Type II report available. Last audit completed December 2024.",
     "Current. Acceptable."),
    ("Data Retention and Deletion",
     "How are documents deleted upon request or contract end?",
     "Documents deleted within 14 days of request. Deletion confirmation provided.",
     "Acceptable."),
    ("Incident Response",
     "Do you have an incident response plan covering data exposure?",
     "Yes. IR plan reviewed annually and tabletop exercise conducted in Q4 2024.",
     "Acceptable."),
]


# ---------------------------------------------------------------------------
# EVIDENCE RECORDS  (30 records)
# ---------------------------------------------------------------------------

EVIDENCE_RECORDS = [
    # HealthBridge Analytics (vendor idx 0)
    dict(vendor_idx=0, evidence_name="HealthBridge SOC 2 Type II – EXPIRED",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="Previous SOC 2 Type II report. Renewal in progress.",
         evidence_status="Expired", evidence_date=d(2023, 6, 1), expiration_date=d(2024, 6, 1),
         evidence_owner="HealthBridge Compliance Team",
         reviewer_notes="Expired. New report not yet available."),
    dict(vendor_idx=0, evidence_name="HealthBridge HITRUST Certificate – EXPIRED",
         evidence_type="ISO 27001 Certificate", related_domain="Compliance Certifications",
         evidence_description="HITRUST CSF certificate issued 2022.",
         evidence_status="Expired", evidence_date=d(2022, 3, 1), expiration_date=d(2024, 3, 1),
         evidence_owner="HealthBridge Compliance Team",
         reviewer_notes="Expired over 12 months ago."),

    # PayFlow Gateway (vendor idx 1)
    dict(vendor_idx=1, evidence_name="PayFlow PCI DSS AOC 2025",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="PCI DSS Level 1 Attestation of Compliance, valid through December 2025.",
         evidence_status="Available", evidence_date=d(2025, 1, 10), expiration_date=d(2025, 12, 31),
         evidence_owner="PayFlow Security Team",
         reviewer_notes="Current and valid."),
    dict(vendor_idx=1, evidence_name="PayFlow Penetration Test 2024",
         evidence_type="Penetration Test Summary", related_domain="Vulnerability Management",
         evidence_description="Annual penetration test by a QSA-approved firm. No critical findings.",
         evidence_status="Available", evidence_date=d(2024, 11, 1), expiration_date=d(2025, 11, 1),
         evidence_owner="PayFlow Security Team",
         reviewer_notes="Current. No critical findings noted."),

    # SecureID Connect (vendor idx 2)
    dict(vendor_idx=2, evidence_name="SecureID SOC 2 Type II 2025",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="SOC 2 Type II covering Security, Availability, and Confidentiality.",
         evidence_status="Available", evidence_date=d(2025, 2, 1), expiration_date=d(2026, 2, 1),
         evidence_owner="SecureID Compliance",
         reviewer_notes="Current and valid."),
    dict(vendor_idx=2, evidence_name="SecureID ISO 27001 Certificate",
         evidence_type="ISO 27001 Certificate", related_domain="Compliance Certifications",
         evidence_description="ISO/IEC 27001:2022 certification valid through 2027.",
         evidence_status="Available", evidence_date=d(2024, 6, 1), expiration_date=d(2027, 6, 1),
         evidence_owner="SecureID Compliance",
         reviewer_notes="Current."),

    # CloudDesk Support (vendor idx 3)
    dict(vendor_idx=3, evidence_name="CloudDesk Data Processing Agreement",
         evidence_type="Data Processing Agreement", related_domain="Data Handling and Privacy",
         evidence_description="GDPR-compliant DPA executed between CloudDesk and our organization.",
         evidence_status="Available", evidence_date=d(2023, 1, 20), expiration_date=None,
         evidence_owner="Legal Department",
         reviewer_notes="Executed. Review for renewal annually."),
    dict(vendor_idx=3, evidence_name="CloudDesk SOC 2 Type II 2024",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="SOC 2 Type II report for cloud support platform.",
         evidence_status="Available", evidence_date=d(2024, 9, 1), expiration_date=d(2025, 9, 1),
         evidence_owner="CloudDesk Security",
         reviewer_notes="Current."),

    # PeopleCore HR (vendor idx 4)
    dict(vendor_idx=4, evidence_name="PeopleCore SOC 2 Type II Sept 2024",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="SOC 2 Type II report with noted exception on legacy admin MFA.",
         evidence_status="Available", evidence_date=d(2024, 9, 15), expiration_date=d(2025, 9, 15),
         evidence_owner="PeopleCore Compliance",
         reviewer_notes="Exception noted on admin MFA. Follow-up required."),
    dict(vendor_idx=4, evidence_name="PeopleCore Encryption Policy",
         evidence_type="Encryption Policy", related_domain="Encryption at Rest",
         evidence_description="Policy covering AES-256 encryption for payroll and PII data.",
         evidence_status="Available", evidence_date=d(2024, 3, 1), expiration_date=None,
         evidence_owner="PeopleCore CISO",
         reviewer_notes="Acceptable."),

    # DataLake Insights (vendor idx 6)
    dict(vendor_idx=6, evidence_name="DataLake Penetration Test – OUTDATED",
         evidence_type="Penetration Test Summary", related_domain="Vulnerability Management",
         evidence_description="Penetration test completed Q3 2022. No current test on file.",
         evidence_status="Outdated", evidence_date=d(2022, 8, 1), expiration_date=d(2023, 8, 1),
         evidence_owner="DataLake Security",
         reviewer_notes="Over 2 years old. New test required."),
    dict(vendor_idx=6, evidence_name="DataLake Encryption Policy – Missing",
         evidence_type="Encryption Policy", related_domain="Encryption at Rest",
         evidence_description="No encryption policy document received from vendor.",
         evidence_status="Missing", evidence_date=None, expiration_date=None,
         evidence_owner="DataLake CISO",
         reviewer_notes="Requested. Not yet provided."),

    # MedForms Processor (vendor idx 7)
    dict(vendor_idx=7, evidence_name="MedForms SOC 2 – MISSING",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="No SOC 2 report available. Vendor acknowledged gap.",
         evidence_status="Missing", evidence_date=None, expiration_date=None,
         evidence_owner="MedForms Compliance",
         reviewer_notes="Critical gap for PHI processor."),
    dict(vendor_idx=7, evidence_name="MedForms BAA – MISSING",
         evidence_type="Data Processing Agreement", related_domain="Data Handling and Privacy",
         evidence_description="Business Associate Agreement not yet executed.",
         evidence_status="Missing", evidence_date=None, expiration_date=None,
         evidence_owner="Legal Department",
         reviewer_notes="Must be executed before PHI processing begins."),
    dict(vendor_idx=7, evidence_name="MedForms Incident Response Plan – MISSING",
         evidence_type="Incident Response Plan", related_domain="Incident Response",
         evidence_description="Vendor confirmed no formal IR plan exists.",
         evidence_status="Missing", evidence_date=None, expiration_date=None,
         evidence_owner="MedForms Security",
         reviewer_notes="Critical. Escalation required."),

    # VendorShield Platform (vendor idx 8)
    dict(vendor_idx=8, evidence_name="VendorShield SOC 2 Type II Feb 2025",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="Current SOC 2 Type II with no noted exceptions.",
         evidence_status="Available", evidence_date=d(2025, 2, 1), expiration_date=d(2026, 2, 1),
         evidence_owner="VendorShield Compliance",
         reviewer_notes="Current."),

    # FinanceSync API (vendor idx 9)
    dict(vendor_idx=9, evidence_name="FinanceSync PCI SAQ – INCOMPLETE",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="PCI SAQ in progress. Not yet completed or submitted.",
         evidence_status="Incomplete", evidence_date=None, expiration_date=None,
         evidence_owner="FinanceSync Compliance",
         reviewer_notes="PCI evidence required for payment data vendor."),

    # AuthLayer SSO (vendor idx 11)
    dict(vendor_idx=11, evidence_name="AuthLayer SOC 2 Type II Mar 2025",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="SOC 2 Type II covering Security and Availability.",
         evidence_status="Available", evidence_date=d(2025, 3, 1), expiration_date=d(2026, 3, 1),
         evidence_owner="AuthLayer Compliance",
         reviewer_notes="Current."),

    # BackupVault Cloud (vendor idx 12)
    dict(vendor_idx=12, evidence_name="BackupVault SOC 2 Type II Nov 2024",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="SOC 2 Type II for cloud backup and DR services.",
         evidence_status="Available", evidence_date=d(2024, 11, 1), expiration_date=d(2025, 11, 1),
         evidence_owner="BackupVault Compliance",
         reviewer_notes="Current."),
    dict(vendor_idx=12, evidence_name="BackupVault BCP/DR Plan",
         evidence_type="Business Continuity Plan", related_domain="Business Continuity and Disaster Recovery",
         evidence_description="Documented BCP and DR plan with monthly recovery testing results.",
         evidence_status="Available", evidence_date=d(2025, 1, 1), expiration_date=None,
         evidence_owner="BackupVault Operations",
         reviewer_notes="Acceptable."),

    # MetricsPulse Analytics (vendor idx 13)
    dict(vendor_idx=13, evidence_name="MetricsPulse SOC 2 Type II Jan 2025",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="SOC 2 Type II covering Security and Confidentiality.",
         evidence_status="Available", evidence_date=d(2025, 1, 10), expiration_date=d(2026, 1, 10),
         evidence_owner="MetricsPulse Compliance",
         reviewer_notes="Current."),

    # DocuSafe Storage (vendor idx 14)
    dict(vendor_idx=14, evidence_name="DocuSafe SOC 2 Type II Dec 2024",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="SOC 2 Type II covering Security and Confidentiality trust service criteria.",
         evidence_status="Available", evidence_date=d(2024, 12, 1), expiration_date=d(2025, 12, 1),
         evidence_owner="DocuSafe Compliance",
         reviewer_notes="Current."),
    dict(vendor_idx=14, evidence_name="DocuSafe Encryption Policy",
         evidence_type="Encryption Policy", related_domain="Encryption at Rest",
         evidence_description="Encryption policy confirming AES-256 at rest and TLS in transit.",
         evidence_status="Available", evidence_date=d(2024, 8, 1), expiration_date=None,
         evidence_owner="DocuSafe CISO",
         reviewer_notes="Acceptable."),

    # LogStream Security (vendor idx 5)
    dict(vendor_idx=5, evidence_name="LogStream Vulnerability Scan Report Q1 2025",
         evidence_type="Vulnerability Scan Report", related_domain="Vulnerability Management",
         evidence_description="Quarterly vulnerability scan report. No critical open findings.",
         evidence_status="Available", evidence_date=d(2025, 3, 1), expiration_date=d(2025, 9, 1),
         evidence_owner="LogStream Security",
         reviewer_notes="Current."),
    dict(vendor_idx=5, evidence_name="LogStream Information Security Policy",
         evidence_type="Information Security Policy", related_domain="Access Management",
         evidence_description="Comprehensive IS policy covering access, encryption, logging, and IR.",
         evidence_status="Available", evidence_date=d(2024, 6, 1), expiration_date=None,
         evidence_owner="LogStream CISO",
         reviewer_notes="Acceptable."),

    # TicketOps Cloud (vendor idx 10)
    dict(vendor_idx=10, evidence_name="TicketOps SOC 2 Type I 2024",
         evidence_type="SOC 2 Type II Report", related_domain="Compliance Certifications",
         evidence_description="SOC 2 Type I report. Type II audit planned for 2025.",
         evidence_status="Available", evidence_date=d(2024, 6, 1), expiration_date=d(2025, 6, 1),
         evidence_owner="TicketOps Compliance",
         reviewer_notes="Type I only. Note for record."),
]


# ---------------------------------------------------------------------------
# RISK ASSESSMENTS (12)
# ---------------------------------------------------------------------------

RISK_ASSESSMENTS = [
    dict(vendor_idx=0, assessment_date=d(2025, 4, 15), assessor="James Okafor",
         inherent_likelihood=5, inherent_impact=5,
         key_risk_drivers="Handles PHI, Missing SOC 2, Missing HITRUST, Missing BAA, No formal IR plan",
         existing_controls="Annual HIPAA training, internal policies",
         control_gaps="No current SOC 2, No HITRUST, No signed BAA, Admin MFA gap",
         compensating_controls="",
         residual_likelihood=4, residual_impact=5,
         risk_decision="Request More Evidence", risk_owner="Dr. Lisa Nguyen",
         approval_required=True,
         notes="Vendor must provide current SOC 2 or HITRUST and signed BAA before approval."),

    dict(vendor_idx=1, assessment_date=d(2025, 1, 15), assessor="Sarah Lin",
         inherent_likelihood=4, inherent_impact=5,
         key_risk_drivers="Handles payment data, Cardholder data, PCI in scope",
         existing_controls="PCI DSS Level 1, Annual pentest, PAM for privileged access",
         control_gaps="None identified",
         compensating_controls="",
         residual_likelihood=2, residual_impact=4,
         risk_decision="Approve", risk_owner="Marcus Webb",
         approval_required=False,
         notes="Strong PCI posture. Approved."),

    dict(vendor_idx=2, assessment_date=d(2025, 2, 25), assessor="James Okafor",
         inherent_likelihood=3, inherent_impact=4,
         key_risk_drivers="Identity platform, Handles authentication logs and PII",
         existing_controls="SOC 2 Type II, ISO 27001, MFA enforced, PAM, SCIM automation",
         control_gaps="None identified",
         compensating_controls="",
         residual_likelihood=1, residual_impact=3,
         risk_decision="Approve", risk_owner="Angela Reyes",
         approval_required=False,
         notes="Strong identity security posture. Approved."),

    dict(vendor_idx=4, assessment_date=d(2024, 12, 5), assessor="James Okafor",
         inherent_likelihood=4, inherent_impact=4,
         key_risk_drivers="Handles employee PII and payroll, Admin MFA gap",
         existing_controls="SOC 2 Type II, AES-256 encryption, RBAC",
         control_gaps="Legacy admin accounts without MFA enforcement",
         compensating_controls="Admin IP allowlisting, enhanced audit logging, quarterly access review",
         residual_likelihood=2, residual_impact=4,
         risk_decision="Approve with Conditions", risk_owner="Kim Peterson",
         approval_required=True,
         notes="Approved with condition: vendor must enforce MFA on all admin accounts within 90 days."),

    dict(vendor_idx=6, assessment_date=d(2025, 4, 12), assessor="James Okafor",
         inherent_likelihood=4, inherent_impact=4,
         key_risk_drivers="Handles PII, Vague encryption controls, Outdated penetration test",
         existing_controls="RBAC, internal policies",
         control_gaps="Outdated pentest, No encryption policy, Vague access control description",
         compensating_controls="",
         residual_likelihood=3, residual_impact=4,
         risk_decision="Request More Evidence", risk_owner="Priya Sharma",
         approval_required=True,
         notes="Pending updated pentest and encryption evidence."),

    dict(vendor_idx=7, assessment_date=d(2025, 2, 10), assessor="James Okafor",
         inherent_likelihood=5, inherent_impact=5,
         key_risk_drivers="Handles PHI, No SOC 2, No HITRUST, No BAA, No IR plan, No DR testing",
         existing_controls="Annual training, internal policies (unvalidated)",
         control_gaps="SOC 2, HITRUST, BAA, IR plan, DR testing all missing",
         compensating_controls="None acceptable at this time",
         residual_likelihood=5, residual_impact=5,
         risk_decision="Require Remediation", risk_owner="Dr. Lisa Nguyen",
         approval_required=True,
         notes="Do not approve until critical evidence gaps are resolved."),

    dict(vendor_idx=9, assessment_date=d(2025, 3, 25), assessor="James Okafor",
         inherent_likelihood=4, inherent_impact=4,
         key_risk_drivers="Handles payment data, PCI evidence incomplete, Cross-border transfer (UK)",
         existing_controls="AES-256 encryption, OAuth 2.0 API access",
         control_gaps="PCI SAQ incomplete, UK GDPR DPA not updated, No anomaly detection",
         compensating_controls="IP allowlisting, manual monitoring",
         residual_likelihood=3, residual_impact=4,
         risk_decision="Request More Evidence", risk_owner="Tom Harrington",
         approval_required=True,
         notes="Pending PCI SAQ completion and UK GDPR DPA update."),

    dict(vendor_idx=3, assessment_date=d(2025, 3, 10), assessor="Sarah Lin",
         inherent_likelihood=3, inherent_impact=3,
         key_risk_drivers="Handles PII, GDPR obligations, Cross-border (Ireland)",
         existing_controls="SOC 2 Type II, DPA executed, TLS 1.3, GDPR 72-hour breach notification",
         control_gaps="Subprocessor list currency unverified",
         compensating_controls="",
         residual_likelihood=1, residual_impact=3,
         risk_decision="Approve", risk_owner="Tom Harrington",
         approval_required=False,
         notes="Approved. Verify subprocessor list at next review."),

    dict(vendor_idx=5, assessment_date=d(2025, 1, 20), assessor="Sarah Lin",
         inherent_likelihood=3, inherent_impact=3,
         key_risk_drivers="On-premise SIEM, access to security logs",
         existing_controls="MFA for admin, RBAC, weekly vuln scans, HA deployment",
         control_gaps="None identified",
         compensating_controls="",
         residual_likelihood=1, residual_impact=3,
         risk_decision="Approve", risk_owner="Angela Reyes",
         approval_required=False,
         notes="Approved."),

    dict(vendor_idx=11, assessment_date=d(2025, 2, 15), assessor="James Okafor",
         inherent_likelihood=3, inherent_impact=4,
         key_risk_drivers="Identity platform, Handles PII",
         existing_controls="SOC 2 Type II, MFA by default, FIDO2, PAM, SIEM integration",
         control_gaps="None identified",
         compensating_controls="",
         residual_likelihood=1, residual_impact=3,
         risk_decision="Approve", risk_owner="Angela Reyes",
         approval_required=False,
         notes="Approved."),

    dict(vendor_idx=12, assessment_date=d(2025, 1, 5), assessor="Sarah Lin",
         inherent_likelihood=3, inherent_impact=4,
         key_risk_drivers="Cloud backup with sensitive data, data availability risk",
         existing_controls="SOC 2 Type II, AES-256, monthly DR testing, MFA",
         control_gaps="None identified",
         compensating_controls="",
         residual_likelihood=1, residual_impact=3,
         risk_decision="Approve", risk_owner="Priya Sharma",
         approval_required=False,
         notes="Approved."),

    dict(vendor_idx=13, assessment_date=d(2025, 1, 10), assessor="Sarah Lin",
         inherent_likelihood=3, inherent_impact=3,
         key_risk_drivers="Handles PII, marketing analytics, pseudonymization",
         existing_controls="SOC 2 Type II, pseudonymization, SSO, RBAC, GDPR DPA",
         control_gaps="None identified",
         compensating_controls="",
         residual_likelihood=1, residual_impact=2,
         risk_decision="Approve", risk_owner="Tom Harrington",
         approval_required=False,
         notes="Approved."),
]


# ---------------------------------------------------------------------------
# FOLLOW-UPS (20)
# ---------------------------------------------------------------------------

FOLLOW_UPS = [
    # HealthBridge Analytics
    dict(vendor_idx=0, follow_up_question="Provide your current SOC 2 Type II report or evidence of renewal status.",
         requested_from="HealthBridge Analytics", owner="James Okafor",
         due_date=d(2025, 3, 1), status="Overdue", vendor_response="", analyst_notes="No response received."),
    dict(vendor_idx=0, follow_up_question="Confirm whether a BAA has been executed and provide a signed copy.",
         requested_from="HealthBridge Analytics", owner="James Okafor",
         due_date=d(2025, 3, 15), status="Overdue", vendor_response="", analyst_notes="Critical."),
    dict(vendor_idx=0, follow_up_question="Provide specific encryption algorithm and key management details for PHI at rest.",
         requested_from="HealthBridge Analytics", owner="James Okafor",
         due_date=d(2025, 4, 1), status="Sent to Vendor", vendor_response="", analyst_notes=""),

    # PayFlow Gateway
    dict(vendor_idx=1, follow_up_question="Confirm QSA name and scope for the most recent PCI DSS assessment.",
         requested_from="PayFlow Gateway", owner="Sarah Lin",
         due_date=d(2025, 2, 1), status="Closed",
         vendor_response="Assessed by Trustwave. Full scope includes card processing and storage environments.",
         analyst_notes="Confirmed. Closed."),

    # PeopleCore HR
    dict(vendor_idx=4, follow_up_question="Provide a remediation timeline for enforcing MFA on all legacy admin accounts.",
         requested_from="PeopleCore HR", owner="James Okafor",
         due_date=d(2025, 3, 1), status="Vendor Responded",
         vendor_response="MFA rollout for legacy admin accounts planned by Q2 2025.",
         analyst_notes="Pending validation."),
    dict(vendor_idx=4, follow_up_question="Provide a copy of your current Incident Response Plan.",
         requested_from="PeopleCore HR", owner="James Okafor",
         due_date=d(2025, 2, 15), status="Overdue", vendor_response="", analyst_notes="No response."),

    # DataLake Insights
    dict(vendor_idx=6, follow_up_question="Provide an updated penetration test report (current year).",
         requested_from="DataLake Insights", owner="James Okafor",
         due_date=d(2025, 4, 30), status="Open", vendor_response="", analyst_notes=""),
    dict(vendor_idx=6, follow_up_question="Provide your Encryption Policy document covering data lake storage.",
         requested_from="DataLake Insights", owner="James Okafor",
         due_date=d(2025, 4, 15), status="Overdue", vendor_response="", analyst_notes="No response received."),
    dict(vendor_idx=6, follow_up_question="Describe specific access control mechanisms for sensitive PII datasets.",
         requested_from="DataLake Insights", owner="James Okafor",
         due_date=d(2025, 5, 1), status="Open", vendor_response="", analyst_notes=""),

    # MedForms Processor
    dict(vendor_idx=7, follow_up_question="Provide SOC 2 Type II or HITRUST certificate or roadmap to certification.",
         requested_from="MedForms Processor", owner="James Okafor",
         due_date=d(2025, 3, 1), status="Overdue", vendor_response="", analyst_notes="Critical gap."),
    dict(vendor_idx=7, follow_up_question="Execute and return the Business Associate Agreement.",
         requested_from="MedForms Processor", owner="James Okafor",
         due_date=d(2025, 2, 15), status="Overdue", vendor_response="", analyst_notes="Must be resolved before any PHI processing."),
    dict(vendor_idx=7, follow_up_question="Provide your formal Incident Response Plan or confirm it is being developed.",
         requested_from="MedForms Processor", owner="James Okafor",
         due_date=d(2025, 3, 30), status="Sent to Vendor", vendor_response="", analyst_notes=""),

    # FinanceSync API
    dict(vendor_idx=9, follow_up_question="Provide completed PCI SAQ or evidence of PCI DSS certification.",
         requested_from="FinanceSync API", owner="James Okafor",
         due_date=d(2025, 4, 30), status="Open", vendor_response="", analyst_notes=""),
    dict(vendor_idx=9, follow_up_question="Provide updated UK GDPR Data Processing Agreement.",
         requested_from="FinanceSync API", owner="James Okafor",
         due_date=d(2025, 5, 15), status="Open", vendor_response="", analyst_notes=""),
    dict(vendor_idx=9, follow_up_question="Describe anomaly detection capability or remediation plan.",
         requested_from="FinanceSync API", owner="James Okafor",
         due_date=d(2025, 4, 15), status="Overdue", vendor_response="", analyst_notes=""),

    # CloudDesk Support
    dict(vendor_idx=3, follow_up_question="Provide current subprocessor list with effective date.",
         requested_from="CloudDesk Support", owner="Sarah Lin",
         due_date=d(2025, 4, 1), status="Vendor Responded",
         vendor_response="Subprocessor list updated March 2025 posted at our trust portal.",
         analyst_notes="Verified current."),

    # SecureID Connect
    dict(vendor_idx=2, follow_up_question="Confirm whether ISO 27001 scope includes cloud-hosted identity services.",
         requested_from="SecureID Connect", owner="James Okafor",
         due_date=d(2025, 3, 1), status="Closed",
         vendor_response="ISO 27001 scope includes all cloud-hosted services including identity federation.",
         analyst_notes="Confirmed. Closed."),

    # AuthLayer SSO
    dict(vendor_idx=11, follow_up_question="Provide SOC 2 report under NDA. Confirm process.",
         requested_from="AuthLayer SSO", owner="James Okafor",
         due_date=d(2025, 3, 15), status="Closed",
         vendor_response="NDA executed. SOC 2 report shared via secure portal.",
         analyst_notes="Received and reviewed."),

    # BackupVault Cloud
    dict(vendor_idx=12, follow_up_question="Confirm customer-managed key option is available for our backup environment.",
         requested_from="BackupVault Cloud", owner="Sarah Lin",
         due_date=d(2025, 2, 1), status="Closed",
         vendor_response="BYOK is available. Configuration guide provided.",
         analyst_notes="Confirmed."),

    # MetricsPulse Analytics
    dict(vendor_idx=13, follow_up_question="Confirm pseudonymization approach meets GDPR Article 25 requirements.",
         requested_from="MetricsPulse Analytics", owner="Sarah Lin",
         due_date=d(2025, 2, 15), status="Closed",
         vendor_response="Pseudonymization uses tokenization with separate key storage. Legal review confirms GDPR compliance.",
         analyst_notes="Acceptable."),
]


# ---------------------------------------------------------------------------
# REMEDIATIONS (8)
# ---------------------------------------------------------------------------

REMEDIATIONS = [
    dict(vendor_idx=0, ra_idx=0,
         title="Obtain Current SOC 2 Type II Report",
         description="HealthBridge SOC 2 report is expired. Current report is required before approval.",
         required_action="Vendor must provide SOC 2 Type II report dated within the past 12 months.",
         owner="James Okafor", due_date=d(2025, 6, 1), status="Open",
         validation_method="Review report and verify scope and period",
         closure_evidence="", closure_notes=""),
    dict(vendor_idx=0, ra_idx=0,
         title="Execute Business Associate Agreement",
         description="No BAA on file for a vendor processing PHI.",
         required_action="Legal to execute BAA with HealthBridge Analytics.",
         owner="Legal Department", due_date=d(2025, 5, 1), status="Open",
         validation_method="Signed BAA received and filed",
         closure_evidence="", closure_notes=""),
    dict(vendor_idx=4, ra_idx=3,
         title="Enforce MFA on All Administrator Accounts",
         description="PeopleCore HR confirmed legacy admin accounts lack MFA. Must be remediated.",
         required_action="Vendor to enforce MFA on all administrator accounts including legacy systems.",
         owner="Kim Peterson", due_date=d(2025, 6, 30), status="In Progress",
         validation_method="Vendor provides MFA enforcement confirmation and evidence",
         closure_evidence="", closure_notes="MFA rollout in progress per vendor."),
    dict(vendor_idx=6, ra_idx=4,
         title="Provide Updated Penetration Test Report",
         description="DataLake Insights pentest is over 2 years old. Current test required.",
         required_action="Vendor must conduct and share a current penetration test (within 12 months).",
         owner="James Okafor", due_date=d(2025, 7, 1), status="Pending Evidence",
         validation_method="Review pentest report scope, findings, and remediation status",
         closure_evidence="", closure_notes="Vendor confirmed pentest scheduled for Q2 2025."),
    dict(vendor_idx=7, ra_idx=5,
         title="Develop and Document Incident Response Plan",
         description="MedForms has no formal IR plan. Required for PHI processor.",
         required_action="Vendor to develop and provide documented IR plan covering PHI breach scenarios.",
         owner="James Okafor", due_date=d(2025, 5, 31), status="Open",
         validation_method="Review IR plan for completeness against NIST IR framework",
         closure_evidence="", closure_notes=""),
    dict(vendor_idx=7, ra_idx=5,
         title="Obtain SOC 2 or HITRUST Certification",
         description="No compliance certification for vendor handling PHI.",
         required_action="Vendor must provide SOC 2 Type II or HITRUST CSF certificate.",
         owner="James Okafor", due_date=d(2025, 12, 31), status="Open",
         validation_method="Receive and review current certification",
         closure_evidence="", closure_notes="Vendor targeting 2026 per questionnaire."),
    dict(vendor_idx=9, ra_idx=6,
         title="Complete PCI SAQ Submission",
         description="FinanceSync PCI SAQ is in progress. Must be completed before approval.",
         required_action="Vendor to complete and provide PCI SAQ or AOC.",
         owner="James Okafor", due_date=d(2025, 6, 30), status="Pending Evidence",
         validation_method="Review SAQ or AOC for scope and findings",
         closure_evidence="", closure_notes=""),
    dict(vendor_idx=9, ra_idx=6,
         title="Update UK GDPR Data Processing Agreement",
         description="UK GDPR DPA is not current. Cross-border data transfer requires updated DPA.",
         required_action="Legal to update DPA to include UK GDPR Standard Contractual Clauses.",
         owner="Legal Department", due_date=d(2025, 5, 31), status="Open",
         validation_method="Executed DPA with UK SCCs on file",
         closure_evidence="", closure_notes=""),
]


# ---------------------------------------------------------------------------
# APPROVALS / EXCEPTIONS (6)
# ---------------------------------------------------------------------------

APPROVALS = [
    dict(vendor_idx=1, risk_decision="Approve", exception_required=False,
         exception_reason="", business_justification="PCI DSS Level 1 certified payment processor.",
         compensating_controls="",
         risk_acceptance_owner="Marcus Webb", approval_status="Approved",
         approval_date=d(2025, 1, 20), expiration_date=d(2026, 1, 20), review_date=d(2026, 1, 1),
         notes="Annual review required."),
    dict(vendor_idx=2, risk_decision="Approve", exception_required=False,
         exception_reason="", business_justification="SOC 2 Type II and ISO 27001 current.",
         compensating_controls="",
         risk_acceptance_owner="Angela Reyes", approval_status="Approved",
         approval_date=d(2025, 2, 28), expiration_date=d(2026, 2, 28), review_date=d(2026, 2, 1),
         notes=""),
    dict(vendor_idx=4, risk_decision="Approve with Conditions", exception_required=True,
         exception_reason="Admin MFA gap on legacy systems accepted with compensating controls.",
         business_justification="Critical HR system. Vendor committed to MFA rollout by Q2 2025.",
         compensating_controls="IP allowlisting, enhanced audit logging, quarterly privileged access review",
         risk_acceptance_owner="Kim Peterson", approval_status="Approved with Exception",
         approval_date=d(2024, 12, 20), expiration_date=d(2025, 9, 30), review_date=d(2025, 6, 30),
         notes="Exception expires September 2025. MFA must be enforced before renewal."),
    dict(vendor_idx=3, risk_decision="Approve", exception_required=False,
         exception_reason="", business_justification="GDPR DPA executed. SOC 2 current.",
         compensating_controls="",
         risk_acceptance_owner="Tom Harrington", approval_status="Approved",
         approval_date=d(2025, 3, 15), expiration_date=d(2026, 3, 15), review_date=d(2026, 3, 1),
         notes=""),
    dict(vendor_idx=7, risk_decision="Require Remediation", exception_required=False,
         exception_reason="", business_justification="",
         compensating_controls="",
         risk_acceptance_owner="Dr. Lisa Nguyen", approval_status="Rejected",
         approval_date=d(2025, 2, 15), expiration_date=None, review_date=d(2025, 6, 1),
         notes="Not approved. Vendor must resolve SOC 2, BAA, and IR plan gaps before resubmission."),
    dict(vendor_idx=0, risk_decision="Request More Evidence", exception_required=False,
         exception_reason="", business_justification="",
         compensating_controls="",
         risk_acceptance_owner="James Okafor", approval_status="Pending Approval",
         approval_date=None, expiration_date=None, review_date=d(2025, 6, 15),
         notes="Pending SOC 2 renewal and BAA execution."),
]


# ---------------------------------------------------------------------------
# MAIN SEED FUNCTION
# ---------------------------------------------------------------------------

def seed_all(app):
    """
    Drop all rows and re-insert sample data.
    Called from app.py via `flask seed` command or on first run.
    """
    with app.app_context():
        # Clear existing data (order matters due to FK constraints)
        Approval.query.delete()
        Remediation.query.delete()
        FollowUp.query.delete()
        RiskAssessment.query.delete()
        Evidence.query.delete()
        QuestionnaireReview.query.delete()
        Vendor.query.delete()
        db.session.commit()

        # ---- Vendors ----
        vendor_objs = []
        for v in VENDORS:
            obj = Vendor(**v)
            db.session.add(obj)
            vendor_objs.append(obj)
        db.session.flush()  # get IDs

        # ---- Questionnaire Reviews ----
        # 5 questions per vendor in order
        for i, vendor in enumerate(vendor_objs):
            start = i * 5
            for domain, question_text, vendor_response, analyst_notes in QR_TEMPLATE[start:start + 5]:
                qr = QuestionnaireReview(
                    vendor_id=vendor.id,
                    domain=domain,
                    question_text=question_text,
                    vendor_response=vendor_response,
                    analyst_notes=analyst_notes,
                    reviewer="James Okafor" if i % 2 == 0 else "Sarah Lin",
                    review_date=date(2025, 4, 1),
                )
                auto_check_response(qr)
                db.session.add(qr)

        # ---- Evidence ----
        ev_objs = []
        for e in EVIDENCE_RECORDS:
            vendor_obj = vendor_objs[e["vendor_idx"]]
            ev = Evidence(
                vendor_id=vendor_obj.id,
                evidence_name=e["evidence_name"],
                evidence_type=e["evidence_type"],
                related_domain=e["related_domain"],
                evidence_description=e["evidence_description"],
                evidence_status=e["evidence_status"],
                evidence_date=e.get("evidence_date"),
                expiration_date=e.get("expiration_date"),
                evidence_owner=e["evidence_owner"],
                reviewer_notes=e["reviewer_notes"],
            )
            auto_check_evidence(ev)
            db.session.add(ev)
            ev_objs.append(ev)
        db.session.flush()

        # ---- Risk Assessments ----
        ra_objs = []
        for ra in RISK_ASSESSMENTS:
            vendor_obj = vendor_objs[ra["vendor_idx"]]
            obj = RiskAssessment(
                vendor_id=vendor_obj.id,
                assessment_date=ra["assessment_date"],
                assessor=ra["assessor"],
                inherent_likelihood=ra["inherent_likelihood"],
                inherent_impact=ra["inherent_impact"],
                key_risk_drivers=ra["key_risk_drivers"],
                existing_controls=ra["existing_controls"],
                control_gaps=ra["control_gaps"],
                compensating_controls=ra.get("compensating_controls", ""),
                residual_likelihood=ra["residual_likelihood"],
                residual_impact=ra["residual_impact"],
                risk_decision=ra["risk_decision"],
                risk_owner=ra["risk_owner"],
                approval_required=ra["approval_required"],
                notes=ra["notes"],
            )
            calculate_risk_scores(obj)
            db.session.add(obj)
            ra_objs.append(obj)
        db.session.flush()

        # ---- Follow-Ups ----
        fu_objs_list = []
        for fu in FOLLOW_UPS:
            vendor_obj = vendor_objs[fu["vendor_idx"]]
            obj = FollowUp(
                vendor_id=vendor_obj.id,
                follow_up_question=fu["follow_up_question"],
                requested_from=fu["requested_from"],
                owner=fu["owner"],
                due_date=fu["due_date"],
                status=fu["status"],
                vendor_response=fu.get("vendor_response", ""),
                analyst_notes=fu.get("analyst_notes", ""),
            )
            fu_objs_list.append(obj)
            db.session.add(obj)

        mark_overdue_followups(fu_objs_list)

        # ---- Remediations ----
        ra_index_map = {r["vendor_idx"]: ra_objs[i] for i, r in enumerate(RISK_ASSESSMENTS)}
        for rem in REMEDIATIONS:
            vendor_obj = vendor_objs[rem["vendor_idx"]]
            ra_obj = ra_objs[rem["ra_idx"]] if rem["ra_idx"] < len(ra_objs) else None
            obj = Remediation(
                vendor_id=vendor_obj.id,
                risk_assessment_id=ra_obj.id if ra_obj else None,
                title=rem["title"],
                description=rem["description"],
                required_action=rem["required_action"],
                owner=rem["owner"],
                due_date=rem["due_date"],
                status=rem["status"],
                validation_method=rem["validation_method"],
                closure_evidence=rem["closure_evidence"],
                closure_notes=rem["closure_notes"],
            )
            db.session.add(obj)

        # ---- Approvals ----
        ap_objs = []
        for ap in APPROVALS:
            vendor_obj = vendor_objs[ap["vendor_idx"]]
            obj = Approval(
                vendor_id=vendor_obj.id,
                risk_decision=ap["risk_decision"],
                exception_required=ap["exception_required"],
                exception_reason=ap["exception_reason"],
                business_justification=ap["business_justification"],
                compensating_controls=ap["compensating_controls"],
                risk_acceptance_owner=ap["risk_acceptance_owner"],
                approval_status=ap["approval_status"],
                approval_date=ap.get("approval_date"),
                expiration_date=ap.get("expiration_date"),
                review_date=ap.get("review_date"),
                notes=ap["notes"],
            )
            ap_objs.append(obj)
            db.session.add(obj)

        mark_expired_approvals(ap_objs)
        db.session.commit()
        print("[SUCCESS] Seed data loaded successfully.")
