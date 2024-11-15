FLASK_DEBUG = True  # Do not use debug mode in production

ROLL_COST = 10

RESPONSE = {
    "code": 200,
    "data": [],
    "message": ""
}


def reset_response():
    RESPONSE["code"] = 200
    RESPONSE["data"] = []
    RESPONSE["message"] = ""


def generic_error():
    RESPONSE["code"] = 500
    RESPONSE["data"] = []
    RESPONSE["message"] = "Unkonwn error"


def not_found():
    RESPONSE["code"] = 404
    RESPONSE["data"] = []
    RESPONSE["message"] = "Error! Not Found."


