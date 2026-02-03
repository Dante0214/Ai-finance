import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import SearchBar from "../components/SearchBar";
import StockInfo from "../components/StockInfo";
import SentimentCard from "../components/SentimentCard";
import NewsList from "../components/NewsList";
import LoadingSpinner from "../components/LoadingSpinner";
import { stockApi } from "../api/client";
import useWatchlistStore from "../store/useWatchlistStore";
import { Star } from "lucide-react";
const fetchAnalysis = async (ticker) => {
  const { data } = await stockApi.analyze(ticker);
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

  return (
    <div className="max-w-6xl mx-auto px-4 pb-12 font-sans text-gray-900">
      <div className="my-6 hidden md:block">
        <SearchBar
          initialValue={searchValue}
          onSearch={handleSearch}
          isMobile={false}
        />
      </div>

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
            price={data.price !== undefined ? data.price : 0}
            companyName={data.company_name || data.ticker}
            market={data.market}
          />

          <div className="flex justify-end mt-2">
            <WatchlistButton stock={data} />
          </div>

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

function WatchlistButton({ stock }) {
  const { toggleStock, isInWatchlist, watchlist } = useWatchlistStore();
  // Check if saved using the store state directly for reactivity
  const isSaved = watchlist.some((item) => item.ticker === stock.ticker);

  return (
    <button
      onClick={() =>
        toggleStock({
          ticker: stock.ticker,
          company_name: stock.company_name || stock.ticker,
          price: stock.price,
          market: stock.market,
        })
      }
      className={`cursor-pointer flex items-center gap-2 px-4 py-2 rounded-full font-medium transition-colors ${
        isSaved
          ? "bg-yellow-100 text-yellow-700 hover:bg-yellow-200"
          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
      }`}
    >
      <Star
        className={`w-5 h-5 ${isSaved ? "fill-yellow-500 text-yellow-500" : "text-gray-500"}`}
      />
      {isSaved ? "관심 종목 저장됨" : "관심 종목 추가"}
    </button>
  );
}

export default Analysis;
