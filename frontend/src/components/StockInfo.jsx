import React from "react";

const StockInfo = ({ ticker, price, companyName, market }) => {
  return (
    <div className="flex items-baseline justify-between mb-8 pb-4 border-b border-gray-200">
      <div>
        <h2 className="text-4xl font-bold text-gray-900">{companyName}</h2>
        <p className="text-lg text-gray-500 mt-1">{ticker}</p>
      </div>
      <div className="text-right">
        <div className="flex items-center gap-1 text-4xl font-bold text-gray-900">
          {market === "KR"
            ? `${price.toLocaleString()}원`
            : `$${price.toLocaleString("en-US", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`}
        </div>
      </div>
    </div>
  );
};

export default StockInfo;
