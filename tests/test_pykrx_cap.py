from pykrx import stock
import datetime

bday = "20260227"
print(f"Testing pykrx for {bday}")

df = stock.get_market_cap(bday, market="KOSPI")
print(df.columns)
print(df.head())
