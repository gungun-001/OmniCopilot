import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User, Copy, Check } from 'lucide-react';
import { motion } from 'framer-motion';

interface MessageProps {
  content: string;
  isUser: boolean;
}

export default function ChatMessage({ content, isUser }: MessageProps) {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={`flex w-full mb-10 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`flex max-w-[90%] md:max-w-3xl w-full group ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-5`}>
        
        {/* Avatar */}
        <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow-lg border ${
          isUser 
            ? 'bg-gradient-to-tr from-primary to-secondary text-white border-primary/20' 
            : 'bg-slate-800 border-slate-700 text-secondary'
        }`}>
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-6 h-6" />}
        </div>
        
        {/* Message Bubble */}
        <div className={`relative flex flex-col ${isUser ? 'items-end' : 'items-start'} flex-1`}>
          <div 
            className={`px-6 py-4 shadow-xl text-[15px] leading-relaxed transition-all duration-300 ${
              isUser 
                ? 'bg-primary text-white rounded-[2rem] rounded-tr-none' 
                : 'glass-card text-slate-200 border border-slate-800/50 rounded-[2rem] rounded-tl-none'
            }`}
          >
            {isUser ? (
              <div className="whitespace-pre-wrap font-medium">{content}</div>
            ) : (
              <div className="prose prose-sm md:prose-base dark:prose-invert prose-p:leading-relaxed prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-800 max-w-none prose-strong:text-secondary prose-a:text-secondary">
                <ReactMarkdown>{content}</ReactMarkdown>
              </div>
            )}
          </div>
          
          {/* Action Row */}
          {!isUser && content && (
            <div className="flex items-center mt-3 opacity-0 group-hover:opacity-100 transition-all transform translate-y-1 group-hover:translate-y-0">
              <button 
                onClick={copyToClipboard}
                className="flex items-center gap-2 px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400 hover:text-white hover:bg-slate-800/80 rounded-xl transition-all border border-transparent hover:border-slate-700"
              >
                {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
                {copied ? 'Copied' : 'Copy Response'}
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
