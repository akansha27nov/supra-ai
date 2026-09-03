# agent/compliance_rules.py

from pydantic import BaseModel, Field

class CompliancePolicyConfig(BaseModel):
    """Structured policy configuration object ensuring repeatability against a defined standard."""
    default_lead_ppm_threshold: float = Field(
        default=1000.0, 
        description="Default maximum allowable lead concentration in ppm."
    )
    known_accreditation_prefixes: tuple[str, ...] = Field(
        default=("DAKKS-", "CNAS-", "DAT-P-", "UKAS-", "ANAB-", "A2LA-"),
        description="Accepted accreditation body prefix identifiers."
    )
    deprecated_safety_standards: tuple[str, ...] = Field(
        default=("EN 60950", "EN 60065", "EN 55020"),
        description="Withdrawn or obsolete safety standards."
    )
    deprecated_rohs_standards: tuple[str, ...] = Field(
        default=("EN 50581",),
        description="Withdrawn or obsolete RoHS standards."
    )
    known_statutory_thresholds: tuple[float, ...] = Field(
        default=(100.0, 1000.0),
        description="Valid statutory limit numbers under RoHS Annex II."
    )
    accreditation_fraud_markers: tuple[str, ...] = Field(
        default=("FAKE", "UNRECOGNIZED", "UNVERIFIED", "TEST-ONLY", "PLACEHOLDER"),
        description="Explicit placeholder or fraudulent accreditation keywords."
    )
    max_issue_age_days: int = Field(
        default=730,
        description="Maximum baseline age for document issue dates (2 years)."
    )
    expiry_warning_window_days: int = Field(
        default=30,
        description="Window in days to flag certificates expiring soon."
    )

# Instantiate the active policy configuration
ACTIVE_POLICY = CompliancePolicyConfig()

# Expose constants for graph/rule engine consumption
DEFAULT_LEAD_PPM_THRESHOLD = ACTIVE_POLICY.default_lead_ppm_threshold
KNOWN_ACCREDITATION_PREFIXES = ACTIVE_POLICY.known_accreditation_prefixes
DEPRECATED_SAFETY_STANDARDS = ACTIVE_POLICY.deprecated_safety_standards
DEPRECATED_ROHS_STANDARDS = ACTIVE_POLICY.deprecated_rohs_standards
KNOWN_STATUTORY_THRESHOLDS = ACTIVE_POLICY.known_statutory_thresholds
ACCREDITATION_FRAUD_MARKERS = ACTIVE_POLICY.accreditation_fraud_markers