// frontend/lib/api.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL 
  ? `${process.env.NEXT_PUBLIC_API_URL}/api` 
  : "http://localhost:8000/api";

export interface AuditLog {
  Timestamp: string;
  "File Name": string;
  SKU: string;
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