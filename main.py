from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

@app.route('/socialwolvez', methods=['GET'])
def socialwolvez():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'Missing parameter: url'}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        script_tag = soup.find('script', {'id': '__NUXT_DATA__'})
        if script_tag and script_tag.string:
            try:
                data = json.loads(script_tag.string)
                
                extracted_url = data.get(5)
                extracted_name = data.get(6)

                if extracted_url and extracted_name:
                    return jsonify({'bypassed_url': extracted_url, 'name': extracted_name})
                else:
                    return jsonify({'error': 'Required data not found in the JSON structure.'}), 500

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                return jsonify({'error': 'Failed to parse JSON data.', 'details': str(e)}), 500
        else:
            return jsonify({'error': 'Script tag with JSON data not found.'}), 404

    except requests.RequestException as e:
        return jsonify({'error': 'Failed to make request to the provided URL.', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
