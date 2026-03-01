import json
import os

DATA_FILE = "data/stock_metadata.json"

industry_names = {
    "005930": "반도체", "000660": "반도체", "042700": "반도체", "007660": "반도체",
    "373220": "이차전지", "051910": "이차전지", "003670": "이차전지", "086520": "이차전지", "247540": "이차전지",
    "032830": "금융", "000810": "금융", "005830": "금융", "001450": "금융", "105560": "금융", "055550": "금융",
    "138040": "금융",
    "036570": "게임", "259960": "게임", "251270": "게임",
    "011170": "화학",
    "005380": "자동차", "000270": "자동차", "012330": "자동차",
    "AAPL": "빅테크", "MSFT": "빅테크", "NVDA": "AI반도체", "GOOGL": "빅테크", "AMZN": "빅테크",
    "TSLA": "전기차", "META": "빅테크", "TSM": "반도체", "AVGO": "반도체", "AMD": "반도체",
    "LLY": "바이오", "UNH": "헬스케어", "JPM": "금융", "V": "결제"
}

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for market in ["KR", "US"]:
        for symbol, info in data.get(market, {}).items():
            if symbol in industry_names:
                if industry_names[symbol] not in info["industry"]:
                    info["industry"].append(industry_names[symbol])
            # Set default if empty
            if not info["industry"]:
                 info["industry"].append("글로벌시황" if market == "US" else "실적/수급")
                 
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Updated industry mappings successfully.")
else:
    print("stock_metadata.json not found.")
