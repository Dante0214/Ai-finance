import { useNavigate } from "react-router-dom";
import { Star } from "lucide-react";
import useWatchlistStore from "../store/useWatchlistStore";

function WatchlistSection() {
  const { watchlist, removeStock } = useWatchlistStore();
  const navigate = useNavigate();

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
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Star className="w-6 h-6 text-yellow-500 fill-yellow-500" />
        즐겨 찾기
      </h2>
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
