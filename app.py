import streamlit as st
import json
import os
import datetime
import crawler
import pandas as pd
import FinanceDataReader as fdr
from dotenv import load_dotenv

# --- Compatibility Wrapper ---
def safe_rerun():
    """Support both legacy (0.89.0) and modern Streamlit rerun."""
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()
    except:
        pass

# --- Initialization ---
load_dotenv()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "HIDDEN_PASSWORD")
DATA_DIR = "data"
STOCK_METADATA_FILE = os.path.join(DATA_DIR, "stock_metadata.json")

# --- Streamlit Config (0.89.0 Compatible) ---
st.set_page_config(
    page_title="시그널 - 실시간 핫이슈",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling for Sticky Header ---
st.markdown("""
<style>
    /* Hide default Streamlit header */
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    
    /* Sticky Top Container for Title & Controls */
    .main .block-container > div:nth-child(1) {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 1000;
        padding-top: 15px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f0f2f6;
    }
    
    .stApp { background-color: #f7f9fb !important; }
    
    .content-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #eef2f6;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Tag Styling */
    .signal-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .tag-industry { background-color: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
    .tag-type { background-color: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }

    /* Button Styling */
    .stButton > button {
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading (0.89.0 Compatible) ---
@st.cache(ttl=600, show_spinner=False)
def load_data(date_str):
    file_path = os.path.join(DATA_DIR, f"{date_str}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return None
    return None

@st.cache(ttl=600, show_spinner=False)
def load_stock_metadata():
    if os.path.exists(STOCK_METADATA_FILE):
        try:
            with open(STOCK_METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"KR": {}, "US": {}}

def format_rate(rate_str):
    if not rate_str: return "0.0%"
    if rate_str.startswith("+"): return f"🔴 {rate_str}"
    elif rate_str.startswith("-"): return f"🔵 {rate_str}"
    return rate_str

# --- Sidebar (Navigation & Login) ---
def render_sidebar():
    st.sidebar.title("📈 시그널 센터")
    
    # 1. Navigation (Moved back to sidebar as requested)
    st.sidebar.markdown("### 🧭 메뉴")
    if "current_view" not in st.session_state:
        st.session_state["current_view"] = "주식 시그널"
    
    nav_options = ["주식 시그널", "관련 주식 조회"]
    if st.session_state.get("admin_logged_in"):
        nav_options.append("관리자 도구")
    
    current_idx = 0
    if st.session_state["current_view"] in nav_options:
        current_idx = nav_options.index(st.session_state["current_view"])
        
    st.session_state["current_view"] = st.sidebar.radio("", nav_options, index=current_idx)
    
    st.sidebar.markdown("---")
    
    # 2. Login
    st.sidebar.markdown("### 🔑 관리자 로그인")
    if not st.session_state.get("admin_logged_in"):
        pwd = st.sidebar.text_input("PASSWORD", type="password", key="sidebar_pwd")
        if st.sidebar.button("LOGIN"):
            if pwd == ADMIN_PASSWORD:
                st.session_state["admin_logged_in"] = True
                safe_rerun()
            else:
                st.sidebar.error("WRONG PASSWORD")
    else:
        st.sidebar.success("✅ 관리자 로그인됨")
        if st.sidebar.button("LOGOUT"):
            st.session_state["admin_logged_in"] = False
            st.session_state["current_view"] = "주식 시그널"
            safe_rerun()

# --- Main Sticky Header ---
def render_main_header():
    # Page Title
    st.title("📊 오늘의 핵심 시그널")
    
    # Market & Date Controls (Stay sticky at top of main area)
    view = st.session_state.get("current_view", "주식 시그널")
    if view == "주식 시그널":
        st.markdown("##### 🔍 조회 설정")
        col_m, col_d, col_spacer = st.columns([2, 2, 4])
        with col_m:
            market = st.selectbox("시장 선택", ["🇰🇷 국내 주식", "🇺🇸 미국 주식"])
        with col_d:
            kst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
            sel_date = st.date_input("날짜 선택", kst_now.date())
            date_str = sel_date.strftime("%Y-%m-%d")
        return market, date_str
    return None, None

# --- Content Views ---
def show_signals(market, date_str):
    prefix = "us_" if market == "🇺🇸 미국 주식" else ""
    data = load_data(f"{prefix}{date_str}")
    
    if not data:
        st.info(f"{date_str}의 시그널 데이터가 아직 생성되지 않았습니다.")
        return
        
    st.caption(f"최종 업데이트: {data.get('last_updated', 'N/A')}")
    
    for signal in data.get("signals", []):
        theme = signal.get("theme", "")
        sig_type = signal.get("signal_type", "")
        m_stock = signal.get("main_stock", {})
        
        with st.container():
            c1, c2 = st.columns([3, 2])
            with c1:
                # Tags
                tag_html = ""
                if theme: tag_html += f"<span class='signal-tag tag-industry'>{theme}</span>"
                if sig_type: tag_html += f"<span class='signal-tag tag-type'>{sig_type}</span>"
                if tag_html: st.markdown(tag_html, unsafe_allow_html=True)
                
                st.markdown(f"### {m_stock.get('name')} : {format_rate(m_stock.get('change_rate'))}")
                st.markdown(f"**{signal.get('short_reason')}**")
                st.write(signal.get("summary"))
                
                with st.expander("관련 뉴스/정보 보기"):
                    for art in signal.get("news_articles", [])[:5]:
                        st.markdown(f"• [{art['title']}]({art['url']}) ({art.get('source', '')})")
            
            with c2:
                st.write("**관련 종목**")
                for rs in signal.get("related_stocks", []):
                    st.write(f"• {rs['name']} ({format_rate(rs['change_rate'])})")
            st.markdown("---")

def show_search():
    st.header("🔍 관련 주식 조회")
    idx = st.selectbox("시장 지수 선택", ["S&P500", "NASDAQ", "KOSPI", "KOSDAQ"])
    if st.button("조회 시작"):
        df = fdr.StockListing(idx)
        st.dataframe(df)

def show_admin():
    st.header("⚙️ 관리자 도구")
    if st.button("🔄 종목 메타데이터 캐시 초기화"):
        from streamlit.legacy_caching import clear_cache
        clear_cache()
        st.success("캐시가 초기화되었습니다.")
    
    st.markdown("---")
    st.subheader("🚀 수동 크롤링 실행")
    c_m = st.selectbox("시장", ["KR", "US"])
    c_d = st.date_input("날짜", datetime.datetime.now().date())
    if st.button("크롤링 실행"):
        with st.spinner("데이터 수집 및 생성 중..."):
            if crawler.generate_daily_json(c_d.strftime("%Y-%m-%d"), market=c_m):
                st.success("데이터 생성 완료!")
            else: st.error("데이터 생성 중 오류가 발생했습니다.")

# --- Main App Flow ---
def main():
    # 1. Sidebar first (Navigation & Auth)
    render_sidebar()
    
    # 2. Main Sticky Header (Title & Controls)
    market, date_str = render_main_header()
    
    # 3. Content Router
    view = st.session_state.get("current_view", "주식 시그널")
    
    if view == "주식 시그널":
        show_signals(market, date_str)
    elif view == "관련 주식 조회":
        show_search()
    elif view == "관리자 도구":
        show_admin()
    else:
        st.session_state["current_view"] = "주식 시그널"
        safe_rerun()

if __name__ == "__main__":
    main()
