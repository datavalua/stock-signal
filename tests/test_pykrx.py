import pykrx.stock as stock
from datetime import datetime

today = datetime.today().strftime("%Y%m%d")
ticker = "005930" # Samsung Electronics

try:
    # get_market_trading_volume_by_investor returns a DataFrame
    df = stock.get_market_trading_value_by_investor(today, today, ticker)
    if not df.empty:
        # Columns might include '금융투자', '보험', '투신', '사모', '은행', '기타금융', '연기금등', '기관합계', '기타법인', '개인', '외국인', '기타외국인', '전체'
        # Or standard like '개인', '외국인', '기관합계'
        print(df)
        print("Columns:", df.columns.tolist())
    else:
        print("No data for today")
except Exception as e:
    print(f"Error: {e}")
