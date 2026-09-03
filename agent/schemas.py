# agent/schemas.py
from datetime import datetime, timezone
from enum import Enum
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

class SourceEvidence(BaseModel):
    """Linkage to the source document for a specific extracted field."""
    field_name: str = Field(..., description="Name of the extracted field (e.g., 'tested_lead_ppm').")
    exact_quote: str = Field(..., description="Exact verbatim text span/quote from the document.")
    page_number: int | None = Field(default=None, description="Page number where the evidence is found.")
    section: str | None = Field(default=None, description="Document section or context heading.")

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

    exemption_independently_verified: bool = Field(
        default=False,
        description=(
            "Only relevant when lead_exemption_cited is True. True if the testing lab "
            "independently verified the material composition underlying the exemption "
            "(e.g. through its own material analysis). False if the document states the "
            "material claim was self-declared by the client/applicant and not "
            "independently verified — look for language like 'claimed as is by client', "
            "'received as is', 'as declared by the client', or similar. A lab passing "
            "along an unverified client claim is meaningfully weaker evidence than a lab "
            "confirming the composition itself."
        ),
    )
    
    evidence_links: list[SourceEvidence] = Field(
        default_factory=list,
        description="Source document evidence (page/section/span quotes) for the extracted values."
    )
    
    @field_validator(
        "issue_date", "expiration_date", "accreditation_id", "issuing_lab", "certificate_id",
        mode="before",
    )
    @classmethod
    def sanitize_placeholder_strings(cls, v):
        """Confirmed via testing: the LLM sometimes returns the literal string "null"
        (not JSON null) for optional fields like accreditation_id. Since "null" is a
        non-empty, truthy Python string, downstream code like `if not acc_id:` treats it
        as a real value present - causing UNACCREDITED_LABORATORY (severity 70, correct
        for a genuinely missing accreditation) to be skipped in favor of the much weaker
        UNVERIFIED_ACCREDITATION (severity 30), a 40-point under-scoring of real risk.
        This was previously only guarded for issue_date/expiration_date; extending it to
        every optional string field that can suffer the same failure mode."""
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
    evidence: SourceEvidence | None = Field(
        default=None, 
        description="Source document evidence linking to this violation."
    )

class AuditResult(BaseModel):
    """Final audit output produced by the deterministic rule engine."""
    score: int = Field(..., ge=0, le=100, description="Cumulative risk priority score capped at 100.")
    decision: Literal["APPROVED", "FLAGGED", "REJECTED", "REQUIRES_HUMAN_REVIEW"] = Field(
        ...,
        description="Final compliance decision."
    )
    sku_match_status: Literal["matched", "unmatched", "not_attempted"] = Field(
        default="not_attempted",
        description="Distinct reviewer-facing state for SKU catalog resolution."
    )
    associated_sku: str | None = Field(
        default=None,
        description="The resolved catalog SKU code if matched, or explicit null if unmatched."
    )
    flags: list[RuleViolation] = Field(
        default_factory=list,
        description="Itemized list of rule violations and risk flags."
    )
    audited_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of audit execution."
    )
    
    
# ==========================================
# 4. Gap Notice Lifecycle Schemas
# ==========================================

class GapNoticeStatus(str, Enum):
    DRAFT = "DRAFT"
    EDITED = "EDITED"
    APPROVED_FOR_SENDING = "APPROVED_FOR_SENDING"
    SENT = "SENT"

class GapNoticeRecord(BaseModel):
    """Persisted record representing the lifecycle of a supplier gap notice."""
    notice_id: str = Field(..., description="Unique identifier for the gap notice record.")
    audit_id: str = Field(..., description="Associated audit run or document reference ID.")
    supplier_name: str = Field(..., description="Name of the target supplier.")
    status: GapNoticeStatus = Field(default=GapNoticeStatus.DRAFT, description="Current lifecycle state.")
    
    # Structured components (can be edited independently or via email text override)
    failed_rules: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    corrective_action: str | None = Field(default=None)
    
    # Final email text (allows human editing prior to dispatch)
    editable_email_draft: str = Field(..., description="The current email body, editable by a reviewer.")
    
    # Audit trail metadata
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    approved_by: str | None = Field(default=None, description="Reviewer ID who approved the final version.")
    approved_at: str | None = Field(default=None, description="Timestamp when the notice was approved for sending.")


class UpdateGapNoticeRequest(BaseModel):
    """Payload for a reviewer editing the draft notice before approval."""
    editable_email_draft: str = Field(..., description="Revised email text.")
    corrective_action: str | None = Field(default=None)


class ApproveGapNoticeRequest(BaseModel):
    """Payload to record that the reviewed version is approved for external sending."""
    reviewer_id: str = Field(..., description="Identifier of the compliance officer approving the notice.")
