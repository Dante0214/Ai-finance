import React from "react";

import { Clock, Star } from "lucide-react";
import useWatchlistStore from "../store/useWatchlistStore";

// --- Utility Functions ---
const formatNum = (num) => new Intl.NumberFormat("en-US").format(num);

const formatCap = (val, market) => {
  if (!val) return "N/A";
  if (market === "us") {
    const trillionVal = val / 1_000_000_000_000;
    return `$${trillionVal.toFixed(2)}조`;
  } else {
    const trillionKRW = val / 10_000;
    return `${trillionKRW.toFixed(2)}조`;
  }
};

const formatPrice = (price, market) => {
  if (market === "us") {
    return `$${price.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  }
  return `${price.toLocaleString()}원`;
};

// --- Sub-components ---

const EmptyState = ({ market }) => (
  <div className="flex flex-col items-center justify-center py-12 text-center">
    <Clock size={40} className="text-gray-300 mb-3" />
    <p className="text-gray-500 font-medium mb-1">장 시작 시간이 아닙니다</p>
    <p className="text-xs text-gray-400">
      {market === "us" ? "미국 증시" : "한국 증시"} 개장 시간에 데이터가
      표시됩니다
    </p>
  </div>
);

const RankBadge = ({ rank }) => {
  const getBadgeStyle = (r) => {
    switch (r) {
      case 1:
        return "bg-yellow-100 text-yellow-700";
      case 2:
        return "bg-gray-200 text-gray-700";
      case 3:
        return "bg-orange-100 text-orange-800";
      default:
        return "text-gray-400";
    }
  };

  return (
    <span
      className={`w-6 h-6 flex items-center justify-center rounded-md text-xs font-bold ${getBadgeStyle(rank)}`}
    >
      {rank}
    </span>
  );
};

const RankingItem = ({ item, index, market, type, onSelect }) => {
  return (
    <div
      onClick={() => onSelect(item.name)}
      className="flex items-center justify-between group cursor-pointer hover:bg-blue-50 p-2 rounded-lg transition-colors"
    >
      <div className="flex items-center gap-3">
        <RankBadge rank={Number(item.rank)} />

        <div className="flex items-center gap-0.5">
          {/* 찜하기 버튼 (이름 옆으로 이동, 간격 좁힘) */}
          <WatchlistToggle item={item} />

          <div className="flex flex-col">
            <span className="font-bold text-gray-900 group-hover:text-blue-600 text-sm">
              {item.name}
            </span>
            <span className="text-xs text-gray-400 truncate max-w-[100px]">
              {item.ticker}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* 우측 가격 정보 */}
        <div className="font-medium text-gray-900 text-sm text-right min-w-[80px]">
          {formatPrice(item.price, market)}

          <div
            className={`text-xs font-medium ${item.rate >= 0 ? "text-green-600" : "text-red-500"}`}
          >
            {item.rate > 0 && "+"}
            {item.rate}%
          </div>

          {/* 타입별 하단 정보 (시총, 거래량 등) */}
          <div className="text-[10px] text-gray-400 mt-0.5">
            {type === "cap" && formatCap(item.value, market)}
            {type === "vol" && (
              <span>
                {market === "kr"
                  ? `${formatNum(item.volume)} Vol`
                  : `${formatNum(item.value)} Vol`}
              </span>
            )}
            {type === "rate" && "\u00A0"}
          </div>
        </div>
      </div>
    </div>
  );
};

const WatchlistToggle = ({ item }) => {
  const { watchlist, toggleStock } = useWatchlistStore();
  const isSaved = watchlist.some((s) => s.ticker === item.ticker);

  const handleToggle = (e) => {
    e.stopPropagation();
    toggleStock({
      ticker: item.ticker,
      company_name: item.name, // Ranking items have 'name', not 'company_name' sometimes? need to check
      price: item.price,
      market: item.market || "US", // Ranking items usually from API, market might need to be passed down if not in item
    });
  };

  return (
    <button
      onClick={handleToggle}
      className="p-1.5 rounded-full hover:bg-gray-100 transition-colors z-10 cursor-pointer"
    >
      <Star
        className={`w-4 h-4 ${isSaved ? "fill-yellow-400 text-yellow-400" : "text-gray-300 hover:text-gray-400"}`}
      />
    </button>
  );
};

// --- Main Component ---

const RankingCard = ({ title, data, type, onSelect, market }) => {
  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex-1">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">{title}</h3>
        <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded">
          {market === "us" ? "NASDAQ" : "KOSPI"}
        </span>
      </div>

      {!data || data.length === 0 ? (
        <EmptyState market={market} />
      ) : (
        <div className="flex flex-col gap-2">
          {data.map((item, index) => (
            <RankingItem
              key={`${item.ticker}-${index}`}
              item={{ ...item, market: market }} // Pass market explicitly to item
              index={index}
              market={market}
              type={type}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default RankingCard;
