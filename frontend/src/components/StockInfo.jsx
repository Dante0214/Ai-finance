import React from 'react';

const StockInfo = ({ ticker, price, companyName }) => {
  return (
    <div className="flex items-baseline justify-between mb-8 pb-4 border-b border-gray-200">
      <div>
        <h2 className="text-4xl font-bold text-gray-900">{ticker}</h2>
        <p className="text-lg text-gray-500 mt-1">{companyName}</p>
      </div>
      <div className="text-right">
        <div className="flex items-center gap-1 text-4xl font-bold text-gray-900">
          <span className="text-2xl text-gray-400">$</span>
          {price.toFixed(2)}
        </div>
      </div>
    </div>
  );
};

export default StockInfo;
