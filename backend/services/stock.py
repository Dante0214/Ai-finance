# 분리된 모듈들 임포트
import logging
from services.stock_definition import find_stock_info
from services.kis_price import get_current_price
from services.stock_news import get_google_news, clean_company_name, get_naver_news
from services.ai import analyze_sentiment
from services.kis_kr_price import get_kr_current_price
from services.auth import get_supabase_client

# 로거 설정
logger = logging.getLogger(__name__)

def get_stock_data(query: str):
    logger.info(f"🔍 [Analyzing] '{query}' 요청 처리 시작...")

    is_korean_stock = False
    ticker = query.upper()
    display_name = query
    search_name = query

    # 1. [종목 식별] Supabase에서 정보 찾기
    info = find_stock_info(query)
    
    if info:
        ticker = info['ticker']
        name_kr = info['name_kr']
        name_en = info['name_en']
        
        logger.info(f"🏢 [Identify] 식별 성공: {name_kr} ({ticker})")
        
        # 화면에 보여줄 이름 (한글 우선)
        display_name = name_kr if name_kr else name_en
        is_korean_stock = not name_en or name_en == name_kr
        if is_korean_stock:
            search_name = name_kr
        else:
            # 뉴스 검색용 이름 (영문명에서 Inc 제거)
            search_name = clean_company_name(name_en)

        
        
    else:
        logger.warning(f"⚠️ [Identify] 식별 실패. 검색어('{query}')를 티커로 간주합니다.")

    # 2. [가격 조회] 해외주식은 KIS 해외주식 현재가 API, 한국 주식은 KIS 국내주식 현재가 API 사용
    if is_korean_stock:
        price = get_kr_current_price(ticker)
    else:
        price = get_current_price(ticker)

    # 3. [뉴스 수집] Google RSS 사용
    if is_korean_stock:
        news = get_naver_news(search_name)
    else:
        news = get_google_news(search_name)
    ai_result = analyze_sentiment(news,is_korean=is_korean_stock)

    # 4. 최종 결과 반환
    return {
        "market": "KR" if is_korean_stock else "US",
        "ticker": ticker,
        "price": price,
        "news": news,
        "company_name": display_name,
        "sentiment_score": ai_result['score'],
        "news_summary": ai_result['summary']
    }
