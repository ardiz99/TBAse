import os

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
