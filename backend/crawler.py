import os
import json
import time
import datetime
from datetime import timedelta
import dotenv
dotenv.load_dotenv()

import FinanceDataReader as fdr
import requests
from bs4 import BeautifulSoup
import traceback

try:
    import google.generativeai as genai
    from google.generativeai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-generativeai package not found. AI summaries will be disabled.")
except Exception as e:
    GENAI_AVAILABLE = False
    print(f"Error loading Gemini SDK: {e}")

GENAI_CLIENT_INITIALIZED = False

def get_genai_client():
    """Initialize Gemini client lazily using Streamlit secrets or env var.
    Returns True if client is ready, False otherwise.
    """
    global GENAI_CLIENT_INITIALIZED
    if not GENAI_AVAILABLE:
        return False
    if GENAI_CLIENT_INITIALIZED:
        return True
    api_key = None
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        GENAI_CLIENT_INITIALIZED = True
        return True
    return False

try:
    import holidays
    HOLIDAYS_AVAILABLE = True
except ImportError:
    HOLIDAYS_AVAILABLE = False


# Constants
DATA_DIR = "data"

def load_stock_metadata():
    """Load stock metadata from JSON file."""
    metadata_path = os.path.join(DATA_DIR, "stock_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"KR": {}, "US": {}}

def get_model_chain():
    """Return a list of models to try in order (Fallback)."""
    env_model = os.getenv("GEMINI_MODEL")
    if env_model:
        return [env_model]
    
    # Priority: High quota model -> High quality model
    return ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-flash-lite-latest']

def call_gemini_with_fallback(prompt, config_kwargs=None, max_retries_per_model=3):
    """
    Execute Gemini API call with fallback models and RPM-aware sleep.
    """
    if not get_genai_client():
        return None
        
    models = get_model_chain()
    config = types.GenerationConfig(**(config_kwargs or {}))
    
    for model_name in models:
        # Give some breathing room to respect RPM limits (e.g. 15 RPM ~ 4s spacing)
        time.sleep(4.5)
        for attempt in range(max_retries_per_model):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt, generation_config=config)
                # Successful call
                return response
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "exhausted" in err_str or "quota" in err_str:
                    print(f"Rate limited or quota exceeded for {model_name} (attempt {attempt+1}).")
                    if attempt < max_retries_per_model - 1:
                        # Wait before retry on same model
                        time.sleep(15 * (attempt + 1))
                        continue
                    else:
                        # Move to fallback model
                        print(f"Moving to fallback model after exhausting {model_name}.")
                        break
                else:
                    print(f"Error calling {model_name}: {e}")
                    break # Not a rate limit issue, skip to next model maybe?
                    
    print("All models in fallback chain failed.")
    return None

# Global configuration loaded once
STOCK_METADATA = load_stock_metadata()

# Reconstruct MAJOR_STOCKS and US_MAJOR_STOCKS lists for backwards compatibility within crawler.py
MAJOR_STOCKS = [{"symbol": k, "name": v["name"]} for k, v in STOCK_METADATA.get("KR", {}).items()]
US_MAJOR_STOCKS = [{"symbol": k, "name": v["name"]} for k, v in STOCK_METADATA.get("US", {}).items()]

def get_investor_data(symbol, date_str):
    """
    Fetch daily net purchases (개인, 외국인, 기관) from Naver Finance.
    """
    try:
        url = f"https://finance.naver.com/item/frgn.naver?code={symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Find the table containing the investor data
        # Note: Depending on market time, top row could be today or yesterday.
        # We will just grab the top row of the investor trend table.
        table = soup.select_one('table.type2')
        if not table:
            return None
            
        rows = table.select('tr')
        target_row = None
        for row in rows:
            # Skip headers and empty rows
            if not row.select_one('td.tc'):
                continue
            
            # Extract date from the first column
            row_date = row.select_one('td.tc span.tah').text.strip()
            # Naver shows YYYY.MM.DD
            formatted_date_str = date_str.replace("-", ".")
            if row_date == formatted_date_str:
                target_row = row
                break
            # If we don't find exact date, just take the first available data row (most recent trading day)
            elif target_row is None:
                target_row = row
        
        if not target_row:
            return None
            
        cols = target_row.select('td')
        if len(cols) >= 7:
            # Indices for Naver Finance table:
            # 0: Date, 1: 종가, 2: 전일비, 3: 등락률, 4: 거래량
            # 5: 기관 순매매량, 6: 외인 순매매량, 7: 외국인 보유주수 (sometimes column structure changes slightly)
            # It's safer to just pick them by their known indices:
            
            # On the 'frgn' tab:
            # 5th index = 기관 (Institution)
            # 6th index = 외국인 (Foreigner)
            inst = cols[5].text.strip()
            foreign = cols[6].text.strip()
            
            # Since Naver doesn't explicitly show '개인(Retail)' on this specific summary table easily, 
            # we can infer it broadly, or we just scrape the basic ones available.
            # Let's format them:
            # Gather up to 7 days
            recent_data = []
            count = 0
            for row in rows:
                if count >= 7:
                    break
                if not row.select_one('td.tc'):
                    continue
                cols = row.select('td')
                if len(cols) >= 7:
                    date_val = row.select_one('td.tc span.tah').text.strip()
                    inst = cols[5].text.strip()
                    foreign = cols[6].text.strip()
                    recent_data.append(f"[{date_val}] 기관: {inst}주, 외국인: {foreign}주")
                    count += 1
            
            return {
                "최근_동향": " | ".join(recent_data),
                "is_realtime": False
            }
            
    except Exception as e:
        print(f"Error scraping Naver investor data: {e}")
        
    return None

