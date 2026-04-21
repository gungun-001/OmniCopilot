import React from 'react';
import { Menu, User, Settings } from 'lucide-react';

interface HeaderProps {
  toggleSidebar: () => void;
}

export default function Header({ toggleSidebar }: HeaderProps) {
  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800/50 bg-slate-900/60 backdrop-blur-xl sticky top-0 z-20">
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleSidebar} 
          className="p-2 hover:bg-slate-800 rounded-xl md:hidden text-slate-200 transition-all active:scale-95"
        >
          <Menu className="w-6 h-6" />
        </button>
        <div className="font-bold text-xl flex items-center text-white tracking-tighter">
          OmniCopilot <span className="ml-3 text-[9px] uppercase font-black px-2.5 py-0.5 bg-gradient-main text-white rounded-full shadow-lg">Beta</span>
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        <button className="p-2.5 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition-all">
          <Settings className="w-5 h-5" />
        </button>
        <button className="w-10 h-10 rounded-2xl bg-gradient-main flex items-center justify-center text-white shadow-lg ring-4 ring-slate-900 hover:scale-110 transition-all duration-300">
          <User className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}
