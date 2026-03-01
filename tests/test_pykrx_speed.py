import time
from pykrx import stock
import datetime

today = datetime.datetime.today()
while today.weekday() >= 5:
    today -= datetime.timedelta(days=1)
bday = today.strftime("%Y%m%d")

start = time.time()
tickers = stock.get_market_ticker_list(bday, market="KOSPI")
names = [stock.get_market_ticker_name(t) for t in tickers]
print(f"Fetched {len(tickers)} KOSPI names in {time.time() - start:.2f} seconds")
