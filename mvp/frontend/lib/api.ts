// frontend/lib/api.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL 
  ? `${process.env.NEXT_PUBLIC_API_URL}/api` 
  : "http://localhost:8000/api";

export interface AuditLog {
  Timestamp: string;
  "File Name": string;
  SKU: string;
  "SKU Match Status"?: string;
  Decision: string;
  Score: number;
  Flags: string;
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