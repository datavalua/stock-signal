import os
import json
import time
import FinanceDataReader as fdr
import dotenv
try:
    import google.generativeai as genai
    from google.generativeai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

dotenv.load_dotenv()

DATA_DIR = "data"
METADATA_FILE = os.path.join(DATA_DIR, "stock_metadata.json")

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"KR": {}, "US": {}}

def save_metadata(metadata):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

def get_genai_config():
    """Support Streamlit secrets and environment variables."""
    if not GENAI_AVAILABLE:
        return None
    
    api_key = None
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY")
        
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return None

def process_batch(market, tickers_info):
    """
    tickers_info: list of {'symbol': '...', 'name': '...'}
    """
    if not get_genai_config():
        return {}
        
    prompt_parts = [
        "당신은 글로벌 주식 시장 전문가입니다. 다음 종목들에 대해 '주요 산업 분야(industry)'와 '관련 기업/경쟁사(peers)' 정보를 분석하세요.\n\n",
        "**분석 조건:**\n",
        "1. **industry**: 해당 기업의 핵심 사업 분야를 1~2개의 키워드로 작성하세요. (예: '반도체', '전기차', '전자상거래')\n",
        "2. **peers**: 해당 기업과 같은 산업군이거나 밀접한 연관이 있는 다른 기업의 **티커/종목코드** 리스트를 3~5개 작성하세요.\n\n",
        "**분석 대상 리스트:**\n"
    ]
    
    for item in tickers_info:
        prompt_parts.append(f"- {item['name']} ({item['symbol']})\n")
        
    prompt_parts.append(
        "\n**출력 형식**: 아래 JSON 구조로만 답변하세요. 다른 텍스트는 포함하지 마세요.\n"
        "{\n"
        "  \"종목코드\": {\"industry\": [\"산업명\"], \"peers\": [\"코드1\", \"코드2\"]}\n"
        "}"
    )
    
    try:
        # Use gemini-1.5-pro for high-quality metadata as previously requested
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content("".join(prompt_parts))
        text = response.text.strip()
        
        # Remove markdown if present
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        return json.loads(text)
    except Exception as e:
        print(f"Error processing batch: {e}")
        return {}

def run_bootstrap(indices=["KOSPI", "KOSDAQ", "S&P500", "NASDAQ"], limit_per_index=50):
    if not GENAI_AVAILABLE:
        print("Gemini SDK not installed.")
        return
        
    metadata = load_metadata()
    
    for idx_name in indices:
        print(f"\n--- Processing {idx_name} ---")
        try:
            df = fdr.StockListing(idx_name)
            # Standardize column names
            if 'Symbol' in df.columns: df = df.rename(columns={'Symbol': 'symbol', 'Name': 'name'})
            elif 'Code' in df.columns: df = df.rename(columns={'Code': 'symbol', 'Name': 'name'})
            
            # Use market mapping
            market = "US" if idx_name in ["S&P500", "NASDAQ"] else "KR"
            
            # Limit for safety
            targets = df.head(limit_per_index).to_dict('records')
            
            batch_size = 10 # Smaller batch for more reliable JSON from Pro model
            for i in range(0, len(targets), batch_size):
                batch = targets[i:i+batch_size]
                # Skip already completed
                batch_to_process = [t for t in batch if t['symbol'] not in metadata[market] or not metadata[market][t['symbol']].get('peers')]
                
                if not batch_to_process:
                    continue
                    
                print(f"Processing batch {i//batch_size + 1} ({market})...")
                results = process_batch(market, batch_to_process)
                
                # Merge results
                for symbol, data in results.items():
                    orig = next((t for t in batch if t['symbol'] == symbol), None)
                    name = orig['name'] if orig else metadata[market].get(symbol, {}).get('name', symbol)
                    
                    metadata[market][symbol] = {
                        "name": name,
                        "industry": data.get("industry", []),
                        "peers": data.get("peers", [])
                    }
                
                save_metadata(metadata)
                time.sleep(10) # More room for Pro model RPD limits
                
        except Exception as e:
            print(f"Error processing index {idx_name}: {e}")
            
    print("\nBootstrap completed!")

if __name__ == "__main__":
    run_bootstrap()
