import os
import json
from google import genai
from google.genai import types
from google.genai.types import HttpOptions
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
gemini_options = HttpOptions(
    timeout=60000,  
)
if not api_key:
    print("⚠️ GOOGLE_API_KEY가 설정되지 않았습니다.")
    client = None
else:
    client = genai.Client(api_key=api_key, http_options=gemini_options)


def analyze_sentiment(news_list, is_korean=False):
    """
    뉴스 리스트를 분석하여 시장 감성을 평가합니다.
    
    Args:
        news_list: 뉴스 리스트
        is_korean: 한국 뉴스 여부 (True일 경우 description 포함)
    """
    if not client or not news_list:
        return {"summary": "AI 분석 중 오류가 발생했습니다.", "score": 50}
    
    # 한국 뉴스는 제목 + 설명, 해외 뉴스는 제목만
    if is_korean:
        # description이 있는 경우 제목과 함께 포함
        news_content = [
            f"{n['title']} - {n.get('description', '')}" 
            for n in news_list
        ]
    else:
        # 제목만 사용
        news_content = [n['title'] for n in news_list]

    response_schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "one or two-sentence summary in Korean."
            },
            "score": {
                "type": "integer", 
                "minimum": 0, 
                "maximum": 100,
                "description": "An integer between 0 and 100."
            }
        },
        "required": ["summary", "score"]
    }
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"다음 주식 뉴스를 분석하여 전반적인 시장 감성을 평가해주세요. 0은 매우 부정적, 50은 중립, 100은 매우 긍정적입니다: {news_content}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema
            )
        )
        
        return response.parsed

    except Exception as e:
        print(f"❌ AI Analysis Error: {e}")
        
        error_msg = str(e)
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            return {
                "summary": "AI 분석 사용량이 많아 잠시 분석을 중단합니다.", 
                "score": 50
            }
            
        return {
            "summary": "AI 분석 중 오류가 발생했습니다.", 
            "score": 50
        }