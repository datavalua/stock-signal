import requests
import pandas as pd

def get_naver_stock_list(market):
    url = f"https://m.stock.naver.com/api/stocks/marketValue/{market}"
    params = {
        "page": 1,
        "pageSize": 3000
    }
    res = requests.get(url, params=params)
    data = res.json()
    stocks = data.get('stocks', [])
    df = pd.DataFrame(stocks)
    return df

try:
    df_kospi = get_naver_stock_list("KOSPI")
    print("KOSPI count:", len(df_kospi))
    if not df_kospi.empty:
        print(df_kospi[['itemCode', 'stockName']].head())
        
    df_kosdaq = get_naver_stock_list("KOSDAQ")
    print("KOSDAQ count:", len(df_kosdaq))
except Exception as e:
    print("Error:", e)
