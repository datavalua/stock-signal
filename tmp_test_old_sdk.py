import os
import dotenv
import google.generativeai as genai

dotenv.load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("GEMINI_API_KEY not found!")
else:
    genai.configure(api_key=api_key)
    models_to_test = [
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]
    
    for m in models_to_test:
        print(f"Testing {m} with old SDK...")
        try:
            model = genai.GenerativeModel(m)
            res = model.generate_content("Hello")
            print(f"  SUCCESS: {res.text[:10]}")
        except Exception as e:
            print(f"  FAILED: {e}")
