"use client";

import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', content: "Hello! I'm Omni Copilot. How can I assist you today?", isUser: false }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    setInput('');

    const userMsgId = Date.now().toString();
    setMessages(prev => [...prev, { id: userMsgId, content: userText, isUser: true }]);
    setIsLoading(true);

    const aiMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: aiMsgId, content: "", isUser: false }]);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText, session_id: 'user_123' }),
      });

      if (!response.ok) throw new Error("API failed");
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            
            if (data.type === "token") {
              fullContent += data.content;
              setMessages(prev => prev.map(m => m.id === aiMsgId ? { ...m, content: fullContent } : m));
            } else if (data.type === "final_answer") {
              if (fullContent.length < 5) {
                 fullContent = data.content;
                 setMessages(prev => prev.map(m => m.id === aiMsgId ? { ...m, content: fullContent } : m));
              }
            } else if (data.type === "error") {
              setMessages(prev => prev.map(m => m.id === aiMsgId ? { ...m, content: data.content } : m));
            }
          } catch (e) {
            console.error("Parse error in stream:", e);
          }
        }
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => prev.map(m => m.id === aiMsgId ? { ...m, content: "Sorry, I encountered an error. Please ensure the backend is running." } : m));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full relative bg-background">
      {/* Background Decor */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-full pointer-events-none opacity-20 overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[30%] bg-primary/20 blur-[100px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[30%] bg-secondary/20 blur-[100px] rounded-full" />
      </div>

      <div className="flex-1 overflow-y-auto w-full custom-scrollbar pb-40">
        <div className="max-w-4xl mx-auto p-6 md:p-10">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <ChatMessage key={msg.id} content={msg.content} isUser={msg.isUser} />
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex w-full mb-10 justify-start"
            >
              <div className="flex max-w-3xl w-full gap-5">
                <div className="w-10 h-10 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center text-secondary shrink-0 shadow-sm">
                  <span className="animate-pulse font-bold text-lg">🤖</span>
                </div>
                <div className="px-6 py-5 glass-card text-slate-200 border border-slate-800 rounded-3xl rounded-tl-sm shadow-xl flex items-center gap-2 h-[64px]">
                  <motion.div
                    animate={{ scale: [1, 1.3, 1], opacity: [0.4, 1, 0.4] }}
                    transition={{ repeat: Infinity, duration: 1.2, delay: 0 }}
                    className="w-2 h-2 bg-primary rounded-full"
                  />
                  <motion.div
                    animate={{ scale: [1, 1.3, 1], opacity: [0.4, 1, 0.4] }}
                    transition={{ repeat: Infinity, duration: 1.2, delay: 0.2 }}
                    className="w-2 h-2 bg-primary rounded-full"
                  />
                  <motion.div
                    animate={{ scale: [1, 1.3, 1], opacity: [0.4, 1, 0.4] }}
                    transition={{ repeat: Infinity, duration: 1.2, delay: 0.4 }}
                    className="w-2 h-2 bg-primary rounded-full"
                  />
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <ChatInput
        input={input}
        setInput={setInput}
        handleSubmit={handleSubmit}
        isLoading={isLoading}
      />
    </div>
  );
}
