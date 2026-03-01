import requests
from bs4 import BeautifulSoup
import re

def get_realtime_investor_data_main(symbol):
    url = f"https://finance.naver.com/item/main.naver?code={symbol}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # In main page, there's usually a section for investor trends
    # Look for '투자자별 매매동향'
    investor_div = soup.find('div', class_='sub_section')
    # Let's just find the headers
    em_tags = soup.find_all('em')
    for em in em_tags:
        if em.text and '외국인' in em.text or '기관' in em.text:
            print(em.parent.text.strip())
            
    # Or look for dl class="blind"
    dl = soup.find('dl', class_='blind')
    if dl:
        print(dl.text)
        
    investor_box = soup.select('.sub_sectionkrx') # This doesn't exist.
    
    print("Trying to find the table in '투자자별 매매동향' section")
    section = soup.find(string=re.compile("투자자별 매매동향"))
    if section:
        print("Found section!")
        parent = section.find_parent('div', class_='sub_section')
        if parent:
            print(parent.text[:200])

get_realtime_investor_data_main("005930")
