import React, { useRef, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { motion } from 'framer-motion';

interface ChatInputProps {
  input: string;
  setInput: (val: string) => void;
  handleSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
}

export default function ChatInput({ input, setInput, handleSubmit, isLoading }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [input]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="absolute bottom-0 w-full bg-gradient-to-t from-background via-background/80 to-transparent pt-10 pb-8 px-6 md:px-12">
      <div className="max-w-4xl mx-auto relative">
        <motion.form 
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          onSubmit={handleSubmit} 
          className="relative shadow-2xl rounded-[2rem] border border-slate-800/50 bg-slate-900/80 backdrop-blur-xl flex flex-col focus-within:border-primary/50 focus-within:ring-4 focus-within:ring-primary/10 transition-all duration-300"
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Message Omni Copilot..."
            className="flex-1 max-h-[200px] min-h-[64px] w-full resize-none p-5 pb-16 outline-none bg-transparent text-slate-100 placeholder:text-slate-500 custom-scrollbar text-[16px]"
            disabled={isLoading}
            rows={1}
          />
          
          <div className="absolute bottom-3 left-3 right-3 flex justify-between items-center">
            <button
              type="button"
              className="p-2.5 text-slate-500 hover:text-white hover:bg-slate-800 rounded-2xl transition-all"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="w-12 h-12 flex items-center justify-center btn-premium rounded-2xl disabled:opacity-30 disabled:grayscale disabled:cursor-not-allowed transition-all shadow-lg"
            >
              <Send className="w-5 h-5 ml-1" />
            </button>
          </div>
        </motion.form>
        <div className="text-center text-[10px] uppercase tracking-[0.2em] font-bold text-slate-600 mt-4">
          Omni Copilot can make mistakes. Consider verifying important information.
        </div>
      </div>
    </div>
  );
}
