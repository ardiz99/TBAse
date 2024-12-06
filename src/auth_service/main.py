from flask import Flask, jsonify, request
import bcrypt
import requests
import re
import base64
import utils as u

# from src import utils as u


app = Flask(__name__)


def hash_password(password):
    """Genera un hash e un salt per una password."""
    # Genera il salt
    salt = bcrypt.gensalt()
    # Genera l'hash della password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Codifica il salt e l'hash in Base64
    encoded_salt = base64.b64encode(salt).decode('utf-8')
    encoded_hash = base64.b64encode(hashed_password).decode('utf-8')
    return encoded_hash, encoded_salt


def verify_password(password, encoded_hash, encoded_salt):
    """Verifica una password con l'hash e il salt."""
    # Decodifica il salt e l'hash da Base64
    salt_bytes = base64.b64decode(encoded_salt.encode('utf-8'))
    hash_bytes = base64.b64decode(encoded_hash.encode('utf-8'))
    # Genera un nuovo hash con la password fornita e il salt decodificato
    new_hash = bcrypt.hashpw(password.encode('utf-8'), salt_bytes)
    # Confronta gli hash
    return new_hash == hash_bytes


# User login route
@app.route('/login', methods=['GET'])
def login():
    # prelevo le informazioni da inserire
    email = request.args.get('Email')
    password = request.args.get('Password')

    # # inserisco i campi appena presi nelvettore di sanificazione
    fields_to_process = [email, password]
    processed_fields = process_fields(fields_to_process)

    # prelevo i campi sanificati
    email = processed_fields[0]
    password = processed_fields[1]

    response = requests.get('https://db-manager:8005/login',
                            verify=False,
                            params={
                                "Email": email})  # effettuiamo un controllo preliminare sulla presenza della email

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    stored_hash = response.json().get("data")[0].get("Password")
    salt = response.json().get("data")[0].get("Salt")
    if verify_password(password, stored_hash, salt):
       # Generazione dei token
        tokens = u.generate_tokens(email, "user")

        # Imposta il token di accesso
        u.set_auth_token(tokens.get("access_token"))

        # Invio della risposta
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = {
            "id_token": tokens.get("id_token"),
            "access_token": tokens.get("access_token")
        }
        u.RESPONSE["message"] = "Login successful"
        return u.send_response()
    else:
        u.generic_error()
        return u.send_response("verify_password failed")


# admin login route
@app.route('/login_admin', methods=['GET'])
def login_admin():
    # prelevo le informazioni da inserire
    email = request.args.get('Email')
    password = request.args.get('Password')

    # inserisco i campi appena presi nelvettore di sanificazione
    fields_to_process = [email, password]
    processed_fields = process_fields(fields_to_process)

    # prelevo i campi sanificati
    email = processed_fields[0]
    password = processed_fields[1]

    if not email or not password:
        u.bad_request()
        return u.send_response()

    response = requests.get('https://db-manager:8005/login_admin',
                            verify=False,
                            params={"Email": email})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    stored_hash = response.json().get("data")[0].get("Password")
    salt = response.json().get("data")[0].get("Salt")
    if verify_password(password, stored_hash, salt):
       # Generazione dei token
        tokens = u.generate_tokens(email, "admin")

        # Imposta il token di accesso
        u.set_auth_token(tokens.get("access_token"))

        # Invio della risposta
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = {
            "id_token": tokens.get("id_token"),
            "access_token": tokens.get("access_token")
        }
        u.RESPONSE["message"] = "Login successful"
        return u.send_response()
    else:
        u.generic_error()
        return u.send_response("verify_password failed")
    


