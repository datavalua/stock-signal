import pykrx.stock as stock

tiger = "005930"
date = "20260220" # Last friday

try:
    df = stock.get_market_trading_volume_by_date(date, date, tiger, detail=True)
    print("get_market_trading_volume_by_date:")
    print(df)
    
except Exception as e:
    print(e)
    
try:
    df2 = stock.get_market_net_purchases_of_equities_by_ticker(date, date, "KOSPI", "개인")
    print("get_market_net_purchases_of_equities_by_ticker (개인):")
    if tiger in df2.index:
        print(df2.loc[tiger])
except Exception as e:
    print(e)
