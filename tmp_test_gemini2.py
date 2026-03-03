import os
import json
import dotenv
dotenv.load_dotenv()

import traceback
from backend.crawler import generate_summary, get_model_name
import google.generativeai as genai

print(f"Model: {get_model_name()}")
articles = [{'title': '대우건설, 빅배스 불구 커지는 배당 압박 선택은', 'content': '...', 'has_name': True}]
try:
    res = generate_summary('대우건설', articles, 14.9, 0, None, None, 'KR')
    print("Result:")
    print(res)
except Exception as e:
    print("Exception!")
    traceback.print_exc()
