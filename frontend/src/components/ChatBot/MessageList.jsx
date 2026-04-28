import { useEffect, useRef } from 'react';
import Message from './Message';

export default function MessageList({ messages, isLoading }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {messages.map((msg, idx) => (
        <Message key={idx} message={msg} isUser={msg.isUser} />
      ))}
      
      {isLoading && (
        <div className="flex justify-start mb-4">
          <div className="bg-gray-100 rounded-lg rounded-bl-none px-4 py-3 max-w-[80%]">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg">🌱</span>
              <span className="text-xs font-semibold text-gray-600">CarbonIQ Assistant</span>
            </div>
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
}
