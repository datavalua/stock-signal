# Toss Signal Clone (토스 시그널 클론)

이 프로젝트는 토스증권의 '시그널' 기능을 벤치마킹하여, 실시간 상승 종목의 원인과 연관 종목을 타임라인 형태로 제공하는 웹 대시보드입니다.

## 기능
* **실시간 핫이슈 포착:** 시장에서 급등하는 종목들을 실시간으로 분석합니다.
* **AI 요약:** 왜 올랐는지 뉴스를 기반으로 Gemini API가 한 줄 요약해 줍니다.
* **테마 연관성 추출:** 함께 오른 관련 종목들을 테마별로 묶어서 보여줍니다.

## 기술 스택
* **Language:** Python 3.10+
* **Frontend:** Streamlit
* **Data Retrieval:** BeautifulSoup4, Requests, FinanceDataReader, yfinance
* **AI/LLM:** Google Gemini API
* **Automation:** GitHub Actions

## 설치 방법
```bash
pip install -r requirements.txt
```

## 실행 방법
1. `.env` 파일을 프로젝트 루트에 생성하고 다음과 같이 Gemini API 키를 입력합니다. (키가 없으면 Mock 데이터로 동작합니다)
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
2. 크롤러를 실행하여 데이터를 수집합니다. (시장별/날짜별)
   ```bash
   python backend/crawler.py --market KR
   ```
3. Streamlit 앱을 실행합니다.
   ```bash
   streamlit run streamlit/app.py
   ```
