from pykrx import stock
import datetime
import pandas as pd

today = datetime.datetime.today().strftime("%Y%m%d")
print(f"Testing pykrx for {today}")

try:
    kospi = stock.get_market_ticker_list(today, market="KOSPI")
    print(f"KOSPI tickers: {len(kospi)}")
    if len(kospi) > 0:
        print("Sample:", kospi[:3])
        print("Names:", [stock.get_market_ticker_name(t) for t in kospi[:3]])
except Exception as e:
    print("KOSPI Failed:", str(e))

try:
    kosdaq = stock.get_market_ticker_list(today, market="KOSDAQ")
    print(f"KOSDAQ tickers: {len(kosdaq)}")
except Exception as e:
    print("KOSDAQ Failed:", str(e))
