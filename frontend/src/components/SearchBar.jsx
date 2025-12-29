import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

const SearchBar = ({ onSearch, initialValue }) => {
  const [value, setValue] = useState(initialValue);

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim()) {
      onSearch(value.toUpperCase());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 max-w-lg mx-auto mb-8 relative">
      <div className="relative w-full">
        <Search 
          size={18} 
          className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
        />
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Enter stock ticker (e.g., TSLA)..."
          className="w-full pl-10 pr-4 py-3 text-base border border-gray-200 rounded-lg outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 shadow-sm"
        />
      </div>
      <button 
  type="submit" 
  className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-sm cursor-pointer whitespace-nowrap shrink-0"
>
  분석
</button>
    </form>
  );
};

export default SearchBar;
