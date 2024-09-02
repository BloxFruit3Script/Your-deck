from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def get_key_from_url(url):
    hwid = url.replace("https://getkey.relzscript.xyz/redirect.php?hwid=", "")

    session = requests.Session()

    initial_cookies = {
        'check1': '1',
        'dom3ic8zudi28v8lr6fgphwffqoz0j6c': '901d9e30-900a-4158-9e0c-b355b36a5f77%3A3%3A1',
        'pp_main_e7e5688c4d672d39846f0eb422e33a7d': '1',
        'hwid': hwid,
        'check2': '1',
        'pp_sub_e7e5688c4d672d39846f0eb422e33a7d': '4'
    }

    session.cookies.update(initial_cookies)

    session.get('https://getkey.relzscript.xyz/check1.php')

    headers = {
        'Priority': 'u=0, i',
        'Referer': 'https://loot-link.com/'
    }

    session.get('https://getkey.relzscript.xyz/check2.php', headers=headers)
    session.get('https://getkey.relzscript.xyz/check3.php', headers=headers)

    final_response = session.get('https://getkey.relzscript.xyz/generate.php', headers=headers)

    soup = BeautifulSoup(final_response.text, 'html.parser')
    scripts = soup.find_all('script')
    pattern = re.compile(r'const keyValue = "(RelzHub_[\w]+)"')

    first_key = None
    for script in scripts:
        match = pattern.search(script.text)
        if match:
            first_key = match.group(1)
            break

    return first_key

@app.route('/api/relz', methods=['GET'])
def bypass():
    link = request.args.get('link')
    if not link:
        return jsonify({'success': False, 'error': 'Missing link parameter'}), 400

    try:
        key = get_key_from_url(link)
        if key:
            return jsonify({'success': True, 'key': key})
        else:
            return jsonify({'success': False, 'error': 'Key not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
