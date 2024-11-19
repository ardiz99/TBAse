from flask import Flask, jsonify, request, Response
import requests
import utils as u

app = Flask(__name__)


@app.route('/')
def index():
    return {"message": "API Gateway is running"}


@app.route('/roll', methods=['GET'])
def roll_gacha():
    response = requests.get('http://currency-service:8004/roll_info')
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    data = response.json().get("data")
    url = data["Link"]
    response = requests.get('http://currency-service:8004/roll_img', json={"url": url})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    return Response(
        response.content,
        content_type=response.headers['Content-Type'],
        status=response.status_code
    )




@app.route('/buy_currency', methods=['PUT'])
def buy_currency():
    data = request.get_json()
    quantity = data.get('quantity')
    if quantity is None:
        u.bad_request()
        return jsonify(u.RESPONSE)

    response = requests.put('http://currency-service:8004/buy_currency', json={"quantity": quantity})
    # response = requests.put('http://127.0.0.1:8004/buy_currency', json={"quantity": quantity})
    return jsonify(response.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=u.FLASK_DEBUG)
