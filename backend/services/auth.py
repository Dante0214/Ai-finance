import requests
import json
import os
import logging
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)

APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")
BASE_URL = os.getenv("KIS_BASE_URL")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

_supabase_client = None

def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

def get_token_from_db():
    """Supabase에서 토큰 조회 및 만료 체크"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('kis_tokens').select('*').eq('id', 1).execute()
        
        if response.data and len(response.data) > 0:
            token_data = response.data[0]
            expired_at_str = token_data['expired_at']
            
            # DB에서 가져온 시간을 offset-aware datetime으로 변환 (UTC 기준 가정)
            # 만약 DB에 '2025-12-31 20:00:00' 형태로 저장되어 있다면 처리 필요
            try:
                # ISO 포맷 파싱 및 UTC 설정
                expired_at = datetime.fromisoformat(expired_at_str.replace(' ', 'T'))
                if expired_at.tzinfo is None:
                    expired_at = expired_at.replace(tzinfo=timezone.utc)
            except ValueError:
                logger.warning(f"⚠️ 시간 포맷 파싱 실패: {expired_at_str}")
                return None
            
            # 현재 시간을 UTC 기준으로 비교
            now_utc = datetime.now(timezone.utc)
            
            # 만료 10분 전이면 재발급하도록 여유 있게 설정
            if now_utc < expired_at - timedelta(minutes=10):
                logger.info(f"✅ 유효한 토큰 사용 중 (만료: {expired_at})")
                return token_data['access_token']
            else:
                logger.info("⏰ 토큰이 곧 만료되거나 이미 만료되었습니다.")
        return None
    except Exception as e:
        logger.warning(f"⚠️ Supabase 조회 실패: {e}")
        return None

def save_token_to_db(access_token, expired_at_str):
    """토큰 저장 시 시간을 ISO 형식의 UTC로 표준화"""
    try:
        supabase = get_supabase_client()
        
        # 한국투자증권 응답값 'YYYY-MM-DD HH:MM:SS'를 datetime 객체로 변환 (KST 기준임)
        # 한국투자 API의 만료시간은 보통 KST 기준이므로 9시간을 빼서 UTC로 저장하거나, 명시적 처리 필요
        kst_time = datetime.strptime(expired_at_str, '%Y-%m-%d %H:%M:%S')
        # KST -> UTC 변환 (KST는 UTC+9)
        utc_time = kst_time - timedelta(hours=9)
        utc_time_iso = utc_time.replace(tzinfo=timezone.utc).isoformat()
        
        supabase.table('kis_tokens').upsert({
            'id': 1,
            'access_token': access_token,
            'expired_at': utc_time_iso,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).execute()
        
        logger.info(f"✅ Supabase에 토큰 저장 완료 (UTC 기준: {utc_time_iso})")
    except Exception as e:
        logger.warning(f"⚠️ Supabase 저장 실패: {e}")

def request_new_token():
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
        return data['access_token'], data['access_token_token_expired']
    else:
        raise Exception(f"❌ KIS 토큰 발급 실패: {res.text}")

def get_access_token():
    # 1. DB 확인
    token = get_token_from_db()
    if token:
        return token
    
    # 2. 만료 시 신규 발급
    logger.info("🔄 토큰이 없거나 만료되어 새로 발급합니다...")
    access_token, expired_at_str = request_new_token()
    
    # 3. 저장
    save_token_to_db(access_token, expired_at_str)
    
    return access_token

def get_kis_headers(tr_id: str) -> dict:
    """
    KIS API 공통 헤더를 생성합니다.
    토큰 자동 발급/갱신 포함.
    
    Args:
        tr_id: 트랜잭션 ID (예: "HHDFS76200200")
    
    Returns:
        dict: KIS API 요청에 필요한 헤더
    """
    return {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {get_access_token()}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P"
    }