def get_stock_change(symbol, date_str):
    """
    Fetch actual stock change rate for a given symbol and date.
    """
    try:
        end_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        start_date = end_date - timedelta(days=10) # Enough buffer for weekends
        
        df = fdr.DataReader(symbol, start_date.strftime("%Y-%m-%d"), date_str)
        if len(df) >= 2:
            prev_close = df['Close'].iloc[-2]
            today_close = df['Close'].iloc[-1]
            change_pct = ((today_close - prev_close) / prev_close) * 100
            return change_pct
    except Exception as e:
        pass
    
    return 0.0

def get_top_movers(date_str, top_n=10, market="KR"):
    """
    Find top movers from MAJOR_STOCKS or US_MAJOR_STOCKS for a given date.
    Sorts by absolute change percentage.
    """
    print(f"Finding top movers for {date_str} among {market} major stocks...")
    movers = []
    stocks_list = US_MAJOR_STOCKS if market == "US" else MAJOR_STOCKS
    
    for stock in stocks_list:
        change = get_stock_change(stock['symbol'], date_str)
        if abs(change) > 0.01: # Ignore tiny changes
            movers.append({
                "symbol": stock['symbol'],
                "name": stock['name'],
                "change": change,
                "change_rate": f"{'+' if change >= 0 else ''}{change:.1f}%",
                "market": market
            })
    
    # Sort by absolute change value descending
    movers.sort(key=lambda x: abs(x['change']), reverse=True)
    return movers[:top_n]

def scrape_article_content(url):
    """
    Fetch and extract the main text content from a Naver news article.
    """
    if "article_id=" in url and "office_id=" in url:
        import re
        article_id = re.search(r'article_id=(\d+)', url)
        office_id = re.search(r'office_id=(\d+)', url)
        if article_id and office_id:
            url = f"https://n.news.naver.com/mnews/article/{office_id.group(1)}/{article_id.group(1)}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Naver Finance is euc-kr, but n.news.naver.com is utf-8
        if "n.news.naver.com" in url:
            response.encoding = 'utf-8'
        else:
            response.encoding = 'euc-kr'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Naver News main content area
        # Try multiple selectors for different Naver news layouts
        content = soup.select_one('#dic_area')
        if not content:
            content = soup.select_one('#newsct_article')
        if not content:
            content = soup.select_one('#articleBodyContents')
        if not content:
            content = soup.select_one('.article_view')
            
        # Yahoo Finance compatibility
        if not content:
            content = soup.select_one('.caas-body')
        if not content:
            content = soup.select_one('article')
            
        if content:
            # Remove scripts and styles
            for script_or_style in content(['script', 'style', 'span', 'a']):
                script_or_style.decompose()
            return content.get_text(strip=True, separator='\n')[:2000] # Limit to 2000 chars
    except Exception as e:
        print(f"Error scraping article content: {e}")
    return ""

def is_relevant_article(title, stock_name):
    """
    Check if the article title is likely relevant to the stock.
    """
    import re
    
    # 1. Broad Market Downranking
    market_terms = ["코스피", "코스닥", "지수", "시황", "마감", "뉴욕증시", "블루칩", "글로벌 증시", "아시아 증시"]
    market_count = sum(1 for term in market_terms if term in title)
    
    # 2. Strict Subject Check (Primary focus on this stock)
    subject_patterns = [
        rf"\[.*{re.escape(stock_name)}.*\]", # [삼성전자]
        rf"{re.escape(stock_name)}\s*[:]",      # 삼성전자 :
        rf"^{re.escape(stock_name)}"          # 삼성전자 (start of title)
    ]
    is_main_subject = any(re.search(p, title) for p in subject_patterns)

    # 3. Decision Logic
    # Reject if it's a broad market wrap-up and the stock isn't the headline subject
    if market_count >= 2 and not is_main_subject:
        return False

    # Standard check: must contain the stock name
    return stock_name in title

