import requests

def save_html(symbol):
    url = f"https://finance.naver.com/item/main.naver?code={symbol}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    res = requests.get(url, headers=headers)
    res.encoding = 'euc-kr'
    with open('naver_main.html', 'w', encoding='utf-8') as f:
        f.write(res.text)

save_html("005930")
