
import requests
from bs4 import BeautifulSoup
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from crawler import scrape_naver_sise_news, scrape_yahoo_quote_news

def test_refinement():
    print("=== Testing Naver Sise News (KOSPI) ===")
    kr_news = scrape_naver_sise_news("KOSPI")
    for i, a in enumerate(kr_news, 1):
        print(f"{i}: {a['title']} ({a['source']}) - {a['url']}")
    
    print("\n=== Testing Yahoo Quote News (^GSPC) ===")
    us_news = scrape_yahoo_quote_news("^GSPC")
    for i, a in enumerate(us_news, 1):
        print(f"{i}: {a['title']} ({a['source']}) - {a['url']}")

    print("\n=== Testing Yahoo Quote News (NVDA) ===")
    stock_news = scrape_yahoo_quote_news("NVDA")
    for i, a in enumerate(stock_news, 1):
        print(f"{i}: {a['title']} ({a['source']}) - {a['url']}")

if __name__ == "__main__":
    test_refinement()
