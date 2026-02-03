import { useState, useEffect, useRef } from "react";
import { useStockSearch } from "./useStockSearch";

export const useSearchBarLogic = ({ onSearch, initialValue = "" }) => {
  const [value, setValue] = useState(initialValue || "");
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
    const trimmedValue = (e.target.value || "").trim();
    if (trimmedValue.length > 0) {
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

  const handleSelectAutoComplete = (item) => {
    const displayName = item.name_kr || item.name_en;
    setValue(displayName);
    setIsOpen(false);
    onSearch(displayName);
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

  return {
    value,
    isOpen,
    dropdownRef,
    results,
    handleInputChange,
    handleSubmit,
    handleSelectAutoComplete,
    handleFocus,
    handleBlur,
  };
};