def scrape_naver_news(symbol, name, target_date_str, max_articles=20):
    """
    Scrape news for a given stock. Performs a 2-day lookback if target date news is not found.
    """
    print(f"Scraping news for {name} ({symbol})...")
    
    # Try current date, then day-1, then day-2
    target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d")
    lookback_days = [target_date, target_date - timedelta(days=1), target_date - timedelta(days=2)]
    
    articles = []
    seen_titles = set()
    seen_hours = set()
    
    for current_date in lookback_days:
        date_clean = current_date.strftime("%Y.%m.%d")
        
        # hour -> list of articles in that hour
        hour_buckets = {}
        # articles without hour info (rare on Naver but possible)
        no_hour_articles = []
        
        found_older_date = False
        for page in range(1, 16):
            url = f"https://finance.naver.com/item/news_news.naver?code={symbol}&page={page}&sm=title_entity_id.basic&clusterId="
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': f'https://finance.naver.com/item/news.naver?code={symbol}'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                response.encoding = 'euc-kr'
                
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.select('table.type5 tbody tr')
                if not rows: break
                
                for row in rows:
                    tds = row.select('td')
                    if len(tds) < 2: continue
                    
                    title_td = row.select_one('td.title')
                    a_tag = title_td.select_one('a') if title_td else row.select_one('a')
                    if not a_tag: continue
                        
                    title = a_tag.get_text(strip=True)
                    href = a_tag.get('href', '')
                    if not title or title in seen_titles: continue
                    
                    date_td = row.select_one('td.date')
                    article_date_full = date_td.get_text(strip=True) if date_td else ""
                    date_parts = article_date_full.split(" ")
                    article_date_only = date_parts[0]
                    article_hour = date_parts[1].split(":")[0] if len(date_parts) > 1 else ""
                    
                    if article_date_only == date_clean:
                        full_url = f"https://finance.naver.com{href}" if href.startswith('/') else href
                        info_td = row.select_one('td.info')
                        source = info_td.get_text(strip=True) if info_td else ""
                        
                        import re
                        has_name = False
                        if len(name) <= 2:
                            # Strict match for short names (e.g. SK, LG)
                            # Match if name is followed by space, punctuation, or start/end of string
                            # Avoid matching subsidiaries like "SK온", "SK하이닉스"
                            pattern = rf"(?:^|[^가-힣a-zA-Z0-9]){re.escape(name)}(?:$|[^가-힣a-zA-Z0-9])"
                            if re.search(pattern, title):
                                has_name = True
                        else:
                            has_name = name in title

                        article_data = {
                            "title": title, 
                            "url": full_url, 
                            "date": article_date_full, 
                            "source": source,
                            "has_name": has_name
                        }
                        
                        if article_hour:
                            if article_hour not in hour_buckets:
                                hour_buckets[article_hour] = []
                            hour_buckets[article_hour].append(article_data)
                        else:
                            no_hour_articles.append(article_data)
                        
                        seen_titles.add(title)
                    elif article_date_only < date_clean and "." in article_date_only:
                        found_older_date = True
                        break
                
                if found_older_date: break
                        
            except Exception as e:
                print(f"Error scraping Naver news page {page}: {e}")
                break
        
        # Process collected articles for the current_date
        deduplicated = []
        for hour in sorted(hour_buckets.keys(), reverse=True):
            bucket = hour_buckets[hour]
            # Preference in this hour: 1. Contains name, 2. Most recent
            matches = [a for a in bucket if a['has_name']]
            if matches:
                deduplicated.append(matches[0]) # Most recent name match
            else:
                deduplicated.append(bucket[0]) # Most recent overall
        
        # Add no-hour articles (briefly deduplicated by title already)
        deduplicated.extend(no_hour_articles)
        
        if deduplicated:
            # Final selection: prioritize company name matches globally for the date
            with_name = [a for a in deduplicated if a['has_name']]
            without_name = [a for a in deduplicated if not a['has_name']]
            
            # Already sorted by recent within buckets, but let's be sure
            with_name.sort(key=lambda x: x['date'], reverse=True)
            without_name.sort(key=lambda x: x['date'], reverse=True)
            
            articles = (with_name + without_name)[:max_articles]
            break

    if not articles:
        # Generic professional fallback
        articles = [{"title": f"{name}, 시장 흐름 및 관련 테마 분석", "url": f"https://finance.naver.com/item/news.naver?code={symbol}", "date": target_date_str.replace("-", ".") + " 09:00", "source": "증권정보"}]
    
    return articles

def scrape_us_news(symbol, name, target_date_str, max_articles=5):
    """
    Scrape English news headlines and links from Yahoo Finance RSS.
    """
    print(f"Scraping US news for {name} ({symbol})...")
    import xml.etree.ElementTree as ET
    
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    articles = []
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        
        root = ET.fromstring(res.text)
        for item in root.findall('./channel/item')[:max_articles]:
            title_el = item.find('title')
            link_el = item.find('link')
            pub_date_el = item.find('pubDate')
            
            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else ""
            pub_date = pub_date_el.text if pub_date_el is not None else ""
            
            # Format pub_date to KST (e.g. 02.24 10:30)
            if pub_date:
                try:
                    import email.utils
                    from datetime import timezone
                    dt = email.utils.parsedate_to_datetime(pub_date)
                    dt_kst = dt.astimezone(timezone(timedelta(hours=9)))
                    pub_date = dt_kst.strftime("%m.%d %H:%M")
                except Exception as e:
                    pass
            
            if title and link:
                articles.append({
                    "title": title,
                    "url": link,
                    "date": pub_date,
                    "source": "Yahoo Finance",
                    "has_name": True # Assume RSS feeds are highly targeted
                })
    except Exception as e:
        print(f"Error scraping US news for {symbol}: {e}")
        
    if not articles:
        articles = [{"title": f"{name} Market Analysis", "url": f"https://finance.yahoo.com/quote/{symbol}", "date": target_date_str, "source": "Yahoo Finance", "has_name": True}]
        
    return articles

