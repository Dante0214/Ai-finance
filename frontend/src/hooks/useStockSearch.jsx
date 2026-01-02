import { useState, useEffect } from "react";
import { stockApi } from "../api/client";

export const useStockSearch = (searchTerm = "", delay = 300) => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const trimmedTerm = (searchTerm || "").trim();
    if (!trimmedTerm) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await stockApi.search(trimmedTerm);
        setResults(response.data.results || []);
      } catch (err) {
        console.error("Stock search error:", err);
        setError(err);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, delay);

    return () => clearTimeout(timer);
  }, [searchTerm, delay]);

  return { results, isLoading, error };
};
