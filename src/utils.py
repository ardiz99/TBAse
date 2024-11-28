import os
import jwt
import datetime
from flask import jsonify


FLASK_DEBUG = True  # Do not use debug mode in production

ROLL_COST = 10

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


RESPONSE = {
    "code": 200,
    "data": [],
    "message": ""
}


def send_response(message=""):
    if message:
        RESPONSE["message"] = message
    return jsonify(RESPONSE), RESPONSE["code"]


def reset_response():
    RESPONSE["code"] = 200
    RESPONSE["data"] = []
    RESPONSE["message"] = ""


def generic_error(message="Unkonwn error"):
    RESPONSE["code"] = 500
    RESPONSE["data"] = []
    RESPONSE["message"] = message


def not_found():
    RESPONSE["code"] = 404
    RESPONSE["data"] = []
    RESPONSE["message"] = "Error! Not Found."


def bad_request():
    RESPONSE["code"] = 400
    RESPONSE["data"] = []
    RESPONSE["message"] = "Bad Request."


def handle_error(code):
    if code == 404:
        not_found()
    if code == 500:
        generic_error()
    if code == 400:
        bad_request()


# Secret keys and configurations
SECRET_KEY = "your-super-secret-key"  # Change to a secure value
JWT_EXPIRATION_TIME = 36000  # 1 hour in seconds
ALGORITHM = "HS256"  # JWT signing algorithm

# Placeholder for user roles
USER_ROLES = ["user", "admin"]

# Blacklist dei token JWT invalidati
BLACKLIST =[]

# Variabile globale per il token
AUTH_TOKEN = None

# Funzione per aggiornare il token
def set_auth_token(token):
    global AUTH_TOKEN
    AUTH_TOKEN = token

# Funzione per ottenere il token
def get_auth_token():
    global AUTH_TOKEN
    if AUTH_TOKEN is None:
        raise ValueError("No authorization token found. Please log in.")
    return AUTH_TOKEN

# Helper: Generate JWT
def generate_token(user_id, role):
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=JWT_EXPIRATION_TIME)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
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
