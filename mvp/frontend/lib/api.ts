// frontend/lib/api.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL 
  ? `${process.env.NEXT_PUBLIC_API_URL}/api` 
  : "http://localhost:8000/api";

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
  ReviewStatus?: string;
  Reviewer?: string;
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

export async function generateGapNotice(params: {
  audit_result: any;
  extracted: any;
  supplier_name?: string;
  associated_sku?: string | null;
}): Promise<{ draft: string }> {
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