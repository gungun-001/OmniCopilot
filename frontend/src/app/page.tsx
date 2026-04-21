"use client";

import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import Intro from '@/components/Intro';
import Auth from '@/components/Auth';
import ChatLayout from '@/components/ChatLayout';
import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  const [view, setView] = useState<'intro' | 'auth' | 'chat'>('intro');

  useEffect(() => {
    const token = localStorage.getItem('omni_token');
    
    const timer = setTimeout(() => {
      if (token) {
        setView('chat');
      } else {
        setView('auth');
      }
    }, 5000); // 5 seconds splash

    return () => clearTimeout(timer);
  }, []);

  return (
    <main className="h-screen w-full bg-background selection:bg-primary/30">
      <AnimatePresence mode="wait">
        {view === 'intro' && <Intro key="intro" />}
        
        {view === 'auth' && (
          <Auth key="auth" onLogin={() => setView('chat')} />
        )}

        {view === 'chat' && (
          <ChatLayout key="chat">
            <ChatInterface />
          </ChatLayout>
        )}
      </AnimatePresence>
    </main>
  );
}
