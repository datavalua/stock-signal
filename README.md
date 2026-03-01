# 📈 Stock Signal: Real-time Market Intelligence

> **토스증권 시그널 클론** - 실시간 시장 급등주의 원인을 AI로 분석하고 연관 테마를 시각화하는 지능형 대시보드입니다.

[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Backend-Python-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

---

## ✨ 핵심 기능 (Key Features)

- **🚀 실시간 핫이슈 포착**: KOSPI, KOSDAQ, S&P 500, NASDAQ 시장의 급등주를 실시간으로 트래킹합니다.
- **🤖 AI 뉴스 인사이트**: Google Gemini API를 활용하여 파편화된 뉴스를 "왜 올랐는지"에 초점을 맞춰 한 줄로 요약합니다.
- **🔗 지능형 테마 매핑**: 단순히 한 종목만 보여주는 것이 아니라, 해당 이슈로 인해 함께 움직이는 **경쟁사 및 공급망 기업**을 자동으로 연결합니다.
- **📅 히스토리 타임라인**: 과거 날짜의 시그널을 조회하여 시장의 흐름이 어떻게 변화했는지 복기할 수 있습니다.

---

## 🛠️ 기술 스택 (Tech Stack)

### **Frontend**
- **Streamlit**: 파이썬 기반의 빠르고 직관적인 데이터 대시보드 UI.
- **Custom CSS**: 토스 스타일의 깔끔한 디자인을 위한 스타일 커스텀 적용.

### **Backend & Data**
- **Python 3.10**: 데이터 크롤링 및 분석 유틸리티.
- **Google Gemini Pro**: 뉴스 컨텐츠 분석 및 의미론적 요약 수행.
- **GitHub Actions**: 20분 단위 자동 데이터 수집 파이프라인.
- **FinanceDataReader & BeautifulSoup4**: 정밀한 금융 데이터 및 뉴스 크롤링.

---

## 📂 프로젝트 구조 (Project Structure)

```text
/
├── backend/            # 데이터 수집 및 AI 분석 코어 로직 (Python)
│   ├── crawler.py      # 뉴스 크롤링 및 Gemini 연동
│   └── bootstrap_*.py  # 종목 메타데이터 초기 구축 스크립트
├── streamlit/          # Streamlit 대시보드 웹 앱 (app.py)
├── data/               # 실시간/과거 시그널 데이터 (JSON)
├── tests/              # 단위 테스트 및 검증 스크립트
├── scripts/            # 기타 유틸리티 및 HTML 샘플
├── .github/workflows/  # 크롤링 및 배포 자동화 (CI/CD)
└── README.md
```

---

## 🚦 시작하기 (Getting Started)

### 1. 환경 설정
`.env` 파일에 Gemini API 키를 설정합니다.
```env
GEMINI_API_KEY=your_gemini_api_key
```

### 2. 데이터 수집 실행
```bash
python backend/crawler.py --market KR
```

### 3. 대시보드 실행
```bash
streamlit run streamlit/app.py
```

---

## 🗺️ 로드맵 (Roadmap)
- [x] Python 기반 데이터 파이프라인 및 AI 요약 엔진 구축
- [x] GitHub Actions 자동화 시스템 완료
- [ ] **Next.js 기반 모던 프론트엔드 전환 (진행 중)**
- [ ] Google AdSense 및 SEO 최적화 적용
- [ ] 실시간 알림 시스템 (Telegram/Discord) 연동

---

## 📄 라이선스 (License)
이 프로젝트는 MIT 라이선스를 따릅니다.

---
**Developed by [datavalua](https://github.com/datavalua)**
