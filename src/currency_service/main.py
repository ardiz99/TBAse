import os
from datetime import datetime
from flask import Flask, request, send_file
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

GOLDEN_DISTRIBUTION = {
    "Legendary": 10,
    "Epic": 90,
}

mock_save_last = None


def save_last(op, args, res):
    """Funzione per salvare l'ultima operazione effettuata."""
    if mock_save_last:
        mock_save_last(op, args, res)
    else:
        # Salvataggio nel formato desiderato
        print(f"Operation: {op}, Arguments: {args}, Result: {res}")


def random_rarity(golden):
    roll = random.uniform(0, 100)
    cumulative = 0
    rarity = None

    distribution = RARITY_DISTRIBUTION if not golden else GOLDEN_DISTRIBUTION

    for key, chance in distribution.items():
        cumulative += chance
        if roll <= cumulative:
            rarity = key
            break
    return rarity


@app.route('/roll_info/<int:cost>', methods=['GET'])
def roll_info(cost):
    if cost != u.ROLL_COST and cost != u.GOLDEN_COST:
        u.bad_request()
        return u.send_response()

    email = request.args.get("email")
    if not email:
        u.bad_request()
        return u.send_response()

    path = u.DB_MANAGER_URL + "/get_amount"
    response = requests.get(path,
                            verify=False,
                            params={'email': email})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    amount = response.json().get("data").get("CurrencyAmount")
    if amount < cost:
        u.generic_error("Insufficient Pokedollars")
        return u.send_response()

    rarity = random_rarity(cost == u.GOLDEN_COST)

    path = u.DB_MANAGER_URL + "/get_gacha_by_rarity"
    response = requests.get(path,
                            verify=False,
                            params={'rarity': rarity})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    target_set = response.json().get("data")
    random2 = random.randint(0, len(target_set) - 1)
    chosen = target_set[random2]
    gacha_id = chosen["GachaId"]

    new_amount = amount - cost
    path = u.DB_MANAGER_URL + "/update_amount"
    response = requests.put(path,
                            verify=False,
                            json={'email': email, 'new_amount': new_amount})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    path = u.DB_MANAGER_URL + "/user/get_by_email"
    response = requests.get(path,
                            verify=False,
                            params={'email': email})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    user_id = response.json().get("data").get("UserId")
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    path = u.MARKET_SERVICE_URL + "/roll"
    response = requests.post(path,
                             verify=False,
                             json={'user_id': user_id,
                                   'gacha_id': gacha_id,
                                   'cost': cost,
                                   'end_date': formatted_datetime})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    else:
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = chosen
        return u.send_response()


@app.route('/roll_img', methods=['GET'])
def roll_img():
    url = request.args.get("url")
    image_path = "." + url
    if not os.path.exists(image_path):
        u.not_found()
        return u.send_response()

    return send_file(image_path, mimetype='image/png')


@app.route('/buy_currency', methods=['PUT'])
def buy_currency():
    u.reset_response()
    quantity = request.get_json().get('quantity')
    email = request.get_json().get('email')

    if quantity <= 0:
        u.generic_error("You can't add a negative quantity.")
        return u.send_response()

    path = u.DB_MANAGER_URL + "/get_amount"
    response = requests.get(path,
                            verify=False,
                            params={'email': email})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    amount = response.json().get("data").get("CurrencyAmount")

    new_amount = amount + quantity
    path = u.DB_MANAGER_URL + "/update_amount"
    response = requests.put(path,
                            verify=False,
                            json={'email': email,
                                  'new_amount': new_amount})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    u.RESPONSE["message"] = f"Currency amount updated successfully. New amount: {new_amount}"
    return u.send_response()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004, debug=u.FLASK_DEBUG)
