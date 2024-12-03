from flask import Flask, jsonify, request
from authlib.jose import JoseError
import string
import bcrypt
import os
import requests
import re, time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

import utils as u

# from src import utils as u

app = Flask(__name__)

mock_save_last = None

def save_last(op, args, res):
    """Funzione per salvare l'ultima operazione effettuata."""
    if mock_save_last:
        mock_save_last(op, args, res)
    else:
        timestamp = time.time()
        payload = {'timestamp': timestamp, 'op': op, 'args': args, 'res': res}
        try:
            requests.post('http://db-manager:8005/notify', json=payload)
        except requests.exceptions.RequestException as e:
            print(f"Error notifying db-manager: {e}")

# Helper: Hash password
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

# # Verify password
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
    # prelevo le informazioni da inserire
    email = request.args.get('Email')
    password = request.args.get('Password')

    # inserisco i campi appena presi nelvettore di sanificazione
    fields_to_process = [email, password]
    processed_fields = process_fields(fields_to_process)
    
    # prelevo i campi sanificati
    #email = processed_fields[0]
    #password = processed_fields[1]

    try:
        response = requests.get('https://db-manager:8005/login',
                                verify=False,
                                params={"Email": email})  # effettuiamo un controllo preliminare sulla presenza della email
        
        if response.status_code == 200:  # se l'email è presente nel db possiamo procedere con l'encrypt della
            #return jsonify(response.json())
            #tmp = response.json().get("data")[0].get("Password")
            stored_hash=response.json().get("data")[0].get("Password")
            salt = response.json().get("data")[0].get("Salt")
            tmp_hash = verify_password(password, stored_hash, salt)
            if verify_password(password, stored_hash, salt):
                role ="user"
                token = u.generate_token(email, role)
                #token_data = u.validate_token(token)#rigenera i campi originali dal token cifrato
                u.set_auth_token(token)
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid password credentials","password":password,"stored_hash":stored_hash,"salt":salt,"tmp_hash":tmp_hash}), 400          


        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500



            # # password ricevuta dall'utente
            # tmp = response.json().get("data")
            # stored_encrypted_password=tmp["Password"]
            # #stored_encrypted_password = response.json().get("data")[0].get("Password")
            # encrypted_password = encrypt_password(password)
            # # Confronta le password
            # if stored_encrypted_password == encrypted_password:
            #     role ="user"
            #     token = u.generate_token(email, role)
            #     token_data = u.validate_token(token)#rigenera i campi originali dal token cifrato
            #     u.set_auth_token(token)
            #     return jsonify({"message": "Login successful"}), 200
            # else:
            #     return jsonify({"error": "Invalid password credentials"}), 400


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
    #email = processed_fields[0]
    #password = processed_fields[1]

    if not email or not password:
        return jsonify(error="Missing email or password"), 400
    try:
        
        response = requests.get('https://db-manager:8005/login_admin',
                                verify=False,
                                params={"Email": email})
        if response.status_code == 200:
            #tmp = response.json().get("data")
            stored_hash=response.json().get("data")[0].get("Password")
            salt = response.json().get("data")[0].get("Salt")   
            tmp_hash = verify_password(password, stored_hash, salt)
            if verify_password(password, stored_hash, salt):
                role ="admin"
                token = u.generate_token(email, role)
                #token_data = u.validate_token(token)#rigenera i campi originali dal token cifrato
                u.set_auth_token(token)
                return jsonify({"message": "Login successful"}), 200        
            # encrypted_password = encrypt_password(password)
            # # Confronta le password
            # if stored_encrypted_password == encrypted_password:
            #     token = u.generate_token(email, "admin")
            #     u.set_auth_token(token)
            #     return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid password credentials","stored_hash":stored_hash,"salt":salt,"tmp_hash":tmp_hash}), 400
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500


