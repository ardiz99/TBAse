from flask import Flask, jsonify
import requests


app = Flask(__name__)


@app.route('/')
def index():
    return {"message": "API Gateway is running"}


@app.route('/roll')
def roll_gacha():
    response = requests.get('http://currency-service:8004/roll')
    return jsonify(response.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
