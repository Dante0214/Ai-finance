import React from "react";
import Header from "./Header";
import MobileHeader from "./MobileHeader";
import SearchBar from "./SearchBar";
import { useLocation, useNavigate } from "react-router-dom";

const Layout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const isAnalysisPage = location.pathname.startsWith("/analysis/");
  const ticker = isAnalysisPage
    ? decodeURIComponent(location.pathname.split("/")[2] || "")
    : "";

  const handleSearch = (name) => {
    if (name) {
      navigate(`/analysis/${name}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* 
        기본 헤더: 
        - 데스크탑: 항상 표시
        - 모바일: Analysis 페이지가 아닐 때만 표시 
      */}
      <div className={isAnalysisPage ? "hidden md:block" : "block"}>
        <Header />
      </div>

      {/* 
        모바일 헤더:
        - 모바일: Analysis 페이지일 때만 표시
        - 데스크탑: 항상 숨김 (MobileHeader 내부에서 md:hidden 처리되어 있어도 여기서 제어 명확화)
      */}
      {isAnalysisPage && (
        <div className="md:hidden">
          <MobileHeader>
            <SearchBar
              onSearch={handleSearch}
              initialValue={ticker}
              isMobile={true}
            />
          </MobileHeader>
        </div>
      )}

      <main className="container mx-auto px-4 py-6">{children}</main>
    </div>
  );
};

export default Layout;
