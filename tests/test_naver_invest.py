import requests
from bs4 import BeautifulSoup

def parse_invest(symbol):
    url = f"https://finance.naver.com/item/invest.naver?code={symbol}" # This URL might not exist
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    print(res.status_code)
    
parse_invest("005930")
