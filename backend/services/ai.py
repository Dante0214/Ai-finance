# backend/services/ai.py
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_sentiment(news_list):
    if not news_list:
        return {"summary": "뉴스가 충분하지 않습니다.", "score": 50}

    titles = [n['title'] for n in news_list]
    
    # 프롬프트 엔지니어링: 명확한 JSON 출력을 요구
    prompt = f"""
    다음은 주식 관련 뉴스 헤드라인들입니다: {titles}
    
    이 뉴스들을 바탕으로 다음 두 가지를 분석해서 JSON 형식으로만 답변해줘. 마크다운 태그 없이 순수 JSON만 줘.
    1. 'summary': 이 종목에 대한 호재/악재 여부를 포함한 한 문장 요약 (한글로)
    2. 'score': 0(매우 부정)에서 100(매우 긍정) 사이의 점수 (정수형)
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # 응답 텍스트에서 JSON 파싱
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {"summary": "분석 중 오류가 발생했습니다.", "score": 50}