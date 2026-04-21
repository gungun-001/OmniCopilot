import React from 'react';
import { Plus, MessageSquare, Settings, PanelLeftClose } from 'lucide-react';
import { cn } from '@/utils/cn';

interface SidebarProps {
  isOpen: boolean;
  closeSidebar: () => void;
}

export default function Sidebar({ isOpen, closeSidebar }: SidebarProps) {
  return (
    <div 
      className={cn(
        "fixed md:relative z-40 h-full w-[280px] bg-slate-900/50 backdrop-blur-xl border-r border-slate-800/50 flex flex-col transition-transform duration-300 ease-in-out shrink-0",
        isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}
    >
      <div className="p-5 flex items-center justify-between">
        <button className="flex-1 flex items-center justify-center gap-2 btn-premium p-3 rounded-2xl transition-all shadow-lg font-semibold text-sm">
          <Plus className="w-5 h-5" />
          <span>New Chat</span>
        </button>
        <button onClick={closeSidebar} className="p-2 ml-2 hover:bg-slate-800 rounded-xl md:hidden text-slate-400 transition-colors">
          <PanelLeftClose className="w-5 h-5" />
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto px-4 py-2 custom-scrollbar">
        <div className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-4 px-2">History</div>
        <div className="space-y-2">
          <button className="w-full text-left flex items-center gap-3 px-4 py-3 rounded-2xl bg-primary/10 border border-primary/20 text-white text-sm font-medium group transition-all hover:bg-primary/20">
            <MessageSquare className="w-4 h-4 text-secondary" />
            <span className="truncate">Schedule Team Sync</span>
          </button>
          <button className="w-full text-left flex items-center gap-3 px-4 py-3 rounded-2xl hover:bg-slate-800/50 text-slate-400 hover:text-white text-sm font-medium transition-all group border border-transparent hover:border-slate-700">
            <MessageSquare className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" />
            <span className="truncate">Drive Analysis</span>
          </button>
        </div>
      </div>
      
      <div className="p-5 border-t border-slate-800/50">
        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-2xl hover:bg-slate-800/50 text-slate-400 hover:text-white text-sm font-medium transition-all border border-transparent hover:border-slate-700">
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </button>
      </div>
    </div>
  );
}
