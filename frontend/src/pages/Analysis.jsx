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

// 환경 변수 설정
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
//const API_BASE_URL = "http://127.0.0.1:8000";

const fetchAnalysis = async (ticker) => {
  const { data } = await axios.get(`${API_BASE_URL}/api/analysis/${ticker}`);
  return data;
};

function Analysis() {
  const { ticker } = useParams(); // URL에서 ticker 가져오기 (예: /analysis/AAPL)
  const navigate = useNavigate();

  // 검색창 상태 관리
  const [searchValue, setSearchValue] = useState(ticker || "");

  // URL의 ticker가 바뀌면 검색창 값도 동기화
  useEffect(() => {
    if (ticker) {
      setSearchValue(ticker);
    }
  }, [ticker]);

  // 데이터 쿼리
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["stock", ticker], // 티커가 바뀌면 쿼리 키도 바뀜 -> 자동 재요청
    queryFn: () => fetchAnalysis(ticker),
    staleTime: 1000 * 60 * 5, // 5분 캐싱
    retry: 1,
    enabled: !!ticker, // 티커가 있을 때만 실행
  });

  const handleSearch = (newTicker) => {
    if (newTicker) {
      // URL 이동 -> useParams 변경 -> useEffect 실행 -> useQuery 실행
      navigate(`/analysis/${newTicker}`);
    }
  };

  const handleReset = () => {
    navigate("/");
  };

  return (
    <div className="max-w-6xl mx-auto px-4 pb-12 font-sans text-gray-900">
      {/* 1. 데스크톱 헤더 */}
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

      {/* 2. 모바일 헤더 */}
      <MobileHeader onReset={handleReset}>
        <SearchBar
          initialValue={searchValue}
          onSearch={handleSearch}
          isMobile={true}
        />
      </MobileHeader>

      {/* 3. 로딩 및 에러 처리 */}
      {isLoading && <LoadingSpinner />}

      {isError && (
        <div className="mt-8 p-4 bg-red-50 text-red-700 rounded-lg text-center border border-red-200 animate-fade-in">
          <p className="font-bold">Error</p>
          <p className="text-sm">{error.message}</p>
          <button
            onClick={() => navigate("/")}
            className="mt-2 text-blue-600 underline text-sm"
          >
            홈으로 돌아가기
          </button>
        </div>
      )}

      {/* 4. 분석 결과 표시 */}
      {data && (
        <div className="animate-fade-in">
          <StockInfo
            ticker={data.ticker}
            // [중요] 백엔드 키값 확인 필요 (current_price vs price)
            price={data.price !== undefined ? data.price : data.current_price}
            companyName={data.company_name || data.ticker}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start mt-6">
            {/* 감성 분석 결과가 없더라도 에러가 나지 않게 방어 코드 추가 */}
            <SentimentCard
              score={data.sentiment_score || 50}
              summary={data.news_summary || "분석된 뉴스 요약이 없습니다."}
            />
            <NewsList news={data.news || []} />
          </div>
        </div>
      )}
    </div>
  );
}

export default Analysis;
