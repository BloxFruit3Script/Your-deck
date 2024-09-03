import requests
from bs4 import BeautifulSoup

def bypass_fluxus(start_url):
    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; GO3C Build/OPM2.171019.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.141 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "referer": "https://linkvertise.com/",
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }

    fluxus_urls = {
        "check": "https://flux.li/android/external/check1.php?hash={hash}",
        "main": "https://flux.li/android/external/main.php?hash={hash}",
    }

    try:
        requests.get(start_url, headers=headers)
        
        check_response = requests.get(fluxus_urls['check'], headers=headers)
        main_response = requests.get(fluxus_urls['main'], headers=headers)
        
        soup = BeautifulSoup(main_response.text, 'html.parser')
        random_stuff = soup.find('code', style="background:#29464A;color:#F0F0F0; font-size: 13px;font-family: 'Open Sans';").get_text().strip()

        return {"success": True, "key": random_stuff}
    except Exception as error:
        return {"success": False, "message": "Internal Server Error"}
