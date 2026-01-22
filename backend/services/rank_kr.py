import requests
import os
from dotenv import load_dotenv
from services.auth import get_access_token

load_dotenv()

APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")
BASE_URL = "https://openapi.koreainvestment.com:9443"

def get_headers(tr_id):
    return {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {get_access_token()}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P"
    }

def parse_kr_data(data,limit=5):
    results = []
    if not data:
        print(f"⚠️ API Error Message: {data.get('msg1')}")
        return results
    
    output = data.get("output", [])
    for item in output[:limit]:
        results.append({
            "rank": item.get("data_rank"),
            # API마다 다른 티커 필드명 통합
            "ticker": item.get("mksc_shrn_iscd") or item.get("stck_shrn_iscd") or item.get("hts_iscd"),
            "name": item.get("hts_kor_isnm"),
            "price": int(item.get("stck_prpr", 0)),
            "rate": float(item.get("prdy_ctrt", 0)),
            "volume": int(item.get("acml_vol", 0)),
            # 시가총액 필드가 있으면 정수로 변환, 없으면 0
            "value": int(item.get("stck_avls", 0)) 
        })
    return results
    

def kr_rank_volume():
    """
    거래량 순위 API 테스트용 함수
    """
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/volume-rank"
    headers = get_headers("FHPST01710000")
    
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",     # 주식 종목 (J)
        "FID_COND_SCR_DIV_CODE": "20171",  # 화면번호 그룹코드
        "FID_INPUT_ISCD": "0000",          # 0000: 전체, 0001: 코스피, 1001: 코스닥
        "FID_DIV_CLS_CODE": "0",           # 0: 전체, 1: 보통주
        "FID_BLNG_CLS_CODE": "0",          # 0: 전체
        "FID_TRGT_CLS_CODE": "111111111",  # 전체 대상
        "FID_TRGT_EXLS_CLS_CODE": "1111111111",# 제외 없음
        "FID_INPUT_PRICE_1": "",          # 가격 최소
        "FID_INPUT_PRICE_2": "",          # 가격 최대
        "FID_VOL_CNT": "",                # 거래량 조건
        "FID_INPUT_DATE_1": ""             # 조회일자 (비워두면 당일)
    }
    
    res=requests.get(url, headers=headers, params=params, timeout=60000)
    return parse_kr_data(res.json(),limit=5)


def kr_market_cap():
    """
    시가총액 순위 API 테스트용 함수
    """
    url = f"{BASE_URL}/uapi/domestic-stock/v1/ranking/market-cap"
    headers = get_headers("FHPST01740000")
    
    params = {
        "fid_input_price_2": "",
        "fid_cond_mrkt_div_code": "J",
        "fid_cond_scr_div_code": "20174",
        "fid_div_cls_code": "0",
        "fid_input_iscd": "0000",
        "fid_trgt_cls_code": "0",
        "fid_trgt_exls_cls_code": "0",
        "fid_input_price_1": "",
        "fid_vol_cnt": "",
        }
    
    res=requests.get(url, headers=headers, params=params, timeout=60000)
    return parse_kr_data(res.json(),limit=5)


def kr_gainer():
    """
    급등주 순위 API 테스트용 함수
    """
    url = f"{BASE_URL}/uapi/domestic-stock/v1/ranking/fluctuation"
    headers = get_headers("FHPST01700000")
    
    params = {
        "fid_rsfl_rate2": "",
        "fid_cond_mrkt_div_code": "J",
        "fid_cond_scr_div_code": "20170",
        "fid_input_iscd": "0000",
        "fid_rank_sort_cls_code": "0",
        "fid_input_cnt_1": "0",
        "fid_prc_cls_code": "1",
        "fid_input_price_1": "",
        "fid_input_price_2": "",
        "fid_vol_cnt": "",
        "fid_trgt_cls_code": "0",
        "fid_trgt_exls_cls_code": "0",  
        "fid_div_cls_code": "0",
        "fid_rsfl_rate1": "",
        }
    res=requests.get(url, headers=headers, params=params, timeout=60000)
    return parse_kr_data(res.json(),limit=5)

def get_all_stock_rankings():
    """모든 랭킹 데이터를 모아서 하나의 딕셔너리로 반환"""
    try:
        return {
            "success": True,
            "market_cap": kr_market_cap(),
            "volume": kr_rank_volume(),
            "gainers": kr_gainer()
        }
    except Exception as e:
        return {"success": False, "error": str(e)} 

def get_kr_current_price(ticker):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = get_headers("FHKST01010100")
    params={
        "FID_COND_MRKT_DIV_CODE" : "UN",
        "FID_INPUT_ISCD" : ticker
    }

    try:
        res = requests.get(url, headers=headers, params=params, timeout=60000)     
        data = res.json()
        
        # 정상 처리(rt_cd == '0')인지 확인 후 stck_prpr 추출
        if data.get("rt_cd") == "0":
            # 가격은 문자열로 들어오므로 숫자로 변환
            current_price = int(data["output"]["stck_prpr"])
            return current_price
        else:
            print(f"❌ API 에러: {data.get('msg1')}")
            return None
            
    except Exception as e:
        print(f"❌ 요청 중 에러 발생: {e}")
        return None
