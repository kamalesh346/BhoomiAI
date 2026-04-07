import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import ChatBubble from '../components/ChatBubble';
import OptionCard from '../components/OptionCard';
import { 
  startChat, 
  sendChatMessage, 
  sendChatChoice, 
  getChatHistory,
  transcribeAudio,
  synthesizeSpeech
} from '../api';
import { Send, Mic, Square, Volume2, VolumeX } from 'lucide-react';

export default function ConsultantChat() {
  const [farmer, setFarmer] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioPlayerRef = useRef(new Audio());
  const navigate = useNavigate();

  useEffect(() => {
    const data = localStorage.getItem('farmer');
    if (!data) {
      navigate('/login');
      return;
    }
    const parsedFarmer = JSON.parse(data);
    setFarmer(parsedFarmer);
    
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
      const assistantMsg = res.data.message;
      setMessages([assistantMsg]);
      
      if (voiceEnabled) {
        playVoice(assistantMsg);
      }
    } catch (e) {
      console.error('Failed to start chat', e);
    } finally {
      setIsLoading(false);
    }
  };

  const playVoice = async (msg) => {
    if (!msg || !msg.content || isLoading) return;
    
    console.log("[Voice] Playback requested for message content:", msg.content.substring(0, 30));

    let audioSrc = msg.audio;

    if (!audioSrc) {
      console.log("[Voice] Audio data missing from message, fetching from server...");
      try {
        const lang = farmer.language_preference || 'en';
        const res = await synthesizeSpeech(msg.content, lang);
        if (res.data.size > 0) {
          audioSrc = URL.createObjectURL(res.data);
          console.log("[Voice] Fetched audio Blob size:", res.data.size);
        } else {
          console.warn("[Voice] Received empty audio Blob from server");
          return;
        }
      } catch (e) {
        console.error('[Voice] TTS Fetch Error:', e);
        return;
      }
    } else {
      console.log("[Voice] Using pre-generated audio (length:", audioSrc.length, ")");
    }

    try {
      console.log("[Voice] Setting audio src and playing...");
      audioPlayerRef.current.pause();
      audioPlayerRef.current.src = audioSrc;
      audioPlayerRef.current.load();
      
      audioPlayerRef.current.oncanplaythrough = async () => {
        try {
          await audioPlayerRef.current.play();
          console.log("[Voice] Playback started successfully!");
        } catch (e) {
          console.error("[Voice] Playback error during start:", e);
        }
      };
      
      audioPlayerRef.current.onerror = (e) => {
        console.error("[Voice] Audio player error event:", e);
      };
      
    } catch (e) {
      console.error('[Voice] General Playback Error:', e);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        handleVoiceSubmit(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (e) {
      console.error('Microphone access denied', e);
      alert('Could not access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleVoiceSubmit = async (blob) => {
    setIsLoading(true);
    try {
      const res = await transcribeAudio(blob);
      const text = res.data.text;
      if (text) {
        await processMessage(text);
      }
    } catch (e) {
      console.error('Transcription failed', e);
    } finally {
      setIsLoading(false);
    }
  };

  const processMessage = async (text) => {
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const lang = farmer.language_preference || 'en';
      const res = await sendChatMessage(farmer.id, sessionId, text, lang);
      const assistantMsg = res.data.message;
      setMessages(prev => [...prev, assistantMsg]);
      
      if (voiceEnabled) {
        playVoice(assistantMsg);
      }
    } catch (e) {
      console.error('Failed to send message', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    const text = input;
    setInput('');
    await processMessage(text);
  };

  const handleOptionSelect = async (messageId, optionId) => {
    setIsLoading(true);
    try {
      const lang = farmer.language_preference || 'en';
      const res = await sendChatChoice(farmer.id, sessionId, messageId, optionId, lang);
      const assistantMsg = res.data.message;
      
      setMessages(prev => [
        ...prev, 
        { role: 'user', content: `I selected option ${optionId}.` }, 
        assistantMsg
      ]);

      if (voiceEnabled) {
        playVoice(assistantMsg);
      }
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
          <div className="flex items-center gap-4">
            <button 
              onClick={() => {
                setVoiceEnabled(!voiceEnabled);
                if (voiceEnabled) audioPlayerRef.current.pause();
              }}
              className={`p-2 rounded-full transition-all ${voiceEnabled ? 'bg-brand-100 text-brand-600 shadow-inner' : 'bg-gray-100 text-gray-400'}`}
              title={voiceEnabled ? "Voice: ON (Auto-play)" : "Voice: OFF (Manual only)"}
            >
              {voiceEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
            </button>
            {farmer.language_preference && farmer.language_preference !== 'en' && (
              <span className="px-3 py-1 bg-brand-100 text-brand-700 text-xs font-bold rounded-full uppercase">
                Mode: {farmer.language_preference}
              </span>
            )}
          </div>
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
                  onPlayVoice={() => playVoice(msg)}
                />
                
                {msg.role === 'assistant' && msg.options && (
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 pl-4 pr-16">
                    {msg.options.map(opt => (
                      <OptionCard 
                        key={opt.id} 
                        option={opt} 
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
            <form onSubmit={handleSend} className="flex gap-2 items-center">
              <button
                type="button"
                onMouseDown={startRecording}
                onMouseUp={stopRecording}
                onMouseLeave={stopRecording}
                className={`rounded-full p-4 transition-all ${
                  isRecording 
                    ? 'bg-red-500 text-white animate-pulse scale-110' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                title="Hold to speak"
              >
                {isRecording ? <Square className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
              </button>

              <div className="flex-1 relative flex items-center">
                <input
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder={isRecording ? "Listening..." : "Ask about crops, weather, subsidies..."}
                  className="w-full border border-gray-300 rounded-full px-6 py-3 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent bg-gray-50 transition-all"
                  disabled={isLoading || isRecording}
                />
                <button 
                  type="submit"
                  disabled={!input.trim() || isLoading || isRecording}
                  className="absolute right-2 bg-brand-600 hover:bg-brand-500 text-white rounded-full p-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </form>
            {isRecording && (
              <div className="text-center text-xs text-red-500 font-medium mt-2 animate-bounce">
                Recording... Release to send
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
