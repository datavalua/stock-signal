import requests
from bs4 import BeautifulSoup
import re

def parse_investor_main(symbol):
    url = f"https://finance.naver.com/item/main.naver?code={symbol}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # search for dt with text '투자자별 매매동향' no, it's a h4 or div
    # Actually it's often a div with class sub_section
    sections = soup.find_all('div', class_='sub_section')
    for sec in sections:
        text = sec.get_text()
        if '외국인' in text and '기관' in text:
            # Look for <em> tags
            ems = sec.find_all('em')
            if len(ems) >= 2:
                print("Found investor data:")
                for em in ems:
                    print(em.parent.get_text(strip=True))
                return
                
    print("Could not find investor data using normal search, trying regex.")
    ems = soup.find_all('em')
    for em in ems:
        if '외국인' in em.text or '기관' in em.text:
            print(em.parent.get_text(strip=True))

parse_investor_main("005930")
