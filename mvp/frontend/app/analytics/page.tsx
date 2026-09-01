"use client";

import React, { useState, useEffect } from 'react';
import { useChat } from '@ai-sdk/react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { Bot, Send, History, Terminal, FileSpreadsheet } from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import { fetchAuditLogs, AuditLog } from '@/lib/api';

export default function AnalyticsDashboard() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch logs from API on mount
  useEffect(() => {
    const loadLogs = async () => {
      try {
        const data = await fetchAuditLogs();
        setLogs(data);
      } catch (error) {
        console.error("Error loading analytics data:", error);
      } finally {
        setLoading(false);
      }
    };
    loadLogs();
  }, []);

  const { messages, input, handleInputChange, handleSubmit } = useChat({
    initialMessages: [
      { id: '1', role: 'user', content: "Analyze Global Packaging Ltd's recent critical safety finding." },
      { id: '2', role: 'assistant', content: "The safety finding involves improper hazardous material storage. Recommend immediate CAPA issuance. Similar past incidents with this supplier took avg 12 days to resolve." }
    ]
  });

  // --- DYNAMIC CALCULATIONS ---
  const totalLogs = logs.length;
  const approvedCount = logs.filter(log => log.Decision === "APPROVED").length;
  const complianceRate = totalLogs ? ((approvedCount / totalLogs) * 100).toFixed(1) : "0.0";
  
  const pendingCount = logs.filter(log => log.Decision === "MANUAL_REVIEW").length;
  const highRiskCount = logs.filter(log => log.Decision === "REJECTED").length;

  // Risk Distribution Tally based on rejected log flags
  const rejectedLogs = logs.filter(log => log.Decision === "REJECTED");
  const riskCounts = { RoHS: 0, REACH: 0, CE: 0, ConflictMinerals: 0 };
  
  rejectedLogs.forEach(log => {
    const flags = (log.Flags || "").toUpperCase();
    if (flags.includes("ROHS") || flags.includes("LEAD") || flags.includes("EXPIRED")) riskCounts.RoHS++;
    if (flags.includes("REACH") || flags.includes("SUBSTANCE")) riskCounts.REACH++;
    if (flags.includes("CE") || flags.includes("STANDARD") || flags.includes("SAFETY")) riskCounts.CE++;
    if (flags.includes("CONFLICT") || flags.includes("MINERAL")) riskCounts.ConflictMinerals++;
  });

  const totalRisks = Object.values(riskCounts).reduce((a, b) => a + b, 0) || 1;
  const rohsPercent = Math.round((riskCounts.RoHS / totalRisks) * 100);
  const reachPercent = Math.round((riskCounts.REACH / totalRisks) * 100);
  const cePercent = Math.round((riskCounts.CE / totalRisks) * 100);
  const conflictPercent = 100 - (rohsPercent + reachPercent + cePercent);

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
    const monthApproved = monthLogs.filter(log => log.Decision === "APPROVED").length;
    const rate = Math.round((monthApproved / monthLogs.length) * 100);
    return { name: m.name, rate };
  });

  return (
    <div className="bg-background text-on-background min-h-screen flex antialiased selection:bg-primary-container selection:text-on-primary-container overflow-hidden">
      {/* Shared Sidebar with 'analytics' active */}
      <Sidebar activePage="analytics" />

      {/* Resizable Panels Container (Dashboard View vs AI Co-Pilot) */}
      <PanelGroup direction="horizontal" className="flex-1 md:ml-64 h-screen">
        
        {/* Main Analytics Content Panel (Showing Dashboard View) */}
        <Panel defaultSize={75} minSize={50} className="flex flex-col h-screen">
          <main className="flex-1 overflow-y-auto p-4 md:p-8 bg-surface-bright custom-scrollbar">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
              <div>
                <h2 className="text-[30px] font-bold font-headline-lg text-on-background leading-tight">Portfolio Analytics & Overview</h2>
                <p className="text-sm text-on-surface-variant mt-0.5 font-body-md">High-level compliance overview and procurement intelligence.</p>
              </div>
              <div className="flex gap-2">
                <button className="flex items-center gap-2 bg-surface-container-highest text-on-surface px-4 py-2 rounded text-sm font-medium border border-outline-variant hover:bg-surface-container transition-colors shadow-sm">
                    <span className="material-symbols-outlined" data-icon="download" style={{ fontSize: '18px' }}>download</span>
                    Export Report
                </button>
                <button className="flex items-center gap-2 bg-primary text-on-primary px-4 py-2 rounded text-sm font-medium hover:bg-surface-tint transition-colors shadow-sm">
                  <span className="material-symbols-outlined" data-icon="done_all" style={{ fontSize: '18px' }}>done_all</span>
                  Run Batch Audit
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
                <div className="text-[30px] font-bold text-on-surface mt-1 pl-2 font-headline-lg">{loading ? "..." : highRiskCount}</div>
                <div className="flex items-center gap-1 mt-2 text-error pl-2 text-xs font-medium">
                  <span className="material-symbols-outlined text-[14px]">arrow_upward</span>
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
                <div className="flex-1 flex flex-col justify-center gap-5">
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
                      <span className="text-on-surface">CE Marking</span>
                      <span className="font-bold">{cePercent}%</span>
                    </div>
                    <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                      <div className="bg-secondary h-full rounded-full transition-all duration-500" style={{ width: `${cePercent}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between items-center mb-1 text-sm font-body-md">
                      <span className="text-error font-medium">Conflict Minerals</span>
                      <span className="font-bold text-error">{conflictPercent}%</span>
                    </div>
                    <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                      <div className="bg-error h-full rounded-full transition-all duration-500" style={{ width: `${conflictPercent}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </Panel>

        {/* Resizable Divider Handle */}
        <PanelResizeHandle className="w-[1px] bg-outline-variant hover:w-1.5 hover:bg-primary-container transition-all cursor-col-resize z-10" />

        {/* AI Co-Pilot Panel */}
        <Panel defaultSize={25} minSize={20} className="bg-surface-container-lowest border-l border-outline-variant flex flex-col relative shadow-sm h-screen">
          <div className="px-6 py-5 border-b border-outline-variant/50">
            <div className="font-headline-sm text-base font-bold text-tertiary flex items-center gap-2">
              <Bot size={18} /> AI Co-Pilot
            </div>
            <div className="text-on-surface-variant text-xs mt-0.5">Contextual Intelligence Engine</div>
          </div>
          
          <nav className="flex flex-col text-sm py-2">
            <span className="flex items-center gap-3 px-6 py-2.5 border-l-4 border-tertiary bg-tertiary-container/10 text-tertiary font-medium"><Bot size={16}/> Co-Pilot Chat</span>
            <span className="flex items-center gap-3 px-6 py-2.5 border-l-4 border-transparent text-on-surface-variant hover:bg-surface-container cursor-pointer"><History size={16}/> History</span>
            <span className="flex items-center gap-3 px-6 py-2.5 border-l-4 border-transparent text-on-surface-variant hover:bg-surface-container cursor-pointer"><Terminal size={16}/> Prompts</span>
            <span className="flex items-center gap-3 px-6 py-2.5 border-l-4 border-transparent text-on-surface-variant hover:bg-surface-container cursor-pointer"><FileSpreadsheet size={16}/> Reports</span>
          </nav>

          {/* Vercel AI SDK Chat Interface */}
          <div className="mt-auto px-5 pb-5 h-[340px] flex flex-col border-t border-outline-variant pt-4">
            <div className="flex-1 overflow-y-auto space-y-3 mb-4 pr-1 text-sm">
              {messages.map((m) => (
                <div key={m.id} className={`p-3 rounded-xl border text-xs leading-relaxed ${m.role === 'user' ? 'bg-surface-container rounded-tl-none border-outline-variant/25' : 'bg-tertiary-container/10 rounded-tr-none border-tertiary/20'}`}>
                  {m.role === 'assistant' && <span className="font-bold text-tertiary mb-1 flex items-center gap-1.5"><Bot size={13}/> Supra AI</span>}
                  {m.content}
                </div>
              ))}
            </div>
            <form onSubmit={handleSubmit} className="relative mt-auto">
              <input value={input} onChange={handleInputChange} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg py-2.5 pl-3 pr-10 text-xs focus:border-tertiary focus:ring-1 focus:ring-tertiary outline-none transition-all shadow-sm" placeholder="Ask Co-Pilot about regulations, CAPAs..." />
              <button type="submit" className="absolute right-3 top-1/2 -translate-y-1/2 text-tertiary hover:text-tertiary-container">
                <Send size={15} />
              </button>
            </form>
          </div>
        </Panel>

      </PanelGroup>
    </div>
  );
}