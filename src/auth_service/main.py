from flask import Flask, jsonify, request
import bcrypt
import requests
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

import utils as u

# from src import utils as u


app = Flask(__name__)


# Helper: Hash password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode(), salt.decode()


# Helper: Verify password
# def verify_password(password, stored_hash, salt):
#     return bcrypt.hashpw(password.encode(), salt.encode()).decode() == stored_hash

# Recupera la chiave e l'IV dai parametri di configurazione
KEY = bytes.fromhex(os.getenv("OPENSSL_KEY", "5A8D67E1C8C3F2F01F61F214D3B69FC8AE02C65B47C703914F7B6E3125678A6F"))
IV = bytes.fromhex(os.getenv("OPENSSL_IV", "1234567890ABCDEF1234567890ABCDEF"))


def encrypt_password(password):
    """Crittografa la password utilizzando AES."""
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding della password per AES (blocco di 16 byte)
    padded_password = password.ljust(16, ' ')
    encrypted = encryptor.update(padded_password.encode()) + encryptor.finalize()

    # Converti in base64 per lo storage
    return base64.b64encode(encrypted).decode()


def decrypt_password(encrypted_password):
    """Decrittografa la password crittografata."""
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decodifica base64 e decrittografa
    encrypted_data = base64.b64decode(encrypted_password)
    decrypted = decryptor.update(encrypted_data) + decryptor.finalize()

    # Rimuove eventuale padding
    return decrypted.decode().strip()


# User login route
@app.route('/login', methods=['GET'])
def login():
    email = request.args.get('Email')
    password = request.args.get('Password')

    path = u.DB_MANAGER_URL + "/login"
    response = requests.get(path,
                            verify=False,
                            params={"Email": email})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    stored_encrypted_password = response.json().get("data").get("Password")
    encrypted_password = encrypt_password(password)

    if stored_encrypted_password != encrypted_password:
        u.unauthorized()
        return u.send_response()

    token = u.generate_token(email, "user")
    u.RESPONSE["data"] = token
    u.RESPONSE["message"] = "Login successful"
    return u.send_response()


# admin login route
@app.route('/login_admin', methods=['GET'])
def login_admin():
    # prelevo le informazioni da inserire
    email = request.args.get('Email')
    password = request.args.get('Password')

    # inserisco i campi appena presi nelvettore di sanificazione
    # fields_to_process = [email, password]
    # processed_fields = process_fields(fields_to_process)
    #
    # # prelevo i campi sanificati
    # email = processed_fields[0]
    # password = processed_fields[1]

    if not email or not password:
        return jsonify(error="Missing email or password"), 400
    try:

        response = requests.get('https://db-manager:8005/login_admin',
                                verify=False,
                                params={"Email": email})
        if response.status_code == 200:
            tmp = response.json().get("data")
            stored_encrypted_password = tmp["Password"]
            encrypted_password = encrypt_password(password)
            # Confronta le password
            if stored_encrypted_password == encrypted_password:
                token = u.generate_token(email, "admin")
                u.set_auth_token(token)
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid password credentials"}), 400
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


# per gli user e admin
@app.route('/logout', methods=['GET'])
def logout():
    # Recupera il token dall'intestazione Authorization
    try:
        auth_token = u.get_auth_token()
    except Exception as e:
        return jsonify({"error": "no token found. PLs log in first"}), 400
    if u.BLACKLIST(auth_token):
        return jsonify({"error": "Logout alredy done"}), 400

    if not auth_token:
        return jsonify({"error": "Authorization header is required"}), 400

    try:
        token = u.validate_token(auth_token)  # rigenera i campi originali dal token cifrato
        if "error" in token:
            return jsonify({"error": token["error"], "token": token, "auth_token": auth_token}), 400

        # Aggiungi il token alla blacklist
        u.BLACKLIST.append(token)
        return jsonify({"message": "Logout successful"}), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}", "token": token, "auth_token": auth_token}), 500


# User registration route
@app.route('/register', methods=['POST'])
def register():
    # prelevo le informazioni da inserire
    firstname = request.get_json().get('FirstName')
    lastname = request.get_json().get('LastName')
    email = request.get_json().get('Email')
    password = request.get_json().get('Password')
    currencyAmount = request.get_json().get('CurrencyAmount')

    # pre la registrazione sono richiesti tutti i campi
    if not email or not password or not firstname or not lastname or not currencyAmount:
        u.bad_request()
        return u.send_response()

    encrypted_password = encrypt_password(password)

    path = u.DB_MANAGER_URL + '/register'
    response = requests.post(path,
                             verify=False,
                             json={"FirstName": firstname, "LastName": lastname, "Email": email,
                                   "Password": encrypted_password, "CurrencyAmount": currencyAmount})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    token = u.generate_token(email, "user")

    u.RESPONSE["data"] = token
    u.RESPONSE["message"] = "Subscription successful"
    return u.send_response()


