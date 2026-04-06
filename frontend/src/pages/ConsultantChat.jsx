import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import ChatBubble from '../components/ChatBubble';
import OptionCard from '../components/OptionCard';
import { startChat, sendChatMessage, sendChatChoice, getChatHistory } from '../api';
import { Send } from 'lucide-react';

export default function ConsultantChat() {
  const [farmer, setFarmer] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const data = localStorage.getItem('farmer');
    if (!data) {
      navigate('/login');
      return;
    }
    const parsedFarmer = JSON.parse(data);
    setFarmer(parsedFarmer);
    
    // Check if we have an existing session
    const existingSession = localStorage.getItem('chat_session_id');
    if (existingSession) {
      setSessionId(parseInt(existingSession));
      loadHistory(parseInt(existingSession), parsedFarmer.language_preference || 'en');
    } else {
      initChat(parsedFarmer.id, parsedFarmer.language_preference || 'en');
    }
  }, [navigate]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const loadHistory = async (sid, lang = 'en') => {
    try {
      const res = await getChatHistory(sid, lang);
      setMessages(res.data.messages);
    } catch (e) {
      // If session not found, start new
      const data = localStorage.getItem('farmer');
      const parsedFarmer = data ? JSON.parse(data) : null;
      initChat(farmer?.id || parsedFarmer?.id, farmer?.language_preference || parsedFarmer?.language_preference || 'en');
    }
  };

  const initChat = async (fid, lang = 'en') => {
    setIsLoading(true);
    try {
      const res = await startChat(fid, lang);
      setSessionId(res.data.session_id);
      localStorage.setItem('chat_session_id', res.data.session_id);
      setMessages([res.data.message]);
    } catch (e) {
      console.error('Failed to start chat', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const lang = farmer.language_preference || 'en';
      const res = await sendChatMessage(farmer.id, sessionId, userMsg.content, lang);
      setMessages(prev => [...prev, res.data.message]);
    } catch (e) {
      console.error('Failed to send message', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptionSelect = async (messageId, optionId) => {
    setIsLoading(true);
    try {
      const lang = farmer.language_preference || 'en';
      const res = await sendChatChoice(farmer.id, sessionId, messageId, optionId, lang);
      setMessages(prev => [
        ...prev, 
        { role: 'user', content: `I selected option ${optionId}.` }, 
        res.data.message
      ]);
    } catch (e) {
      console.error('Failed to select option', e);
    } finally {
      setIsLoading(false);
    }
  };

  if (!farmer) return null;

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <main className="flex flex-col flex-1 relative h-full">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-8 py-4 shadow-sm z-10 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Consultant Chat</h1>
            <p className="text-sm text-gray-500">Your AI-powered farming advisor</p>
          </div>
          {farmer.language_preference && farmer.language_preference !== 'en' && (
            <span className="px-3 py-1 bg-brand-100 text-brand-700 text-xs font-bold rounded-full uppercase">
              Mode: {farmer.language_preference}
            </span>
          )}
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-8 pb-32">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((msg, idx) => (
              <div key={idx}>
                <ChatBubble 
                  role={msg.role} 
                  content={msg.content} 
                  metrics={msg.metrics}
                  agents={msg.agents}
                />
                
                {/* Render Options if they exist on an assistant message */}
                {msg.role === 'assistant' && msg.options && (
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 pl-4 pr-16">
                    {msg.options.map(opt => (
                      <OptionCard 
                        key={opt.id} 
                        option={opt} 
                        // Disable if not the latest message to prevent retroactive choices
                        disabled={idx !== messages.length - 1} 
                        onSelect={(optId) => handleOptionSelect(msg.id, optId)} 
                      />
                    ))}
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && <ChatBubble role="assistant" isThinking={true} />}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 w-full bg-white border-t border-gray-200 p-4">
          <div className="max-w-4xl mx-auto relative">
            <form onSubmit={handleSend} className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Ask about crops, weather, subsidies..."
                className="flex-1 border border-gray-300 rounded-full px-6 py-3 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent bg-gray-50 transition-all"
                disabled={isLoading}
              />
              <button 
                type="submit"
                disabled={!input.trim() || isLoading}
                className="bg-brand-600 hover:bg-brand-500 text-white rounded-full p-3 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
