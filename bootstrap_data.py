import json
import os
import crawler

# Extracting MAJOR_STOCKS and US_MAJOR_STOCKS
data = {
    "KR": {},
    "US": {}
}

# 1. Populate Names and Market
for stock in crawler.MAJOR_STOCKS:
    data["KR"][stock['symbol']] = {"name": stock['name'], "industry": [], "peers": []}

for stock in crawler.US_MAJOR_STOCKS:
    data["US"][stock['symbol']] = {"name": stock['name'], "industry": [], "peers": []}

# 2. Extract Peer Maps from the function
# We can't easily extract local variables from a function without AST parsing,
# so let's use the known peer maps we can see in the file.
kr_peer_map = {
    "005930": ["000660", "042700", "041510", "009150", "007660"],
    "000660": ["005930", "042700", "041510", "009150", "007660"],
    "042700": ["005930", "000660", "007660"],
    "007660": ["005930", "000660", "042700"],
    "373220": ["051910", "003670", "086520", "247540", "005490"],
    "086520": ["247540", "373220", "003670", "051910"],
    "247540": ["086520", "373220", "003670", "051910"],
    "003670": ["005490", "086520", "247540", "373220"],
    "005380": ["000270", "012330", "005930"],
    "000270": ["005380", "012330", "005930"],
    "012330": ["005380", "000270"],
    "105560": ["055550", "323410", "377300"],
    "055550": ["105560", "323410", "377300"],
    "323410": ["035720", "105560", "055550"],
    "032830": ["000810", "005830", "001450", "138040"],
    "000810": ["032830", "005830", "001450", "138040"],
    "005830": ["000810", "032830", "001450", "138040"],
    "001450": ["000810", "032830", "005830", "138040"],
    "036570": ["259960", "251270", "035420"],
    "259960": ["036570", "251270", "035420"],
    "011170": ["051910", "011780", "005490"],
}

us_peer_map = {
    "AAPL": ["MSFT", "GOOGL", "AMZN", "META"],
    "MSFT": ["AAPL", "GOOGL", "AMZN", "META", "ORCL"],
    "GOOGL": ["MSFT", "AAPL", "META", "AMZN"],
    "AMZN": ["MSFT", "GOOGL", "AAPL", "WMT", "NFLX"],
    "META": ["GOOGL", "AAPL", "SNAP", "PINS"],
    "NFLX": ["DIS", "AAPL", "AMZN", "GOOGL"],
    "DIS": ["NFLX", "AAPL", "AMZN"],
    "ORCL": ["MSFT", "CRM", "CSCO", "INTC"],
    "CRM": ["ORCL", "MSFT", "GOOGL"],
    "CSCO": ["ORCL", "MSFT", "INTC", "AVGO"],
    "NVDA": ["AMD", "TSM", "AVGO", "INTC"],
    "AMD": ["NVDA", "INTC", "TSM"],
    "TSM": ["NVDA", "AMD", "ASML", "INTC"],
    "AVGO": ["NVDA", "QCOM", "TXN", "CSCO"],
    "INTC": ["AMD", "NVDA", "TSM", "CSCO"],
    "TSLA": ["RIVN", "LCID", "F", "GM"],
    "LLY": ["NVO", "JNJ", "PFE", "MRK"],
    "JNJ": ["PFE", "MRK", "LLY"],
    "PFE": ["JNJ", "MRK", "LLY"],
    "MRK": ["JNJ", "PFE", "LLY"],
    "JPM": ["BAC", "WFC", "C", "GS", "MS"],
    "BAC": ["JPM", "WFC", "C"],
    "V": ["MA", "AXP", "PYPL"],
    "MA": ["V", "AXP", "PYPL"],
    "WMT": ["TGT", "COST", "AMZN", "HD"],
    "COST": ["WMT", "TGT", "HD"],
    "HD": ["WMT", "COST"],
    "KO": ["PEP", "MCD"],
    "PEP": ["KO", "MCD"],
    "MCD": ["KO", "PEP"],
    "UNH": ["JNJ", "PFE", "LLY"]
}

# 3. Add Peers to data
for sym, peers in kr_peer_map.items():
    if sym in data["KR"]:
        data["KR"][sym]["peers"] = peers

for sym, peers in us_peer_map.items():
    if sym in data["US"]:
        data["US"][sym]["peers"] = peers

# Save to target directory
os.makedirs("data", exist_ok=True)
with open("data/stock_metadata.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Bootstrap successful.")
