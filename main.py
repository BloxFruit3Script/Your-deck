import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import requests
import time
import re
import random

app = Flask(__name__)
key_regex = r'let content = \("([^"]+)"\);'
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
port = int(os.getenv('PORT', 8080))

# Cáº¥u hÃ¬nh logging
logger = logging.getLogger('api_usage')
logger.setLevel(logging.INFO)

log_file_path = '/tmp/api_usage.log'
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Path to the file that stores request count
count_file_path = '/tmp/request_count.txt'

def read_request_count():
    """Read the current request count from file."""
    if os.path.exists(count_file_path):
        with open(count_file_path, 'r') as f:
            return int(f.read().strip())
    return 0

def write_request_count(count):
    """Write the request count to file."""
    with open(count_file_path, 'w') as f:
        f.write(str(count))

def get_client_ip():
    """HÃ m Ä‘á»ƒ láº¥y Ä‘á»‹a chá»‰ IP cá»§a client, xem xÃ©t cáº£ trÆ°á»ng há»£p Ä‘áº±ng sau proxy."""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

@app.route('/')
def index():
    return render_template('index.html')

def fetch(url, headers):
    try:
        # Giáº£ láº­p thá»i gian pháº£n há»“i tá»« 0.1 Ä‘áº¿n 0.2 giÃ¢y
        fake_time = random.uniform(0.1, 0.2)
        time.sleep(fake_time)

        # Thá»±c hiá»‡n yÃªu cáº§u HTTP
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text, fake_time
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch URL: {url}. Error: {e}")

def bypass_link(url):
    try:
        hwid = url.split("HWID=")[-1]
        if not hwid:
            raise Exception("Invalid HWID in URL")

        start_time = time.time()

        endpoints = [
            {"url": f"https://flux.li/android/external/start.php?HWID={hwid}", "referer": ""},
            {"url": "https://flux.li/android/external/check1.php?hash={hash}", "referer": "https://linkvertise.com"},
            {"url": "https://flux.li/android/external/main.php?hash={hash}", "referer": "https://linkvertise.com"}
        ]

        for endpoint in endpoints:
            url = endpoint["url"]
            referer = endpoint["referer"]
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'close',
                'Referer': referer,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            response_text, fake_time = fetch(url, headers)
            if endpoint == endpoints[-1]:  # Chá»‰ kiá»ƒm tra endpoint cuá»‘i cÃ¹ng
                match = re.search(key_regex, response_text)
                if match:
                    end_time = time.time()
                    time_taken = end_time - start_time
                    return match.group(1), time_taken
                else:
                    raise Exception("Failed to find content key")
    except Exception as e:
        raise Exception(f"Failed to bypass link. Error: {e}")

@app.route("/check")
def check():
    request_count = read_request_count()
    return jsonify({"request": request_count})

@app.route("/api/fluxus")
def bypass():
    request_count = read_request_count() + 1
    write_request_count(request_count)
    
    url = request.args.get("url")
    if url and url.startswith("https://flux.li/android/external/start.php?HWID="):
        try:
            content, time_taken = bypass_link(url)
            return jsonify({"key": content, "time_taken": time_taken})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"message": "Please Enter a Valid Fluxus Link!"})
        
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Äáº£m báº£o ráº±ng debug=False trong mÃ´i trÆ°á»ng sáº£n xuáº¥t
    )

from flask import Flask, request, jsonify
import re
import base64
import requests

app = Flask(__name__)

@app.route('/api/boost.ink', methods=['GET'])
def extract():
    # Get the URL from query parameters
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        # Fetch the webpage content
        response = requests.get(url)
        html_content = response.text

        # Regex pattern to match the Base64 value inside bufpsvdhmjybvgfncqfa attribute
        pattern = r'bufpsvdhmjybvgfncqfa="([^"]+)"'

        # Find all matches
        matches = re.findall(pattern, html_content)

        if matches:
            # Extract the first match
            base64_value = matches[0]

            # Decode the Base64 value
            decoded_value = base64.b64decode(base64_value).decode("utf-8")
            
            return jsonify({"bypassed": decoded_value})
        else:
            return jsonify({"error": "No matches found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