def translate_us_article(title, content):
    """Translate US article title and content to Korean."""
    prompt = f"다음 영문 기사의 제목과 본문을 한국어로 자연스럽게 번역해주세요.\n\n[제목]\n{title}\n\n[본문]\n{content}\n\n[번역] (제목과 본문을 줄바꿈으로 구분해서 작성):"
    
    response = call_gemini_with_fallback(prompt, config_kwargs={"temperature": 0.1})
    if response and response.text:
        return response.text.strip()
    return f"제목: {title}\n본문: 내용 요약 불가"

def scrape_market_news(market="KR"):
    """
    Scrape 1-2 latest broad market wrap-up news articles to provide macro context.
    """
    try:
        if market == "US":
            url = "https://search.naver.com/search.naver?where=news&query=뉴욕증시+마감&sm=tab_opt&sort=1&photo=0&field=0&pd=4"
        else:
            url = "https://search.naver.com/search.naver?where=news&query=코스피+마감&sm=tab_opt&sort=1&photo=0&field=0&pd=4"
            
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        articles = soup.select('div.news_area > a.news_tit')
        market_context_text = ""
        for i, a in enumerate(articles[:2]): # Max 2 articles
            title = a.get_text(strip=True)
            href = a.get('href', '')
            content = scrape_article_content(href)[:800] # Limit content size
            market_context_text += f"[시장 시황 {i+1}] {title}\n{content}\n\n"
        
        return market_context_text
    except Exception as e:
        print(f"Error fetching market news: {e}")
        return ""

def select_impactful_article(stock_name, articles, change_val):
    """
    Use Gemini to select the index of the most impactful article from the list.
    Strictly prioritizes company-specific events over broad market news.
    """
    direction = "상승" if change_val >= 0 else "하락"
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_api_key_here" and GENAI_AVAILABLE:
        try:
            prompt = (
                f"{stock_name}의 주가가 오늘 {direction}했습니다. 다음 뉴스 헤드라인 중 "
                f"이 변동에 가장 큰 원인이 되었을 것으로 판단되는 기사의 번호(0부터 시작)만 하나 골라주세요.\n"
                f"**핵심 지침:**\n"
                f"1. **회사 특정적 뉴스 우선**: '실적', '수주', '인수/합병', '신제품', '신고가 경신' 등 {stock_name} 회사 자체의 소식을 최우선으로 선택하세요.\n"
                f"2. **시장/지수 전체 뉴스 배제**: '코스피 상승', '시황 마감', '지수 5000 돌파' 등 시장 전체 흐름을 다루는 뉴스는 {stock_name} 전용 뉴스가 있다면 무조건 제외하세요.\n"
                f"3. 만약 회사와 관련된 뉴스가 하나도 없다면 'none'이라고 답해주세요.\n\n"
                + "\n".join([f"{i}: {a['title']}" for i, a in enumerate(articles)]) +
                "\n\n응답은 반드시 숫자 하나 또는 'none'만 해주세요."
            )
            
            response = call_gemini_with_fallback(prompt, config_kwargs={"temperature": 0.1})
                
            if response and response.text:
                import re
                if 'none' in response.text.lower():
                    return -1
                match = re.search(r'\d+', response.text)
                if match:
                    idx = int(match.group())
                    if 0 <= idx < len(articles):
                        return idx
        except Exception as e:
            print(f"Error selecting article: {e}")
            
    # Fallback: Rule-based best guess (Keywords)
    # Downrank market keywords, Uprank company keywords
    company_keywords = ["신고가", "최다주주", "실적", "수주", "영업이익", "흑자", "배당", "인수", "합병", "공시", "특징주"]
    market_keywords = ["코스피", "지수", "시황", "마감", "뉴욕증시"]
    
    scored_articles = []
    for i, article in enumerate(articles):
        if not isinstance(article, dict):
            print(f"Warning: Article at index {i} is not a dictionary: {type(article)} - {article}")
            continue
        score = 0
        title = article.get('title', '')
        if any(kw in title for kw in company_keywords): score += 10
        if any(kw in title for kw in market_keywords): score -= 5
        if title.startswith(stock_name) or f"[{stock_name}]" in title: score += 5
        scored_articles.append((score, i))
    
    scored_articles.sort(reverse=True)
    return scored_articles[0][1] if scored_articles else 0

