import requests
from flask import Flask, request, jsonify

import utils as u

# from src import utils as u

app = Flask(__name__)


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    data = request.get_json()
    user_id = data.get('user_id')
    gacha_id = data.get('gacha_id')
    cost = data.get('cost')
    datetime = data.get('end_date')
    if user_id is None or gacha_id is None or cost is None or datetime is None:
        u.bad_request()
        return u.send_response()

    path = u.DB_MANAGER_URL + "/new_transaction"
    response = requests.post(path,
                             verify=False,
                             json={'user_id': user_id,
                                   'gacha_id': gacha_id,
                                   'cost': cost,
                                   'end_date': datetime})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()
    else:
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = []
        return u.send_response()


@app.route('/transaction', methods=['GET'])
def transaction():
    email = request.args.get('email')
    if email is None:
        u.bad_request()
        return u.send_response()

    path = u.DB_MANAGER_URL + "/get_id_by_email"
    response = requests.get(path,
                            verify=False,
                            params={'email': email})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    user_id = response.json().get("data").get("UserId")

    path = u.DB_MANAGER_URL + f"/transaction/{user_id}"
    response = requests.get(path,
                            verify=False)

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()


if __name__ == "__main__":
    app.run(debug=u.FLASK_DEBUG)
