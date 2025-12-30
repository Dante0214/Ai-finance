import React from 'react';
import { ThumbsUp, ThumbsDown, Minus } from 'lucide-react';

const SentimentCard = ({ score, summary }) => {
  let colorClass = 'text-yellow-700 bg-yellow-50 border-yellow-200';
  let barColorClass = 'bg-yellow-500';
  let Icon = Minus;
  let label = 'Neutral';

  if (score >= 60) {
    colorClass = 'text-emerald-700 bg-emerald-50 border-emerald-200';
    barColorClass = 'bg-emerald-500';
    Icon = ThumbsUp;
    label = 'Positive';
  } else if (score <= 40) {
    colorClass = 'text-red-700 bg-red-50 border-red-200';
    barColorClass = 'bg-red-500';
    Icon = ThumbsDown;
    label = 'Negative';
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-800">AI Analysis</h3>
        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold border ${colorClass}`}>
          <Icon size={14} />
          {label}
        </div>
      </div>
      
      <div className="mb-6">
        <div className="flex justify-between mb-2 text-sm text-gray-500">
          <span>Score</span>
          <span className="font-bold text-gray-900">{score} / 100</span>
        </div>
        <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
          <div 
            className={`h-full rounded-full transition-all duration-1000 ease-out ${barColorClass}`} 
            style={{ width: `${score}%` }} 
          />
        </div>
      </div>

      <div className="h-full bg-gray-50 rounded-xl p-4 text-gray-700 leading-relaxed border border-gray-100">
        <p>{summary}</p>
      </div>
    </div>
  );
};

export default SentimentCard;
