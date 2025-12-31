# 분리된 모듈들 임포트
from services.stock_definition import find_stock_info
from services.find_price import get_current_price
from services.stock_news import get_google_news, clean_company_name
from services.ai import analyze_sentiment
def get_stock_data(query: str):
    print(f"🔍 [Analyzing] '{query}' 요청 처리 시작...")

    ticker = query.upper()
    display_name = query
    search_name = query

    # 1. [종목 식별] Supabase에서 정보 찾기
    info = find_stock_info(query)
    
    if info:
        ticker = info['ticker']
        name_kr = info['name_kr']
        name_en = info['name_en']
        
        print(f"🏢 [Identify] 식별 성공: {name_kr} ({ticker})")
        
        # 화면에 보여줄 이름 (한글 우선)
        display_name = name_kr if name_kr else name_en
        
        # 뉴스 검색용 이름 (영문명에서 Inc 제거)
        search_name = clean_company_name(name_en)
    else:
        print(f"⚠️ [Identify] 식별 실패. 검색어('{query}')를 티커로 간주합니다.")

    # 2. [가격 조회] yfinance 사용
    price = get_current_price(ticker)

    # 3. [뉴스 수집] Google RSS 사용
    news = get_google_news(search_name)
    ai_result = analyze_sentiment(news)

    # 4. 최종 결과 반환
    return {
        "ticker": ticker,
        "price": price,
        "news": news,
        "company_name": display_name,
        "sentiment_score": ai_result['score'],
        "news_summary": ai_result['summary']
    }