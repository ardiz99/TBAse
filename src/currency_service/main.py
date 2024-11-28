from datetime import datetime
from flask import Flask, jsonify, request, send_file
import requests
import random

import utils as u
# from src import utils as u

app = Flask(__name__)

RARITY_DISTRIBUTION = {
    "Legendary": 0.05,
    "Epic": 0.5,
    "Rare": 5,
    "Uncommon": 40,
    "Common": 54.45
}


def random_rarity():
    roll = random.uniform(0, 100)
    cumulative = 0
    rarity = None
    for key, chance in RARITY_DISTRIBUTION.items():
        cumulative += chance
        if roll <= cumulative:
            rarity = key
            break
    return rarity


@app.route('/roll_info', methods=['GET'])
def roll_info():
    u.reset_response()

    # TODO: PRENDERE L'EMAIL DELL'UTENTE AUTENTICATO
    email = "taylor.smith@example.com"
    user_id = 1

    path = u.DB_MANAGER_URL + "/get_amount"
    response = requests.get(path,
                            verify=False,
                            params={'email': email})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    target_data = response.json().get("data")
    amount = target_data["CurrencyAmount"]
    if amount < u.ROLL_COST:
        u.generic_error("Insufficient Pokedollars")
        return jsonify(u.RESPONSE), u.RESPONSE["code"]

    rarity = random_rarity()

    path = u.DB_MANAGER_URL + "/get_gacha_by_rarity"
    response = requests.get(path,
                            verify=False,
                            params={'rarity': rarity})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    target_set = response.json().get("data")
    random2 = random.randint(0, len(target_set) - 1)
    chosen = target_set[random2]

    # TODO: PRENDERE L'EMAIL DELL'UTENTE AUTENTICATO
    new_amount = amount - 10
    path = u.DB_MANAGER_URL + "/update_amount"
    response = requests.put(path,
                            verify=False,
                            json={'email': email, 'new_amount': new_amount})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    gacha_id = chosen["GachaId"]
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    path = u.MARKET_SERVICE_URL + "/new_transaction"
    response = requests.post(path,
                             verify=False,
                             json={'user_id': user_id,
                                   'gacha_id': gacha_id,
                                   'cost': u.ROLL_COST,
                                   'end-date': formatted_datetime})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    else:
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = chosen
        return jsonify(u.RESPONSE)


@app.route('/roll_img', methods=['GET'])
def roll_img():
    url = request.args.get("url")
    image_path = "." + url

    return send_file(image_path, mimetype='image/png')


@app.route('/buy_currency', methods=['PUT'])
def buy_currency():
    u.reset_response()
    data = request.get_json()
    quantity = data.get('quantity')
    if quantity <= 0:
        u.generic_error("You can't add a negative quantity.")
        return jsonify(u.RESPONSE)

    # TODO: PRENDERE L'EMAIL DELL'UTENTE AUTENTICATO
    email = "taylor.smith@example.com"
    path = u.DB_MANAGER_URL + "/get_amount"
    response = requests.get(path,
                            verify=False,
                            params={'email': email})

    target_data = response.json().get("data")
    amount = target_data["CurrencyAmount"]

    # TODO: PRENDERE L'EMAIL DELL'UTENTE AUTENTICATO
    new_amount = amount + quantity
    path = u.DB_MANAGER_URL + "/update_amount"
    response = requests.put(path,
                            verify=False,
                            json={'email': email,
                                  'new_amount': new_amount})

    if response.json().get("code") != 200:
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "Update Error"
    else:
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "Currency amount updated successfully. New amount: {}".format(new_amount)

    return jsonify(u.RESPONSE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004, debug=u.FLASK_DEBUG)
