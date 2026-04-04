import React from 'react';

export default function OptionCard({ option, onSelect, disabled }) {
  return (
    <button
      onClick={() => onSelect(option.id)}
      disabled={disabled}
      className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
        disabled 
          ? 'opacity-50 cursor-not-allowed border-gray-200 bg-gray-50' 
          : 'border-brand-200 bg-white hover:border-brand-500 hover:shadow-md cursor-pointer'
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-brand-100 text-brand-700 font-bold text-sm">
          {option.id}
        </span>
        <span className="font-semibold text-gray-900 text-lg">{option.label}</span>
      </div>
      <p className="text-gray-600 text-sm">{option.description}</p>
    </button>
  );
}
