import requests
import pandas as pd
import time

def get_naver_stock_list(market):
    url = f"https://m.stock.naver.com/api/stocks/marketValue/{market}"
    headers = {"User-Agent": "Mozilla/5.0"}
    all_stocks = []
    page = 1
    while True:
        res = requests.get(url, params={"page": page, "pageSize": 100}, headers=headers)
        if res.status_code != 200:
            break
        try:
            data = res.json()
        except:
            break
        stocks = data.get('stocks', [])
        if not stocks:
            break
        all_stocks.extend(stocks)
        page += 1
        time.sleep(0.1) # Be nice
    df = pd.DataFrame(all_stocks)
    if not df.empty:
        # Standardize matching FDR columns
        df = df.rename(columns={"itemCode": "Symbol", "stockName": "Name"})
    return df

try:
    df_kospi = get_naver_stock_list("KOSPI")
    print("KOSPI count:", len(df_kospi))
    if not df_kospi.empty:
        print(df_kospi[['Symbol', 'Name']].head(2))
        
    df_kosdaq = get_naver_stock_list("KOSDAQ")
    print("KOSDAQ count:", len(df_kosdaq))
except Exception as e:
    print("Error:", e)
