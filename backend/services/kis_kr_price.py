import httpx
import logging
from services.auth import get_kis_headers, BASE_URL

# 로거 설정
logger = logging.getLogger(__name__)


def get_kr_current_price(ticker):
    """
    한국투자증권 API를 이용해 국내 주식 현재가를 조회합니다.
    
    - API: 주식현재가 시세 [v1_국내주식-008]
    - TR_ID: FHKST01010100
    """
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = get_kis_headers("FHKST01010100")
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD" : ticker
    }

    try:
        res = httpx.get(url, headers=headers, params=params, timeout=10.0)     
        data = res.json()
        
        # 정상 처리(rt_cd == '0')인지 확인 후 stck_prpr 추출
        if data.get("rt_cd") == "0":
            # 가격은 문자열로 들어오므로 숫자로 변환
            current_price = int(data["output"]["stck_prpr"])
            return current_price
        else:
            logger.error(f"❌ API 에러 (현재가): {data.get('msg1')}")
            return None
            
    except Exception as e:
        logger.error(f"❌ 요청 중 에러 발생: {e}")
        return None
