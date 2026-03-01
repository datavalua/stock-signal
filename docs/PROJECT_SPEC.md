구글의 **Antigravity**(실제로는 파이썬의 `import antigravity` 철학을 담은 **Project IDX**나 **AI 기반 개발 환경**을 의미)에서 바로 복사하여 개발을 시작할 수 있도록, 프로젝트 전체 명세서를 Markdown 형식으로 작성해 드립니다.

이 명세서는 AI 가이드(Cursor, Gemini, ChatGPT 등)에게 던져서 바로 코드를 생성하게 하거나, 깃허브 저장소의 `README.md`로 활용하기에 최적화되어 있습니다.

---

# 📋 프로젝트 명세서: 토스증권 시그널 클론 (Toss Signal Clone)

## 1. 프로젝트 개요
*   **목적:** 토스증권의 '시그널' 기능을 벤치마킹하여, 실시간 상승 종목의 원인(이유)과 연관 종목을 타임라인 형태로 제공하는 웹 대시보드 구축.
*   **핵심 가치:** 흩어진 뉴스를 AI가 요약하여 "왜 올랐는지"와 "함께 오른 종목"을 한눈에 파악.
*   **주요 대상:** 코스피, 코스닥, S&P 500, 나스닥 상장 기업.

## 2. 기술 스택 (Tech Stack)
*   **Language:** Python 3.10+
*   **Frontend:** Streamlit (UI 구현 및 웹 배포)
*   **Data Processing:** BeautifulSoup4, Requests, FinanceDataReader, yfinance
*   **AI/LLM:** Google Gemini API (뉴스 요약 및 테마 분류 - 무료 티어)
*   **Storage:** GitHub Repository (JSON 파일 기반 파일럿 DB)
*   **Automation:** GitHub Actions (20분 단위 크롤링 및 데이터 업데이트)
*   **Deployment:** Streamlit Community Cloud (무료 호스팅)

## 3. 시스템 아키텍처
1.  **Collector (GitHub Actions):** 20분마다 실행. 시장별 상승 종목 추출 -> 관련 뉴스 크롤링 -> Gemini API로 요약 및 테마 매핑 -> JSON 저장 및 푸시.
2.  **Storage (GitHub):** `data/YYYY-MM-DD.json` 형태로 날짜별 데이터 보관.
3.  **Client (Streamlit):** 저장된 JSON을 읽어 대시보드 렌더링. 10분 단위 자동 새로고침(Auto-refresh).

## 4. 상세 기능 명세

### A. 메인 화면 (UI/UX)
*   **상단 캘린더:** `st.date_input`을 이용해 과거 날짜의 시그널 조회 가능.
*   **시장 탭:** [국내 주식] [미국 주식] 분리 운영.
*   **시그널 카드 (Row-based):**
    *   **헤더:** 이슈 테마(예: #HBM, #금리인하) 및 AI 요약 한 줄.
    *   **메인 기업:** 기업명, 현재가, 등락률(컬러 적용), 뉴스 링크.
    *   **연관 기업:** 가로 스크롤 또는 컬럼 배치를 통해 해당 이슈로 묶인 다른 종목들 표시.

### B. 데이터 수집 로직 (Crawler)
*   **필터링:** 등락률 상위 10~20개 종목 추출.
*   **이유 분석:** 뉴스 검색 API 또는 크롤링을 통해 해당 종목의 최신 뉴스 헤드라인 수집 후 Gemini API 전달.
*   **연관성 추출:** 
    *   AI가 추출한 키워드와 미리 정의된 `themes.json`(테마 DB) 매핑.
    *   매핑된 테마 내에서 현재 등락률이 높은 다른 종목을 실시간으로 가져옴.

### C. 자동화 및 배포
*   **주기:** 장 운영 시간(한국 09-16시, 미국 22-05시) 내 20분 간격 실행.
*   **무료 한도 최적화:** GitHub Actions의 월 2,000분 무료 사용량을 넘지 않도록 장 종료 후에는 실행 중지.

## 5. 데이터 구조 (JSON Schema)
```json
{
  "last_updated": "2023-10-27 14:20:00",
  "signals": [
    {
      "id": "sig_001",
      "theme": "AI 반도체",
      "summary": "엔비디아 서프라이즈로 인한 HBM 관련주 동반 강세",
      "main_stock": {
        "name": "SK하이닉스",
        "symbol": "000660",
        "change_rate": "+5.2%",
        "news_url": "https://..."
      },
      "related_stocks": [
        {"name": "한미반도체", "change_rate": "+12.1%"},
        {"name": "이수페타시스", "change_rate": "+8.4%"}
      ]
    }
  ]
}
```

## 6. 디렉토리 구조
```text
/
├── .github/workflows/
│   └── cron_crawler.yml      # 자동 크롤러 스케줄러
├── data/
│   ├── YYYY-MM-DD.json       # 일별 데이터 기록
│   └── themes.json           # 테마별 종목 매핑 DB (마스터 데이터)
├── app.py                    # Streamlit 메인 웹 애플리케이션
├── crawler.py                # 데이터 수집 및 AI 요약 스크립트
├── requirements.txt          # 필요 라이브러리
└── README.md
```

## 7. 개발 로드맵
1.  **Phase 1:** `FinanceDataReader`를 이용한 기초 주가 수집 및 `themes.json` 구축.
2.  **Phase 2:** Gemini API 연동을 통한 뉴스 요약 및 연관 종목 매핑 로직 구현.
3.  **Phase 3:** Streamlit을 활용한 토스 스타일 카드 UI 및 캘린더 기능 구현.
4.  **Phase 4:** GitHub Actions 연결을 통한 자동 업데이트 시스템 구축 및 배포.

---

### 💡 AI 개발 가이드 (Antigravity 활용 시 참고)
*   **UI 구현 시:** "Streamlit에서 토스증권의 깔끔한 카드 디자인을 위해 `st.markdown`과 Custom CSS를 생성해줘."라고 요청하세요.
*   **크롤러 구현 시:** "네이버 금융의 특징주 뉴스 섹션을 BeautifulSoup으로 크롤링하는 코드를 작성해줘."라고 요청하세요.
*   **AI 요약 시:** "Gemini Pro API를 사용해 뉴스 헤드라인에서 주가 상승 이유를 1문장으로 요약하는 프롬프트를 만들어줘."라고 요청하세요.

이 명세서를 바탕으로 바로 프로젝트를 생성하시면 됩니다! 가장 먼저 `themes.json`을 간단하게 만들고 `crawler.py`의 기본 골격을 잡는 것을 추천드립니다. 도움이 더 필요하시면 말씀해 주세요.