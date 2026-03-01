import requests
from bs4 import BeautifulSoup

def parse_sise(symbol):
    url = f"https://finance.naver.com/item/sise.naver?code={symbol}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # In sise.naver, search for "투자자별매매동향" or "개인", "외국인", "기관"
    for th in soup.find_all('th'):
        if th.text and '투자자' in th.text:
            print("Found TH:", th.text)
            table = th.find_parent('table')
            if table:
                for row in table.find_all('tr'):
                    print([c.get_text(strip=True) for c in row.find_all(['th', 'td'])])

parse_sise("005930")
