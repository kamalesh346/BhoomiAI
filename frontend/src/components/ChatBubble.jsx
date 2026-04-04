import React from 'react';
import { 
  Radar, RadarChart, PolarGrid, 
  PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer 
} from 'recharts';

export default function ChatBubble({ role, content, isThinking, metrics }) {
  const isUser = role === 'user';
  
  if (isThinking) {
    return (
      <div className="flex w-full mt-4 justify-start">
        <div className="max-w-[80%] rounded-2xl px-5 py-3 bg-white border border-gray-200 shadow-sm text-gray-800">
          <div className="flex space-x-2 items-center h-5">
            <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex w-full mt-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-[80%] rounded-2xl px-5 py-3 shadow-sm ${
          isUser 
            ? 'bg-brand-600 text-white rounded-br-none' 
            : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none'
        }`}
      >
        <div className="text-sm mb-1 opacity-80 font-medium">
          {isUser ? '👨‍🌾 You' : '🌾 Digital Sarathi'}
        </div>
        <div className="whitespace-pre-wrap">{content}</div>
        
        {metrics && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={metrics}>
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#4b5563', fontSize: 12 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar
                    name="Metrics"
                    dataKey="A"
                    stroke="#10b981"
                    fill="#10b981"
                    fillOpacity={0.5}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {metrics.map((m, i) => (
                <div key={i} className="flex items-center justify-between text-xs px-2 py-1 bg-gray-50 rounded">
                  <span className="text-gray-500">{m.subject}</span>
                  <span className="font-bold text-brand-700">{m.A}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
