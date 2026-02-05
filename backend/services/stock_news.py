import feedparser
import urllib.parse
import requests
import re
import os
import logging
import html

# 로거 설정
logger = logging.getLogger(__name__)

def clean_company_name(name: str) -> str:
    """뉴스 검색 정확도를 위해 Inc, Corp 등을 제거"""
    return re.sub(r'[,.]?\s*(Inc|Corp|Ltd|Corporation|Company|Co)\.?$', '', name, flags=re.IGNORECASE).strip()

def get_google_news(keyword: str, limit=10):
    """
    Google RSS를 통해 해외 관련 뉴스를 가져옵니다.
    'stock news' 키워드를 추가하여 주식 관련 뉴스만 필터링
    """
    keyword = clean_company_name(keyword)
    news_list = []
    try:
        encoded_query = urllib.parse.quote(f"{keyword} stock news")
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:limit]:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "date": entry.get('published', '')
            })
            
        logger.info(f"✅ [Google News] '{keyword}' 관련 뉴스 {len(news_list)}개 수집")
        
    except Exception as e:
        logger.error(f"❌ [Google News] Error: {e}")
        
    return news_list

def get_naver_news(keyword: str, limit=10):
    """
    Naver OpenAPI를 통해 국내 관련 뉴스를 가져옵니다.
    """
    keyword = clean_company_name(keyword)
    news_list = []
    try:
        client_id = os.getenv("NAVER_CLIENT_ID")
        client_secret = os.getenv("NAVER_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            logger.warning("⚠️ [Naver News] API 키가 설정되지 않았습니다.")
            return []
        
        encoded_query = urllib.parse.quote(keyword)
        display_count = limit * 10
        url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_query}&display={display_count}&sort=sim"
        
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        items = response.json().get('items', [])
        exclude_keywords = ['증권', '證', 'ETF', 'etf']
        for i in items:
            # 1. HTML 태그(<b> 등) 제거
            title_no_tag = re.sub(r'<[^>]*>', '', i['title'])
            desc_no_tag = re.sub(r'<[^>]*>', '', i['description'])
            
            # 2. HTML 엔티티(&quot; 등)를 특수문자로 변환
            title_clean = html.unescape(title_no_tag)
            description_clean = html.unescape(desc_no_tag)
            
            # 제외 키워드 체크
            if any(exclude in title_clean for exclude in exclude_keywords):
                continue
            
            # 정확도 재검증
            if keyword not in title_clean and keyword not in description_clean:
                continue

            news_list.append({
                "title": title_clean,        
                "description": description_clean, 
                "link": i['link'],
                "date": i.get('pubDate', '')
            })
            
            if len(news_list) >= limit:
                break
        logger.info(f"✅ [Naver News] '{keyword}' 관련 뉴스 {len(news_list)}개 수집")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ [Naver News] Network Error: {e}")
    except Exception as e:
        logger.error(f"❌ [Naver News] Error: {e}")
        
    return news_list
