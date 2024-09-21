```py
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_paste_drop_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://paste-drop.com/'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    content = soup.find('span', id='content')
    if content:
        return content.get_text().replace('\\', '')
    else:
        return None

@app.route('/api/paste', methods=['GET'])
def get_paste_drop_content_endpoint():
    url = request.args.get('url')
    if not url:
        return jsonify({"status": "fail", "message": "URL parameter is missing"}), 400

    html_content = get_paste_drop_content(url)
    if html_content:
        parsed_content = parse_html(html_content)
        if parsed_content:
            return jsonify({"status": "success", "result": parsed_content}), 200
        else:
            return jsonify({"status": "fail", "message": "An Error Occurred"}), 500
    else:
        return jsonify({"status": "fail", "message": "Unknown Error Happened"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)```
