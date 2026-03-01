import requests
from bs4 import BeautifulSoup

def explore_tables(symbol):
    url = f"https://finance.naver.com/item/frgn.naver?code={symbol}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    tables = soup.find_all('table')
    for i, t in enumerate(tables):
        caption = t.find('caption')
        cap_text = caption.text.strip() if caption else "No Caption"
        print(f"Table {i}: {cap_text}")
        if '외국인 기관 순매매 거래량' in cap_text or '순매매 거래량' in cap_text or '잠정' in cap_text:
            print("Found target table!")
            rows = t.find_all('tr')
            for r in rows[:5]:
                print([td.text.strip() for td in r.find_all(['td', 'th'])])

explore_tables("005930")
