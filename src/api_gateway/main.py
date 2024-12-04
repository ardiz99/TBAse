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
    enc_token = request.headers.get("token")
    if not u.check_token(enc_token):
        return u.send_response()

    token = u.validate_token(enc_token)
    email = token.get("sub")

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
    enc_token = request.headers.get("token")
    if not u.check_token(enc_token):
        return u.send_response()

    token = u.validate_token(enc_token)
    email = token.get("sub")

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
    enc_token = request.headers.get("token")
    if not u.check_token(enc_token):
        return u.send_response()

    token = u.validate_token(enc_token)
    email = token.get("sub")

    data = request.get_json()
    quantity = data.get('quantity')
    if quantity is None:
        u.bad_request()
        return u.send_response()

    path = u.CURRENCY_SERVICE_URL + "/buy_currency"
    response = requests.put(path,
                            verify=False,
                            json={"quantity": quantity, "email": email})
    if response.status_code != 200:
        u.handle_error(response.status_code)

    return u.send_response()


# INIZIO ENDPOINT DEL GACHASERVICE_URL ==>

@app.route('/mygacha', methods=['GET'])
def get_allmygacha():
    u.reset_response()

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + "/mygacha"
    # Effettua la richiesta GET al servizio remoto
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)

        return jsonify(u.RESPONSE), response.status_code
    gachas = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gachas
    u.RESPONSE["message"] = "Gacha retrieved successfully!"
    return jsonify(u.RESPONSE)


@app.route('/login', methods=['GET'])
def login():
    email = request.args.get('Email')
    password = request.args.get('Password')
    response = requests.get('https://auth-service:8001/login',
                            verify=False,
                            params={'Email': email, 'Password': password})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    return jsonify(response.json()), 200






@app.route('/register', methods=['POST'])
def register():
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
    return jsonify(response.json())





@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    
    # email = request.args.get('Email')
    # password = request.args.get('Password')  params={'Email': email, 'Password': password}
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




# INIZIO ENDPOINT DEL ADMIN_GACHASERVICE_URL ==>

# Endpoint per aggiungere un nuovo gacha
@app.route('/gacha/add', methods=['POST'])
def add_gacha():
    u.reset_response()
    # Recupera i dati JSON dalla richiesta
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Missing or invalid JSON payload")
    except Exception as e:
        u.RESPONSE["code"] = 400
        u.RESPONSE["message"] = f"Invalid request: {str(e)}"
        return jsonify(u.RESPONSE), 400

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + "/add"

    # Effettua la richiesta POST al servizio remoto
    response = requests.post(url,
                             verify=False,
                             json=data,
                             headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha added successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per aggiornare un gacha
@app.route('/gacha/update/<int:gacha_id>', methods=['PUT'])
def update_gacha(gacha_id):
    u.reset_response()

    # Recupera i dati JSON dalla richiesta
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Missing or invalid JSON payload")
    except Exception as e:
        u.RESPONSE["code"] = 400
        u.RESPONSE["message"] = f"Invalid request: {str(e)}"
        return jsonify(u.RESPONSE), 400

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + f"/update/{gacha_id}"

    # Effettua la richiesta PUT al servizio remoto
    response = requests.put(url,
                            verify=False,
                            json=data,
                            headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha updated successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per eliminare un gacha
@app.route('/gacha/delete/<int:gacha_id>', methods=['DELETE'])
def delete_gacha(gacha_id):
    u.reset_response()

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + f"/delete/{gacha_id}"

    # Effettua la richiesta DELETE al servizio remoto
    response = requests.delete(url, verify=False)

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha deleted successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per ottenere un singolo gacha
@app.route('/gacha/get/<int:gacha_id>', methods=['GET'])
def get_gacha(gacha_id):
    u.reset_response()
    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + f"/get/{gacha_id}"
    # Effettua la richiesta GET al servizio remoto
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code
    gacha = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gacha
    u.RESPONSE["message"] = "Gacha retrieved successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per ottenere un singolo gacha per nome
@app.route('/gacha/getName/<string:gacha_name>', methods=['GET'])
def get_gacha_by_name(gacha_name):
    u.reset_response()
    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + f"/getName/{gacha_name}"
    # Effettua la richiesta GET al servizio remoto
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    gacha = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gacha
    u.RESPONSE["message"] = "Gacha retrieved successfully!"
    return u.send_response()


# Endpoint per ottenere tutti i gachas
@app.route('/gacha/get', methods=['GET'])
def get_all_gachas():
    u.reset_response()

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + "/get"

    # Effettua la richiesta GET al servizio remoto
    response = requests.get(url, verify=False)

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code

    gachas = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gachas
    u.RESPONSE["message"] = "All gachas retrieved successfully!"
    return jsonify(u.RESPONSE)


@app.route('/gacha/mygacha/<int:gacha_id>', methods=['GET'])
def get_mygacha(gacha_id):
    u.reset_response()

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + f"/mygacha/{gacha_id}"
    # Effettua la richiesta GET al servizio remoto
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code
    gachas = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gachas
    u.RESPONSE["message"] = "Gacha retrieved successfully!"
    return jsonify(u.RESPONSE)


@app.route('/gacha/mygacha', methods=['GET'])
def get_mygachaAll():
    u.reset_response()

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + f"/mygacha"
    # Effettua la richiesta GET al servizio remoto
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code
    gachas = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gachas
    u.RESPONSE["message"] = "Gacha retrieved successfully!"
    return jsonify(u.RESPONSE)


# INIZIO ENDPOINT PER IL MARKET-SERVICE ==>
@app.route('/auction')
def get_all_auctions():
    u.reset_response()

    enc_token = request.headers.get("token")
    if not u.check_token(enc_token):
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

    enc_token = request.headers.get("token")
    if not u.check_token(enc_token):
        return u.send_response()

    user_owner = request.get_json().get('user_owner')
    gacha_id = request.get_json().get('gacha_id')
    starting_price = request.get_json().get('starting_price')
    end_date = request.get_json().get('end_date')

    path = u.MARKET_SERVICE_URL + "/new_auction"
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

    enc_token = request.headers.get("token")
    if not u.check_token(enc_token):
        return u.send_response()

    token = u.validate_token(enc_token)

    email = token.get("sub")
    bid = request.get_json().get("bid")

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
        return u.send_response()


@app.route('/my_transaction_history', methods=['GET'])
def my_transaction_history():
    u.reset_response()

    enc_token = request.headers.get("token")
    if not u.check_token(enc_token):
        return u.send_response()

    token = u.validate_token(enc_token)
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