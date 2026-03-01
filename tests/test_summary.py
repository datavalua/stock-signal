import crawler
import json

symbol = "011200" # HMM
name = "HMM"
date_str = "2026-02-23" # Past date to test pykrx properly

print("Fetching investor data...")
investor_data = crawler.get_investor_data(symbol, date_str)
print("Investor Data:", investor_data)

print("Scraping news...")
articles = crawler.scrape_naver_news(symbol, name, date_str)
if articles:
    best_idx = crawler.select_impactful_article(name, articles, 5.0)
    target = articles[best_idx]
    target['content'] = crawler.scrape_article_content(target['url'])
else:
    best_idx = 0

print("Generating summary...")
summary = crawler.generate_summary(name, articles, 5.0, best_idx, investor_data)

print("\n--- Final Summary ---")
print(summary)
