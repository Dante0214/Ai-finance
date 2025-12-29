import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-gray-500">
      <div className="w-10 h-10 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin mb-4" />
      <p>Analyzing market data...</p>
    </div>
  );
};

export default LoadingSpinner;
