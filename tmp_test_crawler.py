import os
import sys
import dotenv
from google import genai

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
import crawler

dotenv.load_dotenv()

def test():
    print("--- Diagnostic Report ---")
    print(f"Python Version: {sys.version}")
    print(f"Cwd: {os.getcwd()}")
    
    # Check GenAI
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key found: {'Yes' if api_key and api_key != 'your_api_key_here' else 'No'}")
    
    models_to_test = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    for m in models_to_test:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=m,
                contents="Hi"
            )
            print(f"Model {m} SUCCESS")
        except Exception as e:
            print(f"Model {m} FAILED: {e}")

    # Check Scraper for HD현대일렉트릭 (322000)
    print("\nTesting Naver News Scraper for HD현대일렉트릭 (322000)...")
    articles = crawler.scrape_naver_news("322000", "HD현대일렉트릭", "2026-03-02")
    for i, a in enumerate(articles[:3]):
        print(f"{i}: {a['title']} ({a.get('date', 'No Date')})")
        
    if "시장 흐름 및 관련 테마 분석" in articles[0]['title']:
        print("!! Scraper Fallback triggered - real news NOT found.")

if __name__ == "__main__":
    test()
