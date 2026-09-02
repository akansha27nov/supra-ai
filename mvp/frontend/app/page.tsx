"use client";

import React, { useState, useEffect, useRef } from 'react';
import Sidebar from '@/components/Sidebar';
import { exportAuditLogsToCSV } from "@/lib/exportUtils";
import { fetchAuditLogs, AuditLog, uploadAuditDocument, generateGapNotice, submitReviewDecision } from '@/lib/api';
import { Plus, FileUp, ShieldCheck, AlertCircle, FileText, CheckCircle2, XCircle, X } from 'lucide-react';

export default function DashboardPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 5;

  // --- Modal & Upload State ---
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [auditResult, setAuditResult] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Gap Notice State ---
  // The draft is generated on demand (not automatically) since it costs an LLM call —
  // only fetch it once the reviewer actually wants to see it.
  const [gapNotice, setGapNotice] = useState<string | null>(null);
  const [gapNoticeLoading, setGapNoticeLoading] = useState(false);
  const [gapNoticeError, setGapNoticeError] = useState<string | null>(null);

  const [reviewLoadingId, setReviewLoadingId] = useState<string | null>(null);
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [reviewer, setReviewer] = useState("Executive Reviewer");

  const handleGenerateGapNotice = async () => {
    if (!auditResult) return;
    setGapNoticeLoading(true);
    setGapNoticeError(null);
    try {
      const { draft } = await generateGapNotice({
        audit_result: auditResult.audit_result || {},
        extracted: auditResult.extracted || {},
        supplier_name: auditResult.extracted?.supplier_name || "Supplier",
        associated_sku: auditResult.associated_sku ?? null,
      });
      setGapNotice(draft);
    } catch (err) {
      console.error("Failed to generate gap notice:", err);
      setGapNoticeError("Couldn't generate a gap notice. Try again.");
    } finally {
      setGapNoticeLoading(false);
    }
  };

  const getDecision = (log: AuditLog): string => {
    return String(log.Decision || "").trim().toUpperCase();
  };

  const handleExport = () => {
    exportAuditLogsToCSV(logs, "procurement-compliance-dashboard.csv");
  };

  // Helper to resolve effective decision (prioritizes human ReviewStatus over AI Decision)
  const getEffectiveDecision = (log: AuditLog): string => {
    const reviewStatus = String(log.ReviewStatus || "").trim().toUpperCase();
    if (reviewStatus === "APPROVED" || reviewStatus === "REJECTED") {
      return reviewStatus;
    }
    return String(log.Decision || "").trim().toUpperCase();
  };

 const needsReview = (log: AuditLog): boolean => {
    const reviewStatus = String(log.ReviewStatus || "").trim().toUpperCase();
    
    // Early return: if a human already approved or rejected, it never needs review
    if (reviewStatus === "APPROVED" || reviewStatus === "REJECTED") {
      return false;
    }

    const decision = getDecision(log);
    return (
      decision === "REQUIRES_HUMAN_REVIEW" ||
      decision === "NEEDS_REVIEW" ||
      decision === "NEEDS HUMAN REVIEW" ||
      reviewStatus === "PENDING" ||
      reviewStatus === ""
    );
  };

  // 1. Fetch data using the centralized API function
  const loadLogs = async () => {
    try {
      const sortedData = await fetchAuditLogs();
      setLogs(sortedData);
    } catch (error) {
      console.error("Error loading dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  // Reset pagination when logs array updates
  useEffect(() => {
    setCurrentPage(1);
  }, [logs]);

  // --- Modal Handlers ---
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setErrorMsg(null);
    }
  };

  const handleRunAudit = async () => {
    if (!selectedFile) return;
    setIsProcessing(true);
    setErrorMsg(null);

    try {
      const response = await uploadAuditDocument(selectedFile);
      setAuditResult(response);
      await loadLogs(); 
    } catch (error: any) {
      setErrorMsg(error.message || "Failed to execute compliance pipeline.");
    } finally {
      setIsProcessing(false);
    }
  };
  const resetAndCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => {
      setSelectedFile(null);
      setAuditResult(null);
      setErrorMsg(null);
    }, 200); 
  };

  const handleReviewDecision = async (
    recordId: string,
    decision: "APPROVED" | "REJECTED"
  ) => {
    if (!recordId) {
      setReviewError("This audit does not have a Record ID.");
      return;
    }

    setReviewLoadingId(recordId);
    setReviewError(null);

    try {
      await submitReviewDecision(recordId, decision, reviewer);

      // Immediately update the table/KPIs without requiring a page refresh.
      setLogs(prev =>
        prev.map(log =>
          log.RecordID === recordId
            ? {
                ...log,
                ReviewStatus: decision,
                Reviewer: reviewer,
              }
            : log
        )
      );

      // Keep the currently displayed audit result consistent.
      setAuditResult((prev: any) =>
        prev
          ? {
              ...prev,
              review_status: decision,
              reviewer,
            }
          : prev
      );
    } catch (error: any) {
      console.error("Failed to submit review decision:", error);
      setReviewError(
        error?.message || "Failed to save the review decision."
      );
    } finally {
      setReviewLoadingId(null);
    }
  };

  // Helper to format the backend decision into your UI badges
  const renderStatusBadge = (log: AuditLog) => {
    const decision = getDecision(log);
    const reviewStatus = String(log.ReviewStatus || "").toUpperCase();

    if (reviewStatus === "APPROVED") {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full bg-tertiary-container/10 text-tertiary font-medium text-xs gap-1 border border-tertiary/20">
          <CheckCircle2 size={12} />
          Approved
        </span>
      );
    }

    if (reviewStatus === "REJECTED") {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full bg-error-container/20 text-error font-medium text-xs gap-1 border border-error/20">
          <XCircle size={12} />
          Rejected
        </span>
      );
    }

    if (needsReview(log)) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full bg-red-600 text-white font-bold text-xs gap-1 border-2 border-red-800 animate-pulse shadow-sm">
          <AlertCircle size={12} />
          Needs Review
        </span>
      );
    }

    if (decision === "FLAGGED") {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full bg-amber-100 text-amber-800 font-medium text-xs gap-1 border border-amber-300">
          <AlertCircle size={12} />
          Flagged
        </span>
      );
    }

    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full bg-secondary-container/20 text-on-surface font-medium text-xs gap-1 border border-outline-variant">
        Processing
      </span>
    );
  };

  // --- DYNAMIC CALCULATIONS ---
  const totalLogs = logs.length;
  // Update metric calculations:
  const approvedCount = logs.filter(log => getEffectiveDecision(log) === "APPROVED").length;
  const complianceRate = totalLogs ? ((approvedCount / totalLogs) * 100).toFixed(1) : "0.0";
  
  const highRiskCount = logs.filter(log => getEffectiveDecision(log) === "REJECTED").length;
  
  // Inside monthly chart data aggregation:
  // const monthApproved = logs.filter(log => getEffectiveDecision(log) === "APPROVED").length;
  
  // Critical alerts:
  const criticalAlerts = logs.filter(log => getEffectiveDecision(log) === "REJECTED" && Number(log.Score) >= 80).slice(0, 3);
  const pendingCount = logs.filter(needsReview).length;
  
  // Risk Distribution Tally based on rejected log flags
  const rejectedLogs = logs.filter(log => getEffectiveDecision(log) === "REJECTED" || getDecision(log) === "FLAGged" || needsReview(log));
  const riskCounts = { RoHS: 0, REACH: 0, CE: 0, ConflictMinerals: 0, Other: 0 };
  
  rejectedLogs.forEach(log => {
    const flags = (log.Flags || "").toUpperCase();
    if (flags.includes("ROHS") || flags.includes("LEAD") || flags.includes("EXPIRED")) riskCounts.RoHS++;
    else if (flags.includes("REACH") || flags.includes("SUBSTANCE")) riskCounts.REACH++;
    else if (flags.includes("CE") || flags.includes("STANDARD") || flags.includes("SAFETY")) riskCounts.CE++;
    else if (flags.includes("CONFLICT") || flags.includes("MINERAL")) riskCounts.ConflictMinerals++;
    else riskCounts.Other++; // Captures SKU mismatches and other operational flags safely
  });

  const totalRisks = Object.values(riskCounts).reduce((a, b) => a + b, 0) || 1;
  const rohsPercent = Math.round((riskCounts.RoHS / totalRisks) * 100);
  const reachPercent = Math.round((riskCounts.REACH / totalRisks) * 100);
  const cePercent = Math.round((riskCounts.CE / totalRisks) * 100);
  const conflictPercent = Math.round((riskCounts.ConflictMinerals / totalRisks) * 100);
  const otherPercent = Math.round((riskCounts.Other / totalRisks) * 100);

  // 6-Month Compliance Chart Data Grouping
  const now = new Date();
  const last6Months = Array.from({ length: 6 }, (_, i) => {
    const d = new Date(now.getFullYear(), now.getMonth() - (5 - i), 1);
    return {
      name: d.toLocaleDateString('en-US', { month: 'short' }),
      year: d.getFullYear(),
      month: d.getMonth(),
    };
  });

  const monthlyChartData = last6Months.map(m => {
    const monthLogs = logs.filter(log => {
      const logDate = new Date(log.Timestamp);
      return !isNaN(logDate.getTime()) && logDate.getFullYear() === m.year && logDate.getMonth() === m.month;
    });
    if (monthLogs.length === 0) return { name: m.name, rate: 0 };
    const monthApproved = monthLogs.filter(log => getEffectiveDecision(log) === "APPROVED").length;
    const rate = Math.round((monthApproved / monthLogs.length) * 100);
    return { name: m.name, rate };
  });

  // Pagination Calculations
  const totalPages = Math.ceil(logs.length / ITEMS_PER_PAGE) || 1;
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedLogs = logs.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  return (
    <div className="bg-background text-on-background min-h-screen flex antialiased selection:bg-primary-container selection:text-on-primary-container overflow-hidden">
      {/* Shared Sidebar */}
      <Sidebar activePage="dashboard" />
      {/* --- UPLOAD MODAL --- */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-surface-bright w-full max-w-2xl rounded-2xl shadow-2xl border border-surface-variant flex flex-col max-h-[90vh] animate-in fade-in zoom-in-95 duration-200">
            
            <div className="flex justify-between items-center p-5 border-b border-surface-variant">
              <h2 className="text-xl font-bold font-headline-md text-on-background">Run Compliance Audit</h2>
              <button onClick={resetAndCloseModal} className="p-1.5 rounded-full hover:bg-surface-container text-on-surface-variant transition-colors">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 overflow-y-auto custom-scrollbar">
              {!auditResult ? (
                <div className="flex flex-col items-center justify-center text-center py-6">
                  <input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".pdf" className="hidden" />
                  
                  <div className="w-16 h-16 rounded-full bg-primary-container/30 text-primary flex items-center justify-center mb-4">
                    <FileUp size={32} />
                  </div>
                  
                  <h3 className="text-lg font-bold text-on-surface font-headline-sm mb-1">Upload Supplier Document</h3>
                  <p className="text-sm text-on-surface-variant max-w-sm mb-6 font-body-md">
                    Upload an SDS, RoHS certificate, or material declaration to run through the AI engine.
                  </p>

                  {selectedFile ? (
                    <div className="flex items-center gap-3 bg-surface-container px-4 py-3 rounded-xl border border-outline-variant mb-6 w-full justify-between">
                      <div className="flex items-center gap-2 overflow-hidden">
                        <FileText size={20} className="text-primary shrink-0" />
                        <span className="text-sm font-medium text-on-surface truncate">{selectedFile.name}</span>
                      </div>
                      <button onClick={() => setSelectedFile(null)} className="text-xs text-error font-medium hover:underline">Remove</button>
                    </div>
                  ) : (
                    <button onClick={() => fileInputRef.current?.click()} className="px-6 py-2.5 rounded-xl border border-outline-variant bg-surface-container-lowest text-on-surface font-medium hover:bg-surface-container transition-colors shadow-sm text-sm mb-6">
                      Browse PDF File
                    </button>
                  )}

                  {errorMsg && (
                    <div className="mb-4 p-3 bg-error-container/20 border border-error/30 text-error rounded-xl text-xs flex items-center gap-2 w-full text-left">
                      <AlertCircle size={16} className="shrink-0" /> {errorMsg}
                    </div>
                  )}

                  <button 
                    onClick={handleRunAudit}
                    disabled={!selectedFile || isProcessing}
                    className="w-full bg-primary text-on-primary font-medium py-3 px-6 rounded-xl flex items-center justify-center gap-2 hover:bg-surface-tint transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? (
                      <><div className="w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin"></div> Executing Pipeline...</>
                    ) : (
                      <><ShieldCheck size={18} /> Analyze & Generate Gap Notice</>
                    )}
                  </button>
                </div>
              ) : (
                <div className="flex flex-col gap-5">
                  <div className={`p-5 rounded-2xl border flex items-start gap-4 ${
                    auditResult.audit_result?.decision === 'APPROVED' ? 'bg-tertiary-container/10 border-tertiary/30 text-tertiary' :
                    auditResult.audit_result?.decision === 'REQUIRES_HUMAN_REVIEW' ? 'bg-red-600/10 border-red-600/40 text-red-700 animate-pulse' :
                    auditResult.audit_result?.decision === 'FLAGGED' ? 'bg-amber-100 border-amber-300 text-amber-800' :
                    'bg-error-container/10 border-error/30 text-error'
                  }`}>
                    {auditResult.audit_result?.decision === 'APPROVED' ? <CheckCircle2 size={24} className="shrink-0 mt-0.5" /> : <XCircle size={24} className="shrink-0 mt-0.5" />}
                    <div>
                      <h4 className="font-bold text-lg mb-0.5">Decision: {auditResult.audit_result?.decision || 'Reviewed'}</h4>
                      <p className="text-sm text-on-surface font-body-md">Risk Score: <strong className="font-bold">{auditResult.audit_result?.score ?? 'N/A'} / 100</strong></p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-surface-container-lowest p-4 rounded-xl border border-surface-variant flex flex-col gap-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-on-surface-variant font-label-caps">Extracted Flags</h4>
                      <div className="p-3 bg-surface-container rounded-lg border border-outline-variant font-mono text-xs text-on-surface">
                        {auditResult.audit_result?.flags && auditResult.audit_result.flags.length > 0 
                          ? JSON.stringify(auditResult.audit_result.flags, null, 2) 
                          : "No compliance infractions flagged."}
                      </div>
                    </div>
                    <div className="bg-surface-container-lowest p-4 rounded-xl border border-surface-variant flex flex-col gap-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-on-surface-variant font-label-caps">
                          Supplier Gap Notice
                        </h4>

                        <FileText size={16} className="text-primary" />
                      </div>

                      {!gapNotice ? (
                        <>
                          <p className="text-sm text-on-surface leading-relaxed font-body-md">
                            Generate a draft supplier email explaining the compliance gaps
                            identified by the audit.
                          </p>

                          <button
                            onClick={handleGenerateGapNotice}
                            disabled={gapNoticeLoading}
                            className="w-full px-3 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium hover:bg-surface-tint disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                          >
                            {gapNoticeLoading ? (
                              <>
                                <span className="w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin" />
                                Generating Draft...
                              </>
                            ) : (
                              <>
                                <FileText size={16} />
                                Generate Gap Notice
                              </>
                            )}
                          </button>
                        </>
                      ) : (
                        <>
                          <textarea
                            value={gapNotice}
                            onChange={e => setGapNotice(e.target.value)}
                            rows={8}
                            className="w-full rounded-lg border border-outline-variant bg-surface-container p-3 text-sm text-on-surface resize-y focus:outline-none focus:ring-2 focus:ring-primary/30"
                          />

                          <p className="text-[11px] text-on-surface-variant">
                            Draft only — review and edit before sending to the supplier.
                          </p>

                          <button
                            onClick={() => setGapNotice(null)}
                            className="self-start px-3 py-1.5 rounded-lg border border-outline-variant text-xs font-medium text-on-surface hover:bg-surface-container"
                          >
                            Regenerate
                          </button>
                        </>
                      )}

                      {gapNoticeError && (
                        <p className="text-xs text-error">
                          {gapNoticeError}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )
              }
            </div>

            {auditResult && (
              <div className="p-5 border-t border-surface-variant bg-surface-container-lowest rounded-b-2xl flex justify-end gap-3">
                <button onClick={() => { setAuditResult(null); setSelectedFile(null); }} className="px-4 py-2 rounded-lg border border-outline-variant bg-surface-bright text-on-surface text-sm font-medium hover:bg-surface-container transition-colors">
                  Run Another
                </button>
                <button onClick={resetAndCloseModal} className="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium hover:bg-surface-tint transition-colors shadow-sm">
                  Done
                </button>
              </div>
            )}

            {auditResult?.record_id && (
              <div className="bg-surface-container-lowest p-4 rounded-xl border border-surface-variant">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-on-surface-variant">
                      Human Review
                    </h4>

                    <p className="text-sm text-on-surface mt-1">
                      {auditResult.review_status
                        ? `Decision saved as ${auditResult.review_status}.`
                        : "AI analysis is complete. A human reviewer must make the final decision."}
                    </p>
                  </div>

                  {!auditResult.review_status && (
                    <div className="flex gap-2 shrink-0">
                      <button
                        onClick={() =>
                          handleReviewDecision(auditResult.record_id, "APPROVED")
                        }
                        disabled={reviewLoadingId === auditResult.record_id}
                        className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-tertiary text-white text-sm font-medium hover:opacity-90 disabled:opacity-50"
                      >
                        <CheckCircle2 size={16} />
                        Approve
                      </button>

                      <button
                        onClick={() =>
                          handleReviewDecision(auditResult.record_id, "REJECTED")
                        }
                        disabled={reviewLoadingId === auditResult.record_id}
                        className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-error text-white text-sm font-medium hover:opacity-90 disabled:opacity-50"
                      >
                        <XCircle size={16} />
                        Reject
                      </button>
                    </div>
                  )}
                </div>

                {reviewError && (
                  <div className="mt-3 p-2.5 rounded-lg bg-error-container/20 border border-error/20 text-error text-xs">
                    {reviewError}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
      {/* Main Content Wrapper */}
      <main className="flex-1 flex flex-col md:ml-64 h-screen overflow-hidden bg-surface-bright">
        {/* TopNavBar (Mobile Only) */}
        <header className="flex justify-between items-center px-4 w-full sticky top-0 z-50 bg-surface border-b border-outline-variant md:hidden h-16">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined cursor-pointer text-on-surface">menu</span>
            <span className="font-headline-md text-xl font-bold text-primary">Supra AI Enterprise</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined cursor-pointer text-on-surface p-1 rounded-full">notifications</span>
            <img 
              alt="Executive User Profile" 
              className="w-8 h-8 rounded-full border border-outline-variant object-cover ml-2" 
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuBiSQE5QcmIz9YRyqQoTtEDvpzNITrYyyn-8BTm-32xDNgqegMFDIA3WdhAufMpiLQPWH4WICnx4My5guHtL8rqy9oEwHVkjCGlI7UKCdhrcNks7RdHHtW-Gc9LupdAhG86mXGyexPU75sOhnIWPgFebpk-73thI_KU6iIvt9Sm1-mhRmZeIFqQgbII4D9ZzO1KWnEsjujOJh9FHxtpLmUTtucB-7Gynf8jmpRsAWtWCzUl9X5Mes4" 
            />
          </div>
        </header>

        {/* Main Scrollable Canvas */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 custom-scrollbar">
          {/* Header Section */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
            <div>
              <h2 className="text-[30px] font-bold font-headline-lg text-on-background leading-tight">Welcome back, Chleo.</h2>
              <p className="text-sm text-on-surface-variant mt-0.5 font-body-md">Here is your procurement compliance overview for today.</p>
            </div>
            {/* CTA */}
            <div className="flex gap-2">
              <button onClick={handleExport}
                className="flex items-center gap-2 bg-surface-container-highest text-on-surface px-4 py-2 rounded text-sm font-medium border border-outline-variant hover:bg-surface-container transition-colors shadow-sm"
              >
                <span className="material-symbols-outlined" data-icon="download" style={{ fontSize: '18px' }}>download</span>
                Export Report
              </button>
              {/* Trigger for the modal */}
              <button 
                onClick={() => setIsModalOpen(true)}
                className="flex items-center gap-2 bg-primary text-on-primary px-4 py-2 rounded text-sm font-medium hover:bg-surface-tint transition-colors shadow-sm"
              >
                <Plus size={18} />
                New Audit
              </button>
            </div>
          </div>

          {/* KPI Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {/* Card 1 */}
            <div className="bg-surface-container-lowest p-4 rounded-lg border border-surface-variant flex flex-col shadow-sm">
              <div className="flex justify-between items-center mb-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-label-caps">Overall Compliance</span>
                <span className="material-symbols-outlined text-tertiary text-[20px]">check_circle</span>
              </div>
              <div className="text-[30px] font-bold text-on-surface mt-1 font-headline-lg">{loading ? "..." : `${complianceRate}%`}</div>
              <div className="flex items-center gap-1 mt-2 text-tertiary text-xs font-medium">
                <span className="material-symbols-outlined text-[14px]">arrow_upward</span>
                <span>Calculated from active logs</span>
              </div>
            </div>

            {/* Card 2 */}
            <div className="bg-surface-container-lowest p-4 rounded-lg border border-surface-variant flex flex-col shadow-sm">
              <div className="flex justify-between items-center mb-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-label-caps">Pending Audits</span>
                <span className="material-symbols-outlined text-secondary text-[20px]">pending_actions</span>
              </div>
              <div className="text-[30px] font-bold text-on-surface mt-1 font-headline-lg">{loading ? "..." : pendingCount}</div>
              <div className="flex items-center gap-1 mt-2 text-secondary text-xs font-medium">
                <span>Requires review workflow</span>
              </div>
            </div>

            {/* Card 3 */}
            <div className="bg-surface-container-lowest p-4 rounded-lg border border-error-container flex flex-col relative overflow-hidden shadow-sm">
              <div className="absolute top-0 left-0 w-1 h-full bg-error"></div>
              <div className="flex justify-between items-center mb-2 pl-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-label-caps">High-Risk SKUs</span>
                <span className="material-symbols-outlined text-error text-[20px]">warning</span>
              </div>
              <div className="text-[30px] font-bold text-on-surface mt-1 pl-2 font-headline-lg">
                {loading ? "..." : highRiskCount}
              </div>
              <div className="flex items-center gap-1 mt-2 text-error pl-2 text-xs font-medium">
                <span className="material-symbols-outlined text-[14px]">info</span>
                <span>Requires immediate action</span>
              </div>
            </div>

            {/* Card 4 */}
            <div className="bg-surface-container-lowest p-4 rounded-lg border border-surface-variant flex flex-col shadow-sm">
              <div className="flex justify-between items-center mb-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-label-caps">Supplier Velocity</span>
                <span className="material-symbols-outlined text-primary text-[20px]">speed</span>
              </div>
              <div className="text-[30px] font-bold text-on-surface mt-1 font-headline-lg">2.4 <span className="text-lg font-semibold text-on-surface-variant">days</span></div>
              <div className="flex items-center gap-1 mt-2 text-tertiary text-xs font-medium">
                <span className="material-symbols-outlined text-[14px]">arrow_downward</span>
                <span>0.3 days faster</span>
              </div>
            </div>
          </div>

          {/* Bento Grid Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
            {/* Compliance Health Chart (Span 2) */}
            <div className="lg:col-span-2 bg-surface-container-lowest rounded-lg border border-surface-variant p-4 flex flex-col min-h-[300px] shadow-sm">
              <div className="flex justify-between items-center mb-4 border-b border-surface-variant pb-3">
                <h3 className="text-[18px] font-semibold text-on-surface font-headline-sm">Compliance Health (6m)</h3>
                <div className="flex gap-2">
                  <span className="px-2.5 py-1 bg-surface-container rounded text-[11px] font-bold text-on-surface-variant cursor-pointer">Monthly</span>
                  <span className="px-2.5 py-1 bg-secondary-container text-primary rounded text-[11px] font-bold cursor-pointer">Weekly</span>
                </div>
              </div>
              
              {/* Chart Visualization */}
              <div className="flex-1 flex items-end justify-between relative pt-8 pb-4">
                <div className="absolute left-0 top-0 bottom-8 flex flex-col justify-between text-on-surface-variant text-xs font-body-sm">
                  <span>100%</span>
                  <span>75%</span>
                  <span>50%</span>
                  <span>25%</span>
                  <span>0%</span>
                </div>
                <div className="absolute left-8 right-0 top-2 bottom-8 flex flex-col justify-between">
                  <div className="w-full border-b border-outline-variant opacity-30"></div>
                  <div className="w-full border-b border-outline-variant opacity-30"></div>
                  <div className="w-full border-b border-outline-variant opacity-30"></div>
                  <div className="w-full border-b border-outline-variant opacity-30"></div>
                </div>
                <div className="w-full flex justify-around items-end h-full ml-8 z-10 gap-2">
                  {monthlyChartData.map((m, i) => (
                    <div 
                      key={i} 
                      className={`w-1/6 rounded-t transition-colors relative group ${i === monthlyChartData.length - 1 ? 'bg-primary' : 'bg-primary-fixed-dim hover:bg-primary'}`}
                      style={{ height: `${Math.max(m.rate, 6)}%` }}
                    >
                      <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                        {m.rate}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex justify-around items-center ml-8 text-on-surface-variant text-xs pt-2 border-t border-outline-variant font-medium">
                {monthlyChartData.map((m, i) => (
                  <span key={i} className={i === monthlyChartData.length - 1 ? 'font-bold text-on-surface' : ''}>{m.name}</span>
                ))}
              </div>
            </div>

            {/* Risk Distribution */}
            <div className="bg-surface-container-lowest rounded-lg border border-surface-variant p-4 flex flex-col shadow-sm">
              <h3 className="text-[18px] font-semibold text-on-surface mb-4 border-b border-surface-variant pb-3 font-headline-sm">Risk Distribution</h3>
              <div className="flex-1 flex flex-col justify-center gap-4">
                <div>
                  <div className="flex justify-between items-center mb-1 text-sm font-body-md">
                    <span className="text-on-surface">RoHS Compliance</span>
                    <span className="font-bold">{rohsPercent}%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                    <div className="bg-primary h-full rounded-full transition-all duration-500" style={{ width: `${rohsPercent}%` }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1 text-sm font-body-md">
                    <span className="text-on-surface">REACH Annex</span>
                    <span className="font-bold">{reachPercent}%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                    <div className="bg-tertiary-container h-full rounded-full transition-all duration-500" style={{ width: `${reachPercent}%` }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1 text-sm font-body-md">
                    <span className="text-on-surface">CE Marking / Standards</span>
                    <span className="font-bold">{cePercent}%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                    <div className="bg-secondary h-full rounded-full transition-all duration-500" style={{ width: `${cePercent}%` }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1 text-sm font-body-md">
                    <span className="text-on-surface font-medium">Conflict Minerals</span>
                    <span className="font-bold">{conflictPercent}%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                    <div className="bg-amber-500 h-full rounded-full transition-all duration-500" style={{ width: `${conflictPercent}%` }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1 text-sm font-body-md">
                    <span className="text-on-surface-variant font-medium">Other / SKU Mismatch</span>
                    <span className="font-bold text-on-surface-variant">{otherPercent}%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                    <div className="bg-outline h-full rounded-full transition-all duration-500" style={{ width: `${otherPercent}%` }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Data Section */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 pb-8">
            {/* Recent Activity Table (Span 2) */}
            <div className="xl:col-span-2 bg-surface-container-lowest rounded-lg border border-surface-variant overflow-hidden flex flex-col shadow-sm">
              <div className="p-4 border-b border-surface-variant flex justify-between items-center bg-surface-container-lowest">
                <h3 className="text-[18px] font-semibold text-on-surface font-headline-sm">Recent Document Submissions</h3>
              </div>
              <div className="overflow-x-auto custom-scrollbar flex-1">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-surface-bright border-b border-surface-variant">
                      <th className="py-2.5 px-4 text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-label-caps">File Name</th>
                      <th className="py-2.5 px-4 text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-label-caps">SKU / Type</th>
                      <th className="py-2.5 px-4 text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-label-caps">Date Audited</th>
                      <th className="py-2.5 px-4 text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-label-caps">Status</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm font-body-md">
                    {loading ? (
                      <tr>
                        <td colSpan={4} className="py-6 px-4 text-center text-on-surface-variant">Loading audits from backend...</td>
                      </tr>
                    ) : paginatedLogs.length > 0 ? (
                      paginatedLogs.map((log, idx) => {
                        const dateObj = new Date(log.Timestamp);
                        const dateStr = isNaN(dateObj.getTime()) ? log.Timestamp : dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

                        return (
                          <tr key={idx} className="border-b border-surface-variant hover:bg-surface transition-colors">
                            <td className="py-3 px-4 font-medium text-on-surface">{log["File Name"]}</td>
                            <td className="py-3 px-4 text-on-surface-variant">{log["SKU"] || "Unknown"}</td>
                            <td className="py-3 px-4 text-on-surface-variant text-xs">{dateStr}</td>
                            <td className="py-3 px-4">
                              <div className="flex flex-col gap-2">
                                {renderStatusBadge(log)}

                                {needsReview(log) && (
                                  <div className="flex gap-1.5">
                                    <button
                                      onClick={() =>
                                        handleReviewDecision(log.RecordID, "APPROVED")
                                      }
                                      disabled={reviewLoadingId === log.RecordID}
                                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-tertiary text-white text-xs font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                      {reviewLoadingId === log.RecordID ? (
                                        <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                      ) : (
                                        <CheckCircle2 size={13} />
                                      )}
                                      Approve
                                    </button>

                                    <button
                                      onClick={() =>
                                        handleReviewDecision(log.RecordID, "REJECTED")
                                      }
                                      disabled={reviewLoadingId === log.RecordID}
                                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-error text-white text-xs font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                      <XCircle size={13} />
                                      Reject
                                    </button>
                                  </div>
                                )}
                              </div>
                            </td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td colSpan={4} className="py-6 px-4 text-center text-on-surface-variant">No audit logs found. Run a batch audit!</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Pagination Controls */}
              {!loading && logs.length > 0 && (
                <div className="p-3 border-t border-surface-variant flex flex-col sm:flex-row items-center justify-between text-xs text-on-surface-variant bg-surface-bright gap-2">
                  <span>
                    Showing <strong className="text-on-surface">{startIndex + 1}</strong> to{' '}
                    <strong className="text-on-surface">
                      {Math.min(startIndex + ITEMS_PER_PAGE, logs.length)}
                    </strong>{' '}
                    of <strong className="text-on-surface">{logs.length}</strong> results
                  </span>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                      disabled={currentPage === 1}
                      className="px-3 py-1.5 rounded border border-outline-variant bg-surface-container-lowest text-on-surface disabled:opacity-40 disabled:cursor-not-allowed hover:bg-surface-container transition-colors font-medium shadow-sm flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[14px]">chevron_left</span>
                      Previous
                    </button>
                    
                    <span className="px-2 font-medium">
                      Page {currentPage} of {totalPages}
                    </span>
                    
                    <button
                      onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                      disabled={currentPage === totalPages}
                      className="px-3 py-1.5 rounded border border-outline-variant bg-surface-container-lowest text-on-surface disabled:opacity-40 disabled:cursor-not-allowed hover:bg-surface-container transition-colors font-medium shadow-sm flex items-center gap-1"
                    >
                      Next
                      <span className="material-symbols-outlined text-[14px]">chevron_right</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Priority Actions */}
            <div className="bg-surface-container-lowest rounded-lg border border-error/20 overflow-hidden flex flex-col relative shadow-sm">
              <div className="absolute top-0 left-0 w-full h-1 bg-error"></div>
              <div className="p-4 border-b border-surface-variant bg-surface-bright flex items-center gap-2">
                <span className="material-symbols-outlined text-error">notification_important</span>
                <h3 className="text-[18px] font-semibold text-on-surface font-headline-sm">Priority Actions</h3>
              </div>
              <div className="p-4 flex flex-col gap-4 flex-1 overflow-y-auto">
                {loading ? (
                  <p className="text-xs text-on-surface-variant text-center py-4">Loading alerts...</p>
                ) : criticalAlerts.length > 0 ? (
                  criticalAlerts.map((alert, idx) => (
                    <div key={idx} className="p-3 bg-red-50/50 border border-error/20 rounded-lg flex items-start gap-3">
                      <div className="mt-1">
                        <span className="material-symbols-outlined text-error text-[18px]">policy</span>
                      </div>
                      <div className="flex-1">
                        <h4 className="text-sm font-bold text-on-surface mb-1 font-body-md">{alert["File Name"]}</h4>
                        <p className="text-xs text-on-surface-variant mb-2 font-body-sm line-clamp-2">{alert.Flags || "High-risk non-compliance flagged."}</p>
                        <div className="flex gap-2">
                          <button className="text-xs font-medium bg-white border border-outline-variant px-2.5 py-1 rounded text-on-surface hover:bg-surface-container transition-colors shadow-sm">View Details</button>
                          <button className="text-xs font-medium bg-error text-white px-2.5 py-1 rounded hover:bg-error/90 transition-colors shadow-sm">Request Doc</button>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-6 text-xs text-on-surface-variant">
                    <span className="material-symbols-outlined text-tertiary text-2xl mb-1">check_circle</span>
                    <p>No critical rejections requiring immediate attention.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}