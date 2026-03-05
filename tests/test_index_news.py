import requests
from bs4 import BeautifulSoup
import re

def test_naver_index_news():
    url = "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=401"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    print(f"--- Naver Index News ({url}) ---")
    items = soup.select('ul.newsList li')
    print(f"Found {len(items)} items in ul.newsList li")
    
    for i, item in enumerate(items[:5]):
        a_tag = item.select_one('dt a') or item.select_one('dd a')
        if a_tag:
            title = a_tag.text.strip()
            print(f"{i}: {title}")
        else:
            print(f"{i}: No a_tag found")

def test_yahoo_index_news(symbol):
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    print(f"--- Yahoo Index News ({symbol}) ---")
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        print(f"Content Length: {len(res.text)}")
        if "<item>" in res.text:
            print("Found <item> in RSS")
            titles = re.findall(r'<title>(.*?)</title>', res.text)
            for i, t in enumerate(titles[:5]):
                print(f"{i}: {t}")
        else:
            print("No <item> found in RSS")

if __name__ == "__main__":
    test_naver_index_news()
    test_yahoo_index_news("SP500")
    test_yahoo_index_news("^GSPC")
    test_yahoo_index_news("NASDAQ")
    test_yahoo_index_news("^IXIC")
