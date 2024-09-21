from flask import Flask, request, jsonify
import asyncio
from aiohttp import ClientSession
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

relzheaders = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Connection': 'close',
    'Referer': 'https://linkvertise.com'
}

relz_key_pattern = r'const\s+keyValue\s*=\s*"([^"]+)"'

async def get_content(url, session):
    async with session.get(url, headers=relzheaders, allow_redirects=True) as response:
        html_text = await response.text()
        return html_text

async def fetch_key_value(link):
    urls = [
        link,
        'https://getkey.relzscript.xyz/check1.php',
        'https://getkey.relzscript.xyz/check2.php',
        'https://getkey.relzscript.xyz/check3.php',
        'https://getkey.relzscript.xyz/generate.php'
    ]

    async with ClientSession() as session:
        for url in urls:
            html_text = await get_content(url, session)
            soup = BeautifulSoup(html_text, 'html.parser')
            script_tags = soup.find_all('script')
            for script_tag in script_tags:
                script_content = script_tag.string
                if script_content:
                    key_match = re.search(relz_key_pattern, script_content)
                    if key_match:
                        key_value = key_match.group(1)
                        return key_value

    return None

@app.route('/api/relz')
def get_key_value():
    link = request.args.get('link')
    if not link:
        return jsonify({'error': 'No link provided'})

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    key_value = loop.run_until_complete(fetch_key_value(link))

    if key_value:
        return jsonify({'status': key_value})
    else:
        return jsonify({'error': 'Key value not found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
