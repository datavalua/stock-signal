import FinanceDataReader as fdr
import pandas as pd
import traceback

print("Testing fdr.StockListing('KRX')...")
try:
    df_krx = fdr.StockListing("KRX")
    print("KRX Success! Shape:", df_krx.shape)
    if not df_krx.empty:
        print("Columns:", df_krx.columns.tolist())
        print("Market values:", df_krx['Market'].unique().tolist() if 'Market' in df_krx.columns else "No Market Column")
except Exception as e:
    print("KRX Failed:", str(e))
    traceback.print_exc()

print("\nTesting fdr.StockListing('KOSPI')...")
try:
    df_kospi = fdr.StockListing("KOSPI")
    print("KOSPI Success! Shape:", df_kospi.shape)
    if not df_kospi.empty:
        print("Columns:", df_kospi.columns.tolist())
except Exception as e:
    print("KOSPI Failed:", str(e))
    traceback.print_exc()

print("\nTesting fdr.StockListing('KOSDAQ')...")
try:
    df_kosdaq = fdr.StockListing("KOSDAQ")
    print("KOSDAQ Success! Shape:", df_kosdaq.shape)
    if not df_kosdaq.empty:
        print("Columns:", df_kosdaq.columns.tolist())
except Exception as e:
    print("KOSDAQ Failed:", str(e))
    traceback.print_exc()
