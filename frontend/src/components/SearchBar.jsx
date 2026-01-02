import React, { useState, useEffect, useRef } from "react";
import { Search } from "lucide-react";
import { useStockSearch } from "../hooks/useStockSearch";

const SearchBar = ({ onSearch, initialValue = "", isMobile = false }) => {
  // 기본값 추가
  const [value, setValue] = useState(initialValue || ""); // 안전장치
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // 커스텀 훅 사용
  const { results, isLoading } = useStockSearch(value);

  // 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // initialValue 변경 시 동기화
  useEffect(() => {
    setValue(initialValue || "");
  }, [initialValue]);

  const handleInputChange = (e) => {
    setValue(e.target.value || "");
    const trimmedValue = (value || "").trim();
    if (trimmedValue.length > 0 && results.length > 0) {
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmedValue = (value || "").trim();
    if (trimmedValue) {
      setIsOpen(false);
      onSearch(trimmedValue.toUpperCase());
    }
  };

  const handleSelectAutoComplete = (ticker) => {
    setValue(ticker);
    setIsOpen(false);
    onSearch(ticker.toUpperCase());
  };

  const handleFocus = () => {
    const trimmedValue = (value || "").trim();
    if (trimmedValue && results.length > 0) {
      setIsOpen(true);
    }
  };
  const handleBlur = () => {
    setTimeout(() => setIsOpen(false), 150);
  };

  return (
    <div
      className={`relative w-full ${isMobile ? "" : "max-w-lg mx-auto mb-8"}`}
      ref={dropdownRef}
    >
      <form onSubmit={handleSubmit} className="flex gap-2 w-full">
        <div className="relative w-full">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          />
          <input
            type="text"
            value={value}
            onChange={handleInputChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder="종목명 또는 티커 입력 (예: TSLA, 테슬라)..."
            className="w-full pl-10 pr-4 py-3 text-base border border-gray-200 rounded-lg outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 shadow-sm"
          />
        </div>
        <button
          type="submit"
          disabled={!(value || "").trim()}
          className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-sm cursor-pointer whitespace-nowrap shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          분석
        </button>
      </form>

      {/* 자동완성 드롭다운 */}
      {isOpen && results.length > 0 && (
        <ul className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl max-h-60 overflow-y-auto">
          {results.map((item) => (
            <li
              key={item.ticker}
              onMouseDown={(e) => {
                e.preventDefault();
                handleSelectAutoComplete(item.ticker);
              }}
              className="px-4 py-3 hover:bg-blue-50 cursor-pointer flex justify-between items-center border-b last:border-none border-gray-50 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <span className="font-bold text-blue-600">{item.ticker}</span>
                <span className="ml-2 text-gray-600 text-sm truncate">
                  {item.name_kr || item.name_en}
                </span>
              </div>
              <Search size={14} className="text-gray-300 ml-2 shrink-0" />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchBar;
