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
    client = genai.Client(api_key=api_key,http_options=gemini_options)



def analyze_sentiment(news_list):
    if not client or not news_list:
        return {"summary": "AI 분석 중 오류가 발생했습니다.", "score": 50}
    
    titles = [n['title'] for n in news_list]

    response_schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string","description": "one or two-sentence summary in Korean."},
            "score": {"type": "integer", "minimum": 0, "maximum": 100,"description": "An integer between 0 and 100."}
        },
        "required": ["summary", "score"]
    }
    

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
           contents=f"다음 주식 뉴스 제목들을 분석하여 전반적인 시장 감성을 평가해주세요. 0은 매우 부정적, 50은 중립, 100은 매우 긍정적입니다: {titles}",
           config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema
            )
        )
        
        return response.parsed

    except Exception as e:
        print(f"❌ AI Analysis Error: {e}")
        # 응답 내용을 로그로 확인 (디버깅용)
        # print(f"Raw Response: {response.text}") 
        
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