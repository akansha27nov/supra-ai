# agent/schemas.py
from datetime import datetime, timezone
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

FieldStatusType = Literal["present", "absent_expected", "absent_appropriate", "ambiguous"]


# ==========================================
# 1. Document Classifier Schema
# ==========================================

class DocumentClassification(BaseModel):
    """Output model for the document classification node."""
    doc_type: Literal["lab_test_report", "manufacturer_self_declaration", "unknown"] = Field(
        ...,
        description="Type of document: official lab test report, manufacturer self-declaration, or unknown."
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="LLM confidence score for the classification."
    )

# ==========================================
# 2. Structured LLM Extraction Schema
# ==========================================

class ExtractedCertificateData(BaseModel):
    """Structured extraction target model for raw certificate PDF text."""
    sku_code: Optional[str] = Field(
        default=None,
        description="Product SKU identifier code found on the certificate (e.g., SKU-ELE-002)."
    )
    issue_date: Optional[str] = Field(
        default=None,
        description="Date document was issued in YYYY-MM-DD format."
    )
    expiration_date: Optional[str] = Field(
        default=None,
        description="Date document expires in YYYY-MM-DD format."
    )
    accreditation_id: Optional[str] = Field(
        default=None,
        description="Testing laboratory accreditation identifier (e.g., DAKKS-12345, CNAS-L0001)."
    )
    standards_tested: List[str] = Field(
        default_factory=list,
        description="List of compliance standards or directives cited."
    )
    tested_lead_ppm: Optional[float] = Field(
        default=None,
        description="Measured lead concentration value in parts per million (ppm)."
    )
    is_statutory_limit: bool = Field(
        default=False,
        description="Set to True ONLY if tested_lead_ppm is a legal limit/threshold, NOT a measured lab value."
    )

    @field_validator("issue_date", "expiration_date", mode="before")
    @classmethod
    def sanitize_date_strings(cls, v: Optional[str]) -> Optional[str]:
        if not v or str(v).lower() in ["n/a", "none", "null", "unknown", "undefined"]:
            return None
        return v


# ==========================================
# 3. Rule Engine Output Schemas
# ==========================================

class RuleViolation(BaseModel):
    """Individual compliance violation flag."""
    code: str = Field(..., description="Machine-readable violation tag.")
    severity_score: int = Field(..., ge=0, le=100, description="Severity points contributed to total risk score.")
    message: str = Field(..., description="Human-readable breach explanation.")

class AuditResult(BaseModel):
    """Final audit output produced by the deterministic rule engine."""
    score: int = Field(..., ge=0, le=100, description="Cumulative risk priority score capped at 100.")
    decision: Literal["APPROVED", "FLAGGED", "REJECTED", "REQUIRES_HUMAN_REVIEW"] = Field(
        ...,
        description="Final compliance decision."
    )
    flags: List[RuleViolation] = Field(
        default_factory=list,
        description="Itemized list of rule violations and risk flags."
    )
    audited_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of audit execution."
    )