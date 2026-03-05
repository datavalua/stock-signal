
import sys
import os
import json
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mocking some imports if needed or just use real ones since we want to verify real behavior
from crawler import fetch_kr_indices, fetch_us_indices, scrape_naver_sise_news, scrape_yahoo_quote_news

def test_index_logic():
    print("--- KR Market Indices ---")
    kr_indices = fetch_kr_indices()
    for idx in kr_indices:
        symbol = idx['symbol']
        name = idx['name']
        # This is the logic from generate_daily_json
        news_url = f"https://finance.naver.com/sise/sise_index.naver?code={symbol}"
        print(f"Name: {name}, Symbol: {symbol}, URL: {news_url}")
        articles = scrape_naver_sise_news(symbol)
        print(f"Articles found: {len(articles)}")
        if articles:
            print(f"   Sample: {articles[0]['title']} ({articles[0]['url']})")

    print("\n--- US Market Indices ---")
    us_indices = fetch_us_indices()
    for idx in us_indices:
        symbol = idx['symbol']
        name = idx['name']
        # This is the mapping logic from generate_daily_json
        ticker = symbol
        if symbol == "SP500": ticker = "^GSPC"
        if symbol == "NASDAQ": ticker = "^IXIC"
        
        news_url = f"https://finance.yahoo.com/quote/{ticker}/"
        print(f"Name: {name}, Original Symbol: {symbol}, Ticker: {ticker}, URL: {news_url}")
        articles = scrape_yahoo_quote_news(ticker, max_articles=3)
        print(f"Articles found: {len(articles)}")
        if articles:
            print(f"   Sample: {articles[0]['title']} ({articles[0]['url']})")

if __name__ == "__main__":
    test_index_logic()
