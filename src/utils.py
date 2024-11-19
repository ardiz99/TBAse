FLASK_DEBUG = True  # Do not use debug mode in production

ROLL_COST = 10

USER_ID = None
USER_EMAIL = None

LOCAL = False
# vabbè questa in realtà non serve praticamente a nulla
SERVICES = {
    "API_GATEWAY": "api-gateway",
    "AUTH_SERVICE": "auth-service",
    "GACHA_SERVICE": "gacha-service",
    "AUCTION_SERVICE": "auction-service",
    "CURRENCY_SERVICE": "currency-service",
    "DB_MANAGER": "db-manager",
}

PORTS = {
    "API_GATEWAY": "8000",
    "AUTH_SERVICE": "8001",
    "GACHA_SERVICE": "8002",
    "AUCTION_SERVICE": "8003",
    "CURRENCY_SERVICE": "8004",
    "DB_MANAGER": "8005",
}

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
