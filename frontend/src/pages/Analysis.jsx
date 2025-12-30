import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import Header from "../components/Header";
import SearchBar from "../components/SearchBar";
import StockInfo from "../components/StockInfo";
import SentimentCard from "../components/SentimentCard";
import NewsList from "../components/NewsList";
import LoadingSpinner from "../components/LoadingSpinner";
import MobileHeader from "../components/MobileHeader";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const fetchAnalysis = async (ticker) => {
  const { data } = await axios.get(`${API_BASE_URL}/api/analysis/${ticker}`);
  return data;
};

function Analysis() {
  const { ticker } = useParams();
  const navigate = useNavigate();

  const [searchValue, setSearchValue] = useState(ticker || "");

  useEffect(() => {
    if (ticker) {
      setSearchValue(ticker);
    }
  }, [ticker]);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["stock", ticker],
    queryFn: () => fetchAnalysis(ticker),
    staleTime: 1000 * 60 * 5,
    retry: 1,
    enabled: !!ticker,
  });

  const handleSearch = (newTicker) => {
    if (newTicker) {
      navigate(`/analysis/${newTicker}`);
    }
  };

  const handleReset = () => {
    navigate("/");
  };

  return (
    <div className="max-w-6xl mx-auto px-4 pb-12 font-sans text-gray-900">
      {/* 데스크톱 헤더 */}
      <div className="hidden md:block">
        <Header onReset={handleReset} />
        <div className="my-6 md:my-0">
          <SearchBar
            initialValue={searchValue}
            onSearch={handleSearch}
            isMobile={false}
          />
        </div>
      </div>

      {/* 모바일 헤더 */}
      <MobileHeader onReset={handleReset}>
        <SearchBar
          initialValue={searchValue}
          onSearch={handleSearch}
          isMobile={true}
        />
      </MobileHeader>

      {isLoading && <LoadingSpinner />}

      {isError && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg text-center border border-red-200">
          Error: {error.message}. Please try again later.
        </div>
      )}

      {data && (
        <div className="animate-fade-in">
          <StockInfo
            ticker={data.ticker}
            price={data.current_price}
            companyName={data.company_name || data.ticker}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
            <SentimentCard
              score={data.sentiment_score}
              summary={data.news_summary}
            />
            <NewsList news={data.news_list} />
          </div>
        </div>
      )}
    </div>
  );
}

export default Analysis;
