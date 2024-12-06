import main as main_app
from unittest.mock import patch
import bcrypt
from flask import request
import base64

flask_app = main_app.app

# Database simulato in memoria
mock_database = {
    "user@example.com": {
        "Password": "$2b$12$/eUJpQzpFomA1Lp9zclBsug47nxbYX8uxL5NbWGJ9KZzDhfYdoDmO",
        "Salt": "JDJiJDEyJC9lVUpwUXpwRm9tQTFMcDl6Y2xCc3U=",
        "FirstName": "John",
        "LastName": "Doe",
        "CurrencyAmount": 100,
        "Role": "user"
    }
}
mock_tokens = {}  # Per gestire i token di autenticazione
mock_blacklist = set()  # Per simulare i token blacklistati

# Funzione mock per il salvataggio delle operazioni
def mock_save_last(op, args, res):
    print(f"Mock save_last: {op} {args} {res}")

main_app.mock_save_last = mock_save_last

# Funzione per simulare la chiamata al DB Manager
def mock_db_manager_get_user(email):
    user_data = mock_database.get(email)
    if user_data:
        return {
            "Password": user_data["Password"],
            "Salt": user_data["Salt"]
        }
    return None

# Mock per il metodo GET
def mock_requests_get(url, params=None, headers=None, **kwargs):
    print(f"Mock GET to {url} with params {params}")
    auth_token = headers.get("Authorization") if headers else None

    if "logout" in url:
        return handle_logout(auth_token)
    if "check_users_profile" in url:
        return handle_check_users_profile(auth_token)
    return MockResponse(404, {"error": "Endpoint not found"})

# Mock per il metodo POST
def mock_requests_post(url, json=None, **kwargs):
    print(f"Mock POST to {url} with json {json}")
    if "login" in url:
        return handle_login(json)
    if "register" in url:
        return handle_register(json)
    return MockResponse(404, {"error": "Endpoint not found"})

# Mock per il metodo PUT
def mock_requests_put(url, json=None, headers=None, **kwargs):
    print(f"Mock PUT to {url} with json {json}")
    if "update_user" in url:
        return handle_update_user(json, headers.get("Authorization"))
    return MockResponse(404, {"error": "Endpoint not found"})

# Mock per il metodo DELETE
def mock_requests_delete(url, json=None, headers=None, **kwargs):
    print(f"Mock DELETE to {url} with json {json}")
    if "delete_user" in url:
        return handle_delete_user(headers.get("Authorization"))
    return MockResponse(404, {"error": "Endpoint not found"})

# Handler per endpoint
def handle_register(json):
    email = json.get("Email")
    if email in mock_database:
        return MockResponse(400, {"error": "User already exists"})

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(json["Password"].encode('utf-8'), salt)

    mock_database[email] = {
        "Password": hashed_password.decode('utf-8'),
        "Salt": base64.b64encode(salt).decode('utf-8'),
        "FirstName": json.get("FirstName"),
        "LastName": json.get("LastName"),
        "CurrencyAmount": json.get("CurrencyAmount", 0),
        "Role": "user"
    }
    return MockResponse(200, {"message": "Mock registration success"})

def handle_login(json):
    email = json.get("Email")
    password = json.get("Password")

    if not email or not password:
        return MockResponse(201, {"error": "Email and password are required"})
    
    user_info = mock_db_manager_get_user(email)
    if not user_info:
        return MockResponse(404, {"error": "User not found"})
    
    stored_hash = user_info["Password"]    
    print(stored_hash)

    salt_bytes = base64.b64decode(user_info["Salt"])
    generated_pwd = bcrypt.hashpw(password.encode('utf-8'), salt_bytes)

    pwd = generated_pwd.decode('utf-8')
    
    if not pwd == stored_hash:
        return MockResponse(400, {"error": "Invalid credentials"})
    
    token = main_app.u.generate_tokens(email, mock_database[email]["Role"])
    mock_tokens[email] = token
    return MockResponse(200, {"data": {"access_token": token}, "message": "Login successful"})

def handle_logout(auth_token):
    if not auth_token:
        return MockResponse(401, {"error": "Unauthorized"})
    token = auth_token.removeprefix("Bearer ").strip()
    if token in mock_blacklist:
        return MockResponse(401, {"error": "Token is blacklisted"})
    mock_blacklist.add(token)
    return MockResponse(200, {"message": "Logout successful"})

def handle_update_user(json, auth_token):
    if not auth_token:
        return MockResponse(401, {"error": "Unauthorized"})
    token = auth_token.removeprefix("Bearer ").strip()
    email = main_app.u.validate_token(token).get("sub")
    if not email or email not in mock_database:
        return MockResponse(401, {"error": "Unauthorized"})
    user_data = mock_database[email]
    user_data.update({
        "FirstName": json.get("FirstName", user_data.get("FirstName")),
        "LastName": json.get("LastName", user_data.get("LastName")),
        "Password": bcrypt.hashpw(json["Password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if json.get("Password") else user_data.get("Password"),
        "CurrencyAmount": json.get("CurrencyAmount", user_data.get("CurrencyAmount"))
    })
    return MockResponse(200, {"message": "Mock user update success"})

def handle_check_users_profile(auth_token):
    # if not auth_token:
    #     return MockResponse(401, {"error": "Unauthorized"})
    # token = auth_token.removeprefix("Bearer ").strip()
    # try:
    #     token_data = main_app.u.validate_token(token)
    # except Exception as e:
    #     return MockResponse(401, {"error": f"Invalid token: {str(e)}"})
    return MockResponse(200, {"data": list(mock_database.values()), "message": "User profiles retrieved successfully"})

def handle_delete_user(auth_token):
    if not auth_token:
        return MockResponse(401, {"error": "Unauthorized"})
    token = auth_token.removeprefix("Bearer ").strip()
    email = main_app.u.validate_token(token).get("sub")
    if email in mock_database:
        del mock_database[email]
        return MockResponse(200, {"message": "User deleted successfully"})
    return MockResponse(404, {"error": "User not found"})

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
