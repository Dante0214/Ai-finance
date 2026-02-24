import logging
import requests
from datetime import datetime, timezone, timedelta
from services.auth import get_kis_headers, BASE_URL

# 로거 설정
logger = logging.getLogger(__name__)

# 한국 표준시 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

# 정규장 거래소코드 → 주간거래 거래소코드 매핑
DAYTIME_MAP = {
    "NAS": "BAQ",  # 나스닥 → 나스닥(주간)
    "NYS": "BAY",  # 뉴욕 → 뉴욕(주간)
    "AMS": "BAA",  # 아멕스 → 아멕스(주간)
}


def _is_us_market_open() -> bool:
    """
    미국 정규장이 현재 열려있는지 판단합니다 (한국시간 기준).
    
    미국 정규장 시간 (ET):
      - 서머타임 (3월~11월): 09:30~16:00 ET (= KST 22:30~05:00)
      - 윈터타임 (11월~3월): 09:30~16:00 ET (= KST 23:30~06:00)
    
    간단하게 KST 22:00~06:30 사이면 정규장으로 판단합니다.
    (서머/윈터 모두 커버하는 넉넉한 범위)
    """
    now_kst = datetime.now(KST)
    hour = now_kst.hour

    # KST 22:00 ~ 다음날 06:30 → 미국 정규장 시간대
    if hour >= 22 or hour < 7:
        return True
    return False


def _get_exchange_code(ticker: str) -> str:
    """
    거래소코드를 반환합니다.
    - 미국 정규장 시간 → NAS (나스닥)
    - 미국 장외시간 (한국 낮) → BAQ (나스닥 주간거래)
    
    ※ 현재는 기본 나스닥만 지원. 추후 DB에 거래소 정보 추가 시 확장 가능.
    """
    base_excd = "NAS"  # 기본: 나스닥

    if _is_us_market_open():
        logger.info(f"📈 [Price] 미국 정규장 시간 → 거래소코드: {base_excd}")
        return base_excd
    else:
        daytime_excd = DAYTIME_MAP.get(base_excd, base_excd)
        logger.info(f"🌙 [Price] 미국 장외시간 (주간거래) → 거래소코드: {daytime_excd}")
        return daytime_excd


def get_current_price(ticker: str) -> float:
    """
    한국투자증권 해외주식 현재가상세 API를 이용해 해외주식 현재가를 가져옵니다.
    
    - 미국 정규장 시간: NAS/NYS/AMS 코드로 실시간 가격 조회
    - 미국 장외시간 (한국 낮): BAQ/BAY/BAA 주간거래 코드로 실시간 가격 조회
    
    - API: 해외주식 현재가 상세 [v1_해외주식-029]
    - HTTP Method: GET
    - TR_ID: HHDFS76200200 (실전투자)
    """
    url = f"{BASE_URL}/uapi/overseas-price/v1/quotations/price-detail"

    # 시간대에 따라 거래소코드 자동 선택 (정규장 vs 주간거래)
    excd = _get_exchange_code(ticker)

    # 공통 헤더 (auth.py에서 토큰 자동 발급/갱신)
    headers = get_kis_headers("HHDFS76200200")

    # Request Query Parameter 구성
    params = {
        "AUTH": "",       # 사용자권한정의 (빈값)
        "EXCD": excd,     # 거래소코드 (시간대에 따라 자동 선택)
        "SYMB": ticker    # 종목코드
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # API 응답 코드 확인
        if data.get("rt_cd") != "0":
            logger.error(f"❌ [Price] API 에러 ({ticker}, EXCD={excd}): {data.get('msg1')}")
            return 0.0

        # 응답상세(output)에서 현재가(last) 추출
        output = data.get("output")
        if output and "last" in output:
            price = float(output["last"])
            logger.info(f"✅ [Price] {ticker} 현재가: ${price:,.2f} (EXCD={excd})")
            return price
        else:
            logger.warning(f"⚠️ [Price] 응답에 현재가 없음 ({ticker}): {data.get('msg1')}")
            return 0.0

    except requests.exceptions.Timeout:
        logger.error(f"❌ [Price] 요청 타임아웃 ({ticker})")
        return 0.0
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ [Price] HTTP 요청 에러 ({ticker}): {e}")
        return 0.0
    except Exception as e:
        logger.error(f"❌ [Price] 예상치 못한 에러 ({ticker}): {e}")
        return 0.0