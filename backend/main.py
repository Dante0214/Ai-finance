from fastapi import FastAPI,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from services.kis_rank import get_rank_market_cap, get_rank_volume, get_rank_gainer
from services.rank_kr import get_all_stock_rankings
from services.stock import get_stock_data
from supabase import create_client, Client
import os

app = FastAPI()

# CORS 설정
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ai-finance-coral.vercel.app", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
supabase = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_SERVICE_KEY")
)


# 1. 개별 종목 분석 API
@app.get("/api/analysis/{query}")
async def get_analysis(query: str):
    """
    개별 종목 분석 API
    (가격 조회 + 뉴스 수집)
    """
    return get_stock_data(query)

# 2. [랭킹 API] 프론트엔드가 호출하는 주소
@app.get("/api/us/rankings")
def us_rankings():
    """
    미국 랭킹 API
    (거래량 순위 + 시가총액 순위 + 급등주 순위 동시 조회)
    """
    print("📊 Fetching US Rankings...") # 로그 확인용
    try:
        # 나스닥(NAS) 기준으로 데이터 가져오기
        cap = get_rank_market_cap("NAS")
        vol = get_rank_volume("NAS")
        gain = get_rank_gainer("NAS")
        
        return {
            "market_cap": cap,
            "volume": vol,
            "gainers": gain
        }
    except Exception as e:
        print(f"❌ Ranking Error: {e}")
        return {"market_cap": [], "volume": [], "gainers": []}

@app.get("/api/stock-search")
async def stock_search(q: str = Query(..., min_length=1, max_length=50, description="검색어")):
    """
    종목 검색 API
    (종목명, 영문명, 티커 동시 조회)
    """
    try:
        # 특수문자 이스케이핑
        sanitized_q = q.replace('%', '\\%').replace('_', '\\_')
        search_pattern = f"%{sanitized_q}%"
        
        response = supabase.table("stock_master")\
            .select("ticker, name_kr, name_en")\
            .or_(f"name_kr.ilike.{search_pattern},name_en.ilike.{search_pattern},ticker.ilike.{search_pattern}")\
            .limit(10)\
            .execute()
        
        return {"results": response.data, "count": len(response.data)}
        
    except Exception as e:
        print(f"❌ Stock Search Error: {e}")
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다")


@app.get("/api/kr/rankings")
def kr_rankings():
    """
    한국투자증권 통합 API
    (거래량 순위 + 시가총액 순위 + 급등주 순위 동시 조회)
    """
    print("🔍 Fetching KR API (Volume & Market Cap & Gainer)...")
    
    # 모든 랭킹 데이터를 한 번에 가져오기
    try:
        # 서비스 함수에서 데이터 가져오기
        all_rankings = get_all_stock_rankings()
        
        return {
            "market_cap": all_rankings.get("market_cap", []),
            "volume": all_rankings.get("volume", []),
            "gainers": all_rankings.get("gainers", [])          }
    except Exception as e:
        print(f"❌ KR Ranking Error: {e}")
        return {"market_cap": [], "volume": [], "gainers": []}