# User registration route
@app.route('/register_admin', methods=['POST'])
def register_admin():
    # prelevo le informazioni da inserire
    data = request.get_json()
    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')

    # inserisco i campi appena presi nelvettore di sanificazione
    # fields_to_process = [firstname, lastname, email, password]
    # processed_fields = process_fields(fields_to_process)
    #
    # # prelevo i campi sanificati
    # firstname = processed_fields[0]
    # lastname = processed_fields[1]
    # email = processed_fields[2]
    # password = processed_fields[3]

    # pre la registrazione sono richiesti tutti i campi
    if not email or not password or not firstname or not lastname:
        return jsonify({"error": "Missing fields"}), 400
    encrypted_password = encrypt_password(password)

    try:
        response = requests.post('https://db-manager:8005/register_admin',
                                 verify=False,
                                 json={"FirstName": firstname, "LastName": lastname, "Email": email,
                                       "Password": encrypted_password})
        if response.status_code == 200:  # dal da-manager abbiamo in riscontro positivo

            token = u.generate_token(email, "admin")
            u.set_auth_token(token)
            return jsonify({"ok": "Registrazione avvenuta con successo!", "encrypted_password": encrypted_password,
                            "password": password}), 200
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


@app.route('/update_user', methods=['PUT'])
def update_user():
    # Verifica l'intestazione Authorization
    try:
        token = u.get_auth_token()
    except Exception as e:
        return jsonify({"error": "no token found. PLs log in first"}), 400
    if not token:
        return jsonify({"error": "Authorization header is required"}), 401

    # token = auth_header.split()[1]
    # token_data = u.validate_token(token)
    # if "error" in token_data:
    #     return jsonify({"error": token_data["error"]}), 401

    # prelevo le informazioni richieste dall'utente da aggiornare
    token_data = u.validate_token(token)  # rigenera i campi originali dal token cifrato
    get_role = token_data.get('sub')  # restituisce il ruolo corretto
    data = request.get_json()
    firstname = ""
    lastname = ""
    email = ""
    password = ""
    currencyAmount = ""

    if data.get('FirstName'):
        firstname = data.get('FirstName')
    if data.get('LastName'):
        lastname = data.get('LastName')
    if get_role:
        email = get_role
    if data.get('Password'):
        password = data.get('Password')
    if data.get('CurrencyAmount'):
        currencyAmount = data.get('CurrencyAmount')

    # inserisco i campi appena presi nelvettore di sanificazione
    # fields_to_process = [firstname, lastname, password, currencyAmount]
    # processed_fields = process_fields(fields_to_process)
    #
    # # prelevo i campi sanificati
    # firstname = processed_fields[0]
    # lastname = processed_fields[1]
    # password = processed_fields[2]
    # currencyAmount = processed_fields[3]

    if password:
        encrypted_password = encrypt_password(password)
    if not email or not password or not firstname or not lastname or not currencyAmount:
        return jsonify({"error=": "Missing fields"}), 400

    try:

        response = requests.put('https://db-manager:8005/update_user',
                                verify=False,
                                params={"FirstName": firstname, "LastName": lastname, "Email": email,
                                        "Password": encrypted_password, "CurrencyAmount": currencyAmount})
        if response.status_code == 200:
            return jsonify("Aggiornamento avvenuto con successo"), 200
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


