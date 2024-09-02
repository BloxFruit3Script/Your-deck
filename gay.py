from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api/user', methods=['GET'])
def get_user_id():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Please Enter Username'}), 400

    try:
        response = requests.post(
            'https://users.roblox.com/v1/usernames/users',
            json={"usernames": [username]}
        )
        response_data = response.json()

        if 'data' not in response_data or len(response_data['data']) == 0:
            return jsonify({'error': 'User Not Found In Database!'}), 400

        user_id = response_data['data'][0]['id']
        return jsonify({'id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
 

