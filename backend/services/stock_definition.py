import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

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