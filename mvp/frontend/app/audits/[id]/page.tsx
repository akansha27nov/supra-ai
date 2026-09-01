"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { ArrowLeft, CheckCircle, XCircle, FileText, AlertTriangle, ShieldAlert } from 'lucide-react';
import { fetchAuditLogs, AuditLog } from '@/lib/api';

export default function AuditDetailPage() {
  const router = useRouter();
  const params = useParams();
  const auditId = params?.id as string || '1';

  const [audit, setAudit] = useState<AuditLog | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAudit = async () => {
      try {
        const logs = await fetchAuditLogs();
        const found = logs.find((l, idx) => String(l.id || idx + 1) === auditId) || logs[0];
        setAudit(found || null);
      } catch (error) {
        console.error("Failed to load audit detail:", error);
      } finally {
        setLoading(false);
      }
    };
    loadAudit();
  }, [auditId]);

  if (loading) {
    return (
      <div className="bg-background text-on-background min-h-screen flex items-center justify-center">
        <p className="text-sm text-on-surface-variant animate-pulse">Loading audit details...</p>
      </div>
    );
  }

  if (!audit) {
    return (
      <div className="bg-background text-on-background min-h-screen flex items-center justify-center flex-col gap-4">
        <p className="text-lg font-bold">Audit not found</p>
        <button onClick={() => router.push('/audits')} className="px-4 py-2 bg-primary text-on-primary rounded">Back to Audits</button>
      </div>
    );
  }

  const riskScore = audit.Score ?? 50;
  const isHighRisk = riskScore > 75 || audit.Decision === "REJECTED";

  return (
    <div className="bg-background text-on-background min-h-screen flex antialiased selection:bg-primary-container selection:text-on-primary-container overflow-hidden">
      <Sidebar activePage="audits" />

      <main className="flex-1 flex flex-col md:ml-64 h-screen overflow-hidden bg-surface-bright">
        {/* Header */}
        <header className="flex justify-between items-center px-6 w-full sticky top-0 z-50 bg-surface border-b border-outline-variant h-16">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => router.push('/audits')}
              className="p-2 rounded-lg hover:bg-surface-container transition-colors text-on-surface-variant"
              title="Back to Audits"
            >
              <ArrowLeft size={20} />
            </button>
            <h2 className="text-xl font-bold text-on-background font-headline-md">Audit Details #{auditId}</h2>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border flex items-center gap-1 ${isHighRisk ? 'bg-error-container/20 text-error border-error/20' : 'bg-secondary-container/20 text-secondary border-secondary/20'}`}>
              <AlertTriangle size={12} /> {audit.Decision || 'Pending'} ({riskScore})
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => alert("Audit rejected successfully")} className="flex items-center gap-2 px-4 py-2 bg-error text-on-error rounded text-sm font-medium hover:opacity-90 transition-opacity shadow-sm">
              <XCircle size={16} /> Reject Audit
            </button>
            <button onClick={() => alert("Audit approved successfully")} className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary rounded text-sm font-medium hover:bg-surface-tint transition-colors shadow-sm">
              <CheckCircle size={16} /> Approve Audit
            </button>
          </div>
        </header>

        {/* Content Canvas */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 custom-scrollbar grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Metadata & AI Analysis */}
          <div className="lg:col-span-1 flex flex-col gap-6">
            <div className="bg-surface-container-lowest p-6 rounded-lg border border-surface-variant shadow-sm flex flex-col gap-4">
              <h3 className="text-lg font-bold font-headline-sm text-on-surface">Supplier Information</h3>
              <div className="flex flex-col gap-2 text-sm">
                <div className="flex justify-between py-1 border-b border-surface-variant">
                  <span className="text-on-surface-variant">Supplier Name</span>
                  <span className="font-medium text-on-surface">{audit.Supplier}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-surface-variant">
                  <span className="text-on-surface-variant">SKU / Item</span>
                  <span className="font-medium text-on-surface">{audit.SKU}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-surface-variant">
                  <span className="text-on-surface-variant">Submission Date</span>
                  <span className="font-medium text-on-surface">{audit.Timestamp ? new Date(audit.Timestamp).toLocaleString() : 'N/A'}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-on-surface-variant">Risk Score</span>
                  <span className={`font-bold ${isHighRisk ? 'text-error' : 'text-primary'}`}>{riskScore} / 100</span>
                </div>
              </div>
            </div>

            <div className="bg-surface-container-lowest p-6 rounded-lg border border-surface-variant shadow-sm flex flex-col gap-4">
              <h3 className="text-lg font-bold font-headline-sm text-on-surface flex items-center gap-2">
                <ShieldAlert size={18} className="text-error" /> AI Compliance Findings
              </h3>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                {audit.Reasoning || audit.Flags || "No specific compliance findings recorded for this audit entry."}
              </p>
            </div>
          </div>

          {/* Right Column: Document Viewer Mock */}
          <div className="lg:col-span-2 bg-surface-container-lowest p-6 rounded-lg border border-surface-variant shadow-sm flex flex-col h-[600px]">
            <div className="flex items-center justify-between pb-4 border-b border-surface-variant mb-4">
              <h3 className="text-sm font-bold font-label-caps text-on-surface uppercase tracking-wider flex items-center gap-2">
                <FileText size={16} className="text-primary" /> Document Preview
              </h3>
              <span className="text-xs text-on-surface-variant">Page 1 of 1</span>
            </div>
            <div className="flex-1 bg-surface-container rounded border border-outline-variant flex items-center justify-center text-on-surface-variant flex-col gap-3">
              <FileText size={48} className="text-outline" />
              <p className="text-sm font-medium">{audit.Document || `${audit.SKU}_Compliance_Doc.pdf`}</p>
              <span className="text-xs text-on-surface-variant/70">Preview rendering active (API Source)</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}