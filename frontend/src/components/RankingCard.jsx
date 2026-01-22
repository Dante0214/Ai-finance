import React from "react";
import { Clock } from "lucide-react";

// 숫자 포맷팅 유틸리티
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
const RankingCard = ({ title, data, type, onSelect, market }) => {
  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex-1">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">{title}</h3>
        <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded">
          {market === "us" ? "NASDAQ" : "KOSPI"}
        </span>
      </div>

      {/* 데이터가 없을 때 */}
      {!data || data.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Clock size={40} className="text-gray-300 mb-3" />
          <p className="text-gray-500 font-medium mb-1">
            장 시작 시간이 아닙니다
          </p>
          <p className="text-xs text-gray-400">
            {market === "us" ? "미국 증시" : "한국 증시"} 개장 시간에 데이터가
            표시됩니다
          </p>
        </div>
      ) : (
        /* 데이터가 있을 때 */
        <div className="flex flex-col gap-2">
          {data.map((item, index) => (
            <div
              key={item.ticker}
              onClick={() => onSelect(item.name)}
              className="flex items-center justify-between group cursor-pointer hover:bg-blue-50 p-2 rounded-lg transition-colors"
            >
              <div className="flex items-center gap-3">
                {/* 순위 뱃지 */}
                <span
                  className={`w-6 h-6 flex items-center justify-center rounded-md text-xs font-bold ${
                    index === 0
                      ? "bg-yellow-100 text-yellow-700"
                      : index === 1
                      ? "bg-gray-200 text-gray-700"
                      : index === 2
                      ? "bg-orange-100 text-orange-800"
                      : "text-gray-400"
                  }`}
                >
                  {item.rank}
                </span>

                <div className="flex flex-col">
                  <span className="font-bold text-gray-900 group-hover:text-blue-600 text-sm">
                    {item.name}
                  </span>
                  <span className="text-xs text-gray-400 truncate max-w-[100px]">
                    {item.ticker}
                  </span>
                </div>
              </div>
              <div className="font-medium text-gray-900 text-sm">
                {market === "us"
                  ? `$${item.price.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}`
                  : `${item.price.toLocaleString()}원`}

                <div
                  className={`text-xs font-medium ${
                    item.rate >= 0 ? "text-green-600" : "text-red-500"
                  }`}
                >
                  {item.rate > 0 && "+"}
                  {item.rate}%
                </div>

                {/* 타입별 하단 정보 (시총, 거래량 등) */}
                <div className="text-[10px] text-gray-400 mt-0.5">
                  {type === "cap" && formatCap(item.value, market)}
                  {type === "vol" && (
                    <>
                      {market === "kr"
                        ? `${formatNum(item.volume)} Vol`
                        : `${formatNum(item.value)} Vol`}
                    </>
                  )}
                  {type === "rate" && "\u00A0"}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RankingCard;
