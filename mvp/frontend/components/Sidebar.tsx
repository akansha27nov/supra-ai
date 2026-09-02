import React from 'react';
import Link from 'next/link';
import { 
  LayoutDashboard, 
  ShieldCheck, 
  BarChart3, 
  HelpCircle, 
  LogOut
} from 'lucide-react';

interface SidebarProps {
  activePage: 'dashboard' | 'audits' | 'suppliers' | 'risk-matrix' | 'analytics' | 'reports';
}

export default function Sidebar({ activePage }: SidebarProps) {
  return (
    <aside className="hidden md:flex flex-col h-full py-6 gap-4 bg-surface-container-low border-r border-outline-variant h-screen w-64 fixed left-0 top-0 z-40">
      {/* Header */}
      <div className="p-6 border-b border-outline-variant flex items-center gap-3">
        <img 
          src="/logo.png" 
          alt="Supra AI Logo" 
          className="w-12 h-12 object-contain" 
        />
        <div>
          <h1 className="font-headline-sm text-[18px] font-black text-on-surface">Supra AI</h1>
          <p className="font-label-caps text-[10px] text-on-surface-variant tracking-wider uppercase font-bold">Enterprise Compliance</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 flex flex-col gap-1 px-4">
        <Link 
          href="/" 
          className={`flex items-center gap-3 px-3 py-2 rounded transition-all duration-200 font-medium text-sm ${
            activePage === 'dashboard' 
              ? 'bg-secondary-container text-on-secondary-container border-r-4 border-primary' 
              : 'text-on-surface-variant hover:bg-surface-container-high'
          }`}
        >
          <LayoutDashboard size={20} />
          Dashboard
        </Link>

        <Link 
          href="/audits" 
          className={`flex items-center gap-3 px-3 py-2 rounded transition-all duration-200 font-medium text-sm ${
            activePage === 'audits' 
              ? 'bg-secondary-container text-on-secondary-container border-r-4 border-primary' 
              : 'text-on-surface-variant hover:bg-surface-container-high'
          }`}
        >
          <ShieldCheck size={20} />
          Audits
        </Link>

    

        <Link 
          href="/analytics" 
          className={`flex items-center gap-3 px-3 py-2 rounded transition-all duration-200 font-medium text-sm ${
            activePage === 'analytics' 
              ? 'bg-secondary-container text-on-secondary-container border-r-4 border-primary' 
              : 'text-on-surface-variant hover:bg-surface-container-high'
          }`}
        >
          <BarChart3 size={20} />
          Reports
        </Link>
      </nav>
    </aside>
  );
}