from flask import Flask, request, jsonify, redirect
import time
import requests
import base64

app = Flask(__name__)

def sleep(seconds):
    time.sleep(seconds)

@app.route('/delta', methods=['GET'])
def delta():
    e = request.args.get("id")
    response = requests.get(f"https://api-gateway.platoboost.com/v1/authenticators/8/{e}")
    t = response.json()

    if t.get("key"):
        return jsonify({"status": "Key found", "key": t["key"]})

    a = request.args.get("tk")
    if a:
        sleep(5)
        session_response = requests.put(
            f"https://api-gateway.platoboost.com/v1/sessions/auth/8/{e}/{a}"
        ).json()
        if 'redirect' in session_response:
            return redirect(session_response['redirect'])
        else:
            return jsonify({"error": session_response})
    else:
        captcha = t.get("captcha", "")
        session_response = requests.post(
            f"https://api-gateway.platoboost.com/v1/sessions/auth/8/{e}",
            json={
                "captcha": captcha or await get_turnstile_response(),
                "type": "Turnstile" if captcha else ""
            },
            headers={"Content-Type": "application/json"}
        ).json()

        sleep(1)
        s = requests.utils.unquote(session_response['redirect'])
        i = s.split('r=')[1]
        decoded_redirect = base64.b64decode(i).decode('utf-8')

        return redirect(decoded_redirect)

def get_turnstile_response():
    # Placeholder for Turnstile response. Could integrate hCaptcha verification here.
    return ""

@app.route('/')
def index():
    return "Delta Bypass API is running."

if __name__ == '__main__':
    app.run(debug=True)
