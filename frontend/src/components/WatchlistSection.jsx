import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Star, RefreshCw } from "lucide-react";
import useWatchlistStore from "../store/useWatchlistStore";
import { stockApi } from "../api/client";

function WatchlistSection() {
  const { watchlist, removeStock, updatePrices } = useWatchlistStore();
  const navigate = useNavigate();
  const [isRefreshing, setIsRefreshing] = useState(false);

  // 즐겨찾기 현재가 자동 새로고침 (컴포넌트 마운트 시)
  const refreshPrices = async () => {
    if (watchlist.length === 0) return;

    setIsRefreshing(true);
    try {
      const items = watchlist.map((s) => ({
        ticker: s.ticker,
        market: s.market || "US",
      }));

      const res = await stockApi.watchlistPrices(items);
      if (res.data?.prices) {
        updatePrices(res.data.prices);
      }
    } catch (err) {
      console.error("⚠️ 즐겨찾기 가격 갱신 실패:", err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    refreshPrices();
  }, []); // 마운트 시 1회 실행

  if (watchlist.length === 0) return null;

  const formatPrice = (price, market) => {
    if (!price) return "-";

    const isUS =
      market === "US" ||
      market === "us" ||
      market === "NASDAQ" ||
      market === "NYSE";

    if (isUS) {
      return `$${price.toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`;
    } else {
      return `${Number(price).toLocaleString()}원`;
    }
  };

  return (
    <div className="mb-10 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Star className="w-6 h-6 text-yellow-500 fill-yellow-500" />
          즐겨 찾기
        </h2>
        <button
          onClick={refreshPrices}
          disabled={isRefreshing}
          className={`${isRefreshing ? "cursor-not-allowed" : "cursor-pointer"} flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors disabled:opacity-50`}
          title="현재가 새로고침"
        >
          <RefreshCw
            className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`}
          />
          {isRefreshing ? "갱신 중..." : "새로고침"}
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {watchlist.map((stock) => (
          <div
            key={stock.ticker}
            onClick={() => navigate(`/analysis/${stock.ticker}`)}
            className="bg-white p-4 rounded-xl shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-100"
          >
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeStock(stock.ticker);
                  }}
                  className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                  title="관심 종목 해제"
                >
                  <Star className="w-5 h-5 fill-yellow-500 text-yellow-500" />
                </button>
                <div>
                  <h3 className="font-bold text-lg leading-tight">
                    {stock.company_name}
                  </h3>
                  <span className="text-sm text-gray-500">{stock.ticker}</span>
                </div>
              </div>
              <div className="text-right">
                <span className="font-mono font-semibold block">
                  {formatPrice(stock.price, stock.market)}
                </span>
                <span className="text-xs text-gray-400">{`${stock.market.toUpperCase()}`}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default WatchlistSection;
