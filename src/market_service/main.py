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
        return jsonify(u.RESPONSE)

    path = u.DB_MANAGER_URL + "/new_transaction"
    response = requests.post(path,
                             verify=False,
                             json={'user_id': user_id,
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
    




@app.route('/see_history_auction_market', methods=['GET'])
def see_history_auction_market():
    try:
        response = requests.get('https://db-manager:8005/see_history_auction_market',verify=False)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        elif response.status_code == 400:
            return jsonify({"Generic error"}), 400
        else:
            return jsonify({"error": "server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500
    


@app.route('/see_auction_market', methods=['GET'])
def see_auction_market():
    try:
        response = requests.get('https://db-manager:8005/see_auction_market',verify=False)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        elif response.status_code == 400:
            return jsonify({"Generic error"}), 400
        else:
            return jsonify({"error": "server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


#per controllare la cronologia personale di qualcuno
@app.route('/see_transaction_history', methods=['GET'])
def see_transaction_history():
    email = request.args.get('Email')
    try:
        response = requests.get('https://db-manager:8005/see_transaction_history',verify=False,params={"Email": email})
        if response.status_code == 200:
            return jsonify(response.json()), 200
        elif response.status_code == 400:
            return jsonify({"Generic error"}), 400
        else:
            return jsonify({"error": "server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


#funzione per vedere una endita specifica(solo per gli admin)
@app.route('/see_specific_auction', methods=['GET'])
def see_specific_auction():
    auth_token=u.get_auth_token()
    if not auth_token:
        return jsonify({"error": "Authorization header is required"}), 401

    token = u.validate_token(auth_token)#rigenera i campi originali dal token cifrato
    role=token.get('role')

    if role == "admin":  
        Transaction = request.args.get('Transaction')
        try:
            response = requests.get('https://db-manager:8005/see_specific_auction',verify=False,params={"Transaction": Transaction})
            if response.status_code == 200:
                return jsonify(response.json()), 200
            elif response.status_code == 400:
                return jsonify({"Generic error"}), 400
            else:
                return jsonify({"error": "server error"}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500
    else:
        return jsonify({"error": "invalid authorization"}), 500



if __name__ == "__main__":
    app.run(debug=u.FLASK_DEBUG)
