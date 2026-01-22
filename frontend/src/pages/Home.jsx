import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import Header from "../components/Header";
import SearchBar from "../components/SearchBar";
import RankingCard from "../components/RankingCard";
import { stockApi, kr_stockApi } from "../api/client";
import { useState } from "react";
const fetchRankings = async () => {
  const { data } = await stockApi.rankings();
  return data;
};
const fetchKrRankings = async () => {
  const { data } = await kr_stockApi.rankings();
  return data;
};

function Home() {
  const navigate = useNavigate();
  const [market, setMarket] = useState("us");

  const { data: usRankingData, isLoading: isUsRankingLoading } = useQuery({
    queryKey: ["usRankings"],
    queryFn: fetchRankings,
    staleTime: 1000 * 60 * 5, // 5분 캐싱
  });

  const { data: krRankingData, isLoading: isKrRankingLoading } = useQuery({
    queryKey: ["krRankings"],
    queryFn: fetchKrRankings,
    staleTime: 1000 * 60 * 5, // 5분 캐싱
  });

  const rankingData = market === "us" ? usRankingData : krRankingData;
  const isRankingLoading =
    market === "us" ? isUsRankingLoading : isKrRankingLoading;

  const handleSearch = (name) => {
    if (name) {
      navigate(`/analysis/${name}`);
    }
  };

  const handleReset = () => {
    navigate("/");
  };
  console.log(rankingData);

  return (
    <div className="max-w-6xl mx-auto px-4 pb-12 font-sans text-gray-900">
      <Header onReset={handleReset} />

      <SearchBar onSearch={handleSearch} />
      <div className="flex justify-center gap-4 mb-8">
        <button
          onClick={() => setMarket("us")}
          className={`px-6 py-3 rounded-lg font-semibold transition-all cursor-pointer ${
            market === "us"
              ? "bg-blue-600 text-white shadow-lg scale-105"
              : "bg-gray-200 text-gray-600 hover:bg-gray-300"
          }`}
        >
          🇺🇸 미국 시장
        </button>
        <button
          onClick={() => setMarket("kr")}
          className={`px-6 py-3 rounded-lg font-semibold transition-all cursor-pointer ${
            market === "kr"
              ? "bg-blue-600 text-white shadow-lg scale-105"
              : "bg-gray-200 text-gray-600 hover:bg-gray-300"
          }`}
        >
          🇰🇷 한국 시장
        </button>
      </div>

      {isRankingLoading ? (
        <div className="py-20 text-center text-gray-500 animate-pulse">
          {market === "us" ? "🇺🇸 미국" : "🇰🇷 한국"} 시장 데이터를 불러오는
          중입니다...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in">
          <RankingCard
            title="💰 시가총액 TOP 5"
            data={rankingData?.market_cap}
            type="cap"
            onSelect={handleSearch}
            market={market}
          />
          <RankingCard
            title="🔥 거래량 폭발 TOP 5"
            data={rankingData?.volume}
            type="vol"
            onSelect={handleSearch}
            market={market}
          />
          <RankingCard
            title="🚀 실시간 급등 TOP 5"
            data={rankingData?.gainers}
            type="rate"
            onSelect={handleSearch}
            market={market}
          />
        </div>
      )}
    </div>
  );
}

export default Home;
