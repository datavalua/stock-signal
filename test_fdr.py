import FinanceDataReader as fdr
import pandas as pd

indices = ["S&P500", "NASDAQ", "KOSPI", "KOSDAQ"]

for idx in indices:
    try:
        print(f"Fetching {idx}...")
        df = fdr.StockListing(idx)
        print(f"  Success: {len(df)} rows found.")
        print(f"  Columns: {df.columns.tolist()}")
    except Exception as e:
        print(f"  Failed {idx}: {e}")
