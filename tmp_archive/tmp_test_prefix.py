import os
import dotenv
from google import genai

dotenv.load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("GEMINI_API_KEY not found!")
else:
    try:
        client = genai.Client(api_key=api_key)
        print("Testing with 'gemini-1.5-flash'...")
        try:
            res = client.models.generate_content(model='gemini-1.5-flash', contents="Hi")
            print(f"Success without prefix: {res.text[:10]}")
        except Exception as e:
            print(f"Failed without prefix: {e}")
            
        print("\nTesting with 'models/gemini-1.5-flash'...")
        try:
            res = client.models.generate_content(model='models/gemini-1.5-flash', contents="Hi")
            print(f"Success with prefix: {res.text[:10]}")
        except Exception as e:
            print(f"Failed with prefix: {e}")
            
    except Exception as e:
        print(f"General error: {e}")
