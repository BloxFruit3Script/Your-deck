import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import requests
import time
import re
import random
import base64

app = Flask(__name__)
key_regex = r'let content = "([^"]+)"'
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
port = int(os.getenv('PORT', 8080))

# Logging configuration
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
    """Function to get the client's IP address, considering the case of being behind a proxy."""
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
        # Simulate a response time from 0.1 to 0.2 seconds
        fake_time = random.uniform(0.1, 0.2)
        time.sleep(fake_time)

        # Perform the HTTP request
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
            {"url": f"https://flux.li/android/external/check1.php?hash={{hash}}", "referer": "https://linkvertise.com"},
            {"url": f"https://flux.li/android/external/main.php?hash={{hash}}", "referer": "https://linkvertise.com"}
        ]

        for endpoint in endpoints:
            current_url = endpoint["url"]
            referer = endpoint["referer"]
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'close',
                'Referer': referer,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            response_text, fake_time = fetch(current_url, headers)
            if endpoint == endpoints[-1]:  # Only check the last endpoint
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

@@app.route("/api/fluxus")
def bypass():
    request_count = read_request_count() + 1
    write_request_count(request_count)
    
    url = request.args.get("url")
    if url and url.startswith("https://flux.li/android/external/start.php?HWID="):
        try:
            content, time_taken = bypass_link(url)
            return jsonify({"key": content, "time_taken": time_taken})
        except Exception as e:
            logger.error(f"Error bypassing link: {e}")
            return jsonify({"error": "Failed to process the request. Please try again later."}), 500
    else:
        return jsonify({"message": "Invalid or missing 'url' parameter!"}), 400
        
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Ensure that debug=False in the production environment
    )
