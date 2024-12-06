from flask import Flask, jsonify, request, Response
import requests
import utils as u

# from src import utils as u

app = Flask(__name__)


@app.route('/')
def index():
    return {"message": "API Gateway is running"}


@app.route('/roll', methods=['GET'])
def roll():
    u.reset_response()

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    try:
        access_token = auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()

    token = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token:
        u.unauthorized(token["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()
    email = token.get("decoded", {}).get("sub")

    path = u.CURRENCY_SERVICE_URL + f"/roll_info/{u.ROLL_COST}"
    response = requests.get(path, verify=False, params={"email": email})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    data = response.json().get("data")
    url = data["Link"]
    path = u.CURRENCY_SERVICE_URL + "/roll_img"
    response = requests.get(path,
                            verify=False,
                            params={"url": url})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    return Response(
        response.content,
        content_type=response.headers['Content-Type'],
        status=response.status_code
    )


@app.route('/golden_roll', methods=['GET'])
def golden():
    u.reset_response()

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    try:
        access_token = auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()
    token = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token:
        u.unauthorized(token["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()
    email = token.get("decoded", {}).get("sub")

    path = u.CURRENCY_SERVICE_URL + f"/roll_info/{u.GOLDEN_COST}"
    response = requests.get(path,
                            verify=False,
                            params={"email": email})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    data = response.json().get("data")
    url = data["Link"]
    path = u.CURRENCY_SERVICE_URL + "/roll_img"
    response = requests.get(path,
                            verify=False,
                            params={"url": url})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    return Response(
        response.content,
        content_type=response.headers['Content-Type'],
        status=response.status_code
    )


@app.route('/buy_currency', methods=['PUT'])
def buy_currency():
    u.reset_response()

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    try:
        access_token = auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()
    token = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token:
        u.unauthorized(token["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()
    email = token.get("decoded", {}).get("sub")

    data = request.get_json()
    quantity = data.get('quantity')
    fields_to_sanitize = u.process_fields([str(quantity)])
    quantity = int(fields_to_sanitize[0])
    if not quantity:
        u.bad_request()
        return u.send_response()

    path = u.CURRENCY_SERVICE_URL + "/buy_currency"
    response = requests.put(path,
                            verify=False,
                            json={"quantity": quantity, "email": email})
    if response.status_code != 200:
        u.handle_error(response.status_code)

    u.set_response(response)
    return u.send_response()


@app.route('/login', methods=['POST'])
def login():
    email = request.get_json().get('Email')
    password = request.get_json().get('Password')
    response = requests.post('https://auth-service:8001/login',
                             verify=False,
                             json={'Email': email, 'Password': password})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        u.set_response(response)
        return u.send_response()

    return jsonify(response.json()), 200


@app.route('/register', methods=['POST'])
def register():
    u.reset_response()

    data = request.get_json()
    first_name = data.get('FirstName')
    last_name = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    amount = data.get('CurrencyAmount')
    response = requests.post('https://auth-service:8001/register',
                             verify=False,
                             json={'FirstName': first_name,
                                   'LastName': last_name,
                                   'Email': email,
                                   'Password': password,
                                   'CurrencyAmount': amount})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        u.set_response(response)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()

    response = requests.delete('https://auth-service:8001/delete_user',
                               verify=False,
                               headers={'Authorization': auth_header}
                               )
    return jsonify(response.json())


@app.route('/logout', methods=['GET'])
def logout():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response("no token found. PLs log in first")
    response = requests.get('https://auth-service:8001/logout',
                            verify=False,
                            headers={'Authorization': auth_header})
    return jsonify(response.json())


@app.route('/update_user', methods=['PUT'])
def update_user():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    data = request.get_json()
    first_name = data.get('FirstName')
    last_name = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    amount = data.get('CurrencyAmount')
    response = requests.put('https://auth-service:8001/update_user',
                            verify=False,
                            json={'FirstName': first_name,
                                  'LastName': last_name,
                                  'Email': email,
                                  'Password': password,
                                  'CurrencyAmount': amount},
                            headers={'Authorization': auth_header})
    return jsonify(response.json())


@app.route('/check_users_profile', methods=['GET'])
def check_users_profile():
    response = requests.get('https://auth-service:8001/check_users_profile',
                            verify=False)
    return jsonify(response.json())


@app.route('/login_admin', methods=['GET'])
def login_admin():
    email = request.args.get('Email')
    password = request.args.get('Password')
    response = requests.get('https://auth-service:8001/login_admin',
                            verify=False,
                            params={'Email': email, 'Password': password})
    return jsonify(response.json())


# INIZIO Endpoint gacha  ====>


# Endpoint per ottenere un singolo gacha
@app.route('/gacha/get/<int:gacha_id>', methods=['GET'])
def get_gacha(gacha_id):
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    if gacha_id is None:
        u.bad_request("Invalid input")
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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()

    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()

    name = u.sanitize(gacha_name, u.ALLOWED_CHAR)
    if name is None:
        u.bad_request("Invalid input")
        return u.send_response()
    url = u.GACHA_SERVICE_URL + f"/getName/{name}"
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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
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
        u.not_found("Gachas not found")
        return u.send_response()
    u.RESPONSE["data"] = gachas
    u.RESPONSE["code"] = 200
    u.RESPONSE["message"] = "Gachas retrivied succesfully"
    return jsonify(u.RESPONSE)


@app.route('/gacha/mygacha/<string:gacha_id>', methods=['GET'])
def get_mygacha(gacha_id):
    u.reset_response()

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    try:
        access_token = auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()
    token = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token:
        u.unauthorized(token["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()
    email = token.get("decoded", {}).get("sub")

    id = u.safe_parse_int(u.sanitize(gacha_id, u.ALLOWED_INT))
    if id is None:
        u.bad_request("Invalid input")
        return u.send_response()
    url = u.GACHA_SERVICE_URL + f"/mygacha/{email}/{id}"
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


@app.route('/gacha/mygacha', methods=['GET'])
def get_mygachaAll():
    u.reset_response()

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    try:
        access_token = auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()
    token = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token:
        u.unauthorized(token["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()
    email = token.get("decoded", {}).get("sub")

    url = u.GACHA_SERVICE_URL + f"/mygacha/{email}"
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
    u.RESPONSE["message"] = "Gachas retrivied succesfully"
    return jsonify(u.RESPONSE)


# INIZIO ENDPOINT PER IL MARKET-SERVICE ==>
@app.route('/auction')
def get_all_auctions():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()

    path = u.MARKET_SERVICE_URL + "/auction"
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

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    try:
        access_token = auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()
    token = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token:
        u.unauthorized(token["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()
    user_owner_email = token.get("decoded", {}).get("sub")

    gacha_id = request.get_json().get('gacha_id')
    starting_price = request.get_json().get('starting_price')
    end_date = request.get_json().get('end_date')
    fields_to_sanitize = u.process_fields([str(gacha_id), str(starting_price), end_date])
    gacha_id = int(fields_to_sanitize[0])
    starting_price = int(fields_to_sanitize[1])
    end_date = fields_to_sanitize[2]
    if not gacha_id or not starting_price or not end_date:
        u.bad_request()
        return u.send_response()

    path = u.MARKET_SERVICE_URL + "/new_auction"
    response = requests.post(path,
                             verify=False,
                             json={'user_owner': user_owner_email,
                                   'gacha_id': gacha_id,
                                   'starting_price': starting_price,
                                   'end_date': end_date})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response("Auction created successfully.")


@app.route('/bid/<int:transaction_id>', methods=["PUT"])
def new_bid(transaction_id):
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    email = token.get("sub")
    bid = request.get_json().get("bid")

    fields_to_sanitize = u.process_fields([str(bid)])
    bid = int(fields_to_sanitize[0])

    if not bid or not transaction_id:
        u.bad_request()
        return u.send_response()

    path = u.MARKET_SERVICE_URL + f"/bid/{transaction_id}"
    response = requests.put(path,
                            verify=False,
                            json={"email": email,
                                  "bid": bid})
    if response.status_code != 200:
        u.handle_error(response.status_code)

    u.set_response(response)
    return u.send_response()


@app.route('/my_transaction_history', methods=['GET'])
def my_transaction_history():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)
    email = token.get("sub")

    path = u.MARKET_SERVICE_URL + "/my_transaction_history"
    response = requests.get(path, verify=False, params={"email": email})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=u.FLASK_DEBUG)
