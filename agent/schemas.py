# agent/schemas.py
from datetime import datetime, timezone
from typing import Literal

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
    """Canonical document extraction schema."""

    document_classification: Literal[
        "DECLARATION_OF_CONFORMITY",
        "LAB_TEST_REPORT",
        "UNKNOWN",
    ] = Field(
        default="UNKNOWN",
        description="Classification of the source document."
    )

    certificate_id: str | None = Field(
        default=None,
        description="Certificate/report/document identifier if explicitly stated."
    )

    supplier_name: str | None = Field(
        default=None,
        description="Manufacturer or supplier name exactly as stated in the document."
    )

    issuing_lab: str | None = Field(
        default=None,
        description="Testing laboratory named in the document, if applicable."
    )

    accreditation_id: str | None = Field(
        default=None,
        description="Laboratory accreditation identifier, if explicitly stated."
    )

    issue_date: str | None = Field(
        default=None,
        description="Document issue date in YYYY-MM-DD format if stated."
    )

    expiration_date: str | None = Field(
        default=None,
        description="Expiration/valid-until date in YYYY-MM-DD format if explicitly stated."
    )

    covered_part_numbers: list[str] = Field(
        default_factory=list,
        description=(
            "Manufacturer model numbers, part numbers, product-family codes, "
            "or covered variants explicitly stated in the document."
        ),
    )

    standards_tested: list[str] = Field(
        default_factory=list,
        description="Standards, directives, or regulations explicitly cited."
    )

    tested_lead_ppm: float | None = Field(
        default=None,
        description=(
            "Actual measured lead concentration in ppm. "
            "Convert scientific notation correctly before returning the number. "
            "Example: 2.93×10^4 mg/kg = 29300 ppm. "
            "Never populate this field with a statutory/legal limit."
        ),
    )

    is_statutory_limit: bool = Field(
        default=False,
        description=(
            "True only when the extracted ppm value is a legal/statutory threshold "
            "rather than an actual measured result."
        ),
    )

    lead_exemption_cited: bool = Field(
        default=False,
        description=(
            "True only if the document explicitly cites a RoHS exemption (e.g. Annex III "
            "or Annex IV, such as 'exemption 6(c) — copper alloy containing up to 4% lead') "
            "that applies to the measured tested_lead_ppm value. False if no exemption is "
            "mentioned, even when the measured value is high."
        ),
    )
    
    @field_validator("issue_date", "expiration_date", mode="before")
    @classmethod
    def sanitize_date_strings(cls, v):
        if v is None:
            return None
        if str(v).strip().lower() in {
            "", "n/a", "none", "null", "unknown", "not stated", "not applicable"
        }:
            return None
        return str(v)

    @field_validator("covered_part_numbers", mode="before")
    @classmethod
    def sanitize_part_numbers(cls, v):
        if not v:
            return []
        if isinstance(v, str):
            return [v]
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
    flags: list[RuleViolation] = Field(
        default_factory=list,
        description="Itemized list of rule violations and risk flags."
    )
    audited_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of audit execution."
    )
