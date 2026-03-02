import sys
import os
import datetime
from datetime import timedelta
from unittest.mock import patch

# Add current directory to path
sys.path.append(os.getcwd())

from backend import crawler

def test_holiday_logic():
    # 2026-03-02 is a Monday. 
    # Let's assume KR market is closed on 3/2 (as per user request).
    # US market is open.
    
    print("Testing Holiday Logic...")
    
    # Mock fdr.DataReader to simulate market holidays
    def mock_data_reader(symbol, start, end):
        import pandas as pd
        # Simulate 2026-03-02 as holiday for KR (KS11)
        if symbol == 'KS11':
            if end == '2026-03-02':
                # Return data only up to 2026-02-27 (Friday)
                dates = pd.date_range(start='2026-02-20', end='2026-02-27')
                return pd.DataFrame({'Close': [100]*len(dates)}, index=dates)
        # Simulate 2026-03-02 as open for US (IXIC)
        if symbol == 'IXIC':
            if end == '2026-03-02':
                dates = pd.date_range(start='2026-02-20', end='2026-03-02')
                return pd.DataFrame({'Close': [100]*len(dates)}, index=dates)
        return pd.DataFrame()

    with patch('FinanceDataReader.DataReader', side_effect=mock_data_reader):
        # Test KR 3/2 -> should return 2/27
        kr_last = crawler.get_last_trading_day('2026-03-02', market='KR')
        print(f"KR 2026-03-02 last trading day: {kr_last}")
        assert kr_last == '2026-02-27', f"Expected 2026-02-27, got {kr_last}"
        
        # Test US 3/2 -> should return 3/2
        us_last = crawler.get_last_trading_day('2026-03-02', market='US')
        print(f"US 2026-03-02 last trading day: {us_last}")
        assert us_last == '2026-03-02', f"Expected 2026-03-02, got {us_last}"

    print("✅ All holiday logic tests passed!")

if __name__ == "__main__":
    test_holiday_logic()
