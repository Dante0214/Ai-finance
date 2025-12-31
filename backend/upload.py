import pandas as pd
import urllib.request
import ssl
import zipfile
import os
import time
from io import BytesIO
from supabase import create_client
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv() 

# 환경변수 확인
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("❌ .env 파일에서 SUPABASE_URL 또는 SUPABASE_SERVICE_KEY를 찾을 수 없습니다.")
    exit()

supabase = create_client(url, key)
ssl._create_default_https_context = ssl._create_unverified_context

# 컬럼 정의
COLUMNS = [
    'National code', 'Exchange id', 'Exchange code', 'Exchange name', 
    'Symbol', 'realtime symbol', 'Korea name', 'English name', 
    'Security type(1:Index,2:Stock,3:ETP(ETF),4:Warrant)', 'currency', 
    'float position', 'data type', 'base price', 'Bid order size', 
    'Ask order size', 'market start time(HHMM)', 'market end time(HHMM)', 
    'DR 여부(Y/N)', 'DR 국가코드', '업종분류코드', 
    '지수구성종목 존재 여부(0:구성종목없음,1:구성종목있음)', 'Tick size Type', 
    '구분코드(001:ETF,002:ETN,003:ETC,004:Others,005:VIX Underlying ETF,006:VIX Underlying ETN)',
    'Tick size type 상세'
]

def get_market_data(market_code):
    """마스터 파일 다운로드 및 파싱"""
    print(f"📥 [{market_code}] 마스터 파일 다운로드 중...")
    
    download_url = f"https://new.real.download.dws.co.kr/common/master/{market_code}mst.cod.zip"
    
    try:
        # 메모리 상에서 다운로드 및 압축 해제
        resp = urllib.request.urlopen(download_url)
        zip_data = BytesIO(resp.read())
        
        with zipfile.ZipFile(zip_data) as z:
            # ZIP 안의 실제 파일명: NASMST.COD (대문자)
            cod_file_name = f"{market_code.upper()}MST.COD"
            
            with z.open(cod_file_name) as f:
                # 탭으로 구분된 파일 읽기
                df = pd.read_csv(f, sep='\t', encoding='cp949', header=None)
                
                # 컬럼명 지정 (실제 컬럼 수와 맞지 않을 수 있으므로 안전하게 처리)
                if len(df.columns) >= 8:
                    # 필요한 컬럼만 추출
                    # 2: Exchange code, 4: Symbol, 6: Korea name, 7: English name
                    df_filtered = df.iloc[:, [2, 4, 6, 7]].copy()
                    df_filtered.columns = ['market', 'ticker', 'name_kr', 'name_en']
                    
                    # 빈 값 제거
                    df_filtered = df_filtered.dropna(subset=['ticker'])
                    df_filtered = df_filtered[df_filtered['ticker'].str.strip() != '']
                    
                    return df_filtered.to_dict('records')
                else:
                    print(f"⚠️ [{market_code}] 예상치 못한 컬럼 구조: {len(df.columns)}개 컬럼")
                    return []
                
    except Exception as e:
        print(f"❌ [{market_code}] 처리 중 오류 발생: {e}")
        return []

def upload_to_supabase():
    """Supabase에 데이터 업로드"""
    # 미국 주요 3대 시장
    markets = ['nas', 'nys', 'ams'] 
    
    all_data = []

    # 데이터 수집
    for market in markets:
        data = get_market_data(market)
        print(f"✅ [{market}] {len(data)}개 종목 수집 완료")
        all_data.extend(data)
    
    if not all_data:
        print("❌ 수집된 데이터가 없습니다. 프로그램을 종료합니다.")
        return
    
    print(f"\n📦 총 {len(all_data)}개 데이터 업로드 시작...")
    
    # 500개씩 끊어서 업로드 (배치 처리)
    batch_size = 500
    success_count = 0
    
    for i in range(0, len(all_data), batch_size):
        batch = all_data[i:i+batch_size]
        try:
            # upsert: ticker를 기준으로 중복 시 업데이트
            supabase.table("stock_master").upsert(batch, on_conflict="ticker").execute()
            success_count += len(batch)
            print(f"🚀 {success_count} / {len(all_data)} 업로드 완료")
            time.sleep(0.1)  # 서버 부하 방지
        except Exception as e:
            print(f"⚠️ 업로드 에러 (일부 건너뜀): {e}")

    print(f"\n🎉 업로드 완료! 총 {success_count}개 데이터가 업데이트되었습니다.")

if __name__ == "__main__":
    # 테이블 초기화가 필요하면 아래 주석 해제
    # print("🗑️ 기존 데이터 삭제 중...")
    # supabase.table("stock_master").delete().neq("ticker", "").execute()
    
    upload_to_supabase()