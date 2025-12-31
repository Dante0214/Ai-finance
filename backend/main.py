from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.kis_rank import get_rank_market_cap, get_rank_volume, get_rank_gainer
from services.stock import get_stock_data

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
async def get_analysis(query: str):
    # 이제 get_stock_data 내부에서 
    # DB조회 -> 가격조회 -> 뉴스수집을 알아서 수행합니다.
    return get_stock_data(query)

# 2. [랭킹 API] 프론트엔드가 호출하는 주소
@app.get("/api/us/rankings")
def us_rankings():
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