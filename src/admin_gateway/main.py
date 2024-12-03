from flask import Flask, jsonify, request, Response
import requests
import utils as u

# from src import utils as u

app = Flask(__name__)


@app.route('/')
def index():
    return {"message": "API Gateway is running for admin"}


# INIZIO ENDPOINT PER IL MARKET-SERVICE ==>
@app.route('/auction')
def get_all_auctions():
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()

    path = u.MARKET_SERVICE_URL + "/auction"
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
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()

    path = u.MARKET_SERVICE_URL + f"/auction/{transaction_id}"
    response = requests.get(path,
                            verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/end_auction/<int:transaction_id>', methods=['PUT'])
def end_auction(transaction_id):
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()

    path = u.MARKET_SERVICE_URL + f"/close_auction/{transaction_id}"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/auction/history', methods=['GET'])
def get_old_transaction():
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()

    path = u.MARKET_SERVICE_URL + f"/auction/history"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()

# INIZIO ENDPOINT DEL ADMIN_GACHASERVICE_URL ==>

# Endpoint per aggiungere un nuovo gacha
@app.route('/gacha/add', methods=['POST'])
def add_gacha():
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()
    # Recupera i dati JSON dalla richiesta
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Missing or invalid JSON payload")
    except Exception as e:
        u.RESPONSE["code"] = 400
        u.RESPONSE["message"] = f"Invalid request: {str(e)}"
        return jsonify(u.RESPONSE), 400
    url = u.GACHA_SERVICE_URL + "/add"
    response = requests.post(url,
                             verify=False,
                             json=data,
                             headers={"Content-Type": "application/json"})
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    u.RESPONSE["data"] = []
    u.RESPONSE["code"] = 200
    u.RESPONSE["message"] = "Gacha added corretly" 
    return jsonify(u.RESPONSE)

# Endpoint per aggiornare un gacha
@app.route('/gacha/update/<int:gacha_id>', methods=['PUT'])
def update_gacha(gacha_id):
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Missing or invalid JSON payload")
    except Exception as e:
        u.RESPONSE["code"] = 400
        u.RESPONSE["message"] = f"Invalid request: {str(e)}"
        return jsonify(u.RESPONSE), 400
    url = u.GACHA_SERVICE_URL + f"/update/{gacha_id}"
    response = requests.put(url,
                            verify=False,
                            json=data,
                            headers={"Content-Type": "application/json"})
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    u.RESPONSE["data"] = []
    u.RESPONSE["code"] = 200
    u.RESPONSE["message"] = "Gacha updated succesfully"
    return jsonify(u.RESPONSE)


# Endpoint per eliminare un gacha
@app.route('/gacha/delete/<int:gacha_id>', methods=['DELETE'])
def delete_gacha(gacha_id):
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()
    url = u.GACHA_SERVICE_URL + f"/delete/{gacha_id}"
    response = requests.delete(url, verify=False)
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    u.RESPONSE["data"] = []
    u.RESPONSE["code"] = 200
    u.RESPONSE["message"] = "Gachas updated succesfully"
    return jsonify(u.RESPONSE)

# Endpoint per ottenere un singolo gacha
@app.route('/gacha/get/<int:gacha_id>', methods=['GET'])
def get_gacha(gacha_id):
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()
    url = u.GACHA_SERVICE_URL + f"/get/{gacha_id}"
    response = requests.get(url, verify=False)
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    gacha = response.json().get("data")
    if not gacha:
        u.not_found("Gacha not found")
        return u.send_response()
    u.RESPONSE["data"] = gacha
    u.RESPONSE["code"] = 200
    u.RESPONSE["message"] = "Gacha retrivied succesfully"
    return jsonify(u.RESPONSE)


# Endpoint per ottenere un singolo gacha per nome
@app.route('/gacha/getName/<string:gacha_name>', methods=['GET'])
def get_gacha_by_name(gacha_name):
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()
    url = u.GACHA_SERVICE_URL + f"/getName/{gacha_name}"
    response = requests.get(url, verify=False)
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    gacha = response.json().get("data")
    if not gacha:
        u.not_found("Gacha not found")
        return u.send_response()
    u.RESPONSE["data"] = gacha
    u.RESPONSE["code"] = 200
    u.RESPONSE["message"] = "Gacha retrivied succesfully"
    return u.send_response()


# Endpoint per ottenere tutti i gachas
@app.route('/gacha/get', methods=['GET'])
def get_all_gachas():
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()
    url = u.GACHA_SERVICE_URL + "/get"
    response = requests.get(url, verify=False)
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    gachas = response.json().get("data")
    if not gachas:
        u.not_found("Gacha not found")
        return u.send_response()
    u.RESPONSE["data"] = gachas
    u.RESPONSE["code"] = 200
    u.RESPONSE["message"] = "Gachas retrivied succesfully"
    return jsonify(u.RESPONSE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=u.FLASK_DEBUG)
