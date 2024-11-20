import requests
from flask import Flask, request, jsonify
import utils as u

app = Flask(__name__)

ROUTING = "http://127.0.0.1:8005/" if u.LOCAL else "http://db-manager:8005/"


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    data = request.get_json()
    user_id = data.get('user_id')
    gacha_id = data.get('gacha_id')
    cost = data.get('cost')
    datetime = data.get('end_date')
    if user_id is None or gacha_id is None or cost is None or datetime is None:
        u.bad_request()
        return jsonify(u.RESPONSE)

    path = ROUTING + "new_transaction"
    response = requests.post(path, json={'user_id': user_id,
                                         'gacha_id': gacha_id,
                                         'cost': cost,
                                         'end_date': datetime})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    else:
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = []
        return jsonify(u.RESPONSE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)
