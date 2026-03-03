import os
import dotenv
from google import genai

dotenv.load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("GEMINI_API_KEY not found!")
else:
    client = genai.Client(api_key=api_key)
    models_to_test = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro-latest',
        'gemini-2.0-flash-exp'
    ]
    
    for m in models_to_test:
        print(f"Testing {m}...")
        try:
            res = client.models.generate_content(model=m, contents="Hello")
            print(f"  SUCCESS: {res.text[:10]}")
        except Exception as e:
            print(f"  FAILED: {e}")
