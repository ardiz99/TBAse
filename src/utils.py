import os

import jwt
import datetime
from flask import jsonify

FLASK_DEBUG = False  # Do not use debug mode in production

ROLL_COST = 10
GOLDEN_COST = 100

USER_ID = None
USER_EMAIL = None

LOCAL = False

HOST = "localhost" if LOCAL else os.getenv('DB_HOST')
USER = "root" if LOCAL else os.getenv('DB_USER')
PASSWORD = "diego" if LOCAL else os.getenv('DB_PASSWORD')
DATABASE = "ase" if LOCAL else os.getenv('DB_NAME')

GACHA_SERVICE_URL = "http://127.0.0.1:8002" if LOCAL else "https://gacha-service:8002"
MARKET_SERVICE_URL = "http://127.0.0.1:8003" if LOCAL else "https://market-service:8003"
CURRENCY_SERVICE_URL = "http://127.0.0.1:8004" if LOCAL else "https://currency-service:8004"
DB_MANAGER_URL = "http://127.0.0.1:8005" if LOCAL else "https://db-manager:8005"
AUCTION_SERVICE_URL = "http://127.0.0.1:8006" if LOCAL else "https://auction-service:8006"

ALLOWED_INT = "0123456789"
ALLOWED_CHAR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@."

RESPONSE = {
    "code": 200,
    "data": [],
    "message": ""
}


def reset_response():
    RESPONSE["code"] = 200
    RESPONSE["data"] = []
    RESPONSE["message"] = ""


def generic_error(message="Unkonwn error"):
    RESPONSE["code"] = 500
    RESPONSE["data"] = []
    RESPONSE["message"] = message


def not_found(message=""):
    RESPONSE["code"] = 404
    RESPONSE["data"] = []
    RESPONSE["message"] = "Error! Not Found. " + message


def bad_request(message=""):
    RESPONSE["code"] = 400
    RESPONSE["data"] = []
    RESPONSE["message"] = "Bad Request. " + message


def unauthorized(message=""):
    RESPONSE["code"] = 401
    RESPONSE["data"] = []
    RESPONSE["message"] = "Unauthorized " + message


def forbidden(message=""):
    RESPONSE["code"] = 403
    RESPONSE["data"] = []
    RESPONSE["message"] = "Forbidden " + message


def method_not_allowed(message=""):
    RESPONSE["code"] = 405
    RESPONSE["data"] = []
    RESPONSE["message"] = "Method not Allowed " + message


def handle_error(code):
    if code == 400:
        bad_request()
    elif code == 401:
        unauthorized()
    elif code == 403:
        forbidden()
    elif code == 404:
        not_found()
    elif code == 405:
        method_not_allowed()
    else:
        generic_error()


def set_response(response):
    RESPONSE["code"] = response.status_code
    RESPONSE["data"] = response.json().get("data")
    if response.json().get("message"):
        RESPONSE["message"] = RESPONSE["message"] + " / " + response.json().get("message")


def send_response(message=""):
    RESPONSE["message"] = RESPONSE["message"] + " / " + message
    return jsonify(RESPONSE), RESPONSE["code"]


# Secret keys and configurations
# Secret keys and configurations
SECRET_KEY = "73e8a1c4efc8d1f9e0e9241bd3c285740be019d57cd6711a2f7635cf09e8dc4a"  # Change to a secure value
JWT_EXPIRATION_TIME = 3600  # 1 hour in seconds
ALGORITHM = "HS256"  # JWT signing algorithm

# Placeholder for user roles
USER_ROLES = ["user", "admin"]

# Blacklist dei token JWT invalidati
BLACKLIST = []

# Variabile globale per il token
AUTH_TOKEN = None


# Funzione per aggiornare il token
def set_auth_token(token):
    global AUTH_TOKEN
    AUTH_TOKEN = token


# Helper: Generate JWT
def generate_tokens(user_id, role):
    """
    Genera un ID Token e un Access Token usando HS256.
    """
    issuer = "https://127.0.0.1:8001"  # Cambia con il tuo URL

    # ID Token
    id_payload = {
        "iss": issuer,
        "sub": user_id,  # Identificativo unico dell'utente
        "role": role,  # Ruolo dell'utente (user/admin)
        "iat": datetime.datetime.now(datetime.timezone.utc),  # Data di emissione
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=JWT_EXPIRATION_TIME)
        # Scadenza
    }
    id_token = jwt.encode(id_payload, SECRET_KEY, algorithm=ALGORITHM)

    # Access Token
    access_payload = {
        "iss": issuer,
        "sub": user_id,  # Identificativo unico dell'utente
        "role": role,  # Ruolo dell'utente (user/admin)
        "scope": "user_operations" if role == "user" else "admin_operations",  # Scope basato sul ruolo
        "iat": datetime.datetime.now(datetime.timezone.utc),  # Data di emissione
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=JWT_EXPIRATION_TIME),
        # Scadenza
        "jti": f"{user_id}-{datetime.datetime.now(datetime.timezone.utc)}"  # ID unico del token
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"id_token": id_token, "access_token": access_token}


def validate_token(token):
    """
    Valida un token JWT e ritorna il payload decodificato.
    """
    # Controlla se il token è nella blacklist
    if token in BLACKLIST:
        return {"error": "Token has been invalidated"}
    try:
        # Decodifica e verifica il token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "decoded": decoded}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Invalid token"}


def check_token(enc_token):
    if enc_token is None:
        unauthorized()
        return False

    return True


def check_token_admin(enc_token):
    if not check_token(enc_token):
        return False

    token = validate_token(enc_token)
    role = token.get("role")

    if role != 'admin':
        unauthorized()
        return False

    return True


def process_fields(fields):
    """
    Itera sui campi forniti e restituisce una lista con i campi elaborati.
    """
    results = []
    for field in fields:
        reset_response()
        if field:
            # Applica la funzione di sanitizzazione
            sanitize_hash(field)
            # controlla la risposta ricevuta dalla funzione sanitize_username e determina se l'input è valido o meno
            if RESPONSE["code"] == 400:
                results.append('')
            else:
                tmp = RESPONSE["data"].strip("[]")
                results.append(tmp)
        else:
            results.append('')
    return results


def sanitize_hash(input_str):
    allowed_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-: "
    sanitized_str = input_str
    for char in sanitized_str:
        if char not in allowed_characters:
            sanitized_str = sanitized_str.replace(char, "")
    if input_str != sanitized_str:
        RESPONSE["code"] = 400
        RESPONSE["data"] = sanitized_str
        return RESPONSE
    else:
        RESPONSE["code"] = 200
        RESPONSE["data"] = sanitized_str
        return RESPONSE


def sanitize(input_str, allowed_characters):
    sanitized_str = input_str
    for char in sanitized_str:
        if char not in allowed_characters:
            sanitized_str = sanitized_str.replace(char, "")
    if input_str != sanitized_str:

        return None
    else:
        return sanitized_str


def safe_parse_int(value: str) -> int:
    if str is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        print(f"Errore: Impossibile convertire '{value}' in un intero.")
        return None
