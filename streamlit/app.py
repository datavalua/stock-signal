import streamlit as st
import json
import os
import datetime
import sys
# Add project root to sys.path so we can import from 'backend'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend import crawler
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

def safe_clear_cache():
    """Support clearing cache across Streamlit versions."""
    try:
        if hasattr(st, "cache_data"):
            st.cache_data.clear()
            st.cache_resource.clear()
        
        # Legacy clearing
        try:
            from streamlit.legacy_caching import clear_cache
            clear_cache()
        except ImportError:
            try:
                import streamlit.runtime.legacy_caching as lc
                lc.clear_cache()
            except:
                pass
    except:
        pass

# --- Initialization ---
load_dotenv()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
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
    /* Make Streamlit header transparent but keep it visible for the mobile sidebar menu (hamburger icon) */
    header[data-testid="stHeader"] { 
        background: transparent !important; 
    }
    
    /* Sticky Top Container for Title & Controls */
    .main .block-container > div:nth-child(1) {
        position: sticky;
        top: 2.5rem; /* Offset to prevent overlapping with the hamburger menu */
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
def load_data(date_str):
    file_path = os.path.join(DATA_DIR, f"{date_str}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return None
    return None

@st.cache(ttl=3600, show_spinner=False, allow_output_mutation=True)
def get_stock_listing_cached(idx):
    try:
        if idx in ["KOSPI", "KOSDAQ"]:
            # Fallback to Naver Mobile API because FDR KRX is often geo-blocked
            import requests
            import pandas as pd
            url = f"https://m.stock.naver.com/api/stocks/marketValue/{idx}"
            headers = {"User-Agent": "Mozilla/5.0"}
            all_stocks = []
            page = 1
            while True:
                res = requests.get(url, params={"page": page, "pageSize": 100}, headers=headers)
                if res.status_code != 200: break
                try: data = res.json()
                except: break
                stocks = data.get('stocks', [])
                if not stocks: break
                all_stocks.extend(stocks)
                page += 1
            
            if all_stocks:
                df = pd.DataFrame(all_stocks)
                df = df.rename(columns={"itemCode": "Symbol", "stockName": "Name"})
                return df
                
            # If Naver fails natively for some reason, try original FDR
            df = fdr.StockListing("KRX")
            return df[df["Market"] == idx]
        
        df = fdr.StockListing(idx)
        return df
    except Exception as e:
        print(f"Error fetching {idx} listing: {e}")
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
    st.info("각 지수별 상장 종목 리스트와 상세 정보(산업군, 경쟁사)를 조회합니다.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        idx = st.selectbox("시장 지수 선택", ["S&P500", "NASDAQ", "KOSPI", "KOSDAQ"])
    with col2:
        st.write("") # Add some spacing so the button aligns better with the selectbox label
        st.write("")
        search_clicked = st.button("조회 시작")
        
    if search_clicked:
        with st.spinner(f"{idx} 종목 리스트를 불러오는 중..."):
            try:
                meta = load_stock_metadata()
                market_key = "US" if idx in ["S&P500", "NASDAQ"] else "KR"
                market_meta = meta.get(market_key, {})
                
                df = get_stock_listing_cached(idx)
                
                if df is None or df.empty:
                    st.warning("종목 리스트를 가져오는 데 실패했습니다. 잠시 후 다시 시도해 주세요.")
                    return
                
                # Standardize columns to US Standard: Symbol, Name
                if "Symbol" in df.columns:
                    df = df.rename(columns={"Symbol": "Symbol"})
                elif "Code" in df.columns:
                    df = df.rename(columns={"Code": "Symbol"})
                
                if "Name" in df.columns:
                    df = df.rename(columns={"Name": "Name"})
                
                # Optimized Enrichment: Add Industrial/Peers from our metadata
                tickers = df["Symbol"].astype(str).tolist()
                industries = []
                peers_list = []
                
                for t in tickers:
                    m = market_meta.get(t, {})
                    industries.append(", ".join(m.get("industry", [])) if m.get("industry") else "-")
                    peers_list.append(", ".join(m.get("peers", [])) if m.get("peers") else "-")
                
                df["Industry"] = industries
                df["Peers"] = peers_list
                
                # Unify layout: force core columns (US Standard)
                display_cols = ["Symbol", "Name", "Industry", "Peers"]
                
                # Ensure all display columns exist, filling missing ones with default '-'
                for col in display_cols:
                    if col not in df.columns:
                        df[col] = "-"
                        
                df_view = df[display_cols].copy()
                
                st.success(f"조회 완료 (총 {len(df)}개 전수 표시)")
                
                # Fixed column widths for consistent size across all markets
                try:
                    st.dataframe(
                        df_view,
                        column_config={
                            "Symbol": st.column_config.TextColumn("Symbol", width=100),
                            "Name": st.column_config.TextColumn("Name", width=200),
                            "Industry": st.column_config.TextColumn("Industry", width=200),
                            "Peers": st.column_config.TextColumn("Peers", width=400)
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                except AttributeError:
                    # Fallback for Streamlit < 1.23.0
                    st.dataframe(df_view, use_container_width=True)
                    
            except Exception as e:
                st.error(f"조회 중 오류 발생: {e}")

def show_admin():
    st.header("⚙️ 관리자 도구")
    if st.button("🔄 종목 메타데이터 캐시 초기화"):
        safe_clear_cache()
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
            
    st.markdown("---")
    st.subheader("🌐 글로벌 종목 정보 자동 확장 (AI Bootstrap)")
    st.info("S&P500, NASDAQ, KOSPI, KOSDAQ 종목의 산업군 및 경쟁사 정보를 AI가 자동으로 수집합니다. (API 할당량 준수를 위해 인덱스별 상위 20개씩 우선 처리)")
    if st.button("🚀 전체 종목 정보 확장 시작"):
        from backend import bootstrap_metadata
        with st.spinner("AI가 전 세계 종목 정보를 분석 중입니다... (약 1~2분 소요)"):
            try:
                bootstrap_metadata.run_bootstrap(limit_per_index=20)
                st.success("종목 정보 확장이 완료되었습니다! 이제 풍부한 관련 주식 정보를 보실 수 있습니다.")
                # Reload metadata after update
                safe_clear_cache()
            except Exception as e:
                st.error(f"확장 중 오류 발생: {e}")

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