def generate_summary(stock_name, articles, change_val, best_idx=0, investor_data=None, analyst_data=None, market="KR", market_context_text=""):
    """
    Generate a 2-3 line summary of why the stock moved, based on news articles.
    Returns a dict containing category, short_reason, summary, and success status.
    """
    direction = "상승" if change_val >= 0 else "하락"
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key and api_key != "your_api_key_here" and GENAI_CLIENT:
        try:
            # Re-order articles to put the "best" one first for Gemini
            reordered = list(articles)
            if 0 <= best_idx < len(articles):
                best = reordered.pop(best_idx)
                reordered.insert(0, best)

            articles_text = ""
            # Use top 3-5 articles with 1500 chars context each
            for i, article in enumerate(reordered[:5]):
                title = article.get("title", "")
                content = article.get("content", "")
                # Format differently based on market (US is pre-translated)
                context_label = "원문 번역" if market == "US" else "내용"
                articles_text += f"기사 {i+1}: {title}\n{context_label}: {content[:1500]}\n\n"
                
            if market == "KR" and investor_data:
                articles_text += f"**오늘 수급 데이터 (개인/외국인/기관):** {investor_data.get('개인','-')} / {investor_data.get('외국인','-')} / {investor_data.get('기관','-')}\n\n"
            elif market == "US" and analyst_data:
                articles_text += f"**애널리스트 투자의견 요약:** {analyst_data}\n\n"
                
            market_context_prompt = f"**오늘의 핵심 시황 (참고용):**\n{market_context_text}\n" if market_context_text else ""

            prompt = (
                f"당신은 금융 시장을 분석하는 최상급 AI 리포터입니다. {stock_name} ({direction})에 관한 최신 개별 종목 기사들과 오늘의 전체 시황 뉴스를 읽고 분석 리포트를 작성하세요.\n"
                f"**분석용 뉴스 데이터**\n"
                f"{articles_text}"
                f"{market_context_prompt}"
                f"**작성 가이드라인 (반드시 준수):**\n"
                f"1. **한국어 요약 (summary)**: 주요 내용을 종합하여 2~3문장으로 요약하세요. 시장 전체 흐름(시황)의 영향이 컸다면 이를 함께 엮어서 설명하고, 단순 사실 나열이 아닌 한국 독자가 이해하기 편한 리포트 어조를 사용하세요.\n"
                f"2. **키워드 압축 (short_reason)**: 위 '요약(summary)'의 핵심을 **2~3개의 명사구/단어**로만 압축하세요. (예: '매출 성장세 지속, 전체 시장 하락세 동조'). 문장이나 마침표를 사용하지 마세요.\n"
                f"3. **카테고리 분류 (category)**: '실적', '수급', '이슈', '거시경제', '빅테크' 중 하나를 선택하세요.\n"
                f"4. **금지 사항**: '{stock_name}은(는) ~로 인해 주가가 상승했습니다' 처럼 주가가 올랐다는 단순 서술어는 피하세요.\n"
                f"5. **출력 형식**: 아래 JSON 구조로만 응답하세요. 다른 설명이나 텍스트를 절대 포함하지 마세요.\n"
                f"{{\"category\": \"카테고리\", \"short_reason\": \"핵심 키워드\", \"summary\": \"규칙을 준수한 자연스러운 요약 리포트\"}}"
            )
            
            response = call_gemini_with_fallback(
                prompt,
                config_kwargs={"temperature": 0.2, "response_mime_type": 'application/json'}
            )
                
            if response and response.text:
                try:
                    import re
                    clean_json = re.sub(r'```(?:json)?', '', response.text).strip()
                    parsed = json.loads(clean_json)
                    parsed["summary_success"] = True
                    return parsed
                except Exception as e:
                    print(f"Failed to parse Gemini JSON: {e}")
        except Exception as e:
            print(f"Gemini API failure: {e}")
    
    # Fallback logic
    news_titles = [a["title"] for a in articles if "title" in a]
    main_news = news_titles[best_idx] if (news_titles and 0 <= best_idx < len(news_titles)) else "시장 수급 변화"
    
    if market == "US":
        main_news = "외신 보도 및 주요 지표 변화"
        
    return {
        "category": "이슈", 
        "short_reason": "수급 변화, 업황 변동", 
        "summary": f"{stock_name}은(는) {main_news} 등의 영향으로 {direction} 마감했습니다.",
        "summary_success": False
    }

def generate_short_reason(stock_name, articles, change_val, best_idx=0, translated_title=None):
    if translated_title:
        words = [w for w in translated_title.split() if len(w) > 1]
        return f"{words[0]}, {words[1]}" if len(words) >= 2 else "업황 변동, 수급 변화"
    
    return "업황 변동, 수급 변화"