# per gli user e admin
@app.route('/logout', methods=['GET'])
def logout():
    u.reset_response()
    # Recupera il token dall'intestazione Authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header in u.BLACKLIST:
        u.unauthorized()
        return u.send_response("no token found. PLs log in first")
    acces_token = auth_header.removeprefix("Bearer ").strip()
    try:
        u.BLACKLIST.append(acces_token)
        u.set_auth_token(None)
        return u.send_response("Logout successful")

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# User registration route
@app.route('/register', methods=['POST'])
def register():
    u.reset_response()

    # prelevo le informazioni da inserire
    data = request.get_json()
    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    currencyAmount = data.get('CurrencyAmount')

    # inserisco i campi appena presi nelvettore di sanificazione
    fields_to_process = [firstname, lastname, email, password, str(currencyAmount)]
    processed_fields = process_fields(fields_to_process)

    # prelevo i campi sanificati
    firstname = processed_fields[0]
    lastname = processed_fields[1]
    email = processed_fields[2]
    password = processed_fields[3]
    currencyAmount = int(processed_fields[4])

    # pre la registrazione sono richiesti tutti i campi
    if not email or not password or not firstname or not lastname or not currencyAmount:
        return jsonify({"error": "Missing fields"}), 400
    hashed_password, salt = hash_password(password)
    response = requests.post('https://db-manager:8005/register',
                             verify=False,
                             json={"FirstName": firstname, "LastName": lastname, "Email": email,
                                   "Password": hashed_password, "CurrencyAmount": currencyAmount, "Salt": salt})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        u.set_response(response)
        return u.send_response()

    # Generazione dei token
    tokens = u.generate_tokens(email, "user")
    # Imposta il token di accesso
    u.set_auth_token(tokens.get("access_token"))
    # Invio della risposta
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = {
        "id_token": tokens.get("id_token"),
        "access_token": tokens.get("access_token")
    }
    u.RESPONSE["message"] = "Registration successful"
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
    fields_to_process = [firstname, lastname, email, password]
    processed_fields = process_fields(fields_to_process)

    # prelevo i campi sanificati
    firstname = processed_fields[0]
    lastname = processed_fields[1]
    email = processed_fields[2]
    password = processed_fields[3]

    # pre la registrazione sono richiesti tutti i campi
    if not email or not password or not firstname or not lastname:
        return jsonify({"error": "Missing fields"}), 400
    hashed_password, salt = hash_password(password)

    try:
        response = requests.post('https://db-manager:8005/register_admin',
                                 verify=False,
                                 json={"FirstName": firstname,
                                       "LastName": lastname,
                                       "Email": email,
                                       "Password": hashed_password,
                                       "Salt": salt})
        if response.status_code == 200:  # dal da-manager abbiamo in riscontro positivo
            # Generazione dei token
            tokens = u.generate_tokens(email, "admin")
            # Imposta il token di accesso
            u.set_auth_token(tokens.get("access_token"))
            # Invio della risposta
            u.RESPONSE["code"] = 200
            u.RESPONSE["data"] = {
                "id_token": tokens.get("id_token"),
                "access_token": tokens.get("access_token")
            }
            u.RESPONSE["message"] = "Registration successful"
            return u.send_response()
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


