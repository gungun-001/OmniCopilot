import React from 'react';

interface MessageProps {
  content: string;
  isUser: boolean;
}

export default function MessageBubble({ content, isUser }: MessageProps) {
  return (
    <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className="flex max-w-3xl w-full">
        {!isUser && (
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold mr-4 shrink-0">
            AI
          </div>
        )}
        <div 
          className={`flex-1 p-4 rounded-xl shadow-sm ${
            isUser 
              ? 'bg-blue-50 text-gray-800 rounded-tr-none ml-auto max-w-xl' 
              : 'bg-white border border-gray-100 text-gray-800'
          }`}
        >
          <div className="prose prose-sm max-w-none whitespace-pre-wrap">
            {content}
          </div>
        </div>
      </div>
    </div>
  );
}
