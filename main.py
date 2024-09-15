from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def bypass_mediafire(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            download_button = soup.find('a', {'id': 'downloadButton'})
            if download_button:
                frfr = download_button.get('href')
                return frfr
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f'Error: {e}')
        return None

@app.route('/api/mediafire', methods=['GET'])
def get_mediafire_link():
    url = request.args.get('url')
    if not url:
        return jsonify({"status": "fail", "message": "URL parameter is missing"}), 400

    frfr = bypass_mediafire(url)
    if frfr:
        return jsonify({"status": "success", "result": frfr}), 200
    else:
        return jsonify({"status": "fail", "message": "error?"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
