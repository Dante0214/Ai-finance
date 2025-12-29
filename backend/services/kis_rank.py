import requests
import os
from dotenv import load_dotenv
from services.auth import get_access_token

load_dotenv()

APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")
BASE_URL = "https://openapi.koreainvestment.com:9443"

def get_headers(tr_id):
    access_token = get_access_token()
    return {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id
    }

# 공통: 데이터 정제 함수 (정확히 5개만 처리)
def parse_ranking_data(items, rank_type):
    result = []
    
    if not items:
        print(f"⚠️ {rank_type} - 데이터가 비어있습니다")
        return result
    
    # 정확히 5개만 처리
    for i, item in enumerate(items):
        try:
            ticker = item.get('symb', 'N/A')
            name = item.get('name', 'Unknown')
            
            # 가격
            price = float(item.get('last', 0))
            
            # 등락률 (rate 필드 사용)
            rate = float(item.get('rate', 0))
            
            # 시총 or 거래량
            if rank_type == 'cap':
                # 시가총액 API는 valx 필드 없음, 대신 tamt(거래대금) 사용 가능
                value = float(item.get('tamt', 0)) / 1000000  # 백만 단위로 변환
            else:
                value = int(item.get('tvol', 0))
            
            result.append({
                "rank": i + 1,
                "ticker": ticker,
                "name": name,
                "price": price,
                "rate": rate,
                "value": value
            })
            
        except Exception as e:
            print(f"❌ {rank_type} 파싱 에러 (항목 {i}): {e}")
            continue
    
    return result

# 1. 시가총액 순위 (TOP 5만 요청)
def get_rank_market_cap(excd="NAS"):
    path = "/uapi/overseas-stock/v1/ranking/market-cap"
    headers = get_headers("HHDFS76350100")
    
    params = {
        "AUTH": "",
        "EXCD": excd,
        "KEYB": "",
        "VOL_RANG": "0"
    }
    
    try:
        res = requests.get(f"{BASE_URL}{path}", headers=headers, params=params, timeout=10)
        res.raise_for_status()
        
        data = res.json()
        
        if data.get('rt_cd') != '0':
            print(f"❌ API 에러 (시가총액): {data.get('msg1')}")
            return []
        
        # ⭐ TOP 5만 추출
        items = data.get('output2', [])[:5]
        print(f"✅ 시가총액 TOP 5 수신")
        return parse_ranking_data(items, 'cap')
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 시가총액 API 호출 실패: {e}")
        return []

# 2. 거래량 순위 (TOP 5만 요청)
def get_rank_volume(excd="NAS"):
    path = "/uapi/overseas-stock/v1/ranking/trade-vol"
    headers = get_headers("HHDFS76310010")
    
    params = {
        "AUTH": "",
        "EXCD": excd,
        "NDAY": "0",
        "vol_rang": "0",
        "keyb": "",
        "gb": "0"
    }
    
    try:
        res = requests.get(f"{BASE_URL}{path}", headers=headers, params=params, timeout=10)
        res.raise_for_status()
        
        data = res.json()
        
        if data.get('rt_cd') != '0':
            print(f"❌ API 에러 (거래량): {data.get('msg1')}")
            return []
        
        # ⭐ TOP 5만 추출
        items = data.get('output2', [])[:5]
        print(f"✅ 거래량 TOP 5 수신")
        return parse_ranking_data(items, 'vol')
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 거래량 API 호출 실패: {e}")
        return []

# 3. 급등률 순위 (TOP 5만 요청)
def get_rank_gainer(excd="NAS"):
    path = "/uapi/overseas-stock/v1/ranking/updown-rate"
    headers = get_headers("HHDFS76290000")
    
    params = {
        "AUTH": "",
        "EXCD": excd,
        "GUBN": "1",
        "NDAY": "0",
        "vol_rang": "1"
    }
    
    try:
        res = requests.get(f"{BASE_URL}{path}", headers=headers, params=params, timeout=10)
        res.raise_for_status()
        
        data = res.json()
        
        if data.get('rt_cd') != '0':
            print(f"❌ API 에러 (급등률): {data.get('msg1')}")
            return []
        
        # ⭐ TOP 5만 추출
        items = data.get('output2', [])[:5]
        print(f"✅ 급등률 TOP 5 수신")
        return parse_ranking_data(items, 'rate')
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 급등률 API 호출 실패: {e}")
        return []