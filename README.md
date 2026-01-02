# AI Finance Project
**[바로가기](https://ai-finance-coral.vercel.app/)**

AI 기반 주식 분석 및 정보 제공 플랫폼입니다.
사용자가 주식 종목을 검색하면 AI를 활용하여 심층적인 분석 정보를 제공하며, 실시간 랭킹 및 검색 기능을 지원합니다.

## 🛠 기술 스택 (Tech Stack)

### Frontend

- **Framework**: React (Vite)
- **Styling**: Tailwind CSS
- **State Management**: React Query (@tanstack/react-query)
- **Routing**: React Router Dom
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Backend

- **Framework**: FastAPI (Python)
- **Database**: Supabase(KIS 인증 토큰 및 검색을 위한 마스터 데이터 저장)
- **AI Models**: Google Gemini
- **Data Sources**: YFinance (Yahoo Finance), Feedparser (News), KIS(한국투자증권 API)

## ✨ 주요 기능 (Features)

1.  **주식 심층 분석 (Deep Analysis)**
    - AI를 활용하여 특정 종목에 대한 종합적인 분석 리포트 제공
    - 뉴스, 재무 데이터 등을 기반으로 인사이트 도출
2.  **미국 주식 랭킹 (US Stock Rankings)**
    - 시가총액, 거래량, 상승률 등을 기준으로 한 실시간 랭킹 정보 제공
3.  **종목 검색 (Stock Search)**
    - 종목명(한글/영어) 또는 티커로 주식 검색 지원

## 🚀 시작하기 (Getting Started)

프로젝트를 로컬 환경에서 실행하는 방법입니다.

### 1. 백엔드 설정 (Backend)

```bash
cd backend

# 가상환경 생성 (선택사항)
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 필요)
# 필요한 키: SUPABASE_URL, SUPABASE_SERVICE_KEY, GOOGLE_API_KEY 등

# 서버 실행
uvicorn main:app --reload
```

### 2. 프론트엔드 설정 (Frontend)

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

## 📂 프로젝트 구조 (Project Structure)

```
Ai-finance/
├── backend/           # FastAPI 백엔드 서버
│   ├── services/      # 분석 및 랭킹 로직
│   ├── main.py        # 메인 애플리케이션 진입점
│   └── ...
├── frontend/          # React 프론트엔드
│   ├── src/
│   │   ├── api/       # API 통신 로직
│   │   ├── components/# UI 컴포넌트
│   │   ├── pages/     # 페이지 단위 컴포넌트
│   │   └── ...
│   └── ...
└── ...
```
