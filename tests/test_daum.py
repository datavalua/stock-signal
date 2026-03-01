import requests

def get_daum_investor(symbol):
    # Daum Finance API for investor data (intraday)
    url = f"https://finance.daum.net/api/investor/days?symbolCode=A{symbol}&page=1&perPage=10"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': f'https://finance.daum.net/quotes/A{symbol}#influential_investors'
    }
    
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        print("Success fetching Daum API:")
        for item in data.get('data', [])[:2]:
            print(f"Date: {item.get('date')}")
            print(f"Foreign: {item.get('foreignStraightPurchasePrice')}")
            print(f"Institution: {item.get('institutionStraightPurchasePrice')}")
            print(f"Individual: {item.get('individualStraightPurchasePrice')}")
            print("---")
    else:
        print("Failed Daum API:", res.status_code)

get_daum_investor("005930")
