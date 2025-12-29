from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.stock import get_stock_data
from services.ai import analyze_sentiment
from services.kis_rank import (
    get_rank_market_cap,
    get_rank_volume,
    get_rank_gainer,
)

app = FastAPI()

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

@app.get("/api/analysis/{ticker}")
async def get_analysis(ticker: str):
    stock_data = get_stock_data(ticker)
    ai_result = analyze_sentiment(stock_data["news"])

    return {
        "ticker": ticker.upper(),
        "current_price": stock_data["price"],
        "news_summary": ai_result.get("summary"),
        "sentiment_score": ai_result.get("score"),
        "news_list": stock_data["news"],
        "company_name": stock_data.get("company_name"),
    }

@app.get("/api/us/rankings")
def us_rankings():
    cap = get_rank_market_cap("NAS")
    vol = get_rank_volume("NAS")
    gain = get_rank_gainer("NAS")

    return {
        "market_cap": cap,
        "volume": vol,
        "gainers": gain,
    }
