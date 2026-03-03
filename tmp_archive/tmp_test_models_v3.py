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
        'gemini-2.0-flash',
        'gemini-2.0-flash-lite-preview-09-2025',
        'gemini-2.0-pro-exp-02-05'
    ]
    
    for m in models_to_test:
        print(f"Testing {m}...")
        try:
            res = client.models.generate_content(model=m, contents="Hello")
            print(f"  SUCCESS: {res.text[:10]}")
        except Exception as e:
            print(f"  FAILED: {e}")
