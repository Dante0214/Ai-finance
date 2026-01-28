# 분리된 모듈들 임포트
import logging
from services.stock_definition import find_stock_info
from services.find_price import get_current_price
from services.stock_news import get_google_news, clean_company_name, get_naver_news
from services.ai import analyze_sentiment
from services.rank_kr import get_kr_current_price
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

    # 2. [가격 조회] yfinance 사용 한국 주식은 KIS 사용
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

def search_stocks(query: str, limit: int = 10):
    """
    종목 검색 서비스 로직
    (종목명, 영문명, 티커 동시 조회 및 정렬)
    """
    try:
        supabase = get_supabase_client()
        
        # 특수문자 이스케이핑
        sanitized_q = query.replace('%', '\\%').replace('_', '\\_')
        search_pattern = f"%{sanitized_q}%"
        
        # 1. DB에서 더 많은 후보군 가져오기
        fetch_limit = limit * 3
        
        response = supabase.table("stock_master")\
            .select("ticker, name_kr, name_en")\
            .or_(f"name_kr.ilike.{search_pattern},name_en.ilike.{search_pattern},ticker.ilike.{search_pattern}")\
            .limit(fetch_limit)\
            .execute()
        
        results = response.data or []
        
        # 2. Python 레벨 정렬 (정확도 우선)
        # Score 0: 정확 일치
        # Score 1: 시작 일치
        # Score 2: 포함
        
        q_upper = query.upper()
        
        def calculate_score(item):
            t = (item['ticker'] or "").upper()
            kr = (item['name_kr'] or "").upper()
            en = (item['name_en'] or "").upper()
            
            # 정확 일치 (최우선)
            if q_upper in [t, kr, en]:
                return 0
            
            # 시작 일치 (차선)
            if t.startswith(q_upper) or kr.startswith(q_upper) or en.startswith(q_upper):
                return 1
            
            return 2 # 그 외 포함
            
        # 점수 오름차순 정렬 (0 -> 1 -> 2)
        results.sort(key=calculate_score)
        
        # 3. 요청된 limit만큼 자르기
        final_results = results[:limit]
        
        return {"results": final_results, "count": len(final_results)}
        
    except Exception as e:
        logger.error(f"❌ Stock Search Error: {e}")
        # 에러 시 빈 배열 반환하여 프론트 터짐 방지
        return {"results": [], "count": 0}
