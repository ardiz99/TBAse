from flask import Flask, jsonify, request
from authlib.jose import JsonWebToken, JWTClaims, JoseError
import requests
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

import utils as u

# from src import utils as u


app = Flask(__name__)

# Configure JWT with Authlib
jwt = JsonWebToken(['HS256'])
SECRET_KEY = "your-secret-key"  # This should be kept secure

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

    try:
        response = requests.get('https://db-manager:8005/login',
                                verify=False,
                                params={"Email": email})  # effettuiamo un controllo preliminare sulla presenza della
        # email
        if response.status_code == 200:  # se l'email è presente nel db possiamo procedere con l'encrypt della
            # password ricevuta dall'utente
            stored_encrypted_password = response.json().get("Password")
            encrypted_password = encrypt_password(password)
            # Confronta le password
            if stored_encrypted_password == encrypted_password:
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid password credentials"}), 400
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


# User registration route
@app.route('/register', methods=['POST'])
def register():
    # prelevo le informazioni da inserire
    data = request.get_json()
    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    currencyAmount = data.get('CurrencyAmount')

    # inserisco i campi appena presi nelvettore di sanificazione
    # fields_to_process = [firstname, lastname, email, password, currencyAmount]
    # processed_fields = process_fields(fields_to_process)
    #
    # # prelevo i campi sanificati
    # firstname = processed_fields[0]
    # lastname = processed_fields[1]
    # email = processed_fields[2]
    # password = processed_fields[3]
    # currencyAmount = processed_fields[4]

    # pre la registrazione sono richiesti tutti i campi
    if not email or not password or not firstname or not lastname or not currencyAmount:
        return jsonify({"error": "Missing fields"}), 400
    encrypted_password = encrypt_password(password)

    try:
        response = requests.post('https://db-manager:8005/register',
                                 verify=False,
                                 json={"FirstName": firstname, "LastName": lastname, "Email": email,
                                       "Password": encrypted_password, "CurrencyAmount": currencyAmount})
        if response.status_code == 200:  # dal da-manager abbiamo in riscontro positivo
            # LASCIARE QUESTA PARTE PERCHE' CI SERVIRà PER LA PARTE DI AUTENTICAZIONE/AUTORIZZAZIONE: TO DO
            # Crea un token JWT per l'utente autenticato
            # header = {'alg': 'HS256'}
            # payload = {'sub': username}
            # token = jwt.encode(header, payload, SECRET_KEY)
            # return jsonify({"access_token": token.decode('utf-8')}), 200
            return jsonify("Registrazione avvenuta con successo!"), 200
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


@app.route('/update_user', methods=['PUT'])
def update_user():
    # prelevo le informazioni richieste dall'utente da aggiornare

    data = request.get_json()
    userid = ""
    firstname = ""
    lastname = ""
    email = ""
    password = ""
    currencyAmount = ""

    userid = data.get('UserId')
    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    currencyAmount = data.get('CurrencyAmount')

    # inserisco i campi appena presi nelvettore di sanificazione
    # fields_to_process = [userid, firstname, lastname, email, password, currencyAmount]
    # processed_fields = process_fields(fields_to_process)
    #
    # # prelevo i campi sanificati
    # userid = processed_fields[0]
    # firstname = processed_fields[1]
    # lastname = processed_fields[2]
    # email = processed_fields[3]
    # password = processed_fields[4]
    # currencyAmount = processed_fields[5]

    if password:
        encrypted_password = encrypt_password(password)
    if not email or not password or not firstname or not lastname or not currencyAmount:
        return jsonify({"error=": "Missing fields"}), 400

    try:
        response = requests.put('https://db-manager:8005/update_user',
                                verify=False,
                                params={"UserId": userid, "FirstName": firstname, "LastName": lastname, "Email": email,
                                        "Password": encrypted_password, "CurrencyAmount": currencyAmount})
        if response.status_code == 200:
            return jsonify("Aggiornamento avvenuto con successo"), 200
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


# Admin check all users accounts/profiles
@app.route('/check_users_profile', methods=['GET'])
def check_users_profile():
    # da effettuare il controllo sul JWT TOKEN
    try:
        response = requests.get('https://db-manager:8005/check_users_profile',
                                verify=False)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        elif response.status_code == 400:
            return jsonify({"Generic error"}), 400
        else:
            return jsonify({"error": "server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


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
            stored_encrypted_password = response.json().get("Password")
            encrypted_password = encrypt_password(password)
            # Confronta le password
            if stored_encrypted_password == encrypted_password:
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid password credentials"}), 400
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


# User delete route
@app.route('/delete_user', methods=['GET'])
def delete_user():
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
        response = requests.get('https://db-manager:8005/delete_user',
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


# User delete route
@app.route('/delete_admin', methods=['GET'])
def delete_admin():
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


def process_fields(fields):
    """
    Itera sui campi forniti e restituisce una lista con i campi elaborati.
    """
    results = []
    for field in fields:
        u.reset_response()
        if field:
            # Applica la funzione di sanitizzazione
            sanitize_username(field)
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


# Protected endpoint example
@app.route('/protected', methods=['GET'])
def protected():
    token = requests.headers.get('Authorization').split()[1]
    try:
        claims = jwt.decode(token, SECRET_KEY)
        return jsonify(message="Access granted", user=claims['sub']), 200
    except JoseError:
        return jsonify(error="Invalid or expired token"), 401


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8001)
