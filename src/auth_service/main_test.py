import main as main_app
from unittest.mock import patch

flask_app = main_app.app

# Database simulato in memoria
mock_database = {}

# Mock generico per intercettare le richieste
def mock_save_last(op, args, res):
    print(f"Mock save_last: {op} {args} {res}")

main_app.mock_save_last = mock_save_last

# Mock universale per intercettare richieste HTTP
def mock_requests(url, method="GET", params=None, json=None, **kwargs):
    print(f"Intercepted {method} request to {url}")
    print(f"Params: {params}, JSON: {json}")

    # Simula comportamento specifico per endpoint
    if "register" in url and method.upper() == "POST":
        # Simulazione endpoint /register
        email = json.get("Email")
        if email in mock_database:
            return MockResponse(400, {"error": "User already exists"})
        mock_database[email] = {
            "Password": json["Password"],
            "FirstName": json.get("FirstName"),
            "LastName": json.get("LastName"),
            "CurrencyAmount": json.get("CurrencyAmount"),
        }
        return MockResponse(200, {"message": "User registered successfully"})

    elif "login" in url and method.upper() == "GET":
        # Simulazione endpoint /login
        email = params.get("Email")
        if email in mock_database:
            return MockResponse(200, {"Password": mock_database[email]["Password"]})
        return MockResponse(400, {"error": "User not found"})

    elif "update_user" in url and method.upper() == "PUT":
    # Simulazione endpoint /update_user
        if not json:
            return MockResponse(400, {"error": "Request body is missing"})
        email = json.get("Email")
        if not email:
            return MockResponse(400, {"error": "Email is required for update"})
        if email in mock_database:
        # Aggiorna solo i campi forniti nel JSON
            for key, value in json.items():
                mock_database[email][key] = value
            return MockResponse(200, {"message": "User updated successfully"})
        return MockResponse(400, {"error": "User not found"})

    elif "delete_user" in url and method.upper() == "GET":
        # Simulazione endpoint /delete_user
        email = params.get("Email")
        if email in mock_database:
            del mock_database[email]
            return MockResponse(200, {"message": "User deleted successfully"})
        return MockResponse(400, {"error": "User not found"})

    elif "delete_admin" in url and method.upper() == "GET":
        # Simulazione endpoint /delete_admin
        email = params.get("Email")
        if email in mock_database:
            del mock_database[email]
            return MockResponse(200, {"message": "Admin deleted successfully"})
        return MockResponse(400, {"error": "Admin not found"})

    elif "check_users_profile" in url and method.upper() == "GET":
        # Simulazione endpoint /check_users_profile
        return MockResponse(200, {"users": list(mock_database.keys())})

    elif "protected" in url and method.upper() == "GET":
        # Simulazione endpoint /protected
        return MockResponse(200, {"message": "Access granted", "users": list(mock_database.keys())})

    # Default: endpoint non gestiti
    return MockResponse(404, {"error": "Unsupported endpoint or method"})

# Classe per simulare una risposta
class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json

# Patch per intercettare tutte le richieste HTTP
patch_requests_post = patch("requests.post", side_effect=lambda url, **kwargs: mock_requests(url, method="POST", **kwargs))
patch_requests_get = patch("requests.get", side_effect=lambda url, **kwargs: mock_requests(url, method="GET", **kwargs))
patch_requests_put = patch("requests.put", side_effect=lambda url, **kwargs: mock_requests(url, method="PUT", **kwargs))

# Avvia i mock
patch_requests_post.start()
patch_requests_get.start()
patch_requests_put.start()