# only for admin
@app.route('/update_specific_user', methods=['PUT'])
def update_specific_user():
    try:
        auth_token = u.get_auth_token()
    except Exception as e:
        return jsonify({"error": "no token found. PLs log in first"}), 400

    token_data = u.validate_token(auth_token)  # rigenera i campi originali dal token cifrato
    role = token_data.get('role')  # restituisce il ruolo corretto
    if not auth_token:
        return jsonify({"error": "Authorization header is required"}), 401

    if role == "admin":

        data = request.get_json()
        firstname = ""
        lastname = ""
        email = ""
        password = ""
        currencyAmount = ""

        if data.get('FirstName'):
            firstname = data.get('FirstName')
        if data.get('LastName'):
            lastname = data.get('LastName')
        if token_data.get('sub'):
            email = token_data.get('sub')
        if data.get('Password'):
            password = data.get('Password')
        if data.get('CurrencyAmount'):
            currencyAmount = data.get('CurrencyAmount')

        # inserisco i campi appena presi nelvettore di sanificazione
        # fields_to_process = [firstname, lastname, password, currencyAmount]
        # processed_fields = process_fields(fields_to_process)
        #
        # # prelevo i campi sanificati
        # firstname = processed_fields[0]
        # lastname = processed_fields[1]
        # password = processed_fields[2]
        # currencyAmount = processed_fields[3]

        if password:
            encrypted_password = encrypt_password(password)
        if not email or not password or not firstname or not lastname or not currencyAmount:
            return jsonify({"error=": "Missing fields"}), 400

        try:

            response = requests.put('https://db-manager:8005/update_specific_user',
                                    verify=False,
                                    params={"FirstName": firstname, "LastName": lastname, "Email": email,
                                            "Password": encrypted_password, "CurrencyAmount": currencyAmount})
            if response.status_code == 200:
                return jsonify("Aggiornamento avvenuto con successo"), 200
            elif response.status_code == 400:
                return jsonify({"error": "Invalid credentials"}), 400
            else:
                return jsonify({"error": "Internal server error", "response": response}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500

    else:
        return jsonify({"error=": "authorization required"}), 400


# Admin check all users accounts/profiles
@app.route('/check_users_profile', methods=['GET'])
def check_users_profile():
    # Verifica l'intestazione Authorization
    try:
        auth_token = u.get_auth_token()
    except Exception as e:
        return jsonify({"no token found. PLs log in first": str(e), "auth_token": str(auth_token)}), 400

    token_data = u.validate_token(auth_token)  # rigenera i campi originali dal token cifrato
    if not auth_token:
        return jsonify({"error": "Authorization header is required"}), 400
    # token_data = u.validate_token(auth_token)#rigenera i campi originali dal token cifrato
    get_role = token_data.get('role')  # restituisce il ruolo corretto

    if get_role == "admin":
        try:
            response = requests.get('https://db-manager:8005/check_users_profile',
                                    verify=False)
            if response.status_code == 200:
                return jsonify(response.json()), 200
            elif response.status_code == 400:
                return jsonify({"Generic error"}), 400
            else:
                return jsonify({"error": "server error", "response": response}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500
    else:
        return jsonify({"Insufficent permission"}), 400
    # da effettuare il controllo sul JWT TOKEN


# User delete route
@app.route('/delete_user', methods=['GET'])
def delete_user():
    # inserire il get param
    try:
        auth_token = u.get_auth_token()
    except Exception as e:
        return jsonify({"error": "no token found. PLs log in first"}), 400

    token_data = u.validate_token(auth_token)  # rigenera i campi originali dal token cifrato

    if not auth_token:
        return jsonify({"error": "Authorization header is required"}), 401

    email = token_data.get('sub')  # restituisce il ruolo corretto
    # valid_token=u.validate_token(token)

    password = request.args.get('Password')
    # inserisco i campi appena presi nelvettore di sanificazione
    # fields_to_process = [email, password]
    # processed_fields = process_fields(fields_to_process)
    #
    # # prelevo i campi sanificati
    # email = processed_fields[0]
    # password = processed_fields[1]
    if not email or not password:
        return jsonify(error="Missing email or password"), 400
    try:
        encrypted_password = encrypt_password(password)
        response = requests.get('https://db-manager:8005/delete_user',
                                verify=False,
                                params={"Email": email, "Password": encrypted_password})
        if response.status_code == 200:
            return jsonify("delete done!"), 200
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error", "response": response}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


# User delete route
@app.route('/delete_admin', methods=['GET'])
def delete_admin():
    try:
        auth_token = u.get_auth_token()
    except Exception as e:
        return jsonify({"error": "no token found. PLs log in first"}), 400

    token_data = u.validate_token(auth_token)  # rigenera i campi originali dal token cifrato

    if not auth_token:
        return jsonify({"error": "Authorization header is required"}), 401

    get_role = token_data.get('role')  # restituisce il ruolo corretto

    if get_role == "admin":
        # inserire il get param
        email = request.args.get('Email')
        password = request.args.get('Password')
        # inserisco i campi appena presi nelvettore di sanificazione
        # fields_to_process = [email, password]
        # processed_fields = process_fields(fields_to_process)
        #
        # # prelevo i campi sanificati
        # email = processed_fields[0]
        # password = processed_fields[1]
        if not email or not password:
            return jsonify(error="Missing email or password"), 400
        try:
            encrypted_password = encrypt_password(password)
            response = requests.get('https://db-manager:8005/delete_admin',
                                    verify=False,
                                    params={"Email": email, "Password": encrypted_password})
            if response.status_code == 200:
                return jsonify("delete done!"), 200
            elif response.status_code == 400:
                return jsonify({"error": "Invalid credentials"}), 400
            else:
                return jsonify({"error": "Internal server error"}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500

    else:
        return jsonify({"error": "Insufficent authorization"}), 400


def process_fields(fields):
    """
    Itera sui campi forniti e restituisce una lista con i campi elaborati.
    """
    results = []
    for field in fields:
        u.reset_response()
        if field:
            # Applica la funzione di sanitizzazione
            # sanitize_username(field)
            # controlla la risposta ricevuta dalla funzione sanitize_username e determina se l'input è valido o meno
            if u.RESPONSE["code"] == 400:
                results.append('')
            else:
                tmp = u.RESPONSE["data"].strip("[]")
                results.append(tmp)
        else:
            results.append('')
    return results


def sanitize_username(input_str):
    # Only allows alphanumeric characters, underscores,space,underscore dot and snail
    sanitized_str = re.sub('[a-zA-Z0-9_@ .]*g', '', input_str)
    if input_str != sanitized_str:
        u.RESPONSE["code"] = 400
        u.RESPONSE["data"] = sanitized_str
        return u.RESPONSE
    else:
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = sanitized_str
        return u.RESPONSE


@app.route('/protected', methods=['GET'])
def protected():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Authorization header is required"}), 400

    token = auth_header.split()[1]
    token_data = u.validate_token(token)

    if "error" in token_data:
        return jsonify({"error": token_data["error"]}), 400

    return jsonify({"message": "Access granted", "data": token_data}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8001)
