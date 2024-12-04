import main as main_app
from unittest.mock import patch
from flask import request

flask_app = main_app.app

# Database simulato in memoria
mock_database = {}
mock_tokens = {}  # Per gestire i token di autenticazione
mock_blacklist = set()  # Per simulare i token blacklistati

# Funzione mock per il salvataggio delle operazioni
def mock_save_last(op, args, res):
    print(f"Mock save_last: {op} {args} {res}")

main_app.mock_save_last = mock_save_last

# Mock per il metodo GET
def mock_requests_get(url, params=None, **kwargs):
    print(f"Mock GET to {url} with params {params}")

    if "login" in url:
        return handle_login(request.args)

    if "check_users_profile" in url:
        return handle_check_users_profile()

    if "protected" in url:
        return handle_protected()

    return MockResponse(404, {"error": "Endpoint not found"})

# Mock per il metodo POST
def mock_requests_post(url, json=None, **kwargs):
    print(f"Mock POST to {url} with json {json}")

    if "register" in url:
        return handle_register(json)

    if "register_admin" in url:
        return handle_register_admin(json)

    return MockResponse(404, {"error": "Endpoint not found"})

# Mock per il metodo PUT
def mock_requests_put(url, json=None, **kwargs):
    print(f"Mock PUT to {url} with json {json}")

    if "update_user" in url:
        return handle_update_user(json)

    if "update_specific_user" in url:
        return handle_update_specific_user(json)

    if "update_admin" in url:
        return handle_update_admin(json)

    return MockResponse(404, {"error": "Endpoint not found"})

# Mock per il metodo DELETE
def mock_requests_delete(url, json=None, **kwargs):
    print(f"Mock DELETE to {url} with json {json}")

    if "delete_user" in url:
        return handle_delete_user(json)

    if "delete_admin" in url:
        return handle_delete_admin(json)

    return MockResponse(404, {"error": "Endpoint not found"})

# Gestione specifica degli endpoint
def handle_register(json):
    email = json.get("Email")
    if email in mock_database:
        return MockResponse(400, {"error": "User already exists"})
    mock_database[email] = {
        "Password": json["Password"],
        "FirstName": json.get("FirstName"),
        "LastName": json.get("LastName"),
        "CurrencyAmount": json.get("CurrencyAmount", 0),
        "Role": "user",
    }
    return MockResponse(200, {"message": "Mock registration success"})

def handle_register_admin(json):
    email = json.get("Email")
    if email in mock_database:
        return MockResponse(400, {"error": "Admin already exists"})
    mock_database[email] = {
        "Password": json["Password"],
        "FirstName": json.get("FirstName"),
        "LastName": json.get("LastName"),
        "Role": "admin",
    }
    return MockResponse(200, {"message": "Mock admin registration success"})

def handle_login(args):
    email = args.get("Email")
    password = args.get("Password")

    if not email or not password:
        return MockResponse(400, {"error": "Email and password are required"})

    user_data = mock_database.get(email)
    if not user_data:
        return MockResponse(400, {"error": "User not found"})

    encrypted_password = main_app.encrypt_password(password)
    if user_data["Password"] != encrypted_password:
        return MockResponse(400, {"error": "Invalid credentials"})

    token = main_app.u.generate_token(email, user_data["Role"])
    mock_tokens[email] = token
    return MockResponse(200, {"data": {"Password": user_data["Password"]}, "message": "Login successful"})

def handle_update_user(json):
    print(f"Handling update_user with data: {json}")
    email = json.get("Email")
    if email not in mock_database:
        return MockResponse(400, {"error": "User not found"})

    mock_database[email].update({
        "FirstName": json.get("FirstName", mock_database[email]["FirstName"]),
        "LastName": json.get("LastName", mock_database[email]["LastName"]),
        "Password": json.get("Password", mock_database[email]["Password"]),
        "CurrencyAmount": json.get("CurrencyAmount", mock_database[email]["CurrencyAmount"]),
    })
    return MockResponse(200, {"message": "Mock user update success"})

def handle_update_specific_user(json):
    email = json.get("Email")
    if email not in mock_database:
        return MockResponse(400, {"error": "User not found"})

    mock_database[email].update({
        "FirstName": json.get("FirstName", mock_database[email]["FirstName"]),
        "LastName": json.get("LastName", mock_database[email]["LastName"]),
        "Password": json.get("Password", mock_database[email]["Password"]),
        "CurrencyAmount": json.get("CurrencyAmount", mock_database[email]["CurrencyAmount"]),
    })
    return MockResponse(200, {"message": "Mock specific user update success"})

def handle_update_admin(json):
    email = json.get("Email")
    if email not in mock_database:
        return MockResponse(400, {"error": "Admin not found"})

    mock_database[email].update({
        "FirstName": json.get("FirstName", mock_database[email]["FirstName"]),
        "LastName": json.get("LastName", mock_database[email]["LastName"]),
        "Password": json.get("Password", mock_database[email]["Password"]),
    })
    return MockResponse(200, {"message": "Mock admin update success"})

def handle_delete_user(json):
    email = json.get("Email")
    if email not in mock_database:
        return MockResponse(400, {"error": "User not found"})
    del mock_database[email]
    return MockResponse(200, {"message": "Mock user delete success"})

def handle_delete_admin(json):
    email = json.get("Email")
    if email not in mock_database:
        return MockResponse(400, {"error": "Admin not found"})
    del mock_database[email]
    return MockResponse(200, {"message": "Mock admin delete success"})

def handle_check_users_profile():
    return MockResponse(200, {"users": mock_database})

def handle_protected():
    return MockResponse(200, {"message": "Access granted"})

# Classe per simulare una risposta
class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json

# Applica i mock ai metodi HTTP
patch_requests_get = patch("requests.get", side_effect=mock_requests_get)
patch_requests_post = patch("requests.post", side_effect=mock_requests_post)
patch_requests_put = patch("requests.put", side_effect=mock_requests_put)
patch_requests_delete = patch("requests.delete", side_effect=mock_requests_delete)

patch_requests_get.start()
patch_requests_post.start()
patch_requests_put.start()
patch_requests_delete.start()
