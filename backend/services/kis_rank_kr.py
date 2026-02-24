import httpx
import logging
import asyncio
from services.auth import get_kis_headers, BASE_URL

# 로거 설정
logger = logging.getLogger(__name__)


def parse_kr_data(data, limit=5):
    """
    API 응답 데이터를 파싱하여 랭킹 리스트를 반환합니다.
    """
    results = []
    if not data:
        logger.warning(f"⚠️ API 데이터 없음")
        return results
    
    # 에러 메시지 확인
    if data.get('rt_cd') != '0':
         logger.error(f"⚠️ API Error Message: {data.get('msg1')}")
         return results

    output = data.get("output", [])
    for item in output[:limit]:
        try:
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
        except Exception as e:
            logger.error(f"❌ 파싱 중 에러 발생: {e}")
            continue

    return results

async def _fetch_kr_ranking(client, path, tr_id, params, limit=5, rank_name="Unknown"):
    """
    한국 주식 랭킹 데이터 요청 공통 함수 (Async)
    """
    url = f"{BASE_URL}{path}"
    headers = get_kis_headers(tr_id)
    
    try:
        res = await client.get(url, headers=headers, params=params, timeout=10.0)
        res.raise_for_status()
        
        data = res.json()
        logger.info(f"✅ {rank_name} 데이터 수신 완료")
        return parse_kr_data(data, limit=limit)
        
    except Exception as e:
        logger.error(f"❌ {rank_name} API 호출 실패: {e}")
        return []

async def kr_rank_volume(client):
    """거래량 순위 API 조회"""
    return await _fetch_kr_ranking(
        client=client,
        path="/uapi/domestic-stock/v1/quotations/volume-rank",
        tr_id="FHPST01710000",
        params={
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
        },
        rank_name="KR 거래량 순위"
    )

async def kr_market_cap(client):
    """시가총액 순위 API 조회"""
    return await _fetch_kr_ranking(
        client=client,
        path="/uapi/domestic-stock/v1/ranking/market-cap",
        tr_id="FHPST01740000",
        params={
            "fid_input_price_2": "",
            "fid_cond_mrkt_div_code": "J",
            "fid_cond_scr_div_code": "20174",
            "fid_div_cls_code": "0",
            "fid_input_iscd": "0000",
            "fid_trgt_cls_code": "0",
            "fid_trgt_exls_cls_code": "0",
            "fid_input_price_1": "",
            "fid_vol_cnt": "",
        },
        rank_name="KR 시가총액 순위"
    )

async def kr_gainer(client):
    """급등주 순위 API 조회"""
    return await _fetch_kr_ranking(
        client=client,
        path="/uapi/domestic-stock/v1/ranking/fluctuation",
        tr_id="FHPST01700000",
        params={
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
        },
        rank_name="KR 급등주 순위"
    )

async def get_all_stock_rankings():
    """모든 랭킹 데이터를 모아서 하나의 딕셔너리로 반환 (Parallel)"""
    try:
        async with httpx.AsyncClient() as client:
            market_cap, volume, gainers = await asyncio.gather(
                kr_market_cap(client),
                kr_rank_volume(client),
                kr_gainer(client)
            )
            
            return {
                "success": True,
                "market_cap": market_cap,
                "volume": volume,
                "gainers": gainers
            }
    except Exception as e:
        logger.error(f"❌ 전체 랭킹 취합 중 에러: {e}")
        return {"success": False, "error": str(e)} 
