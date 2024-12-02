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
ADMIN_GACHA_SERVICE_URL = "https://127.0.0.1:8006" if LOCAL else "https://admin-gacha-service:8006"

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


def handle_error(code):
    if code == 401:
        unauthorized()
    if code == 403:
        forbidden()
    if code == 404:
        not_found()
    if code == 500:
        generic_error()
    if code == 400:
        bad_request()


def set_response(response):
    RESPONSE["code"] = response.status_code
    RESPONSE["data"] = response.json().get("data")


def send_response(message=""):
    RESPONSE["message"] = RESPONSE["message"] + " / " + message
    return jsonify(RESPONSE), RESPONSE["code"]


# Secret keys and configurations
SECRET_KEY = "your-super-secret-key"  # Change to a secure value
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
def generate_token(email, role):
    payload = {
        "sub": email,
        "role": role,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=JWT_EXPIRATION_TIME)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    set_auth_token(token)
    return token


# Helper: Validate JWT
def validate_token(token):
    # Controlla se il token è nella blacklist
    if token in BLACKLIST:
        return {"error": "Token has been invalidated"}
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