@app.route('/logout', methods=['GET'])
def logout():
    # Recupera il token dall'intestazione Authorization
    try:
        auth_token=u.AUTH_TOKEN
    except Exception as e:
        return jsonify({"error": "no token found. PLs log in first"}), 400
    try:
            #return jsonify({"error": "Logout alredy done"}), 400
            u.BLACKLIST.append(auth_token)
            u.set_auth_token(None)
            return jsonify({"message": "Logout successful"}), 200

    except Exception as e:
            return jsonify({"error": str(e)}), 400

    # try:
    #     token = u.validate_token(auth_token)#rigenera i campi originali dal token cifrato
    #     if "error" in token:
    #         return jsonify({"error": token["error"],"token":token,"auth_token":auth_token}), 400

    #     # Aggiungi il token alla blacklist

    # except Exception as e:
    #     return jsonify({"error": f"Unexpected error: {str(e)}","token":token,"auth_token":auth_token}), 500

# User registration route
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
    fields_to_process = [firstname, lastname, email, password, currencyAmount]
    processed_fields = process_fields(fields_to_process)
    
    # prelevo i campi sanificati
    #firstname = processed_fields[0]
    #lastname = processed_fields[1]
    #email = processed_fields[2]
    #password = processed_fields[3]
    #currencyAmount = processed_fields[4]

    # pre la registrazione sono richiesti tutti i campi
    if not email or not password or not firstname or not lastname or not currencyAmount:
        return jsonify({"error": "Missing fields"}), 400
    #encrypted_password = encrypt_password(password)
    hashed_password, salt = hash_password(password)
    # salt=sanitize_hash(salt)
    # hashed_password=sanitize_hash(hashed_password)
    try:
        response = requests.post('https://db-manager:8005/register',
                                 verify=False,
                                 json={"FirstName": firstname, "LastName": lastname, "Email": email,
                                       "Password": hashed_password, "CurrencyAmount": currencyAmount, "Salt": salt})
        if response.status_code == 200:  # dal da-manager abbiamo in riscontro positivo  
  
            token = u.generate_token(email, "user")
            u.set_auth_token(token)
            return jsonify({"ok":"Registrazione avvenuta con successo!"}), 200
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            
            #return jsonify({response}), 500
            return jsonify({"error": "Internal server error","encrypted_password":hashed_password,"password":password,"salt":salt}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500

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
    # firstname = processed_fields[0]
    # lastname = processed_fields[1]
    # email = processed_fields[2]
    # password = processed_fields[3]


    # pre la registrazione sono richiesti tutti i campi
    if not email or not password or not firstname or not lastname:
        return jsonify({"error": "Missing fields"}), 400
    #encrypted_password = encrypt_password(password)
    hashed_password, salt = hash_password(password)
    # salt=sanitize_hash(salt)
    # hashed_password=sanitize_hash(hashed_password)
    try:
        response = requests.post('https://db-manager:8005/register_admin',
                                 verify=False,
                                 json={"FirstName": firstname, "LastName": lastname, "Email": email,
                                       "Password": hashed_password, "Salt": salt})
        if response.status_code == 200:  # dal da-manager abbiamo in riscontro positivo   
  
            token = u.generate_token(email, "admin")
            u.set_auth_token(token)
            return jsonify({"ok":"Registrazione avvenuta con successo!","token":token,"Salt": salt,"hashed_password": hashed_password,"password": password}), 200
        elif response.status_code == 400:
            return jsonify({"error": "Invalid credentials"}), 400
        else:
            return jsonify({"error": "Internal server error","Salt": salt,"hashed_password": hashed_password,"password": password}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500






#only for admin
@app.route('/update_specific_user', methods=['PUT'])
def update_specific_user():
    # Recupera il token di autenticazione
    try:
        auth_token = u.AUTH_TOKEN
    except Exception as e:
        save_last('update_specific_user', {}, {"error": "No token found. Please log in first"})
        return jsonify({"error": "No token found. Please log in first"}), 400

    if not auth_token:
        save_last('update_specific_user', {}, {"error": "Authorization header is required"})
        return jsonify({"error": "Authorization header is required"}), 400

    # Valida il token e controlla il ruolo
    token_data = u.validate_token(auth_token)
    role = token_data.get('role')
    if role != "admin":
        save_last('update_specific_user', {}, {"error": "Unauthorized. Admin role required"})
        return jsonify({"error": "Unauthorized. Admin role required"}), 400

    # Estrai i dati dal corpo della richiesta
    data = request.get_json()
    if not data:
        save_last('update_specific_user', {}, {"error": "Missing fields"})
        return jsonify({"error": "Missing fields"}), 400

    # firstname = data.get('FirstName')
    # lastname = data.get('LastName')
    # email = data.get('Email')
    # password = data.get('Password')
    # currency_amount = data.get('CurrencyAmount')
    if data.get('FirstName'):
        firstname = data.get('FirstName')
    if  data.get('LastName'):
        lastname = data.get('LastName')
    if data.get('Email'):
        email = data.get('Email')
    if data.get('Password'):
        password = data.get('Password')
    if data.get('CurrencyAmount'):
        currencyAmount = data.get('CurrencyAmount')


    # inserisco i campi appena presi nelvettore di sanificazione
    #fields_to_process = [firstname, lastname, password, currencyAmount]
    #processed_fields = process_fields(fields_to_process)
    
    # prelevo i campi sanificati
    #firstname = processed_fields[0]
    #lastname = processed_fields[1]
    #password = processed_fields[2]
    #currencyAmount = processed_fields[3]

    if not email or not any([firstname, lastname, password, currencyAmount]):
        save_last('update_specific_user', {}, {"error": "At least one field is required"})
        return jsonify({"error": "At least one field is required"}), 400

    if password:
        encrypted_password = encrypt_password(password)

    # Invio della richiesta al db-manager
    try:
        response = requests.put(
            'https://db-manager:8005/update_specific_user',
            verify=False,
            json={
                "FirstName": firstname,
                "LastName": lastname,
                "Email": email,
                "Password": encrypted_password if password else None,
                "CurrencyAmount": currencyAmount
            }
        )
        save_last('update_specific_user', data, response.json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        save_last('update_specific_user', data, {"error": str(e)})
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500





#only for admin
@app.route('/update_admin', methods=['PUT'])
def update_admin():
    # Recupera il token di autenticazione
    try:
        auth_token = u.AUTH_TOKEN
    except Exception as e:
        save_last('update_admin', {}, {"error": "No token found. Please log in first"})
        return jsonify({"error": "No token found. Please log in first"}), 400

    if not auth_token:
        save_last('update_admin', {}, {"error": "Authorization header is required"})
        return jsonify({"error": "Authorization header is required"}), 400

    # Valida il token e controlla il ruolo
    token_data = u.validate_token(auth_token)
    role = token_data.get('role')
    if role != "admin":
        save_last('update_admin', {}, {"error": "Unauthorized. Admin role required"})
        return jsonify({"error": "Unauthorized. Admin role required"}), 403

    # Estrai i dati dal corpo della richiesta
    data = request.get_json()
    if not data:
        save_last('update_admin', {}, {"error": "Missing fields"})
        return jsonify({"error": "Missing fields"}), 400

    if data.get('FirstName'):
        firstname = data.get('FirstName')
    if  data.get('LastName'):
        lastname = data.get('LastName')
    if data.get('Email'):
        email = data.get('Email')
    if not data.get("email"):
        email = token_data.get('role')
    if data.get('Password'):
        password = data.get('Password')
    if data.get('CurrencyAmount'):
        currencyAmount = data.get('CurrencyAmount')


    # inserisco i campi appena presi nelvettore di sanificazione
    #fields_to_process = [firstname, lastname, password, currencyAmount]
    #processed_fields = process_fields(fields_to_process)
    
    # prelevo i campi sanificati
    #firstname = processed_fields[0]
    #lastname = processed_fields[1]
    #password = processed_fields[2]
    #currencyAmount = processed_fields[3]

    if not email or not any([firstname, lastname, password, currencyAmount]):
        save_last('update_admin', {}, {"error": "At least one field is required"})
        return jsonify({"error": "At least one field is required"}), 400

    if password:
        encrypted_password = encrypt_password(password)

    # Invio della richiesta al db-manager
    try:
        response = requests.put(
            'https://db-manager:8005/update_admin',
            verify=False,
            json={
                "FirstName": firstname,
                "LastName": lastname,
                "Email": email,
                "Password": encrypted_password if password else None,
                "CurrencyAmount": currencyAmount
            }
        )
        save_last('update_admin', data, response.json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        save_last('update_admin', data, {"error": str(e)})
        return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500






# Admin check all users accounts/profiles
@app.route('/check_users_profile', methods=['GET'])
def check_users_profile():
   # Verifica l'intestazione Authorization
    try:
        auth_token=u.AUTH_TOKEN
    except Exception as e:
        save_last('check_users_profile', {}, {"no token found. PLs log in first": str(e), "auth token": str(auth_token)})
        return jsonify({"no token found. PLs log in first":str(e),"auth_token":str(auth_token)}), 400
    
    token_data = u.validate_token(auth_token)#rigenera i campi originali dal token cifrato
    if not auth_token:
        save_last('check_users_profile', {}, {"error": "Authorization header is required"})
        return jsonify({"error": "Authorization header is required"}), 400
    # token_data = u.validate_token(auth_token)#rigenera i campi originali dal token cifrato
    get_role=token_data.get('role')#restituisce il ruolo corretto
    try:
        if get_role=="admin":
            try:
                response = requests.get('https://db-manager:8005/check_users_profile',
                                        verify=False)
                if response.status_code == 200:
                    save_last('check_user_profile', {}, response.json())
                    return jsonify(response.json()), 200
                elif response.status_code == 400:
                    save_last('check_user_profile', {}, {"Generic error"})
                    return jsonify({"Generic error"}), 400
                else:
                    save_last('check_user_profile', {}, {"error": "server error","response":response})
                    return jsonify({"error": "server error","response":response}), 500
            except requests.exceptions.RequestException as e:
                save_last('check_user_profile', {}, {"error": str(e)})
                return jsonify({"error": "Could not connect to db_manager", "details": str(e)}), 500
    except Exception as e:
            save_last('check_users_profile', {}, {"Insufficent permission"})
            return jsonify({"Insufficent permission"}), 400
    # da effettuare il controllo sul JWT TOKEN



@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    # Recupera i dati dal corpo della richiesta
    data = request.get_json()
    email = data.get('Email')
    password = data.get('Password')

    # Verifica che i campi richiesti siano presenti
    if not email or not password:
        save_last('delete_user', data, {"error": "Email and Password are required"})
        return jsonify({"error": "Email and Password are required"}), 400

    try:
        # Invia una richiesta DELETE al db-manager
        response = requests.delete(
            'https://db-manager:8005/delete_user',
            verify=False,
            json={"Email": email, "Password": encrypt_password(password)}
        )
        save_last('delete_user', data, response.json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        save_last('delete_user', data, {"error": str(e)})
        return jsonify({"error": "Failed to connect to db_manager", "details": str(e)}), 500


@app.route('/delete_admin', methods=['DELETE'])
def delete_admin():
    # Verifica il token di autenticazione
    try:
        auth_token = u.AUTH_TOKEN
    except Exception as e:
        save_last('delete_admin', {}, {"error": "No token found"})
        return jsonify({"error": "No token found. Please log in first"}), 400

    if not auth_token:
        save_last('delete_admin', {}, {"error": "Authorization header is required"})
        return jsonify({"error": "Authorization header is required"}), 400

    # Valida il token e controlla il ruolo
    token_data = u.validate_token(auth_token)
    role = token_data.get('role')
    if role != "admin":
        save_last('delete_admin', {}, {"error": "Unauthorized. Admin role required"})
        return jsonify({"error": "Unauthorized. Admin role required"}), 403

    # Recupera i dati dal corpo della richiesta
    data = request.get_json()
    email = data.get('Email')
    password = data.get('Password')

    if not email or not password:
        save_last('delete_admin', data, {"error": "Email and Password are required"})
        return jsonify({"error": "Email and Password are required"}), 400

    try:
        # Invia una richiesta DELETE al db-manager
        response = requests.delete(
            'https://db-manager:8005/delete_admin',
            verify=False,
            json={"Email": email, "Password": encrypt_password(password)}
        )
        save_last('delete_admin', data, response.json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        save_last('delete_admin', data, {"error": str(e)})
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


@app.route('/protected', methods=['GET'])
def protected():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        save_last('protected', {}, {"error": "Authorization header is required"})
        return jsonify({"error": "Authorization header is required"}), 400

    token = auth_header.split()[1]
    token_data = u.validate_token(token)

    if "error" in token_data:
        save_last('protected', {}, {"error": token_data["error"]})
        return jsonify({"error": token_data["error"]}), 400
    
    save_last('protected', {}, {"message": "Access granted", "data": token_data})
    return jsonify({"message": "Access granted", "data": token_data}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8001)
