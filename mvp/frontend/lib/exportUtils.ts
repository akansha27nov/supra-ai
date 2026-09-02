import { AuditLog } from "@/lib/api";

export const exportAuditLogsToCSV = (logs: AuditLog[], filename = "compliance-audit-report.csv") => {
  if (!logs || logs.length === 0) {
    alert("No audit logs available to export.");
    return;
  }

  // Define CSV headers based on key AuditLog properties
  const headers = ["RecordID", "Timestamp", "File Name", "SKU", "Decision", "ReviewStatus", "Score", "Reviewer", "Flags"];

  // Map rows to CSV safe strings
  const csvRows = logs.map(log => {
    return [
      log.RecordID || "",
      `"${(log.Timestamp || "").replace(/"/g, '""')}"`,
      `"${(log["File Name"] || "").replace(/"/g, '""')}"`,
      `"${(log.SKU || "").replace(/"/g, '""')}"`,
      log.Decision || "",
      log.ReviewStatus || "",
      log.Score ?? "",
      `"${(log.Reviewer || "").replace(/"/g, '""')}"`,
      `"${(log.Flags || "").replace(/"/g, '""')}"`
    ].join(",");
  });

  // Combine headers and rows
  const csvContent = [headers.join(","), ...csvRows].join("\n");

  // Create a Blob and trigger browser download
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};