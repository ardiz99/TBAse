import main as main_app
from unittest.mock import patch

flask_app = main_app.app

# Database simulato in memoria
mock_database = {
    "users": {
        "alice@example.com": {
            "CurrencyAmount": 500,
            "UserId": 1
        }
    },
    "gacha_items": {
        "Legendary": [{"GachaId": 101, "Name": "Legendary Sword"}],
        "Epic": [{"GachaId": 102, "Name": "Epic Shield"}]
    },
    "images": {
        "/img/bulbasaur.png": "Image file content simulated for testing"
    }
}

# Mock per il salvataggio delle operazioni
def mock_save_last(op, args, res):
    print(f"Mock save_last: {op} {args} {res}")

main_app.mock_save_last = mock_save_last

# Mock per le richieste GET
def mock_requests_get(url, params=None, **kwargs):
    print(f"Mock GET to {url} with params {params}")

    if "/get_amount" in url:
        return handle_get_amount(params)
    if "/get_gacha_by_rarity" in url:
        return handle_get_gacha_by_rarity(params)
    if "/user/get_by_email" in url:
        return handle_get_user_by_email(params)
    if "/roll_img" in url:
        return handle_roll_img(params)

    return MockResponse(404, {"error": "Endpoint not found or unsupported GET method"})

# Mock per le richieste POST
def mock_requests_post(url, json=None, **kwargs):
    print(f"Mock POST to {url} with json {json}")

    if "/roll" in url:
        return handle_market_roll(json)

    return MockResponse(404, {"error": "Endpoint not found or unsupported POST method"})

# Mock per le richieste PUT
def mock_requests_put(url, json=None, **kwargs):
    print(f"Mock PUT to {url} with json {json}")

    if "/update_amount" in url:
        return handle_update_amount(json)

    return MockResponse(404, {"error": "Endpoint not found or unsupported PUT method"})

# Mock per le richieste DELETE (non usate in questo caso, ma lasciate per completezza)
def mock_requests_delete(url, json=None, **kwargs):
    print(f"Mock DELETE to {url} with json {json}")

    return MockResponse(404, {"error": "Endpoint not found or unsupported DELETE method"})

# Funzioni specifiche per la gestione dei vari endpoint
def handle_get_amount(params):
    email = params.get("email")
    if email not in mock_database["users"]:
        return MockResponse(400, {"error": "User not found"})
    user = mock_database["users"][email]
    return MockResponse(200, {"data": {"CurrencyAmount": user["CurrencyAmount"]}})

def handle_get_gacha_by_rarity(params):
    rarity = params.get("rarity")
    if rarity not in mock_database["gacha_items"]:
        return MockResponse(400, {"error": "Invalid rarity"})
    return MockResponse(200, {"data": mock_database["gacha_items"][rarity]})

def handle_get_user_by_email(params):
    email = params.get("email")
    if email not in mock_database["users"]:
        return MockResponse(400, {"error": "User not found"})
    user = mock_database["users"][email]
    return MockResponse(200, {"data": {"UserId": user["UserId"]}})

def handle_roll_img(params):
    url = params.get("url")
    if url in mock_database["images"]:
        return MockResponse(200, {"message": "Image found"})
    return MockResponse(404, {"error": "Image not found"})

def handle_market_roll(data):
    # Simula il salvataggio di una roll
    print(f"Mock Market Roll: {data}")
    return MockResponse(200, {"message": "Roll successful"})

def handle_update_amount(data):
    email = data.get("email")
    new_amount = data.get("new_amount")

    if email not in mock_database["users"]:
        return MockResponse(400, {"error": "User not found"})
    if new_amount < 0:
        return MockResponse(400, {"error": "Amount cannot be negative"})

    mock_database["users"][email]["CurrencyAmount"] = new_amount
    return MockResponse(200, {"message": "Amount updated successfully"})

# Classe per simulare una risposta
class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json

# Applicazione dei mock
patch_requests_get = patch("requests.get", side_effect=mock_requests_get)
patch_requests_post = patch("requests.post", side_effect=mock_requests_post)
patch_requests_put = patch("requests.put", side_effect=mock_requests_put)
patch_requests_delete = patch("requests.delete", side_effect=mock_requests_delete)

patch_requests_get.start()
patch_requests_post.start()
patch_requests_put.start()
patch_requests_delete.start()