@app.route('/update_user', methods=['PUT'])
def update_user():
    check_email = False
    u.reset_response()

    # Estrai l'header di autorizzazione
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    # Rimuovi il prefisso "Bearer"
    try:
        access_token =  auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()
    
    # Valida il token
    token_data = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token_data:
        u.unauthorized(token_data["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()
    email = token_data.get("decoded", {}).get("sub")
    tmp_email = email

    response = requests.get(
        'https://db-manager:8005/check_one_user',
        verify=False,
        params={
            "Email": email
        }
    )
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response

    firstname = response.json().get("data").get("FirstName")
    lastname = response.json().get("data").get("LastName")
    password = response.json().get("data").get("Password")
    Currency = response.json().get("data").get("CurrencyAmount")
    salt = response.json().get("data").get("Salt")

    # Estrai i dati dal corpo della richiesta
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing fields"}), 400

    if data.get('FirstName'):
        firstname = data.get('FirstName')
    if data.get('LastName'):
        lastname = data.get('LastName')
    if data.get('Email'):
        check_email = True
        email = data.get('Email')
    if data.get('Password'):
        tmp_pass = data.get('Password')
        hashed_password, tmp_salt = hash_password(tmp_pass)
        password = hashed_password
        salt = tmp_salt
    if data.get('CurrencyAmount'):
        Currency = data.get('CurrencyAmount')

    # inserisco i campi appena presi nelvettore di sanificazione
    fields_to_process = [firstname, lastname, email, password, str(Currency)]
    processed_fields = process_fields(fields_to_process)

    # prelevo i campi sanificati
    firstname = processed_fields[0]
    lastname = processed_fields[1]
    email = processed_fields[2]
    password = processed_fields[3]
    Currency = processed_fields[4]

    if not email or not any([firstname, lastname, password, Currency, salt]):
        return jsonify({"error": "At least one field is required"}), 400

    # Invio della richiesta al db-manager
    try:
        response = requests.put(
            'https://db-manager:8005/update_user',
            verify=False,
            json={
                "FirstName": firstname,
                "LastName": lastname,
                "Email": email,
                "tmp_email": tmp_email,
                "Password": password,
                "CurrencyAmount": Currency,
                "Salt": salt
            }
        )
        if check_email and response.status_code == 200:
            u.BLACKLIST.append(access_token)
            u.set_auth_token(None)
            return jsonify({"a": "Update done! pls LOG IN now to continue", "b": response.json()}), response.status_code
        if response.status_code == 200:

            return jsonify("Update done! You can continue now"), response.status_code
        else:
            return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


# only for admin
@app.route('/update_specific_user', methods=['PUT'])
def update_specific_user():
    check_email = False
    u.reset_response()

    # Estrai l'header di autorizzazione
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    # Rimuovi il prefisso "Bearer"
    try:
        access_token =  auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()
    
    # Valida il token
    token_data = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token_data:
        u.unauthorized(token_data["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()

    role = token_data.get("decoded", {}).get('role')
    if role != "admin":
        return jsonify({"error": "Unauthorized. Admin role required"}), 400

    # Estrai i dati dal corpo della richiesta
    data = request.get_json()
    if not data:
        u.bad_request()
        return u.send_response()

    tmp_email = data.get('search_email')

    response = requests.get(
        'https://db-manager:8005/check_one_user',
        verify=False,
        params={
            "Email": tmp_email
        }
    )
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    firstname = response.json().get("data").get("FirstName")
    lastname = response.json().get("data").get("LastName")
    password = response.json().get("data").get("Password")
    Currency = response.json().get("data").get("CurrencyAmount")
    salt = response.json().get("data").get("Salt")

    if data.get('FirstName'):
        firstname = data.get('FirstName')
    if data.get('LastName'):
        lastname = data.get('LastName')
    if data.get('Email'):
        check_email = True
        email = data.get('Email')
    if data.get('Password'):
        tmp_pass = data.get('Password')
        hashed_password, tmp_salt = hash_password(tmp_pass)
        password = hashed_password
        salt = tmp_salt
    if data.get('CurrencyAmount'):
        Currency = data.get('CurrencyAmount')

    # inserisco i campi appena presi nelvettore di sanificazione
    fields_to_process = [firstname, lastname, email, password, str(Currency)]
    processed_fields = process_fields(fields_to_process)

    # prelevo i campi sanificati
    firstname = processed_fields[0]
    lastname = processed_fields[1]
    email = processed_fields[2]
    password = processed_fields[3]
    Currency = processed_fields[4]

    if not email or not any([firstname, lastname, password, Currency, salt]):
        return jsonify({"error": "At least one field is required"}), 400

    # Invio della richiesta al db-manager
    try:
        response = requests.put(
            'https://db-manager:8005/update_user',
            verify=False,
            json={
                "FirstName": firstname,
                "LastName": lastname,
                "Email": email,
                "tmp_email": tmp_email,
                "Password": password,
                "CurrencyAmount": Currency,
                "Salt": salt
            }
        )
        if check_email and response.status_code == 200:
            u.BLACKLIST.append(access_token)
            u.set_auth_token(None)
            return jsonify({"a": "Update done! pls LOG IN now to continue", "b": response.json()}), response.status_code
        if response.status_code == 200:

            return jsonify("Update done! You can continue now"), response.status_code
        else:
            return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


# only for admin
@app.route('/update_admin', methods=['PUT'])
def update_admin():
    u.reset_response()

    # Estrai l'header di autorizzazione
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    # Rimuovi il prefisso "Bearer"
    try:
        access_token =  auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()
    
    # Valida il token
    token_data = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token_data:
        u.unauthorized(token_data["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()

    role = token_data.get("decoded", {}).get('role')
    if role != "admin":
        return jsonify({"error": "Unauthorized. Admin role required"}), 400

        # Estrai i dati dal corpo della richiesta
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing fields"}), 400
    check_email = False
    email = token_data.get('sub')

    try:
        response = requests.get(
            'https://db-manager:8005/check_one_admin',
            verify=False,
            params={
                "Email": email
            }
        )
        if response.status_code == 200:
            firstname = response.json().get("data")[0].get("FirstName")
            lastname = response.json().get("data")[0].get("LastName")
            password = response.json().get("data")[0].get("Password")
            salt = response.json().get("data")[0].get("Salt")
        else:
            return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify(response.json()), response.status_code

    tmp_email = email
    if data.get('FirstName'):
        firstname = data.get('FirstName')
    if data.get('LastName'):
        lastname = data.get('LastName')
    if data.get('Email'):
        check_email = True
        email = data.get('Email')
    else:
        email = token_data.get('sub')
    if data.get('Password'):
        tmp_pass = data.get('Password')
        hashed_password, tmp_salt = hash_password(tmp_pass)
        password = hashed_password
        salt = tmp_salt

    # inserisco i campi appena presi nelvettore di sanificazione
    fields_to_process = [firstname, lastname, email, password]
    processed_fields = process_fields(fields_to_process)

    # prelevo i campi sanificati
    firstname = processed_fields[0]
    lastname = processed_fields[1]
    email = processed_fields[2]
    password = processed_fields[3]

    if not email or not any([firstname, lastname, password, salt]):
        return jsonify({"error": "At least one field is required"}), 400

    # Invio della richiesta al db-manager
    try:
        response = requests.put(
            'https://db-manager:8005/update_admin',
            verify=False,
            json={
                "FirstName": firstname,
                "LastName": lastname,
                "Email": email,
                "Password": password,
                "Salt": salt,
                "tmp_email": tmp_email
            }
        )
        if check_email and response.status_code == 200:
            u.BLACKLIST.append(access_token)
            u.set_auth_token(None)
            return jsonify("Update done! pls LOG IN now to continue"), response.status_code
        if response.status_code == 200:
            return jsonify("Update done! You can continue now"), response.status_code
        else:
            return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


# Admin check all users accounts/profiles
@app.route('/check_users_profile', methods=['GET'])
def check_users_profile():
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


@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    u.reset_response()

    # Estrai l'header di autorizzazione
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    # Rimuovi il prefisso "Bearer"
    try:
        access_token =  auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()
    
    # Valida il token
    token_data = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token_data:
        u.unauthorized(token_data["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()

    role = token_data.get("decoded", {}).get('role')
    if role != "user":
        return jsonify({"error": "Unauthorized. Admin role required"}), 400

    email = token_data.get('sub')  # restituisce l'email  corretta
    password = token_data.get('pass')

    # Verifica che i campi richiesti siano presenti
    if not email or not password:
        return jsonify({"error": "Email and Password are required"}), 400
    # check_one_user
    try:
        # Invia una richiesta DELETE al db-manager
        # VERIFICARE PRIMA SE L'UTENTE ESISTE
        response = requests.delete(
            'https://db-manager:8005/delete_user',
            verify=False,
            json={"Email": email, "Password": password}
        )
        if response.status_code == 200:
            u.BLACKLIST.append(access_token)
            u.set_auth_token(None)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to db_manager", "details": str(e)}), 500


@app.route('/delete_admin', methods=['DELETE'])
def delete_admin():
    u.reset_response()

    # Estrai l'header di autorizzazione
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        u.unauthorized("Authorization header missing")
        return u.send_response()

    # Rimuovi il prefisso "Bearer"
    try:
        access_token =  auth_header.removeprefix("Bearer ").strip()
        print("Access Token:", access_token)  # Log del token estratto
    except IndexError:
        u.unauthorized("Malformed Authorization header")
        return u.send_response()
    
    # Valida il token
    token_data = u.validate_token(access_token)  # Funzione per decodificare e validare il token
    if "error" in token_data:
        u.unauthorized(token_data["error"])  # Se c'è un errore, rispondi con 401
        return u.send_response()

    role = token_data.get("decoded", {}).get('role')
    if role != "admin":
        return jsonify({"error": "Unauthorized. Admin role required"}), 400

    email = token_data.get('sub')  # restituisce l'email  corretta
    password = token_data.get('pass')
    if not email or not password:
        return jsonify({"error": "Email and Password are required"}), 400

    try:
        # Invia una richiesta DELETE al db-manager
        response = requests.delete(
            'https://db-manager:8005/delete_admin',
            verify=False,
            json={"Email": email, "Password": password}
        )
        if response.status_code == 200:
            u.BLACKLIST.append(access_token)
            u.set_auth_token(None)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to db_manager", "details": str(e)}), 500


def process_fields(fields):
    """
    Itera sui campi forniti e restituisce una lista con i campi elaborati.
    """
    results = []
    for field in fields:
        u.reset_response()
        if field:
            # Applica la funzione di sanitizzazione
            sanitize_hash(field)
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


# def sanitize_hash(input_str):
#     allowed_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@"
#     sanitized_str = input_str
#     for char in sanitized_str:
#         if char not in allowed_characters:
#             sanitized_str = sanitized_str.replace(char, "")
#     return sanitized_str


def sanitize_hash(input_str):
    allowed_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@."
    sanitized_str = input_str
    for char in sanitized_str:
        if char not in allowed_characters:
            sanitized_str = sanitized_str.replace(char, "")
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
