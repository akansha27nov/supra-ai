// frontend/lib/api.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL 
  ? `${process.env.NEXT_PUBLIC_API_URL}/api` 
  : "http://localhost:8000/api";

// Mirrors agent/schemas.py::SourceEvidence.
export interface SourceEvidence {
  field_name: string;
  exact_quote: string;
  page_number: number | null;
  section: string | null;
}

// Mirrors agent/schemas.py::RuleViolation.
export interface RuleViolationDetail {
  code: string;
  severity_score: number;
  message: string;
  evidence: SourceEvidence | null;
}

export interface AuditLog {
  RecordID: string;
  Timestamp: string;
  "File Name": string;
  Supplier?: string;
  SKU: string;
  "SKU Match Status"?: string;
  Decision: string;
  Score: number;
  Flags: string;
  FlagsDetail?: RuleViolationDetail[];
  ReviewStatus?: string;
  Reviewer?: string;
  GapNoticeStatus?: GapNoticeStatus | "";
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export async function fetchAuditLogs(): Promise<AuditLog[]> {
  const response = await fetch(`${API_BASE_URL}/logs`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch audit logs: ${response.statusText}`);
  }
  
  const data: AuditLog[] = await response.json();
  
  // Sort by timestamp descending (newest first)
  return data.sort((a, b) => new Date(b.Timestamp).getTime() - new Date(a.Timestamp).getTime());
}

export async function uploadAuditDocument(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/audit`, {
    method: 'POST',
    body: formData, // FormData automatically sets multipart/form-data headers
  });

  if (!response.ok) {
    throw new Error(`Failed to process audit workflow: ${response.statusText}`);
  }

  return response.json();
}

export async function submitReviewDecision(
  recordId: string,
  decision: "APPROVED" | "REJECTED",
  reviewer?: string
): Promise<{ record_id: string; review_status: string }> {
  const response = await fetch(`${API_BASE_URL}/logs/${recordId}/review`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decision, reviewer }),
  });

  if (!response.ok) {
    throw new Error(`Failed to submit review decision: ${response.statusText}`);
  }

  return response.json();
}

// Mirrors agent/schemas.py::GapNoticeStatus / GapNoticeRecord.
export type GapNoticeStatus = "DRAFT" | "EDITED" | "APPROVED_FOR_SENDING" | "SENT";

// Mirrors agent/schemas.py::GapNoticeEvidenceEntry.
export interface GapNoticeEvidenceEntry {
  rule_code: string;
  exact_quote: string | null;
  page_number: number | null;
  section: string | null;
}

export interface GapNoticeRecord {
  notice_id: string;
  audit_id: string;
  supplier_name: string;
  status: GapNoticeStatus;
  failed_rules: string[];
  // Structured evidence sourced from the rule engine's own RuleViolation.evidence
  // (not the LLM's prose) -- see agent/gap_notice.py's evidence_detail handling.
  evidence: GapNoticeEvidenceEntry[];
  corrective_action: string | null;
  editable_email_draft: string;
  created_at: string;
  updated_at: string;
  approved_by: string | null;
  approved_at: string | null;
}

interface CreateGapNoticeResponse {
  record: GapNoticeRecord | null;
  created: boolean;
  message?: string;
}

// Idempotent per audit_id: if a notice already exists for this audit, the
// persisted record is returned as-is (with any prior edits/approval state)
// instead of generating a throwaway draft every time the modal is opened.
export async function generateGapNotice(params: {
  audit_id: string;
  audit_result: any;
  extracted: any;
  supplier_name?: string;
  associated_sku?: string | null;
}): Promise<CreateGapNoticeResponse> {
  const response = await fetch(`${API_BASE_URL}/gap-notice`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    throw new Error(`Failed to generate gap notice: ${response.statusText}`);
  }

  return response.json();
}

// Returns null (rather than throwing) when no notice exists yet for this
// audit, so callers can use it as a plain existence check.
export async function fetchGapNoticeByAudit(auditId: string): Promise<GapNoticeRecord | null> {
  const response = await fetch(`${API_BASE_URL}/gap-notice/by-audit/${auditId}`);

  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`Failed to fetch gap notice: ${response.statusText}`);
  }

  return response.json();
}

export async function editGapNotice(
  noticeId: string,
  updates: { editable_email_draft: string; corrective_action?: string | null }
): Promise<GapNoticeRecord> {
  const response = await fetch(`${API_BASE_URL}/gap-notice/${noticeId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });

  if (!response.ok) {
    throw new Error(`Failed to save gap notice edits: ${response.statusText}`);
  }

  return response.json();
}

export async function approveGapNotice(noticeId: string, reviewerId: string): Promise<GapNoticeRecord> {
  const response = await fetch(`${API_BASE_URL}/gap-notice/${noticeId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reviewer_id: reviewerId }),
  });

  if (!response.ok) {
    throw new Error(`Failed to approve gap notice: ${response.statusText}`);
  }

  return response.json();
}

// Marks the notice SENT server-side. `dispatch_status` (supplier delivery)
// stays "simulated" — no email provider is wired up. `telegram_notification`
// reports whether the best-effort internal Telegram alert (same Bot API
// pattern as the Round 1 n8n POC) went out: "notified" | "failed" | "not_configured".
export async function sendGapNotice(noticeId: string): Promise<{
  record: GapNoticeRecord;
  dispatch_status: string;
  telegram_notification: 'notified' | 'failed' | 'not_configured';
}> {
  const response = await fetch(`${API_BASE_URL}/gap-notice/${noticeId}/send`, {
    method: 'POST',
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Failed to send gap notice: ${response.statusText}`);
  }

  return response.json();
}

export async function sendCopilotMessage(
  recordId: string,
  payload: { message: string; history: ChatMessage[] }
): Promise<{ reply: string; grounded: boolean }> {
  const response = await fetch(`${API_BASE_URL}/logs/${recordId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to get copilot response: ${response.statusText}`);
  }

  return response.json();
}