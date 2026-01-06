import os
import json
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 로드 (API 가이드에 따른 필수 헤더 정보)
# Authorization: Bearer {API_KEY} 형태 
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY") 
CLOVA_HOST = "https://clovastudio.stream.ntruss.com"

def clean_json_text(text):
    """
    AI 응답 텍스트에서 순수 JSON 부분만 추출합니다.
    (기존 로직 유지)
    """
    try:
        text = text.replace("```json", "").replace("```", "")
        text = text.strip()
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx : end_idx + 1]
        return text
    except Exception:
        return text

def analyze_sentiment_naver(news_list):
    # 1. 예외 처리
    if not CLOVA_API_KEY:
        return {"summary": "API 키 설정 오류", "score": 50}

    if not news_list:
        return {"summary": "최근 관련 뉴스가 없어 분석할 수 없습니다.", "score": 50}

    titles = [n['title'] for n in news_list]
    titles_text = "\n".join(titles)

    # 2. 요청 헤더 구성 (API GUIDE  참조)
    headers = {
        'Authorization': f'Bearer {CLOVA_API_KEY}',      # 필수: 인증 키 
        'X-NCP-CLOVASTUDIO-REQUEST-ID': str(uuid.uuid4()), # 선택: 요청 ID (트래킹용) 
        'Content-Type': 'application/json',               # 필수: JSON 형식 
        'Accept': 'application/json'                      # 기본값 (스트림 아님) 
    }


    # HCX-005 모델 엔드포인트 지정 
    request_url = f"{CLOVA_HOST}/v3/chat-completions/HCX-DASH-002"

    payload = {
        "messages": [ # 필수: 대화 메시지 배열 [cite: 31]
            {
                "role": "system", # 시스템 메시지 (지시문) [cite: 35]
                "content": [
                    {
                        "type": "text", # 텍스트 유형 
                        "text": """당신은 주식 뉴스의 감성을 분석하는 전문가입니다.
                        아래 뉴스 제목들의 전반적인 시장 심리를 분석하여 
                        반드시 다음 JSON 형식으로만 응답하세요:

                        {"summary": "전체 내용을 아우르는 한글 요약 (두 문장 이내)", "score": 0~100}

                        - score: 0(매우 부정)~50(중립)~100(매우 긍정)
                        - 마크다운, 코드블록, 추가 설명 절대 금지
                        """
                    }
                ]
            },
            {
                "role": "user", # 사용자 메시지 (질문) [cite: 35]
                "content": [
                    {
                        "type": "text",
                        "text": f"다음 뉴스 제목들을 분석해주세요:\n{titles_text}"
                    }
                ]
            }
        ],
        "topP": 0.8,            # 생성 토큰 샘플링 (기본값 0.8) [cite: 31]
        "topK": 0,              # (기본값 0) [cite: 31]
        "maxTokens": 256,       # 최대 생성 토큰 수 [cite: 31]
        "temperature": 0.5,     # 다양성 정도 (기본값 0.5) [cite: 31]
        "repetitionPenalty": 1.1, # 반복 패널티 (문서 예시값 참고) [cite: 31]
        "includeAiFilters": True, # AI 필터 결과 포함 여부 [cite: 31]
        "seed": 0                 # 결과 일관성 유지 [cite: 31]
    }

    try:
        # 4. API 요청 전송
        response = requests.post(request_url, headers=headers, json=payload)
        
        # 5. 응답 처리 (API GUIDE  참조)
        if response.status_code == 200:
            result_json = response.json()
            
            # 응답 구조: result -> message -> content 
            # content는 일반 텍스트 문자열로 반환됩니다 
            raw_text = result_json['result']['message']['content']
            
            cleaned_text = clean_json_text(raw_text)
            parsed_result = json.loads(cleaned_text)
            
            return {
                "summary": parsed_result.get('summary', '요약 실패'), 
                "score": parsed_result.get('score', 50)
            }
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return {
                "summary": "AI 분석 중 오류가 발생했습니다.", 
                "score": 50
            }

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {
            "summary": "시스템 오류가 발생했습니다.", 
            "score": 50
        }