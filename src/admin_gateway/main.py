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
                            json={'search_email':search_email,
                                   'FirstName': first_name,
                                   'LastName': last_name,
                                   'Email': email,
                                   'Password': password,
                                   'CurrencyAmount': amount},
                            headers={'Authorization': auth_header})
    return jsonify(response.json())




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



@app.route('/login_admin', methods=['GET'])
def login_admin():
    u.reset_response()

    
    email = request.args.get('Email')
    password = request.args.get('Password')
    response = requests.get('https://auth-service:8001/login_admin',
                            verify=False,
                            params={'Email': email, 'Password': password})
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=u.FLASK_DEBUG)