import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
# from src import utils as u
import utils as u

app = Flask(__name__)


@app.route('/roll', methods=['POST'])
def roll():
    u.reset_response()
    data = request.get_json()
    user_id = data.get('user_id')
    gacha_id = data.get('gacha_id')
    cost = data.get('cost')
    end_date = data.get('end_date')
    if user_id is None or gacha_id is None or cost is None or end_date is None:
        u.bad_request()
        return u.send_response()

    path = u.DB_MANAGER_URL + "/roll"
    response = requests.post(path,
                             verify=False,
                             json={'user_id': user_id,
                                   'gacha_id': gacha_id,
                                   'cost': cost,
                                   'end_date': end_date})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response("Roll transaction created successfully.")


@app.route('/transaction', methods=['GET'])
def get_all_transaction():
    path = u.DB_MANAGER_URL + "/transaction"
    response = requests.get(path,
                            verify=False)

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/auction/<int:transaction_id>')
def get_specific_auction(transaction_id):
    u.reset_response()
    path = u.DB_MANAGER_URL + f"/auction/{transaction_id}"
    response = requests.get(path,
                            verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/auction')
def get_all_auctions():
    u.reset_response()
    path = u.DB_MANAGER_URL + "/auction"
    response = requests.get(path,
                            verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/active_auction')
def get_all_active_auction():
    u.reset_response()
    path = u.DB_MANAGER_URL + "/active_auction"
    response = requests.get(path,
                            verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/new_auction', methods=["POST"])
def new_auction():
    u.reset_response()
    data = request.get_json()
    user_owner = data.get('user_owner')
    gacha_id = data.get('gacha_id')
    starting_price = data.get('starting_price')
    end_date = data.get('end_date')
    if not user_owner or not gacha_id or not starting_price or not datetime:
        u.bad_request()
        return u.send_response()

    if starting_price < 0:
        u.bad_request()
        return u.send_response()

    try:
        date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        if date < now:
            u.bad_request("Date already passed.")
            return u.send_response()
    except BaseException as e:
        u.bad_request(str(e))
        return u.send_response()

    # TODO: controllare che il gacha sia nella collection dell'utente

    path = u.DB_MANAGER_URL + "/new_auction"
    response = requests.post(path,
                             verify=False,
                             json={'user_owner': user_owner,
                                   'gacha_id': gacha_id,
                                   'starting_price': starting_price,
                                   'end_date': end_date})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response("Auction created successfully.")


@app.route('/bid/<transaction_id>', methods=["PUT"])
def new_bid(transaction_id):
    u.reset_response()
    bid = request.get_json().get("bid")
    email = request.get_json().get("email")
    if not bid or not transaction_id:
        u.bad_request()
        return u.send_response()

    path = u.DB_MANAGER_URL + f"/auction/{transaction_id}/get_bid"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    # INFO DELLA TRANSACTION
    old_requesting_user_id = response.json().get("data").get("RequestingUser")
    actual_price = response.json().get("data").get("ActualPrice")
    stored_date = response.json().get("data").get("EndDate")
    user_owner_id = response.json().get("data").get("UserOwner")
    old_requesting_user_email = None

    if old_requesting_user_id is not None:
        path = u.DB_MANAGER_URL + f"/user/get_by_id/{old_requesting_user_id}"
        response = requests.get(path, verify=False)
        if response.status_code != 200:
            u.handle_error(response.status_code)
            return u.send_response()

        # INFO DELL' OLD REQUESTING USER se presente
        old_requesting_user_email = response.json().get("data").get("Email")

    path = u.DB_MANAGER_URL + "/user/get_by_email"
    response = requests.get(path, verify=False, params={"email": email})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    # INFO DEL REQUESTING USER ATTUALE
    old_amount = response.json().get("data").get("CurrencyAmount")
    new_requesting_user_id = response.json().get("data").get("UserId")

    path = u.DB_MANAGER_URL + f"/user/get_by_id/{user_owner_id}"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    # INFO DELLO USER OWNER
    user_owner_amount = response.json().get("data").get("CurrencyAmount")
    user_owner_email = response.json().get("data").get("Email")

    # 1) CONTROLLO sul end_date perché dopo 24h l'asta si chiude
    end_date = datetime.strptime(stored_date, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    if now >= end_date:
        u.generic_error("Auction alredy closed.")
        return u.send_response()

    # 2) CONTROLLO sul prezzo perché devo fare una bid >= ActualPrice,
    # ma anche >= del mio CurrencyAmount
    if bid <= actual_price:
        u.generic_error("Please insert a bid greater than the actual price.")
        return u.send_response()

    if bid > old_amount:
        u.generic_error("Insufficient currency.")
        return u.send_response()

    # 3) CONTROLLO sull'id dell'offerente per verificare che non sia lo stesso di UserOwner o
    # dell'OldRequestingUser
    if new_requesting_user_id == user_owner_id:
        u.generic_error("UserOwner and RequestingUser are the same")
        return u.send_response()
    if new_requesting_user_id == old_requesting_user_id:
        u.generic_error("You can't raise your own bid")
        return u.send_response()

    # 4) si prende l'email del requesting_user precedente per potergli restituire i soldi spesi
    if old_requesting_user_email is not None:
        path = u.CURRENCY_SERVICE_URL + "/buy_currency"
        response = requests.put(path,
                                verify=False,
                                json={"email": old_requesting_user_email,
                                      "quantity": actual_price})
        if response.status_code != 200:
            u.handle_error(response.status_code)
            return u.send_response()

    # 5) AGGIORNO l'actual price
    path = u.DB_MANAGER_URL + f"/auction/{transaction_id}/update_actual_price"
    response = requests.put(path,
                            verify=False,
                            json={"bid": bid,
                                  "requesting_user": new_requesting_user_id})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    # 6) AGGIORNO il conto dell'offerente
    new_amount = old_amount - bid
    path = u.DB_MANAGER_URL + "/update_amount"
    response = requests.put(path, verify=False, json={"email": email, "new_amount": new_amount})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    # 6) AGGIORNO il conto dello UserOwner
    increase_amount = bid if not old_requesting_user_id else bid - actual_price
    new_amount = user_owner_amount + increase_amount
    path = u.DB_MANAGER_URL + "/update_amount"
    response = requests.put(path, verify=False, json={"email": user_owner_email, "new_amount": new_amount})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()
    
    u.set_response(response)
    return u.send_response("Bid inserted successfully.")


@app.route('/end_auction/<int:transaction_id>', methods=['PUT'])
def end_auction(transaction_id):
    u.reset_response()
    path = u.DB_MANAGER_URL + f"/auction/{transaction_id}/get_bid"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    # INFO DELLA TRANSACTION
    user_owner_id = response.json().get("data").get("UserOwner")
    requesting_user = response.json().get("data").get("RequestingUser")
    gacha_id = response.json().get("data").get("GachaId")

    if requesting_user is None:
        path = u.DB_MANAGER_URL + f"/auction/{transaction_id}/delete"
        response = requests.get(path, verify=False)
        if response.status_code != 200:
            u.handle_error(response.status_code)
            return u.send_response()

        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "Auction deleted because it didn't take any bid."
        return u.send_response()

    path = u.DB_MANAGER_URL + f"/transaction/{gacha_id}/{user_owner_id}"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    transaction_target = response.json().get("data").get("TransactionId")

    path = u.DB_MANAGER_URL + f"/transaction/{transaction_target}/sended_to"
    response = requests.put(path, verify=False, json={"sended_to": requesting_user})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()
    
    u.set_response(response)
    return u.send_response("Auction closed successfully.")


@app.route('/transaction_history/<int:user_id>', methods=['GET'])
def transaction_history(user_id):
    u.reset_response()
    path = u.DB_MANAGER_URL + f"/transaction_history/{user_id}"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()
    
    u.set_response(response)
    return u.send_response()


@app.route('/close_auction/<int:transaction_id>', methods=['PUT'])
def close_auction(transaction_id):
    u.reset_response()
    path = u.DB_MANAGER_URL + f"/auction/{transaction_id}/close_auction"
    response = requests.put(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response("Auction closed successfully")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003, debug=u.FLASK_DEBUG)
