import httpx
import logging
import asyncio
from services.auth import get_kis_headers, BASE_URL

# 로거 설정
logger = logging.getLogger(__name__)


def parse_ranking_data(items, rank_type):
    """
    공통: 데이터 정제 함수 (정확히 5개만 처리)
    """
    result = []
    
    if not items:
        logger.warning(f"⚠️ {rank_type} - 데이터가 비어있습니다")
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
                value = float(item.get('tomv', 0))  # 백만 단위로 변환
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
            logger.error(f"❌ {rank_type} 파싱 에러 (항목 {i}): {e}")
            continue
    
    return result

async def _fetch_rank_data(client, path, tr_id, params, rank_type):
    """
    [Internal] 랭킹 데이터 요청 공통 함수 (Async)
    """
    headers = get_kis_headers(tr_id)
    try:
        res = await client.get(f"{BASE_URL}{path}", headers=headers, params=params, timeout=10.0)
        res.raise_for_status()
        
        data = res.json()
        
        if data.get('rt_cd') != '0':
            logger.error(f"❌ API 에러 ({rank_type}): {data.get('msg1')}")
            return []
        
        # ⭐ TOP 5만 추출
        items = data.get('output2', [])[:5]
        logger.info(f"✅ {rank_type} TOP 5 수신 완료")
        return parse_ranking_data(items, rank_type)
        
    except httpx.RequestError as e:
        logger.error(f"❌ {rank_type} API 호출 실패: {e}")
        return []

# 1. 시가총액 순위 (TOP 5만 요청)
async def get_rank_market_cap(client, excd="NAS"):
    """미국 주식 시가총액 순위 조회"""
    return await _fetch_rank_data(
        client=client,
        path="/uapi/overseas-stock/v1/ranking/market-cap",
        tr_id="HHDFS76350100",
        params={
            "AUTH": "",
            "EXCD": excd,
            "KEYB": "",
            "VOL_RANG": "0",
            "CURR_GB": "1"
        },
        rank_type='cap'
    )

# 2. 거래량 순위 (TOP 5만 요청)
async def get_rank_volume(client, excd="NAS"):
    """미국 주식 거래량 순위 조회"""
    return await _fetch_rank_data(
        client=client,
        path="/uapi/overseas-stock/v1/ranking/trade-vol",
        tr_id="HHDFS76310010",
        params={
            "AUTH": "",
            "EXCD": excd,
            "NDAY": "0",
            "VOL_RANG": "0",
            "KEYB": "",
            "PRC1": "0",
            "PRC2": "0"
        },
        rank_type='vol'
    )

# 3. 급등률 순위 (TOP 5만 요청)
async def get_rank_gainer(client, excd="NAS"):
    """미국 주식 급등 순위 조회"""
    return await _fetch_rank_data(
        client=client,
        path="/uapi/overseas-stock/v1/ranking/updown-rate",
        tr_id="HHDFS76290000",
        params={
            "AUTH": "",
            "KEYB": "",
            "EXCD": excd,
            "GUBN": "1",
            "NDAY": "0",
            "VOL_RANG": "1"
        },
        rank_type='rate'
    )

async def get_all_us_rankings():
    """모든 미국 랭킹 데이터를 모아서 하나의 딕셔너리로 반환"""
    try:
        async with httpx.AsyncClient() as client:
            market_cap, volume, gainers = await asyncio.gather(
                get_rank_market_cap(client),
                get_rank_volume(client),
                get_rank_gainer(client)
            )
            
            return {
                "market_cap": market_cap,
                "volume": volume,
                "gainers": gainers
            }
    except Exception as e:
        logger.error(f"❌ US Ranking Error: {e}")
        return {"market_cap": [], "volume": [], "gainers": []}
