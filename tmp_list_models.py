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
        print("Listing available models:")
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
