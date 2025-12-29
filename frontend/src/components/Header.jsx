import React from 'react';
import { Bot } from 'lucide-react';

const Header = ({onReset}) => {
  return (
    <header className="flex flex-col items-center justify-center gap-3 py-8 mb-8">
      <div 
        onClick={onReset}
        className="flex items-center justify-center p-3 text-white shadow-md bg-blue-600 rounded-xl cursor-pointer hover:bg-blue-700 transition-colors"
      >
        <Bot size={32} />
      </div>
      <div className="text-center">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">AI 주식분석기</h1>
        <p className="text-gray-500 mt-1">
          실시간 주식가격과 뉴스를 분석하여 주식의 전망을 예측합니다.
        </p>
      </div>
    </header>
  );
};

export default Header;
