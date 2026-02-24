from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# 서비스 모듈 임포트
from services.kis_rank_us import get_all_us_rankings
from services.kis_rank_kr import get_all_stock_rankings
from services.stock import get_stock_data
from services.stock_definition import search_stocks
from services.kis_price import get_current_price
from services.kis_kr_price import get_kr_current_price

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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

# 1. 개별 종목 분석 API
@app.get("/api/analysis/{query}")
def get_analysis(query: str):
    """
    개별 종목 분석 API
    (가격 조회 + 뉴스 수집)
    """
    return get_stock_data(query)

# 2. [랭킹 API] 미국 (비동기)
@app.get("/api/us/rankings")
async def us_rankings():
    """
    미국 랭킹 API
    (거래량 순위 + 시가총액 순위 + 급등주 순위 동시 조회)
    """
    logger.info("📊 Fetching US Rankings (Async Parallel)...")
    return await get_all_us_rankings()

# 3. 종목 검색 API
@app.get("/api/stock-search")
def stock_search(q: str = Query(..., min_length=1, max_length=50, description="검색어")):
    """
    종목 검색 API
    (종목명, 영문명, 티커 동시 조회)
    """
    try:
        return search_stocks(q)
    except Exception as e:
        logger.error(f"❌ Stock Search Error: {e}")
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다")

# 4. [랭킹 API] 한국 (비동기)
@app.get("/api/kr/rankings")
async def kr_rankings():
    """
    한국투자증권 통합 API
    (거래량 순위 + 시가총액 순위 + 급등주 순위 동시 조회)
    """
    logger.info("🔍 Fetching KR Rankings (Async Parallel)...")
    return await get_all_stock_rankings()


# 5. [즐겨찾기] 일괄 현재가 조회 API
class WatchlistItem(BaseModel):
    ticker: str
    market: str  # "US" 또는 "KR"

class WatchlistPriceRequest(BaseModel):
    items: list[WatchlistItem]

@app.post("/api/watchlist/prices")
def watchlist_prices(request: WatchlistPriceRequest):
    """
    즐겨찾기 종목들의 최신 가격을 일괄 조회합니다.
    각 종목의 ticker와 market을 받아 해당 API로 현재가를 조회합니다.
    """
    logger.info(f"⭐ [Watchlist] {len(request.items)}개 종목 현재가 일괄 조회 시작")
    
    prices = {}
    for item in request.items:
        try:
            if item.market.upper() == "KR":
                price = get_kr_current_price(item.ticker)
            else:
                price = get_current_price(item.ticker)
            
            prices[item.ticker] = price if price else 0
        except Exception as e:
            logger.error(f"❌ [Watchlist] {item.ticker} 가격 조회 실패: {e}")
            prices[item.ticker] = 0
    
    logger.info(f"✅ [Watchlist] 일괄 조회 완료: {prices}")
    return {"prices": prices}
