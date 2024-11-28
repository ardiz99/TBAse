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
    path = u.CURRENCY_SERVICE_URL + "/roll_info"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    data = response.json().get("data")
    url = data["Link"]
    path = u.CURRENCY_SERVICE_URL + "/roll_img"
    response = requests.get(path,
                            verify=False,
                            params={"url": url})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    return Response(
        response.content,
        content_type=response.headers['Content-Type'],
        status=response.status_code
    )


@app.route('/buy_currency', methods=['PUT'])
def buy_currency():
    data = request.get_json()
    quantity = data.get('quantity')
    if quantity is None:
        u.bad_request()
        return jsonify(u.RESPONSE)

    path = u.CURRENCY_SERVICE_URL + "/buy_currency"
    response = requests.put(path,
                            verify=False,
                            json={"quantity": quantity})
    return jsonify(response.json())


# INIZIO ENDPOINT DEL GACHASERVICE_URL ==>

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
    url = u.GACHA_SERVICE_URL + "gacha/add"

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
    url = u.GACHA_SERVICE_URL + f"gacha/update/{gacha_id}"

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
    url = u.GACHA_SERVICE_URL + f"gacha/delete/{gacha_id}"

    # Effettua la richiesta DELETE al servizio remoto
    response = requests.delete(url)

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha deleted successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per ottenere un singolo gacha
@app.route('/gacha/<int:gacha_id>', methods=['GET'])
def get_gacha(gacha_id):
    u.reset_response()

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + f"/gacha/{gacha_id}"

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


# Endpoint per ottenere tutti i gachas
@app.route('/gacha', methods=['GET'])
def get_all_gachas():
    u.reset_response()

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + "/gacha"

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


@app.route('/login', methods=['GET'])
def login():
    email = request.args.get('Email')
    password = request.args.get('Password')
    
    response = requests.get('https://auth-service:8001/login',
                            verify=False,
                            params={'Email': email, 'Password': password})
    return jsonify(response.json())



@app.route('/login_admin', methods=['GET'])
def login_admin():
    email = request.args.get('Email')
    password = request.args.get('Password')
    response = requests.get('https://auth-service:8001/login_admin',
                            verify=False,
                            params={'Email': email, 'Password': password})
    return jsonify(response.json())


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


@app.route('/register_admin', methods=['POST'])
def register_admin():
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


@app.route('/delete_user', methods=['GET'])
def delete_user():
    email = request.args.get('Email')
    password = request.args.get('Password')
    response = requests.get('https://auth-service:8001/delete_user',
                            verify=False,
                            params={'Email': email, 'Password': password})
    return jsonify(response.json())


@app.route('/delete_admin', methods=['GET'])
def delete_admin():
    email = request.args.get('Email')
    password = request.args.get('Password')
    response = requests.get('https://auth-service:8001/delete_admin',
                            verify=False,
                            params={'Email': email, 'Password': password})
    return jsonify(response.json())


@app.route('/update_user', methods=['PUT'])
def update_user():
    #Authorization=request.args.get('Authorization')
    response = requests.put('https://auth-service:8001/update_user',
                            verify=False)
    return jsonify(response.json())


@app.route('/update_specific_user', methods=['PUT'])
def update_specific_user():
    email = request.args.get('Email')
    password = request.args.get('Password')
    first_name = request.args.get('FirstName')
    last_name = request.args.get('LastName')
    amount = request.args.get('CurrencyAmount')
    #Authorization=request.args.get('Authorization')
    response = requests.put('https://auth-service:8001/update_specific_user',
                            verify=False,
                            json={'FirstName': first_name,
                                   'LastName': last_name,
                                   'Email': email,
                                   'Password': password,
                                   'CurrencyAmount': amount})
    return jsonify(response.json())


@app.route('/check_users_profile', methods=['GET'])
def check_users_profile():
    response = requests.get('https://auth-service:8001/check_users_profile',
                            verify=False)
    return jsonify(response.json())





@app.route('/logout', methods=['GET'])
def logout():
    response = requests.get('https://auth-service:8001/logout',
                            verify=False)
    return jsonify(response.json())


@app.route('/see_auction_market', methods=['GET'])
def see_auction_market():
    response = requests.get('https://auth-service:8003/see_auction_market',
                            verify=False)
    return jsonify(response.json())


@app.route('/see_history_auction_market', methods=['GET'])
def see_history_auction_market():
    response = requests.get('https://auth-service:8003/see_history_auction_market',
                            verify=False)
    return jsonify(response.json())


@app.route('/see_transaction_history', methods=['GET'])
def see_transaction_history():
    email = request.args.get('Email')
    response = requests.get('https://auth-service:8003/see_transaction_history',verify=False,params={'Email': email})
    return jsonify(response.json())


@app.route('/see_specific_auction', methods=['GET'])
def see_specific_auction():
    Transaction = request.args.get('Transaction')
    response = requests.get('https://auth-service:8003/see_specific_auction',verify=False,params={'Transaction': Transaction})
    return jsonify(response.json())



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=u.FLASK_DEBUG)
