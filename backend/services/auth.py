# services/auth.py
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# KIS API 환경 변수
APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")
BASE_URL = "https://openapi.koreainvestment.com:9443"

# Supabase 환경 변수
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Supabase 클라이언트 싱글톤
_supabase_client = None

def get_supabase_client():
    """Supabase 클라이언트 싱글톤 패턴"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

def get_token_from_db():
    """Supabase에서 토큰 조회"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('kis_tokens').select('*').eq('id', 1).execute()
        
        if response.data and len(response.data) > 0:
            token_data = response.data[0]
            
            # 만료 시간 파싱 (ISO 8601 형식)
            expired_at_str = token_data['expired_at']
            # Z 또는 +00:00 제거 후 파싱
            expired_at_str = expired_at_str.replace('Z', '').replace('+00:00', '')
            expired_at = datetime.fromisoformat(expired_at_str)
            
            # 만료 1분 전까지 유효하면 사용
            if datetime.now() < expired_at - timedelta(minutes=1):
                print("✅ Supabase에서 유효한 토큰 조회")
                return token_data['access_token']
            else:
                print("⏰ 토큰 만료됨, 재발급 필요")
        else:
            print("📭 DB에 토큰 없음, 최초 발급 필요")
        
        return None
        
    except Exception as e:
        print(f"⚠️ Supabase 조회 실패: {e}")
        return None

def save_token_to_db(access_token, expired_at):
    """Supabase에 토큰 저장 (upsert)"""
    try:
        supabase = get_supabase_client()
        
        # upsert: id=1이 있으면 업데이트, 없으면 삽입
        supabase.table('kis_tokens').upsert({
            'id': 1,
            'access_token': access_token,
            'expired_at': expired_at,
            'updated_at': datetime.now().isoformat()
        }).execute()
        
        print(f"✅ Supabase에 토큰 저장 완료 (만료: {expired_at})")
        
    except Exception as e:
        print(f"⚠️ Supabase 저장 실패: {e}")
        raise

def request_new_token():
    """한국투자증권 API에서 새 토큰 발급"""
    print("🔄 실전용 접근 토큰 발급 중...")
    
    url = f"{BASE_URL}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }

    res = requests.post(url, headers=headers, data=json.dumps(body))
    
    if res.status_code == 200:
        data = res.json()
        access_token = data['access_token']
        expired_at_str = data['access_token_token_expired']
        
        print(f"✅ 토큰 발급 완료 (만료: {expired_at_str})")
        return access_token, expired_at_str
    else:
        raise Exception(f"❌ 토큰 발급 실패: {res.text}")

def get_access_token():
    """
    메인 함수: 토큰 관리 로직
    1. Supabase에서 토큰 확인
    2. 유효하면 바로 반환
    3. 없거나 만료되면 새로 발급 후 저장
    """
    
    # 1. DB에서 토큰 확인
    token = get_token_from_db()
    if token:
        return token
    
    # 2. 토큰이 없거나 만료됨 → 새로 발급
    access_token, expired_at_str = request_new_token()
    
    # 3. DB에 저장
    save_token_to_db(access_token, expired_at_str)
    
    return access_token