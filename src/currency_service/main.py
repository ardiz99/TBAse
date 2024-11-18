from flask import Flask, jsonify, request
import requests
import random

import utils as u

app = Flask(__name__)

# ROUTING = u.SERVICES["LOCAL"] + ":" + u.PORTS["DB_MANAGER"]


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


@app.route('/roll', methods=['GET'])
def roll_gacha():
    u.reset_response()

    # TODO: PRENDERE L'EMAIL DELL'UTENTE AUTENTICATO
    email = "taylor.smith@example.com"
    # response = requests.get('http://127.0.0.1:8005/get_amount', params={'email': email})
    response = requests.get('http://db-manager:8005/get_amount', params={'email': email})

    target_data = response.json().get("data")
    amount = target_data[0]["CurrencyAmount"]
    if amount < u.ROLL_COST:
        u.RESPONSE["code"] = 500
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "Insufficient Pokedollars"
        return jsonify(u.RESPONSE)

    rarity = random_rarity()

    # response = requests.get('http://127.0.0.1:8005/get_gacha_by_rarity', params={'rarity': 'Legendary'})
    response = requests.get('http://db-manager:8005/get_gacha_by_rarity', params={'rarity': rarity})

    target_set = response.json().get("data")
    random2 = random.randint(0, len(target_set) - 1)
    chosen = target_set[random2]

    # TODO: PRENDERE L'EMAIL DELL'UTENTE AUTENTICATO
    new_amount = amount - 10
    # response = requests.get('http://127.0.0.1:8005/update_amount',
    #                           params={'email': email, 'new_amount': new_amount})
    response = requests.get('http://db-manager:8005/update_amount',
                            params={'email': email, 'new_amount': new_amount})

    if response.json().get("code") != 200:
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "Update Error"
    else:
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = chosen

    return jsonify(u.RESPONSE)


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
    # response = requests.get('http://127.0.0.1:8005/get_amount', params={'email': email})
    response = requests.get('http://db-manager:8005/get_amount', params={'email': email})

    target_data = response.json().get("data")
    amount = target_data[0]["CurrencyAmount"]

    # TODO: PRENDERE L'EMAIL DELL'UTENTE AUTENTICATO
    new_amount = amount + quantity
    # response = requests.get('http://127.0.0.1:8005/update_amount',
    #                          params={'email': email, 'new_amount': new_amount})
    response = requests.get('http://db-manager:8005/update_amount',
                            params={'email': email, 'new_amount': new_amount})

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
