import React, { useRef, useEffect, useState } from 'react';
import { Send, Paperclip, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface ChatInputProps {
  input: string;
  setInput: (val: string) => void;
  handleSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
  attachedFile: { filename: string; content: string } | null;
  setAttachedFile: (file: { filename: string; content: string } | null) => void;
}

export default function ChatInput({ 
  input, 
  setInput, 
  handleSubmit, 
  isLoading, 
  attachedFile, 
  setAttachedFile 
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

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

  const handlePaperclipClick = () => {
    if (isUploading) return;
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const response = await fetch(`${apiUrl}/api/chat/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setAttachedFile({
        filename: data.filename,
        content: data.content,
      });
    } catch (err: any) {
      console.error('File upload error:', err);
      setUploadError(err.message || 'Failed to upload and parse file.');
      setTimeout(() => setUploadError(null), 5000); // Clear error after 5s
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = ''; // Reset file input
      }
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
          {/* Hidden File Input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept=".pdf,.txt,.py,.js,.ts,.tsx,.json,.csv,.md,.html,.css"
          />

          {/* Attached File Preview Badge */}
          {attachedFile && (
            <div className="mx-5 mt-4 p-3 flex items-center justify-between glass-card border border-slate-800/60 bg-slate-950/50 rounded-2xl max-w-sm">
              <div className="flex items-center gap-3">
                <span className="text-xl">📄</span>
                <div className="flex flex-col">
                  <span className="text-slate-200 text-sm font-semibold truncate max-w-[220px]">{attachedFile.filename}</span>
                  <span className="text-[10px] text-primary font-bold uppercase tracking-wider">Ready to analyze</span>
                </div>
              </div>
              <button 
                type="button" 
                onClick={() => setAttachedFile(null)} 
                className="p-1.5 hover:bg-slate-800 text-slate-400 hover:text-white rounded-lg transition-all"
              >
                <span className="text-xs font-bold">✕</span>
              </button>
            </div>
          )}

          {/* Upload Status / Error Indicator */}
          {uploadError && (
            <div className="mx-5 mt-4 text-xs text-red-400 font-semibold bg-red-950/20 border border-red-900/30 p-2.5 rounded-xl">
              ⚠️ {uploadError}
            </div>
          )}

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder={isUploading ? "Uploading & parsing file..." : "Message Omni Copilot..."}
            className="flex-1 max-h-[200px] min-h-[64px] w-full resize-none p-5 pb-16 outline-none bg-transparent text-slate-100 placeholder:text-slate-500 custom-scrollbar text-[16px]"
            disabled={isLoading || isUploading}
            rows={1}
          />
          
          <div className="absolute bottom-3 left-3 right-3 flex justify-between items-center">
            <button
              type="button"
              onClick={handlePaperclipClick}
              disabled={isLoading || isUploading}
              className="p-2.5 text-slate-500 hover:text-white hover:bg-slate-800 rounded-2xl transition-all disabled:opacity-50 flex items-center justify-center"
            >
              {isUploading ? (
                <Loader2 className="w-5 h-5 animate-spin text-primary" />
              ) : (
                <Paperclip className="w-5 h-5" />
              )}
            </button>
            
            <button
              type="submit"
              disabled={isLoading || isUploading || (!input.trim() && !attachedFile)}
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
