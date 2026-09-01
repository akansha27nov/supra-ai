"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { fetchAuditLogs, AuditLog } from '@/lib/api';

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

  const filteredLogs = logs.filter((log: any) => {
    const matchesSearch = 
      (log.SKU || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (log.Supplier || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (log.Item || "").toLowerCase().includes(searchQuery.toLowerCase());
    
    if (statusFilter === 'ALL') return matchesSearch;
    return matchesSearch && (log.Decision || "").toUpperCase() === statusFilter;
  });

  const pendingCount = logs.filter(l => l.Decision === "MANUAL_REVIEW" || !l.Decision).length;

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
          <div className="flex items-center gap-3">
            <button className="p-2 text-on-surface-variant hover:bg-surface-container-low rounded-full transition-colors duration-200">
              <span className="material-symbols-outlined" data-icon="notifications">notifications</span>
            </button>
            <button className="p-2 text-on-surface-variant hover:bg-surface-container-low rounded-full transition-colors duration-200">
              <span className="material-symbols-outlined" data-icon="help">help</span>
            </button>
            <div className="w-8 h-8 rounded-full overflow-hidden border border-outline-variant">
              <img className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBAiUzOaI5xb_1zhghnE-Pfa1VsdzLkIMnABt0qPos4bRdX70C5AkPsY4tq3bu1f3UzlyXSgHq3m4RY-N8v8lJup5GLyAKlPm08mXrqECihz4Fh3y-0A3TmLNqnmEpUlOk_CEogQwEyeMMos-9_vZOg4CIqCQfbwYkhyoC1_kJ9dVRVKYj6iXLMvByZY21gKhfoiSEvQcKYFoetTFeKLsqJgfDdgN_t2QIhSLRPM790SrgPVqQO2H4" alt="Profile" />
            </div>
          </div>
        </header>

        {/* Content Scrollable Area */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Toolbar / Filters */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
            <div className="flex flex-wrap items-center gap-3">
              {/* Search Input */}
              <div className="relative w-64">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" data-icon="search" style={{ fontSize: '20px' }}>search</span>
                <input 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all shadow-sm" 
                  placeholder="Search SKU or Supplier..." 
                  type="text" 
                />
              </div>
              {/* Filter Dropdown */}
              <div className="relative">
                <select 
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="flex items-center gap-2 px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg font-body-sm text-body-sm text-on-surface hover:bg-surface-container-low transition-colors shadow-sm outline-none cursor-pointer"
                >
                  <option value="ALL">All Statuses</option>
                  <option value="APPROVED">Approved</option>
                  <option value="REJECTED">Rejected</option>
                  <option value="MANUAL_REVIEW">Manual Review</option>
                </select>
              </div>
            </div>
            {/* Bulk Actions */}
            <div className="flex items-center gap-3">
              <button className="flex items-center gap-2 px-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md text-body-md font-medium text-on-surface hover:bg-surface-container-low transition-colors shadow-sm">
                <span className="material-symbols-outlined" data-icon="download" style={{ fontSize: '18px' }}>download</span>
                Export Report
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary rounded-lg font-body-md text-body-md font-medium hover:bg-surface-tint transition-colors shadow-sm">
                <span className="material-symbols-outlined" data-icon="done_all" style={{ fontSize: '18px' }}>done_all</span>
                Batch Approve
              </button>
            </div>
          </div>

          {/* Data Table Card */}
          <div className="bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden shadow-sm flex flex-col">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[800px]">
                <thead className="bg-surface-container-low border-b border-outline-variant">
                  <tr>
                    <th className="py-3 px-4 w-12 text-center">
                      <input className="w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary focus:ring-offset-0" type="checkbox" />
                    </th>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">SKU / ITEM</th>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">SUPPLIER</th>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">DOCUMENT TYPE</th>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">DATE SUBMITTED</th>
                    <th className="py-3 px-4 font-label-caps text-label-caps text-on-surface-variant whitespace-nowrap">RISK SCORE</th>
                    <th className="py-3 px-4 w-12"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant font-body-sm text-body-sm text-on-surface">
                  {loading ? (
                    <tr>
                      <td colSpan={7} className="text-center py-8 text-on-surface-variant">Loading audit queue from API...</td>
                    </tr>
                  ) : filteredLogs.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="text-center py-8 text-on-surface-variant">No audit records found.</td>
                    </tr>
                  ) : (
                    filteredLogs.map((log: any, index: number) => {
                      const logId = log.id || index + 1;
                      const riskScore = log.Score ?? 50;
                      const isRejected = log.Decision === "REJECTED";
                      const isReview = log.Decision === "MANUAL_REVIEW";
                      const riskColor = isRejected ? 'bg-error' : isReview ? 'bg-[#d97706]' : 'bg-tertiary';

                      return (
                        <tr key={logId} onClick={() => router.push(`/audits/${logId}`)} className="hover:bg-surface transition-colors group relative cursor-pointer">
                          <td className="py-3 px-4 text-center align-middle relative" onClick={(e) => e.stopPropagation()}>
                            <div className={`absolute left-0 top-0 bottom-0 w-1 ${riskColor}`}></div>
                            <input className="w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary focus:ring-offset-0 mt-1" type="checkbox" />
                          </td>
                          <td className="py-3 px-4 font-code-md text-code-md text-on-surface-variant">
                            {log.SKU || "SKU-UNKNOWN"}
                            <div className="font-body-sm text-body-sm text-on-surface mt-0.5 truncate max-w-[200px]">{log.Item || log.Document || "Compliance Document"}</div>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <div className="w-6 h-6 rounded bg-surface-variant flex items-center justify-center font-label-caps text-[10px] text-on-surface-variant">
                                {(log.Supplier || "SP").substring(0, 2).toUpperCase()}
                              </div>
                              <span>{log.Supplier || "Unknown Supplier"}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-surface-container border border-outline-variant">
                              <span className="material-symbols-outlined text-on-surface-variant" data-icon="policy" style={{ fontSize: '14px' }}>policy</span>
                              {log.Document || log.Flags || "Compliance Cert"}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-on-surface-variant">
                            {log.Timestamp ? new Date(log.Timestamp).toLocaleDateString() : 'N/A'} 
                            <span className="text-xs ml-1 opacity-70">{log.Timestamp ? new Date(log.Timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}</span>
                          </td>
                          <td className="py-3 px-4">
                            <div className={`inline-flex items-center px-2 py-1 rounded-full font-medium gap-1.5 ${isRejected ? 'bg-error/10 text-error' : isReview ? 'bg-[#d97706]/10 text-[#b45309]' : 'bg-tertiary/10 text-tertiary'}`}>
                              <span className={`w-2 h-2 rounded-full ${riskColor}`}></span>
                              {riskScore} ({log.Decision || 'Pending'})
                            </div>
                          </td>
                          <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                            <button className="p-1 text-on-surface-variant opacity-0 group-hover:opacity-100 transition-opacity hover:bg-surface-container rounded">
                              <span className="material-symbols-outlined" data-icon="more_vert" style={{ fontSize: '20px' }}>more_vert</span>
                            </button>
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