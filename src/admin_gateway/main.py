from flask import Flask, jsonify, request
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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
        return u.send_response()

    path = u.MARKET_SERVICE_URL + f"/auction/{transaction_id}"
    response = requests.get(path,
                            verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/close_auction/<int:transaction_id>', methods=['PUT'])
def close_auction(transaction_id):
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
        return u.send_response()

    path = u.MARKET_SERVICE_URL + f"/close_auction/{transaction_id}"
    response = requests.put(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/register_admin', methods=['POST'])
def register_admin():
    u.reset_response()

    data = request.get_json()
    first_name = data.get('FirstName')
    last_name = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    response = requests.post('https://auth-service:8001/register_admin',
                             verify=False,
                             json={'FirstName': first_name,
                                   'LastName': last_name,
                                   'Email': email,
                                   'Password': password})
    return jsonify(response.json())


@app.route('/delete_admin', methods=['DELETE'])
def delete_admin():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
        return u.send_response()

    # email = request.args.get('Email') params={'Email': email, 'Password': password}
    # password = request.args.get('Password')
    response = requests.delete('https://auth-service:8001/delete_admin',
                               verify=False,
                               headers={'Authorization': auth_header})
    return jsonify(response.json())


@app.route('/login_admin', methods=['POST'])
def login_admin():
    u.reset_response()

    email = request.get_json().get('Email')
    password = request.get_json().get('Password')
    response = requests.post('https://auth-service:8001/login_admin',
                             verify=False,
                             json={'Email': email, 'Password': password})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    return jsonify(response.json()), 200


@app.route('/check_users_profile', methods=['GET'])
def check_users_profile():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
        return u.send_response()
    response = requests.get('https://auth-service:8001/check_users_profile',
                            verify=False,
                            headers={'Authorization': auth_header})
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


@app.route('/update_admin', methods=['PUT'])
def update_admin():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
        return u.send_response()

    data = request.get_json()
    first_name = data.get('FirstName')
    last_name = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    response = requests.put('https://auth-service:8001/update_admin',
                            verify=False,
                            json={'FirstName': first_name,
                                  'LastName': last_name,
                                  'Email': email,
                                  'Password': password
                                  },
                            headers={'Authorization': auth_header})
    return jsonify(response.json())


@app.route('/update_specific_user', methods=['PUT'])
def update_specific_user():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
        return u.send_response()

    data = request.get_json()
    search_email = data.get('search_email')
    first_name = data.get('FirstName')
    last_name = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    amount = data.get('CurrencyAmount')
    response = requests.put('https://auth-service:8001/update_specific_user',
                            verify=False,
                            json={'search_email': search_email,
                                  'FirstName': first_name,
                                  'LastName': last_name,
                                  'Email': email,
                                  'Password': password,
                                  'CurrencyAmount': amount},
                            headers={'Authorization': auth_header})
    return jsonify(response.json())


@app.route('/auction/history', methods=['GET'])
def get_old_transaction():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
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
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
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


@app.route('/specific_history', methods=['GET'])
def specific_history():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
        return u.send_response()

    response = requests.get('http://auth-service:8004/specific_history')
    return jsonify(response.json())


@app.route('/specific_market_history', methods=['GET'])
def specific_market_history():
    u.reset_response()
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized()
        return u.send_response()
    acces_token = auth_header.removeprefix("Bearer ").strip()
    token = u.validate_token(acces_token)

    role = token.get("role")
    if role != "admin":
        u.forbidden()
        return u.send_response()

    response = requests.get('http://auth-service:8004/specific_market_history')
    return jsonify(response.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=u.FLASK_DEBUG)
