"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { fetchAuditLogs, AuditLog } from '@/lib/api';
import { exportAuditLogsToCSV } from '@/lib/exportUtils';

export default function AuditsPage() {
  const router = useRouter();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const data = await fetchAuditLogs();
        setLogs(data);
      } catch (err) {
        console.error("Failed to fetch audits:", err);
      } finally {
        setLoading(false);
      }
    };
    loadLogs();
  }, []);

  // Helper to resolve effective status (prioritizes human ReviewStatus over AI Decision)
  const getEffectiveStatus = (log: any): string => {
    const reviewStatus = String(log.ReviewStatus || "").trim().toUpperCase();
    if (reviewStatus && reviewStatus !== "PENDING") {
      return reviewStatus;
    }
    return String(log.Decision || "PENDING").trim().toUpperCase();
  };

  // Dynamically extract unique effective statuses from loaded logs for the dropdown
  const availableStatuses = Array.from(
    new Set(logs.map((l: any) => getEffectiveStatus(l)))
  );

  const filteredLogs = logs.filter((log: any) => {
    const query = searchQuery.toLowerCase().trim();
    const matchesSearch = 
      !query ||
      (log.SKU || "").toLowerCase().includes(query) ||
      (log.Supplier || "").toLowerCase().includes(query) ||
      (log.Item || "").toLowerCase().includes(query) ||
      (log.Document || "").toLowerCase().includes(query) ||
      (log.Flags || "").toLowerCase().includes(query) ||
      (log["File Name"] || "").toLowerCase().includes(query);
    
    const logStatus = getEffectiveStatus(log);
    if (statusFilter === 'ALL') return matchesSearch;
    return matchesSearch && logStatus === statusFilter;
  });

  const pendingCount = logs.filter(l => getEffectiveStatus(l) === "PENDING" || l.Decision === "MANUAL_REVIEW" || !l.Decision).length;

  // --- Export Handler ---
  const handleExport = () => {
    exportAuditLogsToCSV(filteredLogs, "audit-queue-report.csv");
  };

  return (
    <div className="bg-background text-on-background font-body-md min-h-screen flex antialiased selection:bg-primary-container selection:text-on-primary-container">
      {/* Shared Sidebar Component (Fixed position) */}
      <Sidebar activePage="audits" />

      {/* Main Content Area with ml-64 to offset the fixed sidebar */}
      <main className="flex-1 flex flex-col h-screen min-w-0 ml-64 overflow-hidden bg-background">
        {/* Top Header Area */}
        <header className="bg-surface border-b border-outline-variant h-16 flex items-center justify-between px-6 w-full z-30 flex-shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="font-headline-md text-headline-md text-on-surface">Audit Queue Management</h2>
            <span className="bg-secondary-container text-on-secondary-container font-label-caps text-label-caps px-2.5 py-1 rounded-full flex items-center justify-center">
              {loading ? "..." : `${pendingCount} Pending`}
            </span>
          </div>
          <div className="flex items-center gap-3"></div>
        </header>

        {/* Content Scrollable Area */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Toolbar / Filters */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
            <div className="flex flex-wrap items-center gap-3">
              {/* Search Input */}
              <div className="relative w-72">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" data-icon="search" style={{ fontSize: '20px' }}>search</span>
                <input 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all shadow-sm" 
                  placeholder="Search file name, SKU, flags..." 
                  type="text" 
                />
              </div>

              {/* Styled Filter Dropdown */}
              <div className="relative">
                <select 
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-44 px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg font-body-sm text-body-sm text-on-surface hover:bg-surface-container-low transition-colors shadow-sm outline-none cursor-pointer appearance-none pr-8"
                >
                  <option value="ALL">All Statuses</option>
                  {availableStatuses.map((status) => (
                    <option key={status} value={status}>
                      {status.charAt(0) + status.slice(1).toLowerCase().replace('_', ' ')}
                    </option>
                  ))}
                </select>
                <span className="material-symbols-outlined absolute right-2.5 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none" style={{ fontSize: '18px' }}>
                  expand_more
                </span>
              </div>
            </div>

            {/* Bulk Actions */}
            <div className="flex items-center gap-2">
              <button 
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md text-body-md font-medium text-on-surface hover:bg-surface-container-low transition-colors shadow-sm"
              >
                <span className="material-symbols-outlined" data-icon="download" style={{ fontSize: '18px' }}>download</span>
                Export Report
              </button>
            </div>
          </div>

          {/* Data Table Card */}
          <div className="bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden shadow-sm flex flex-col">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[800px]">
                <thead className="bg-surface-container-low border-b border-outline-variant">
                  <tr>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">SKU / FILE NAME</th>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">SUPPLIER</th>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">DOCUMENT / FLAGS</th>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">DATE SUBMITTED</th>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">RISK SCORE & STATUS</th>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">GAP NOTICE</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant font-body-sm text-body-sm text-on-surface">
                  {loading ? (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-on-surface-variant">Loading audit queue from API...</td>
                    </tr>
                  ) : filteredLogs.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-on-surface-variant">No audit records found matching your filters.</td>
                    </tr>
                  ) : (
                    filteredLogs.map((log: any, index: number) => {
                      const logId = log.RecordID || index + 1;
                      const riskScore = log.Score ?? 50;
                      const effectiveStatus = getEffectiveStatus(log);
                      
                      const isApproved = effectiveStatus === "APPROVED";
                      const isRejected = effectiveStatus === "REJECTED";
                      
                      const riskColor = isRejected ? 'bg-error' : isApproved ? 'bg-tertiary' : 'bg-[#d97706]';

                      return (
                        <tr key={logId} onClick={() => router.push(`/audits/${logId}`)} className="hover:bg-surface transition-colors group relative cursor-pointer">
                          <td className="py-3 px-4 font-code-md text-code-md text-on-surface-variant">
                            <span className="font-semibold text-primary">{log.SKU || "UNMATCHED"}</span>
                            <div className="font-body-sm text-body-sm text-on-surface mt-0.5 truncate max-w-[240px]" title={log["File Name"]}>
                              {log["File Name"] || log.Item || "Compliance Document"}
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <div className="w-6 h-6 rounded bg-surface-variant flex items-center justify-center font-label-caps text-[10px] text-on-surface-variant flex-shrink-0">
                                {(log.Supplier || "SP").substring(0, 2).toUpperCase()}
                              </div>
                              <span className="truncate max-w-[140px]">{log.Supplier || "Unknown Supplier"}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-surface-container border border-outline-variant max-w-[260px] truncate" title={log.Flags}>
                              <span className="material-symbols-outlined text-on-surface-variant flex-shrink-0" data-icon="policy" style={{ fontSize: '14px' }}>policy</span>
                              <span className="truncate text-xs">{log.Flags || log.Document || "No flags recorded"}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-on-surface-variant whitespace-nowrap">
                            {log.Timestamp ? new Date(log.Timestamp).toLocaleDateString() : 'N/A'} 
                            <span className="text-xs ml-1 opacity-70">{log.Timestamp ? new Date(log.Timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}</span>
                          </td>
                          <td className="py-3 px-4 whitespace-nowrap">
                            <div className={`inline-flex items-center px-2.5 py-1 rounded-full font-medium gap-1.5 ${isRejected ? 'bg-error/10 text-error' : isApproved ? 'bg-tertiary/10 text-tertiary' : 'bg-amber-100 text-amber-800'}`}>
                              <span className={`w-2 h-2 rounded-full flex-shrink-0 ${riskColor}`}></span>
                              {riskScore} ({effectiveStatus})
                            </div>
                          </td>
                          <td className="py-3 px-4 whitespace-nowrap">
                            {log.GapNoticeStatus ? (
                              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${
                                log.GapNoticeStatus === 'SENT' ? 'bg-tertiary/10 text-tertiary' :
                                log.GapNoticeStatus === 'APPROVED_FOR_SENDING' ? 'bg-primary/10 text-primary' :
                                log.GapNoticeStatus === 'EDITED' ? 'bg-secondary-container text-on-secondary-container' :
                                'bg-surface-container text-on-surface-variant'
                              }`}>
                                {log.GapNoticeStatus.replace(/_/g, ' ')}
                              </span>
                            ) : (
                              <span className="text-xs text-on-surface-variant">—</span>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Footer */}
            <div className="bg-surface-container-low border-t border-outline-variant py-3 px-4 flex items-center justify-between">
              <span className="font-body-sm text-body-sm text-on-surface-variant">Showing {filteredLogs.length} of {logs.length} audits</span>
              <div className="flex items-center gap-1">
                <button className="p-1 rounded text-on-surface-variant hover:bg-surface-container disabled:opacity-50" disabled>
                  <span className="material-symbols-outlined" data-icon="chevron_left" style={{ fontSize: '20px' }}>chevron_left</span>
                </button>
                <button className="w-7 h-7 rounded bg-primary text-on-primary font-body-sm text-body-sm font-medium flex items-center justify-center">1</button>
                <button className="p-1 rounded text-on-surface-variant hover:bg-surface-container">
                  <span className="material-symbols-outlined" data-icon="chevron_right" style={{ fontSize: '20px' }}>chevron_right</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}