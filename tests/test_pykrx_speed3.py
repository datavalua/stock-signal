import time
from pykrx import stock
import datetime

bday = datetime.datetime.today()
tickers = []
for _ in range(10):
    bday_str = bday.strftime("%Y%m%d")
    tickers = stock.get_market_ticker_list(bday_str, market="KOSPI")
    if tickers:
        print("Found valid bday:", bday_str)
        break
    bday -= datetime.timedelta(days=1)

start = time.time()
names = [stock.get_market_ticker_name(t) for t in tickers]
print(f"Fetched {len(tickers)} KOSPI names in {time.time() - start:.2f} seconds")
