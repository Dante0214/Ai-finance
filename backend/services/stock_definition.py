import os
import logging
from supabase import create_client
from dotenv import load_dotenv
from services.auth import get_supabase_client

load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)

supabase = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_SERVICE_KEY")
)

def find_stock_info(query: str):
    """
    Supabase DB에서 종목 정보를 찾습니다.
    우선순위:
    1. 티커 정확 일치 (AAPL)
    2. 이름 정확 일치 (애플, Apple)
    3. 이름 포함 검색 (애플...)
    """
    query = query.strip().upper()
    
    try:
        # 1. [우선순위 1] 티커 정확 일치
        res = supabase.table("stock_master").select("*").eq("ticker", query).execute()
        if res.data: 
            return res.data[0]

        # 2. [우선순위 2] 이름 정확 일치 (한글 or 영문)
        res = supabase.table("stock_master")\
            .select("*")\
            .or_(f"name_kr.ilike.{query},name_en.ilike.{query}")\
            .limit(1)\
            .execute()
        if res.data:
            return res.data[0]

        # 3. [우선순위 3] 유사 검색 (포함 검색)
        res = supabase.table("stock_master")\
            .select("*")\
            .or_(f"name_kr.ilike.%{query}%,name_en.ilike.%{query}%")\
            .limit(1)\
            .execute()
            
        if res.data: 
            return res.data[0]
            
    except Exception as e:
        print(f"❌ [Master] DB Search Error: {e}")
        
    return None


def search_stocks(query: str, limit: int = 10):
    """
    종목 검색 서비스 로직
    (종목명, 영문명, 티커 동시 조회 및 정렬)
    """
    try:
        supabase_client = get_supabase_client()
        
        # 특수문자 이스케이핑
        sanitized_q = query.replace('%', '\\%').replace('_', '\\_')
        search_pattern = f"%{sanitized_q}%"
        
        # 1. DB에서 더 많은 후보군 가져오기
        fetch_limit = limit * 3
        
        response = supabase_client.table("stock_master")\
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