def get_related_stocks(symbol, name, date_str, theme=None, market="KR"):
    """
    Tiered approach to find related stocks:
    1. Strategic/Industry Peers (Predefined mapping)
    2. Parent/Group Affiliate (name prefix)
    3. Theme-based Fallback (Stocks in the same sector)
    """
    related_candidates = []
    seen_symbols = {symbol}
    
    # Select the correct stock list based on market
    stocks_list = US_MAJOR_STOCKS if market == "US" else MAJOR_STOCKS
    
    # --- Tier 1: Strategic Peer Mapping from JSON Config ---
    market_data = STOCK_METADATA.get(market, {})
    peer_list = market_data.get(symbol, {}).get("peers", [])
    
    for p_code in peer_list:
        if p_code not in seen_symbols:
            # Find the stock info from the correct predefined list
            peer_info = next((s for s in stocks_list if s['symbol'] == p_code), None)
            if peer_info:
                related_candidates.append(peer_info)
                seen_symbols.add(p_code)
                    
    # --- Tier 2: Conglomerate Group (Prefix Match) (KR Market Only really) ---
    if market == "KR":
        prefix = name[:2]
        if len(prefix) >= 2:
            for s in stocks_list:
                if s['symbol'] not in seen_symbols and s['name'].startswith(prefix):
                    related_candidates.append(s)
                    seen_symbols.add(s['symbol'])
    
    # --- Tier 3: Sector-based Fallback (If still empty or fewer than 3) ---
    # Use industry information from metadata if available
    if not related_candidates:
        stock_info = market_data.get(symbol, {})
        industries = stock_info.get("industry", [])
        if industries:
            main_industry = industries[0]
            # Simple fallback: Find other stocks in the same main industry
            for s_code, s_info in market_data.items():
                if s_code != symbol and main_industry in s_info.get("industry", []):
                    related_candidates.append({"symbol": s_code, "name": s_info.get("name", s_code)})
                    if len(related_candidates) >= 5:
                        break
                        
    final_related = []
    
    # 4. Attach prefix labels to the related stock names
    # Rules: 
    # - If same primary industry -> [Industry Name]
    # - If name starts with same 2 chars (KR) -> [그룹사]
    # - Otherwise -> [경쟁사]
    main_industry_list = STOCK_METADATA.get(market, {}).get(symbol, {}).get("industry", [])
    main_industry = main_industry_list[0] if main_industry_list else None

    for rc in related_candidates[:5]:
        r_symbol = rc['symbol']
        r_name = rc['name']
        
        # Determine prefix
        prefix_tag = "[관련주]"
        
        # Check stock_metadata.json for peer industry
        peer_meta = STOCK_METADATA.get(market, {}).get(r_symbol, {})
        peer_industry_list = peer_meta.get("industry", [])
        peer_industry = peer_industry_list[0] if peer_industry_list else None

        if main_industry and peer_industry == main_industry:
            prefix_tag = f"[{main_industry}]"
        elif market == "KR" and len(name) >= 2 and r_name.startswith(name[:2]):
            prefix_tag = "[그룹사]"
        elif peer_industry:
            prefix_tag = f"[{peer_industry}]"
        else:
            prefix_tag = "[경쟁사]"

        final_related.append({
            "name": f"{prefix_tag} {r_name}",
            "change_rate": f"{get_stock_change(r_symbol, date_str):+.1f}%"
        })
    return final_related

def get_last_trading_day(target_date_str=None, market="KR"):
    """
    Find the most recent trading day.
    """
    kst_now = datetime.datetime.utcnow() + timedelta(hours=9)
    
    if target_date_str is None:
        base_date = kst_now
        if market == "US" and kst_now.hour < 9:
            base_date = kst_now - timedelta(days=1)
    else:
        base_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d")

    # Initialize holiday checker
    kr_holidays = holidays.KR() if HOLIDAYS_AVAILABLE else {}
    us_holidays = holidays.US() if HOLIDAYS_AVAILABLE else {}

    def is_holiday(d, m):
        # Weekends
        if d.weekday() > 4: return True
        
        d_str = d.strftime("%Y-%m-%d")
        
        if m == "KR":
            # KR Market specific: 12/31 is always a holiday
            if d.month == 12 and d.day == 31: return True
            if HOLIDAYS_AVAILABLE and d_str in kr_holidays: return True
        else:
            if HOLIDAYS_AVAILABLE and d_str in us_holidays: return True
            
        return False

    # Look back until we find a trading day
    check_date = base_date
    # If we are checking "today" and it's a holiday, we definitely want the previous one.
    # If we are checking a specific date and it's a holiday, we want the previous one.
    while is_holiday(check_date, market):
        check_date -= timedelta(days=1)
        
    return check_date.strftime("%Y-%m-%d")

