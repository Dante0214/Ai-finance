import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("⚠️ GOOGLE_API_KEY가 설정되지 않았습니다.")
    client = None
else:
    client = genai.Client(api_key=api_key)

def clean_json_text(text):
    """
    AI 응답 텍스트에서 순수 JSON 부분만 추출합니다.
    (마크다운, 앞뒤 공백, 부가 설명 제거)
    """
    try:
        # 1. 마크다운 코드 블록 제거
        text = text.replace("```json", "").replace("```", "")
        
        # 2. 앞뒤 공백 제거
        text = text.strip()
        
        # 3. JSON의 시작('{')과 끝('}') 위치를 찾아서 그 사이만 추출
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            # +1을 해야 '}'까지 포함됨
            text = text[start_idx : end_idx + 1]
            
        return text
    except Exception:
        return text

def analyze_sentiment(news_list):
    if not client:
        return {"summary": "API 키 설정 오류", "score": 50}

    if not news_list:
        return {"summary": "최근 관련 뉴스가 없어 분석할 수 없습니다.", "score": 50}

    titles = [n['title'] for n in news_list[:5]]
    
    prompt = f"""
    Analyze the sentiment of the following stock news headlines:
    {titles}

    Please provide the output strictly in JSON format with the following keys:
    1. "summary": A one-sentence summary in Korean.
    2. "score": An integer between 0 and 100.

    Return ONLY the JSON string.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        raw_text = response.text
        cleaned_text = clean_json_text(raw_text)
        result = json.loads(cleaned_text)
        
        return {
            "summary": result.get('summary', '요약 실패'), 
            "score": result.get('score', 50)
        }

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