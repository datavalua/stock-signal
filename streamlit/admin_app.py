import os
import json
import streamlit as st
import pandas as pd

# This will get robust soon. For now we just implement the shell.
# It should allow pulling the current MAJOR_STOCKS arrays and peer maps from crawler.py
# to bootstrap the JSON file if it doesn't exist.

DATA_FILE = "data/stock_metadata.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"KR": {}, "US": {}}

def save_data(data):
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
import FinanceDataReader as fdr

def fetch_index_stocks(index_name):
    """Fetch stock listing for a given index using FinanceDataReader."""
    try:
        df = fdr.StockListing(index_name)
        return df
    except Exception as e:
        st.error(f"Error fetching {index_name}: {e}")
        return pd.DataFrame()

def main():
    st.set_page_config(page_title="Stock Signal Admin", page_icon="⚙️", layout="wide")
    st.title("⚙️ Stock Data Management Admin")
    
    st.markdown("이 페이지에서는 애플리케이션에서 모니터링할 **타겟 종목(KR/US)** 및 **관련 산업/경쟁사 매핑** 데이터를 JSON 파일로 관리합니다.")
    
    data = load_data()
    
    # Fallback to simple selectbox for 0.89.0 compatibility instead of st.tabs
    menu = st.sidebar.selectbox("메뉴 선택", ["KR Market 모니터링", "US Market 모니터링", "지수 종목 검색 (추가용)"])
    
    # ---------------- KR Market ----------------
    if menu == "KR Market 모니터링":
        st.subheader("한국(KR) 타겟 종목 관리")
        kr_data = data.get("KR", {})
                
        st.write("Streamlit 0.89 환경에서는 표 편집이 지원되지 않아, JSON 텍스트 형태로 직접 편집합니다.")
        
        # Convert dictionary to pretty JSON string for editing
        kr_json_str = json.dumps(kr_data, ensure_ascii=False, indent=4)
        
        edited_kr_json = st.text_area("KR 종목 JSON 데이터", value=kr_json_str, height=500)
        
        if st.button("변경사항 저장 (KR)", key="kr_save"):
            try:
                new_kr_data = json.loads(edited_kr_json)
                data['KR'] = new_kr_data
                save_data(data)
                st.success("한국 종목 데이터가 저장되었습니다! (crawler.py에 즉시 반영됨)")
            except json.JSONDecodeError:
                st.error("JSON 형식이 잘못되었습니다. 괄호와 따옴표를 확인해 주세요.")
                
    # ---------------- US Market ----------------
    elif menu == "US Market 모니터링":
        st.subheader("미국(US) 타겟 종목 관리")
        us_data = data.get("US", {})
                 
        st.write("Streamlit 0.89 환경에서는 표 편집이 지원되지 않아, JSON 텍스트 형태로 직접 편집합니다.")
        
        us_json_str = json.dumps(us_data, ensure_ascii=False, indent=4)
        
        edited_us_json = st.text_area("US 종목 JSON 데이터", value=us_json_str, height=500)
        
        if st.button("변경사항 저장 (US)", key="us_save"):
            try:
                new_us_data = json.loads(edited_us_json)
                data['US'] = new_us_data
                save_data(data)
                st.success("미국 종목 데이터가 저장되었습니다! (crawler.py에 즉시 반영됨)")
            except json.JSONDecodeError:
                st.error("JSON 형식이 잘못되었습니다. 괄호와 따옴표를 확인해 주세요.")

    # ---------------- Index Fetcher ----------------
    elif menu == "지수 종목 검색 (추가용)":
        st.subheader("시장 지수 구성종목 조회")
        st.markdown("FinanceDataReader를 이용하여 지수의 편입 종목 리스트를 조회합니다. 조회된 종목의 코드를 복사해서 모니터링 탭에 수동으로 추가하세요.")
        
        idx_option = st.selectbox("조회할 지수 선택", ["S&P500", "NASDAQ", "KOSPI", "KOSDAQ"])
        if st.button(f"{idx_option} 종목 가져오기"):
            with st.spinner(f"Fetching {idx_option} data..."):
                df = fetch_index_stocks(idx_option)
                if not df.empty:
                    st.success(f"총 {len(df)}개의 종목을 불러왔습니다.")
                    st.dataframe(df) # st.dataframe does not support use_container_width in 0.89
                else:
                    st.warning("데이터를 불러오지 못했습니다.")

if __name__ == "__main__":
    main()
