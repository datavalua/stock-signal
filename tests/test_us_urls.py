import yfinance as yf

def print_us_index_urls():
    sp_symbol = '^GSPC'
    ndq_symbol = '^IXIC'
    sp_url = f"https://finance.yahoo.com/quote/{sp_symbol}/"
    ndq_url = f"https://finance.yahoo.com/quote/{ndq_symbol}/"
    print('S&P 500 news_url:', sp_url)
    print('NASDAQ news_url:', ndq_url)

if __name__ == '__main__':
    print_us_index_urls()
