import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { stockApi, kr_stockApi } from "../api/client";

const fetchRankings = async () => {
  const { data } = await stockApi.rankings();
  return data;
};

const fetchKrRankings = async () => {
  const { data } = await kr_stockApi.rankings();
  return data;
};

export const useHomeLogic = () => {
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

  return {
    market,
    setMarket,
    rankingData,
    isRankingLoading,
    handleSearch,
  };
};
