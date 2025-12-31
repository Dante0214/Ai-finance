import feedparser
import urllib.parse
import re

def clean_company_name(name: str) -> str:
    """뉴스 검색 정확도를 위해 Inc, Corp 등을 제거"""
    return re.sub(r'[,.]?\s*(Inc|Corp|Ltd|Corporation|Company|Co)\.?$', '', name, flags=re.IGNORECASE).strip()

def get_google_news(keyword: str, limit=10):
    """
    Google RSS를 통해 관련 뉴스를 가져옵니다.
    """
    news_list = []
    try:
        # 검색어 인코딩
        encoded_query = urllib.parse.quote(f"{keyword} stock news")
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:limit]:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "date": entry.get('published', '') # 날짜 정보 있으면 추가
            })
            
        print(f"✅ [News] '{keyword}' 관련 뉴스 {len(news_list)}개 수집")
        
    except Exception as e:
        print(f"❌ [News] Error: {e}")
        
    return news_list