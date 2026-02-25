import streamlit as st
import json
import os
import datetime
import crawler
import pandas as pd
import FinanceDataReader as fdr
from dotenv import load_dotenv

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
    
    /* Make the TOP container sticky */
    /* In Streamlit, the main content is in a vertical block. 
       We target the first child of the block-container. */
    .main .block-container > div:nth-child(1) {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 1000;
        padding-top: 10px;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f2f6;
    }
    
    /* Content Padding so it doesn't hide under the sticky header */
    /* Since we use position: sticky instead of fixed, we don't need excessive padding,
       but nth-child(1) being sticky might be enough. */

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

# --- Header & Nav (Sticky Area) ---
def render_sticky_header():
    # Everything in this function MUST be at the very top of the script calls
    # for the CSS nth-child(1) to target it correctly.
    
    # Title row
    st.title("📈 시그널 - 실시간 핵심 정보")
    
    # 1. Navigation Row
    if "view" not in st.session_state:
        st.session_state["view"] = "주식 시그널"
    
    nav_opts = ["주식 시그널", "관련 주식 조회"]
    if st.session_state.get("admin_logged_in"):
        nav_opts.append("관리자 도구")
    
    cols_nav = st.columns(len(nav_opts))
    for i, opt in enumerate(nav_opts):
        btn_label = f"**{opt}**" if st.session_state["view"] == opt else opt
        if cols_nav[i].button(btn_label, key=f"nav_{opt}"):
            st.session_state["view"] = opt
            st.experimental_rerun()
            
    # 2. Market & Date Controls (Fixed Area)
    if st.session_state["view"] == "주식 시그널":
        st.markdown("### 📊 조회 설정")
        col_m, col_d, col_spacer = st.columns([2, 2, 4])
        with col_m:
            market = st.selectbox("시장", ["🇰🇷 국내 주식", "🇺🇸 미국 주식"])
        with col_d:
            kst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
            sel_date = st.date_input("날짜", kst_now.date())
            date_str = sel_date.strftime("%Y-%m-%d")
        return market, date_str
    
    return None, None

# --- Sidebar (Login/Logout) ---
def render_sidebar():
    st.sidebar.markdown("### 🔑 관리자")
    if not st.session_state.get("admin_logged_in"):
        pwd = st.sidebar.text_input("PASSWORD", type="password")
        if st.sidebar.button("LOGIN"):
            if pwd == ADMIN_PASSWORD:
                st.session_state["admin_logged_in"] = True
                st.experimental_rerun()
            else:
                st.sidebar.error("WRONG PASSWORD")
    else:
        st.sidebar.success("ADMIN LOGGED IN")
        if st.sidebar.button("LOGOUT"):
            st.session_state["admin_logged_in"] = False
            st.session_state["view"] = "주식 시그널"
            st.experimental_rerun()

# --- Main Views ---
def show_signals(market, date_str):
    prefix = "us_" if market == "🇺🇸 미국 주식" else ""
    data = load_data(f"{prefix}{date_str}")
    
    if not data:
        st.info(f"{date_str} 시그널 데이터가 없습니다.")
        return
        
    st.caption(f"Last updated: {data.get('last_updated', 'N/A')}")
    
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
                
                with st.expander("뉴스 보기"):
                    for art in signal.get("news_articles", [])[:5]:
                        st.markdown(f"• [{art['title']}]({art['url']}) ({art.get('source', '')})")
            
            with c2:
                st.write("**관련 종목**")
                for rs in signal.get("related_stocks", []):
                    st.write(f"• {rs['name']} ({format_rate(rs['change_rate'])})")
            st.markdown("---")

def show_search():
    st.header("🔍 관련 주식 조회")
    idx = st.selectbox("Index", ["S&P500", "NASDAQ", "KOSPI", "KOSDAQ"])
    if st.button("Fetch"):
        df = fdr.StockListing(idx)
        st.dataframe(df)

def show_admin():
    st.header("⚙️ 관리 도구")
    if st.button("Reload Metadata Cache"):
        from streamlit.legacy_caching import clear_cache
        clear_cache()
        st.success("Cache Cleared")
    
    st.markdown("---")
    st.subheader("Manual Crawler")
    m = st.selectbox("Market", ["KR", "US"])
    d = st.date_input("Date", datetime.datetime.now().date())
    if st.button("Run Crawler"):
        with st.spinner("Crawling..."):
            if crawler.generate_daily_json(d.strftime("%Y-%m-%d"), market=m):
                st.success("Success")
            else: st.error("Failed")

# --- Application Flow ---
def main():
    # 1. First, we define the sticky area
    market, date_str = render_sticky_header()
    
    # 2. Sidebar for login
    render_sidebar()
    
    # 3. Main content
    view = st.session_state["view"]
    if view == "주식 시그널":
        show_signals(market, date_str)
    elif view == "관련 주식 조회":
        show_search()
    elif view == "관리자 도구":
        show_admin()

if __name__ == "__main__":
    main()
