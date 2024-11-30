from flask import Flask, jsonify, request, Response
import requests
from datetime import datetime, timedelta
import utils as u

# from src import utils as u

app = Flask(__name__)


@app.route('/auction')
def get_all_auctions():
    u.reset_response()
    path = u.DB_MANAGER_URL + "/auction"
    response = requests.get(path,
                            verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.RESPONSE["data"] = response.json().get("data")
    return u.send_response()


@app.route('/new_auction', methods=["POST"])
def new_auction():
    u.reset_response()
    data = request.get_json()
    user_id = data.get('user_id')
    gacha_id = data.get('gacha_id')
    starting_price = data.get('starting_price')
    datetime = data.get('starting_datetime')
    if not user_id or not gacha_id or not starting_price or not datetime:
        u.bad_request()
        return u.send_response()

    if starting_price < 0:
        u.bad_request()
        return u.send_response()

    try:
        starting_date = datetime.strptime(datetime, "%Y-%m-%d %H:%M:%S")
    except BaseException as e:
        u.bad_request(str(e))
        return u.send_response()

    path = u.DB_MANAGER_URL + "/new_auction"
    response = requests.post(path,
                             verify=False,
                             json={'user_id': user_id,
                                   'gacha_id': gacha_id,
                                   'starting_price': starting_price,
                                   'starting_datetime': datetime})
    if response.status_code != 200:
        u.handle_error(response.status_code)
    return u.send_response()


@app.route('/bid', methods=["PUT"])
def new_bid():
    u.reset_response()
    auction_id = request.get_json().get("auction_id")
    bid = request.get_json().get("bid")
    email = request.get_json().get("email")
    if not bid or not auction_id:
        u.bad_request()
        return u.send_response()

    path = u.DB_MANAGER_URL + f"/auction/{auction_id}/get_bid"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    # 1) si prende il datetime perché dopo 24h l'asta si chiude
    stored_date = response.json().get("data").get("StartingDate")
    starting_date = datetime.strptime(stored_date, "%Y-%m-%d %H:%M:%S")

    now = datetime.now()
    time_difference = now - starting_date

    if time_difference >= timedelta(days=1):
        u.generic_error("Auction alredy closed.")
        return u.send_response()

    # 2) si prende il prezzo perché devo fare una bid >=
    actual_price = response.json().get("data").get("ActualPrice")
    if bid <= actual_price:
        u.generic_error("Please insert a bid greater than the actual price.")
        return u.send_response()

    # 3) si fa una put sull'actual price
    path = u.DB_MANAGER_URL + f"/auction/{auction_id}/update_actual_price"
    response = requests.put(path, verify=False, json={"bid": bid, "email": email})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    # 4) si fa un update del conto dell'offerente
    path = u.CURRENCY_SERVICE_URL + "/buy_currency"
    response = requests.put(path, verify=False, json={"quantity": bid})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Bid inserted successfully"
    return u.send_response()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8006, debug=u.FLASK_DEBUG)
