# 📈 Stock Signal: Real-time Market Intelligence

> **Toss Securities Signal Clone** - An intelligent dashboard that analyzes the causes of real-time market surges using AI and visualizes related themes with a premium, user-centric interface.

[![Python](https://img.shields.io/badge/Backend-Python-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![Gemini](https://img.shields.io/badge/AI-Google_Gemini-8E75B2?style=flat-square&logo=google-gemini)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

---

## ✨ 핵심 기능 (Key Features)

- **🚀 Real-time Market Tracking**: KOSPI, KOSDAQ, S&P 500, and NASDAQ 시장의 급등주 및 테마를 실시간(20분 단위)으로 트래킹합니다.
- **🤖 AI-Powered Insights**: Google Gemini AI를 활용하여 파편화된 뉴스를 분석, "왜 주가가 움직였는지"에 대한 핵심 이유를 자연스러운 문장으로 요약합니다.
- **🔍 Intelligent Short Reasons**: 단순 키워드 나열이 아닌, 문맥이 담긴 명사구/어절 단위의 한 줄 요약을 제공하여 가독성을 극대화했습니다.
- **🔗 Contextual Theme Mapping**: 개별 종목의 이슈뿐만 아니라, 동일한 재료로 함께 움직이는 연관 테마와 기업들을 지능적으로 연결합니다.
- **📅 Historical Archive**: 과거 특정 날짜의 시장 시그널을 조회하여 과거 트렌드와 복기(Backtesting) 기능을 지원합니다.
- **⚖️ Smart Data Management**: 중복 데이터 수집을 방지하고 API 쿼리를 최적화하는 'Smart Skip' 로직 및 로컬용 'Force Regeneration' 모드를 탑재했습니다.

---

## 🛠️ 기술 스택 (Tech Stack)

### **Frontend & UI/UX**
- **Streamlit**: 데이터 중심의 빠르고 인터랙티브한 대시보드 환경 구축.
- **Custom Design System**: 토스의 'Super App' 감성을 로컬화한 프리미엄 CSS 테마 및 마이크로 애니메이션 적용.

### **Intelligence Engine**
- **Google Gemini 2.0 Pro / Flash**: 정교한 텍스트 분석 및 다국어(영어/한국어) 요약/번역 엔진.
- **Natural Language Processing**: 도메인 특화 프롬프트 엔지니어링을 통한 고품질 금융 리포트 생성.

### **Automated Infrastructure**
- **Python 3.9+**: 데이터 수집, 가공 및 자동화 파이프라인 코어.
- **GitHub Actions**: 24/7 무중단 자동 크롤링 및 배포 자동화.
- **Incremental Data Store**: JSON 기반의 경량화된 증분 데이터 저장 시스템.

---

## 📂 프로젝트 구조 (Project Structure)

```text
/
├── backend/            # Data collection & AI Intelligence Core
│   ├── crawler.py      # Core engine for scraping, AI summary, and logic
│   └── bootstrap_*.py  # Metadata & Infrastructure setup scripts
├── data/               # Daily Signal JSON artifacts
├── posts/              # Product Devlogs and project history
├── tests/              # Validation & Quality assurance scripts
├── app.py              # Streamlit Presentation layer
└── requirements.txt    # System dependencies
```

---

## 🚦 시작하기 (Getting Started)

### 1. 전제 조건
- Python 3.9 이상
- Google Gemini API Key

### 2. 환경 설정
`.env` 파일에 아래 변수를 설정합니다.
```env
GEMINI_API_KEY=your_key_here
ADMIN_PASSWORD=your_password
```

### 3. 수집 엔진 가동 (Local Force Mode)
```bash
# 특정 날짜의 데이터를 강제로 최신 프롬프트로 재생성
python backend/crawler.py --date 2026-03-06 --market KR --force
```

### 4. 대시보드 런칭
```bash
streamlit run app.py
```

---

## 🗺️ 로드맵 (Roadmap)
- [x] AI 정밀 요약 엔진 및 프롬프트 고도화
- [x] GitHub Actions 자동 스케줄링 시스템 구축
- [x] 로컬 데이터 강제 갱신(--force) 인프라 완료
- [ ] **Modern Web Frontend (Next.js/React) 전환**
- [ ] 실시간 알림 서비스 연동 (Webhook)
- [ ] 다국어 지원 엔진 확장

---

## 📄 라이선스 (License)
This project is licensed under the MIT License.

---
**Crafted with Passion by [datavalua](https://github.com/datavalua)**
