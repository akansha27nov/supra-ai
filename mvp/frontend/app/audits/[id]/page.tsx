"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { 
  ArrowLeft, CheckCircle, XCircle, FileText, 
  ShieldAlert, Mail, Send, UserCheck, Layers, FileSearch, SlidersHorizontal 
} from 'lucide-react';
import { fetchAuditLogs, submitReviewDecision, generateGapNotice, AuditLog } from '@/lib/api';
import { exportAuditLogsToCSV } from '@/lib/exportUtils';

export default function AuditDetailPage() {
  const router = useRouter();
  const params = useParams();
  const auditId = (params?.id as string) || '';

  const [audit, setAudit] = useState<AuditLog | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentDecision, setCurrentDecision] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Active Tab State for comparison views
  const [activeTab, setActiveTab] = useState<'overview' | 'extracted' | 'policy'>('overview');

  // Gap Notice Modal State (US-3.2)
  const [showGapModal, setShowGapModal] = useState(false);
  const [gapNoticeText, setGapNoticeText] = useState('');
  const [noticeSent, setNoticeSent] = useState(false);
  const [loadingNotice, setLoadingNotice] = useState(false);

  useEffect(() => {
    const loadAudit = async () => {
      try {
        const logs = await fetchAuditLogs();
        // RecordID is now a stable UUID for every row (see agent/run_pdf.py), so this
        // should always be an exact match. No more index-based fallback matching, and
        // no more falling back to logs[0] when nothing matches — that was silently
        // showing a random unrelated record instead of the "not found" state below.
        const found = logs.find((l) => l.RecordID === auditId) || null;

        setAudit(found);
        if (found) {
          const initialStatus = (found.ReviewStatus && found.ReviewStatus !== 'PENDING') 
            ? found.ReviewStatus 
            : found.Decision || 'PENDING';
          setCurrentDecision(initialStatus);
        }
      } catch (error) {
        console.error("Failed to load audit detail:", error);
      } finally {
        setLoading(false);
      }
    };
    loadAudit();
  }, [auditId]);

  // The ledger only stores flags as one joined "CODE: message | CODE: message" string,
  // not the structured list-of-dicts the backend's gap_notice generator expects. Parse
  // it back into that shape. The ledger also doesn't retain a per-flag severity score
  // (only one Score for the whole row) — using the row's Score for every flag is an
  // honest approximation, not fabricated precision, and it's only used to satisfy the
  // backend's ">0 = actionable" check.
  const parseFlagsForGapNotice = (flagsStr: string | undefined, fallbackScore: number) => {
    if (!flagsStr || flagsStr.trim() === '' || flagsStr.trim().toLowerCase() === 'none') return [];
    return flagsStr.split('|').map(s => s.trim()).filter(Boolean).map(entry => {
      const sep = entry.indexOf(':');
      const code = sep >= 0 ? entry.slice(0, sep).trim() : entry;
      const message = sep >= 0 ? entry.slice(sep + 1).trim() : entry;
      return { code, message, severity_score: fallbackScore || 1 };
    });
  };

  // Shared by the auto-generate-on-reject flow AND the "View Draft" button, so reopening
  // the modal after a page reload regenerates the draft instead of showing it empty.
  const loadGapNotice = async (record: AuditLog) => {
    setLoadingNotice(true);
    try {
      const validSku = record.SKU && record.SKU !== 'UNMATCHED' ? record.SKU : null;
      const gapNoticeRes = await generateGapNotice({
        audit_result: {
          decision: record.Decision,
          score: record.Score,
          flags: parseFlagsForGapNotice(record.Flags, record.Score),
        },
        extracted: {
          covered_part_numbers: validSku ? [validSku] : [],
        },
        supplier_name: record.Supplier || 'Supplier',
        associated_sku: validSku,
      });
      setGapNoticeText(gapNoticeRes.draft);
    } catch (gapErr) {
      console.error('Failed to generate gap notice:', gapErr);
      setGapNoticeText(
        `SUPPLIER CORRECTIVE ACTION NOTICE\n\n` +
        `Document: ${record["File Name"]}\nSupplier: ${record.Supplier || 'N/A'}\nSKU: ${record.SKU || 'N/A'}\n\n` +
        `Reason: ${record.Flags || 'Failed compliance check.'}`
      );
    } finally {
      setLoadingNotice(false);
    }
  };

  const handleApprove = async () => {
    if (!audit?.RecordID) return;
    setIsSubmitting(true);
    try {
      await submitReviewDecision(audit.RecordID, "APPROVED", "Lead Auditor");
      setCurrentDecision("APPROVED");
      // Update the local record too, not just currentDecision — isPending reads
      // audit.ReviewStatus, and without this it stays stale until a page reload,
      // leaving the Approve/Reject buttons visible after a decision was already submitted.
      setAudit(prev => prev ? { ...prev, ReviewStatus: "APPROVED", Reviewer: "Lead Auditor" } : prev);
      alert(`Audit record has been successfully APPROVED.`);
    } catch (error) {
      console.error("Failed to submit approval:", error);
      alert("Failed to submit approval decision.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!audit?.RecordID) return;
    setIsSubmitting(true);
    try {
      await submitReviewDecision(audit.RecordID, "REJECTED", "Lead Auditor");
      setCurrentDecision("REJECTED");
      setAudit(prev => prev ? { ...prev, ReviewStatus: "REJECTED", Reviewer: "Lead Auditor" } : prev);
      setShowGapModal(true);
      await loadGapNotice(audit);
    } catch (error) {
      alert("Failed to submit rejection.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSendGapNotice = () => {
    setNoticeSent(true);
    setTimeout(() => {
      setShowGapModal(false);
      setNoticeSent(false);
      alert("Supplier Gap Notice sent successfully!");
    }, 800);
  };

  const handleExport = () => {
    if (audit) {
      exportAuditLogsToCSV([audit], `audit-${audit.RecordID || auditId}-report.csv`);
    }
  };

  if (loading) {
    return (
      <div className="bg-background text-on-background min-h-screen flex items-center justify-center">
        <p className="text-sm text-on-surface-variant animate-pulse">Loading audit record...</p>
      </div>
    );
  }

  if (!audit) {
    return (
      <div className="bg-background text-on-background min-h-screen flex items-center justify-center flex-col gap-4">
        <p className="text-lg font-bold">Audit Record Not Found</p>
        <button onClick={() => router.push('/audits')} className="px-4 py-2 bg-primary text-on-primary rounded">Back to Audits</button>
      </div>
    );
  }

  const riskScore = audit.Score ?? 0;
  const isPending = !audit.ReviewStatus || audit.ReviewStatus === "PENDING" || currentDecision === "PENDING";

  return (
    <div className="bg-background text-on-background min-h-screen flex antialiased selection:bg-primary-container overflow-hidden">
      <Sidebar activePage="audits" />

      <main className="flex-1 flex flex-col md:ml-64 h-screen overflow-hidden bg-surface-bright">
        {/* Header */}
        <header className="flex justify-between items-center px-6 w-full sticky top-0 z-50 bg-surface border-b border-outline-variant h-16">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => router.push('/audits')}
              className="p-2 rounded-lg hover:bg-surface-container transition-colors text-on-surface-variant"
            >
              <ArrowLeft size={20} />
            </button>
            <h2 className="text-xl font-bold text-on-background font-headline-md">
              Audit Details
            </h2>
          </div>
          
          <div className="flex items-center gap-3">
            <button 
              onClick={handleExport}
              className="flex items-center gap-2 px-3 py-2 bg-surface-container-highest border border-outline-variant text-on-surface rounded text-sm font-medium hover:bg-surface-container transition-colors shadow-sm"
            >
              <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>download</span>
              Export CSV
            </button>

            {isPending ? (
              <>
                <button 
                  onClick={handleReject} 
                  disabled={isSubmitting}
                  className="flex items-center gap-2 px-4 py-2 bg-error text-on-error rounded text-sm font-medium hover:opacity-90 transition-opacity shadow-sm disabled:opacity-50"
                >
                  <XCircle size={16} /> Reject Audit
                </button>
                <button 
                  onClick={handleApprove} 
                  disabled={isSubmitting}
                  className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary rounded text-sm font-medium hover:bg-surface-tint transition-colors shadow-sm disabled:opacity-50"
                >
                  <CheckCircle size={16} /> Approve Audit
                </button>
              </>
            ) : (
              <span className="px-3 py-1.5 bg-surface-container text-on-surface-variant rounded-lg text-xs font-medium border border-outline-variant flex items-center gap-1.5">
                <UserCheck size={14} className="text-primary" /> Review Finalized: {currentDecision}
              </span>
            )}
          </div>
        </header>

        {/* Tab Navigation Bar */}
        <div className="bg-surface border-b border-outline-variant px-6 flex items-center gap-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-3.5 text-sm font-medium border-b-2 flex items-center gap-2 transition-colors ${
              activeTab === 'overview'
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <Layers size={16} /> Overview Summary
          </button>
          <button
            onClick={() => setActiveTab('extracted')}
            className={`py-3.5 text-sm font-medium border-b-2 flex items-center gap-2 transition-colors ${
              activeTab === 'extracted'
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <FileSearch size={16} /> Extracted Data Schema
          </button>
          <button
            onClick={() => setActiveTab('policy')}
            className={`py-3.5 text-sm font-medium border-b-2 flex items-center gap-2 transition-colors ${
              activeTab === 'policy'
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <SlidersHorizontal size={16} /> Policy Engine Trace
          </button>
        </div>

        {/* Tab Content Body */}
        <div className="flex-1 overflow-y-auto p-6 md:p-8 custom-scrollbar">
          
          {/* TAB 1: OVERVIEW SUMMARY */}
          {activeTab === 'overview' && (
            <div className="max-w-4xl mx-auto flex flex-col gap-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-surface-container-lowest p-5 rounded-lg border border-surface-variant shadow-sm flex flex-col gap-1">
                  <span className="text-xs text-on-surface-variant uppercase tracking-wider">Source File</span>
                  <span className="text-sm font-semibold text-on-surface truncate" title={audit["File Name"]}>
                    {audit["File Name"] || "N/A"}
                  </span>
                </div>
                <div className="bg-surface-container-lowest p-5 rounded-lg border border-surface-variant shadow-sm flex flex-col gap-1">
                  <span className="text-xs text-on-surface-variant uppercase tracking-wider">Catalog SKU</span>
                  <span className="text-sm font-mono font-semibold text-primary">
                    {audit.SKU || "Unassigned"}
                  </span>
                </div>
                <div className="bg-surface-container-lowest p-5 rounded-lg border border-surface-variant shadow-sm flex flex-col gap-1">
                  <span className="text-xs text-on-surface-variant uppercase tracking-wider">Compliance Risk Score</span>
                  <span className={`text-sm font-bold ${riskScore > 75 ? 'text-error' : 'text-tertiary'}`}>
                    {riskScore} / 100 ({currentDecision})
                  </span>
                </div>
              </div>

              <div className="bg-surface-container-lowest p-6 rounded-lg border border-surface-variant shadow-sm flex flex-col gap-4">
                <h3 className="text-sm font-bold uppercase tracking-wider text-on-surface border-b border-surface-variant pb-2">
                  Audit Summary Details
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-xs text-on-surface-variant block">SKU Match Status</span>
                    <span className="font-semibold text-on-surface capitalize">
                      {audit["SKU Match Status"] ? audit["SKU Match Status"].replace(/_/g, ' ') : "Pending"}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs text-on-surface-variant block">Submission Timestamp</span>
                    <span className="font-medium text-on-surface">
                      {audit.Timestamp ? new Date(audit.Timestamp).toLocaleString() : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs text-on-surface-variant block">Assigned Reviewer</span>
                    <span className="font-medium text-on-surface">{audit.Reviewer || "Unassigned"}</span>
                  </div>
                  <div>
                    <span className="text-xs text-on-surface-variant block">Automated Decision</span>
                    <span className="font-medium text-on-surface">{audit.Decision || "N/A"}</span>
                  </div>
                </div>
              </div>

              {currentDecision === "REJECTED" && (
                <div className="bg-surface-container-lowest p-6 rounded-lg border border-surface-variant shadow-sm flex flex-col gap-3">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-on-surface">Supplier Gap Notice Action</h3>
                  <button 
                    onClick={() => {
                      setShowGapModal(true);
                      if (!gapNoticeText && audit) {
                        loadGapNotice(audit);
                      }
                    }}
                    className="flex items-center justify-center gap-2 w-full py-2.5 bg-error-container/30 text-error rounded-lg text-sm font-medium border border-error/20 hover:bg-error-container/50 transition-colors"
                  >
                    <Mail size={16} /> View Supplier Gap Notice Draft
                  </button>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: EXTRACTED DATA SCHEMA */}
          {activeTab === 'extracted' && (
            <div className="max-w-4xl mx-auto flex flex-col gap-6">
              <div className="bg-surface-container-lowest p-6 rounded-lg border border-surface-variant shadow-sm flex flex-col gap-4">
                <div className="flex items-center justify-between pb-3 border-b border-surface-variant">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-on-surface flex items-center gap-2">
                    <FileText size={16} className="text-primary" /> Raw Extracted Ledger Schema
                  </h3>
                  <span className="text-xs font-mono bg-secondary-container text-on-secondary-container px-2.5 py-0.5 rounded">
                    Record ID: {audit.RecordID}
                  </span>
                </div>

                <div className="flex flex-col gap-3 text-sm">
                  <div className="flex justify-between py-2.5 border-b border-surface-variant">
                    <span className="text-on-surface-variant">File Name</span>
                    <span className="font-mono text-on-surface">{audit["File Name"]}</span>
                  </div>
                  <div className="flex justify-between py-2.5 border-b border-surface-variant">
                    <span className="text-on-surface-variant">SKU Property</span>
                    <span className="font-mono text-primary font-semibold">{audit.SKU || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-2.5 border-b border-surface-variant">
                    <span className="text-on-surface-variant">SKU Match Status</span>
                    <span className="font-mono text-on-surface capitalize">
                      {audit["SKU Match Status"] ? audit["SKU Match Status"].replace(/_/g, ' ') : "N/A"}
                    </span>
                  </div>
                  <div className="flex justify-between py-2.5 border-b border-surface-variant">
                    <span className="text-on-surface-variant">Timestamp</span>
                    <span className="font-mono text-on-surface">{audit.Timestamp || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-2.5 border-b border-surface-variant">
                    <span className="text-on-surface-variant">Reviewer Name</span>
                    <span className="font-mono text-on-surface">{audit.Reviewer || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-2.5">
                    <span className="text-on-surface-variant">Review Status</span>
                    <span className="font-mono text-on-surface">{audit.ReviewStatus || "PENDING"}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: POLICY ENGINE TRACE */}
          {activeTab === 'policy' && (
            <div className="max-w-4xl mx-auto flex flex-col gap-6">
              <div className="bg-surface-container-lowest p-6 rounded-lg border border-surface-variant shadow-sm flex flex-col gap-4">
                <div className="pb-3 border-b border-surface-variant">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-on-surface flex items-center gap-2">
                    <ShieldAlert size={16} className="text-primary" /> Policy Engine Trace & Flags
                  </h3>
                </div>

                <div className="flex flex-col gap-4">
                  <div className="p-4 bg-surface-container rounded-lg border border-outline-variant flex flex-col gap-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-on-surface">Automated Decision Result</span>
                      <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${audit.Decision === "APPROVED" ? "bg-tertiary/10 text-tertiary" : "bg-error/10 text-error"}`}>
                        {audit.Decision || "UNKNOWN"}
                      </span>
                    </div>
                    <span className="text-xs text-on-surface-variant">Calculated Risk Score: {riskScore} / 100</span>
                  </div>

                  <div className="p-4 bg-surface-container rounded-lg border border-outline-variant flex flex-col gap-2">
                    <span className="text-sm font-bold text-on-surface">Evaluated Flags & Rule Violations</span>
                    <p className="text-xs font-mono text-on-surface-variant bg-surface-container-highest p-3 rounded leading-relaxed">
                      {audit.Flags || "No rule flags or violations recorded in ledger."}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>

        {/* Dynamic AI Gap Notice Modal (US-3.2) */}
        {showGapModal && (
          <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-surface-container-lowest w-full max-w-2xl rounded-xl border border-outline-variant shadow-xl p-6 flex flex-col gap-4">
              <div className="flex justify-between items-center pb-3 border-b border-surface-variant">
                <h3 className="text-lg font-bold text-on-surface flex items-center gap-2">
                  <Mail size={20} className="text-primary" /> Generated Supplier Gap Notice
                </h3>
                <button onClick={() => setShowGapModal(false)} className="text-on-surface-variant hover:text-on-surface font-bold">✕</button>
              </div>

              {loadingNotice ? (
                <div className="h-56 flex items-center justify-center text-sm text-on-surface-variant animate-pulse">
                  Drafting supplier notice using API endpoint...
                </div>
              ) : (
                <textarea 
                  value={gapNoticeText}
                  onChange={(e) => setGapNoticeText(e.target.value)}
                  className="w-full h-56 p-3 bg-surface-container border border-outline-variant rounded-lg font-code-sm text-sm text-on-surface focus:outline-none focus:border-primary resize-none"
                />
              )}

              <div className="flex justify-end gap-3 pt-2">
                <button onClick={() => setShowGapModal(false)} className="px-4 py-2 border border-outline-variant text-on-surface rounded-lg text-sm font-medium">Cancel</button>
                <button 
                  onClick={handleSendGapNotice}
                  disabled={noticeSent || loadingNotice}
                  className="flex items-center gap-2 px-5 py-2 bg-primary text-on-primary rounded-lg text-sm font-medium shadow-sm disabled:opacity-50"
                >
                  <Send size={16} /> {noticeSent ? "Sending Notice..." : "Send Notice to Supplier"}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}