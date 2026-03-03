import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

with open("tmp/models_output.txt", "w", encoding="utf-8") as f:
    f.write("Listing available models:\n")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"- {m.name} ({m.display_name})\n")
    except Exception as e:
        f.write(f"Error: {e}\n")

print("Done. Output written to tmp/models_output.txt")
