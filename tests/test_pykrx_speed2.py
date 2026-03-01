import time
from pykrx import stock
import datetime

today = datetime.datetime.today()
bdays = stock.get_business_days_of_month(today.year, today.month)
if not bdays or today.day == 1 and today < bdays[0]:
    last_month = today.replace(day=1) - datetime.timedelta(days=1)
    bdays = stock.get_business_days_of_month(last_month.year, last_month.month)

valid_bdays = [d for d in bdays if d.date() <= today.date()]
if not valid_bdays:
    # Safest fallback
    last_bday = bdays[-1]
else:
    last_bday = valid_bdays[-1]

bday_str = last_bday.strftime("%Y%m%d")
print("Using bday:", bday_str)

start = time.time()
tickers = stock.get_market_ticker_list(bday_str, market="KOSPI")
names = [stock.get_market_ticker_name(t) for t in tickers]
print(f"Fetched {len(tickers)} KOSPI names in {time.time() - start:.2f} seconds")
