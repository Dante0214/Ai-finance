import React from "react";
import { Clock } from "lucide-react";

// 숫자 포맷팅 유틸리티
const formatNum = (num) => new Intl.NumberFormat("en-US").format(num);
const formatCap = (val) =>
  val >= 1000 ? `$${(val / 1000).toFixed(1)}T` : `$${val.toFixed(1)}B`;

const RankingCard = ({ title, data, type, onSelect }) => {
  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex-1">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">{title}</h3>
        <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded">
          NASDAQ
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
            미국 증시 개장 시간에 데이터가 표시됩니다
          </p>
        </div>
      ) : (
        /* 데이터가 있을 때 */
        <div className="flex flex-col gap-2">
          {data.map((item, index) => (
            <div
              key={item.ticker}
              onClick={() => onSelect(item.ticker)}
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
                    {item.ticker}
                  </span>
                  <span className="text-xs text-gray-400 truncate max-w-[100px]">
                    {item.name}
                  </span>
                </div>
              </div>

              <div className="text-right">
                <div className="font-medium text-gray-900 text-sm">
                  ${item.price.toFixed(2)}
                </div>

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
                  {type === "cap" && formatCap(item.value)}
                  {type === "vol" && `${formatNum(item.value)} Vol`}
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
