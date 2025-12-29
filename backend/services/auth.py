import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 (실전 키만 사용)
APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")

# [수정됨] 분기 없이 무조건 실전 도메인 사용
BASE_URL = "https://openapi.koreainvestment.com:9443"
TOKEN_FILE = "token.json"

def get_access_token():
    # 1. 기존 토큰 파일 확인
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
            
            # 만료 시간 체크 (여유 있게 1분 전)
            expired_at = datetime.strptime(token_data['expired_at'], "%Y-%m-%d %H:%M:%S")
            if datetime.now() < expired_at - timedelta(minutes=1):
                return token_data['access_token']
        except Exception:
            print("⚠️ 토큰 파일 읽기 오류, 재발급을 시도합니다.")

    # 2. 토큰 재발급 요청 (실전 서버)
    print("🔄 실전용 접근 토큰(Token) 발급 중...")
    
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
        
        # 3. 파일 저장
        with open(TOKEN_FILE, 'w') as f:
            json.dump({
                "access_token": access_token,
                "expired_at": expired_at_str
            }, f)
            
        print(f"✅ 토큰 발급 완료 (만료: {expired_at_str})")
        return access_token
    else:
        raise Exception(f"❌ 토큰 발급 실패: {res.text}")