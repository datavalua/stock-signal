# Add project root to sys.path
import sys
import os
sys.path.append(os.getcwd())

from backend import crawler

def test_holiday(date_str, market):
    last_trading = crawler.get_last_trading_day(date_str, market=market)
    is_holiday = date_str != last_trading
    print(f"[{market}] Date: {date_str} -> Last Trading Day: {last_trading} (Is Holiday: {is_holiday})")

print("--- KR Market ---")
test_holiday("2026-03-02", "KR") # Should be 2026-02-27 (Samiljeol substitute)
test_holiday("2026-03-01", "KR") # Should be 2026-02-27 (Sunday)
test_holiday("2026-02-27", "KR") # Should be 2026-02-27 (Friday)
test_holiday("2026-12-31", "KR") # Should be 2026-12-30 (Year-end)

print("\n--- US Market ---")
test_holiday("2026-01-01", "US") # Should be 2025-12-31 (New Year)
test_holiday("2026-03-02", "US") # Should be 2026-03-02 (Monday, not a US holiday)
