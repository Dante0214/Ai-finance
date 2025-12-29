import yfinance as yf
import feedparser
import urllib.parse
import re

def get_stock_data(ticker: str):
    print(f"🔍 [Data Fetch] {ticker} 데이터 수집 및 분석 시작...")
    
    stock = yf.Ticker(ticker)
    price = 0
    company_name = ticker # 기본값은 티커

    # 1. 회사 이름 및 주가 정보 가져오기
    try:
        # fast_info로 가격을 빠르게 가져옴
        price = stock.fast_info.last_price
        
        # 회사 상세 정보에서 이름 추출 (속도가 약간 걸릴 수 있음)
        # shortName이 보통 깔끔함 (예: "Tesla, Inc.")
        # 데이터가 없을 경우를 대비해 get 사용
        info = stock.info
        company_name = info.get('shortName') or info.get('longName') or ticker
        
        # 이름 뒤에 붙은 'Inc.', 'Corp.', 'Ltd.' 등 제거하여 검색 정확도 높이기 (선택 사항)
        # 예: "Tesla, Inc." -> "Tesla"
        company_name = re.sub(r'[,.]?\s*(Inc|Corp|Ltd|Corporation|Company|Co)\.?$', '', company_name, flags=re.IGNORECASE).strip()
        
        print(f"🏢 회사명 식별: {ticker} -> {company_name}")

    except Exception as e:
        print(f"⚠️ Info Fetch Error: {e}")
        # 에러 나면 그냥 티커 사용
        company_name = ticker
        price = 0 if price == 0 else price

    # 2. 뉴스 정보 가져오기 (회사 이름으로 검색)
    news_list = []
    try:
        # 검색어 생성: "Tesla stock news" 형태가 가장 정확도가 높음
        search_query = f"{company_name} stock news"
        encoded_query = urllib.parse.quote(search_query)
        
        # 구글 뉴스 RSS URL (미국 주식 기준)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        
        # 최신 뉴스 20개만 추출
        for entry in feed.entries[:20]:
            news_list.append({
                "title": entry.title,
                "link": entry.link
            })
            
        print(f"✅ '{search_query}' 관련 뉴스 {len(news_list)}개 수집 완료")
        
    except Exception as e:
        print(f"❌ News Error: {e}")

    # 3. 데이터 반환
    return {
        "price": price,
        "news": news_list,
        "company_name": company_name # 프론트에서 보여주기 위해 회사명도 반환
    }