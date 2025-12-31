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
    반환: {"ticker": "AAPL", "name_kr": "애플", ...} 또는 None
    """
    query = query.strip().upper()
    
    try:
        # 1. 티커 정확 일치 검색
        res = supabase.table("stock_master").select("*").eq("ticker", query).execute()
        if res.data: 
            return res.data[0]

        # 2. 이름(한글/영문) 유사 검색
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