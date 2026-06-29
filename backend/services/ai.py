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
# gemini-2.5-flash-lite: 지역 제한 없이 동작하는 경량 모델 (Render 서버 호환)
# gemini-2.5-flash: 로컬에서는 동작하지만 일부 서버 환경에서 FAILED_PRECONDITION 발생
GEMINI_MODEL = "gemini-3.1-flash-lite"

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
            model=GEMINI_MODEL,
            contents=f"다음 주식 뉴스를 분석하여 전반적인 시장 감성을 평가해주세요. 0은 매우 부정적, 50은 중립, 100은 매우 긍정적입니다: {news_content}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema
            )
        )

        result = response.parsed
        # parsed가 None이면 text를 직접 파싱
        if result is None and response.text:
            import json
            result = json.loads(response.text)
        return result

    except Exception as e:
        error_msg = str(e)
        print(f"❌ AI Analysis Error [{GEMINI_MODEL}]: {error_msg[:200]}")

        if "429" in error_msg or "ResourceExhausted" in error_msg:
            return {
                "summary": "AI 분석 사용량이 많아 잠시 분석을 중단합니다.",
                "score": 50
            }
        if "FAILED_PRECONDITION" in error_msg or "location is not supported" in error_msg:
            return {
                "summary": "현재 서버 위치에서 AI 분석이 지원되지 않습니다.",
                "score": 50
            }
        if "NOT_FOUND" in error_msg or "404" in error_msg:
            return {
                "summary": "AI 모델을 찾을 수 없습니다. 관리자에게 문의하세요.",
                "score": 50
            }

        return {
            "summary": "AI 분석 중 오류가 발생했습니다.",
            "score": 50
        }
