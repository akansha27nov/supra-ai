import { AuditLog } from "@/lib/api";

// Flattens FlagsDetail's structured evidence into a single readable cell,
// consistent with how the existing Flags column already reads
// ("CODE: message | CODE: message"). Falls back to an empty string when a
// row has no FlagsDetail (older ledger rows, or violations with no
// evidence attached) rather than a raw JSON blob -- keeps the export a
// plain, Excel/Tableau-friendly tabular file rather than one with
// unstructured JSON sitting in a cell.
const formatEvidenceForExport = (log: AuditLog): string => {
  if (!log.FlagsDetail || log.FlagsDetail.length === 0) return "";

  return log.FlagsDetail
    .filter((v) => v.evidence?.exact_quote)
    .map((v) => {
      const loc = [
        v.evidence!.page_number != null ? `p.${v.evidence!.page_number}` : null,
        v.evidence!.section || null,
      ].filter(Boolean).join(", ");
      const locSuffix = loc ? ` (${loc})` : "";
      return `${v.code}${locSuffix}: "${v.evidence!.exact_quote}"`;
    })
    .join(" | ");
};

export const exportAuditLogsToCSV = (logs: AuditLog[], filename = "compliance-audit-report.csv") => {
  if (!logs || logs.length === 0) {
    alert("No audit logs available to export.");
    return;
  }

  // Define CSV headers based on key AuditLog properties
  const headers = ["RecordID", "Timestamp", "File Name", "Supplier", "SKU", "Decision", "ReviewStatus", "Score", "Reviewer", "Flags", "Evidence"];

  // Map rows to CSV safe strings
  const csvRows = logs.map(log => {
    return [
      log.RecordID || "",
      `"${(log.Timestamp || "").replace(/"/g, '""')}"`,
      `"${(log["File Name"] || "").replace(/"/g, '""')}"`,
      `"${(log.Supplier || "").replace(/"/g, '""')}"`,
      `"${(log.SKU || "").replace(/"/g, '""')}"`,
      log.Decision || "",
      log.ReviewStatus || "",
      log.Score ?? "",
      `"${(log.Reviewer || "").replace(/"/g, '""')}"`,
      `"${(log.Flags || "").replace(/"/g, '""')}"`,
      `"${formatEvidenceForExport(log).replace(/"/g, '""')}"`
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