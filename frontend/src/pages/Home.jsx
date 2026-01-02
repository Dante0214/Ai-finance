import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import Header from "../components/Header";
import SearchBar from "../components/SearchBar";
import RankingCard from "../components/RankingCard";
import { stockApi } from "../api/client";

const fetchRankings = async () => {
  const { data } = await stockApi.rankings();
  return data;
};

function Home() {
  const navigate = useNavigate();

  const { data: rankingData, isLoading: isRankingLoading } = useQuery({
    queryKey: ["usRankings"],
    queryFn: fetchRankings,
    staleTime: 1000 * 60 * 5, // 5분 캐싱
  });

  const handleSearch = (ticker) => {
    if (ticker) {
      navigate(`/analysis/${ticker}`);
    }
  };

  const handleReset = () => {
    // Already on home, maybe just clear search if we had one, but here we just route
    navigate("/");
  };

  return (
    <div className="max-w-6xl mx-auto px-4 pb-12 font-sans text-gray-900">
      <Header onReset={handleReset} />

      <SearchBar onSearch={handleSearch} />

      {isRankingLoading ? (
        <div className="py-20 text-center text-gray-500 animate-pulse">
          미국 시장 데이터를 불러오는 중입니다... 🇺🇸
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in">
          <RankingCard
            title="💰 시가총액 TOP 5"
            data={rankingData?.market_cap}
            type="cap"
            onSelect={handleSearch}
          />
          <RankingCard
            title="🔥 거래량 폭발 TOP 5"
            data={rankingData?.volume}
            type="vol"
            onSelect={handleSearch}
          />
          <RankingCard
            title="🚀 실시간 급등 TOP 5"
            data={rankingData?.gainers}
            type="rate"
            onSelect={handleSearch}
          />
        </div>
      )}
    </div>
  );
}

export default Home;
