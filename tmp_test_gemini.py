import os
import json
import dotenv
dotenv.load_dotenv()

from backend.crawler import generate_summary

articles = [{'title': '대우건설, 빅배스 불구 커지는 배당 압박 선택은', 'content': '...', 'has_name': True}]
res = generate_summary('대우건설', articles, 14.9, 0, None, None, 'KR')
print(res)