def generate_daily_json(date_str=None, market="KR"):
    if date_str is None: 
        date_str = get_last_trading_day(market=market)
    print(f"Generating data for {date_str} ({market} market)...")
    
    kst_now = datetime.datetime.utcnow() + timedelta(hours=9)
    
    prefix = "us_" if market == "US" else ""
    output_file = os.path.join(DATA_DIR, f"{prefix}{date_str}.json")
    
    # 0. Check if the requested date is a valid trading day
    last_trading = get_last_trading_day(date_str, market=market)
    if date_str != last_trading:
        print(f"!!! Error: {date_str} is NOT a trading day for {market} market.")
        print(f"!!! Last available trading day: {last_trading}")
        print("!!! Skipping JSON generation to avoid duplicate/misleading data.")
        return

    # Load existing articles to accumulate them throughout the day
    existing_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"Error loading existing JSON: {e}")
            
    existing_signals = {s['main_stock']['symbol']: s for s in existing_data.get('signals', [])}
    
    existing_signals = {s['main_stock']['symbol']: s for s in existing_data.get('signals', [])}
    
    # 0.5. Get Market Indices (Insert at top)
    signals = []
    
    def fetch_kr_indices():
         try:
             url = "https://finance.naver.com/sise/"
             res = requests.get(url, timeout=10)
             soup = BeautifulSoup(res.text, 'html.parser')
             
             kospi_val = soup.select_one('#KOSPI_now').text
             kospi_change = soup.select_one('#KOSPI_change').text
             
             kosdaq_val = soup.select_one('#KOSDAQ_now').text
             kosdaq_change = soup.select_one('#KOSDAQ_change').text
             
             return [
                 {"name": "KOSPI", "symbol": "KOSPI", "val": kospi_val, "change_rate": kospi_change},
                 {"name": "KOSDAQ", "symbol": "KOSDAQ", "val": kosdaq_val, "change_rate": kosdaq_change}
             ]
         except Exception as e:
             print(f"Error fetching KR Indices: {e}")
             return []

    def fetch_us_indices():
         try:
             import yfinance as yf
             sp_ticker = yf.Ticker('^GSPC')
             sp_data = sp_ticker.history(period="2d")
             sp_change = ((sp_data['Close'].iloc[-1] - sp_data['Close'].iloc[-2]) / sp_data['Close'].iloc[-2]) * 100
             
             ndq_ticker = yf.Ticker('^IXIC')
             ndq_data = ndq_ticker.history(period="2d")
             ndq_change = ((ndq_data['Close'].iloc[-1] - ndq_data['Close'].iloc[-2]) / ndq_data['Close'].iloc[-2]) * 100
             
             return [
                 {"name": "S&P 500", "symbol": "SP500", "val": f"{sp_data['Close'].iloc[-1]:.2f}", "change_rate": f"{sp_change:+.2f}%"},
                 {"name": "NASDAQ", "symbol": "NASDAQ", "val": f"{ndq_data['Close'].iloc[-1]:.2f}", "change_rate": f"{ndq_change:+.2f}%"}
             ]
         except Exception as e:
             print(f"Error fetching US Indices: {e}")
             return []

    indices = fetch_us_indices() if market == "US" else fetch_kr_indices()
    for idx_data in indices:
        i_name = idx_data['name']
        i_symbol = idx_data['symbol']
        i_val = idx_data['val']
        i_change_rate = idx_data['change_rate']
        
        # Crawl news for the index specifically
        if market == "US":
            i_articles = scrape_us_news(i_symbol, i_name, date_str)
        else:
            i_articles = scrape_naver_news(i_symbol, i_name, date_str)
        
        # Enrich content for index articles
        for k in range(min(3, len(i_articles))):
             c_content = scrape_article_content(i_articles[k]['url'])[:1500]
             i_articles[k]['content'] = c_content

        print(f"Generating AI summary for Index: {i_name}...")
        i_ai_res = generate_summary(
            i_name, i_articles, 0.0, # Change value not strictly needed for index summary but passed 0.0
            market=market
        )

        signals.append({
            "id": f"sig_{date_str.replace('-','')}_{market}_IDX_{i_symbol}",
            "theme": "#시장지수",
            "signal_type": "시황",
            "short_reason": i_ai_res.get("short_reason", "시장 전체 흐름"),
            "summary": i_ai_res.get("summary", f"[{i_name}] 마감 지수: {i_val} ({i_change_rate})"),
            "summary_success": i_ai_res.get("summary_success", False),
            "is_index": True,
            "main_stock": {
                "name": i_name,
                "symbol": i_symbol,
                "change_rate": i_change_rate,
                "news_url": ""
            },
            "news_articles": i_articles[:5],
            "related_stocks": [],
            "timestamp": kst_now.strftime("%Y-%m-%d %H:%M:%S")
        })

    # 0.6. Get Market Context News
    print(f"Fetching market news context for {market}...")
    market_context_text = scrape_market_news(market)

    # 1. Get real movers
    movers = get_top_movers(date_str, market=market)
    
    for idx, stock in enumerate(movers):
        symbol = stock['symbol']
        name = stock['name']
        change_val = stock['change']
        
        print(f"[{idx+1}/{len(movers)}] Processing {name} ({symbol})...")
        
        # 2. News Headlines
        if market == "US":
            new_articles = scrape_us_news(symbol, name, date_str)
        else:
            new_articles = scrape_naver_news(symbol, name, date_str)
            
        # Merge new articles with existing ones (avoiding duplicates)
        articles = []
        seen_urls = set()
        for a in new_articles:
            if a['url'] not in seen_urls:
                articles.append(a)
                seen_urls.add(a['url'])
                
        if symbol in existing_signals:
            for a in existing_signals[symbol].get('news_articles', []):
                if isinstance(a, dict) and a.get('url') and a['url'] not in seen_urls:
                    articles.append(a)
                    seen_urls.add(a['url'])
        
        # Filter invalid articles (must be dict with url and title)
        articles = [a for a in articles if isinstance(a, dict) and 'url' in a and 'title' in a]
        
        # 3. [Tier 1 Smart Skip] Check previous success, same direction, and change_rate delta
        ai_result = None
        if symbol in existing_signals:
            old_signal = existing_signals[symbol]
            old_success = old_signal.get("summary_success", False)
            
            if old_success:
                try:
                    old_change_rate_str = old_signal.get("main_stock", {}).get("change_rate", "0%")
                    old_change_val = float(old_change_rate_str.replace('%', '').replace('+', ''))
                    
                    # Ensure both are moving in the same direction (both positive or both negative)
                    same_direction = (old_change_val * change_val) > 0 or (old_change_val == 0 and change_val == 0)
                    
                    # If same direction AND absolute difference in change rate is <= 3.0 percentage points, skip AI.
                    if same_direction and abs(old_change_val - change_val) <= 3.0:
                        print(f"[{idx+1}/{len(movers)}] [Tier 1 Skip] Valid prior summary exists, same direction, and change gap (abs({abs(old_change_val - change_val):.2f}%)) <= 3.0%. Skipping AI.")
                        ai_result = {
                            "category": old_signal.get("signal_type", "이슈"),
                            "short_reason": old_signal.get("short_reason", "수급 변화"),
                            "summary": old_signal.get("summary", ""),
                            "summary_success": True
                        }
                except Exception as e:
                    print(f"Error parsing old change_rate for {symbol}: {e}")
        
        # 4. If not skipped, select impactful info and scrape multiple contents
        if not ai_result and articles:
            best_idx = select_impactful_article(name, articles, change_val)
            if best_idx == -1: best_idx = 0
            
            if 0 <= best_idx < len(articles):
                # Enrich up to 5 articles with content for better context
                for i in range(min(5, len(articles))):
                    content = scrape_article_content(articles[i]['url'])[:1500]
                    # Specific to US: translate content directly
                    if market == "US" and content:
                        trans = translate_us_article(articles[i]['title'], content)
                        articles[i]['content'] = trans
                    else:
                        articles[i]['content'] = content

                investor_data = None
                if market == "KR":
                    try:
                        investor_data = get_investor_data(symbol, date_str)
                    except Exception as e:
                        print(f"Error fetching investor data: {e}")

                print(f"[{idx+1}/{len(movers)}] Generating new AI summary for {name}...")
                ai_result = generate_summary(
                    name, articles, change_val, 
                    best_idx=best_idx, 
                    investor_data=investor_data, 
                    market=market,
                    market_context_text=market_context_text
                )
        elif not ai_result:
            # No articles found case
            ai_result = {
                "category": "이슈", 
                "short_reason": "수급 변화", 
                "summary": f"{name}은(는) 시장 수급 변화 등의 영향으로 변동을 보였습니다.",
                "summary_success": False
            }

        # 8. Assemble Signal
        market_data = STOCK_METADATA.get(market, {})
        stock_info = market_data.get(symbol, {})
        industry_list = stock_info.get("industry", [])
        theme = f"#{industry_list[0]}" if industry_list else ""
        
        related = get_related_stocks(symbol, name, date_str, theme=theme, market=market)
        news_url = f"https://finance.yahoo.com/quote/{symbol}" if market == "US" else f"https://finance.naver.com/item/news.naver?code={symbol}"
        
        signal_data = {
            "id": f"sig_{date_str.replace('-','')}_{market}_{idx+1:03d}",
            "theme": theme,
            "signal_type": ai_result.get("category", "이슈"),
            "short_reason": ai_result.get("short_reason", "수급 변화"),
            "summary": ai_result.get("summary", ""),
            "summary_success": ai_result.get("summary_success", False),
            "main_stock": {
                "name": name, "symbol": symbol, "change_rate": stock['change_rate'],
                "news_url": news_url
            },
            "news_articles": articles[:5],
            "related_stocks": related,
            "timestamp": kst_now.strftime("%Y-%m-%d %H:%M:%S")
        }
        signals.append(signal_data)
        
        # Incremental save
        try:
            output_data = {"last_updated": kst_now.strftime("%Y-%m-%d %H:%M:%S"), "signals": signals}
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error during incremental save: {e}")

    # 6. Final success: Save the latest trading date for the frontend
    try:
        latest_date_path = os.path.join(DATA_DIR, "latest_date.json")
        prefix = "us_" if market == "US" else "kr_"
        # We also keep a generic one for the main entry
        with open(latest_date_path, "w", encoding="utf-8") as f:
            json.dump({
                "date": date_str, 
                "market": market, 
                "updated_at": kst_now.strftime("%Y-%m-%d %H:%M:%S")
            }, f, ensure_ascii=False)
        
        # Also save a market-specific one
        with open(os.path.join(DATA_DIR, f"latest_{prefix}date.json"), "w", encoding="utf-8") as f:
            json.dump({"date": date_str}, f, ensure_ascii=False)
            
        print(f"Successfully updated latest_date.json with {date_str}")
    except Exception as e:
        print(f"Error updating latest_date.json: {e}")

    print(f"Successfully generated/updated {output_file}")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Toss Signal Crawler")
    parser.add_argument("--date", type=str, default=None, help="Target date YYYY-MM-DD")
    parser.add_argument("--market", type=str, choices=["KR", "US"], default="KR", help="Market to crawl (KR or US)")
    args = parser.parse_args()
    
    target_day = args.date if args.date else get_last_trading_day()
    generate_daily_json(target_day, market=args.market)
