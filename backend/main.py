from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 기존 서비스들
from services.stock import get_stock_data
from services.ai import analyze_sentiment
# 방금 만든 랭킹 서비스 임포트
from services.kis_rank import get_rank_market_cap, get_rank_volume, get_rank_gainer

app = FastAPI()

# CORS 설정 (프론트엔드와 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 개별 종목 분석 API
@app.get("/api/analysis/{ticker}")
async def get_analysis(ticker: str):
    print(f"🔍 Analyzing: {ticker}")
    stock_data = get_stock_data(ticker)
    ai_result = analyze_sentiment(stock_data['news'])
    
    return {
        "ticker": ticker.upper(),
        "current_price": stock_data['price'],
        "news_summary": ai_result.get('summary'),
        "sentiment_score": ai_result.get('score'),
        "news_list": stock_data['news'],
        "company_name": stock_data.get('company_name')
    }

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