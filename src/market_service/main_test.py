import main as main_app
from unittest.mock import patch
from flask import request

flask_app = main_app.app

# Database simulato in memoria
mock_database = {
    "users": {
        "alice@example.com": {"user_id": 1, "CurrencyAmount": 500},
        "bob@example.com": {"user_id": 2, "CurrencyAmount": 300},
    },
    "gacha": {
        1: {"gacha_id": 1, "Name": "Rare Sword", "OwnerId": 1},
        2: {"gacha_id": 2, "Name": "Epic Shield", "OwnerId": 2},
    },
    "auctions": {},
    "transactions": [],
}

mock_save_last = None


# Funzione mock per il salvataggio delle operazioni
def mock_save_last(op, args, res):
    print(f"Mock save_last: {op} {args} {res}")


main_app.mock_save_last = mock_save_last


# Mock per il metodo GET
def mock_requests_get(url, params=None, **kwargs):
    print(f"Mock GET to {url} with params {params}")

    if "user/get_by_email" in url:
        return handle_get_user_by_email(params)
    
    if "transaction" in url:
        return handle_transaction()

    if "auction" in url and "/get_bid" in url:
        return handle_get_auction_bid(url)

    if "/transaction_history" in url:
        return handle_transaction_history(url)

    if "auction" in url:
        return handle_get_auctions()

    return MockResponse(404, {"error": "Endpoint not found"})


# Mock per il metodo POST
def mock_requests_post(url, json=None, **kwargs):
    print(f"Mock POST to {url} with json {json}")

    if "roll" in url:
        return handle_roll(json)

    if "new_auction" in url:
        return handle_new_auction(json)

    return MockResponse(404, {"error": "Endpoint not found"})


# Mock per il metodo PUT
def mock_requests_put(url, json=None, **kwargs):
    print(f"Mock PUT to {url} with json {json}")

    if "auction" in url and "/update_actual_price" in url:
        return handle_update_actual_price(json)

    if "update_amount" in url:
        return handle_update_amount(json)

    return MockResponse(404, {"error": "Endpoint not found"})


# Gestione specifica degli endpoint
def handle_get_user_by_email(params):
    email = params.get("email")
    user = mock_database["users"].get(email)
    if user:
        return MockResponse(200, {"data": user})
    return MockResponse(404, {"error": "User not found"})


def handle_roll(json):
    user_id = json.get("user_id")
    gacha_id = json.get("gacha_id")
    cost = json.get("cost")
    end_date = json.get("end_date")

    print("Debug Info:")
    print(f"User ID: {user_id}, Gacha ID: {gacha_id}, Cost: {cost}, End Date: {end_date}")

    # Verifica che l'user_id esista in mock_database
    user_exists = any(user["user_id"] == user_id for user in mock_database["users"].values())
    if not user_exists:
        return MockResponse(404, {"error": "User not found"})

    # Verifica che il gacha_id esista in mock_database
    if gacha_id not in mock_database["gacha"]:
        return MockResponse(404, {"error": "Gacha not found"})

    # Aggiungi la transazione
    mock_database["transactions"].append(
        {"user_id": user_id, "gacha_id": gacha_id, "cost": cost, "end_date": end_date}
    )
    return MockResponse(200, {"message": "Roll transaction created successfully"})

def handle_new_auction(json):
    user_owner_email = json.get("user_owner")
    gacha_id = json.get("gacha_id")
    starting_price = json.get("starting_price")
    end_date = json.get("end_date")

    # Controlla se l'utente esiste
    user_data = mock_database["users"].get(user_owner_email)
    if not user_data:
        return MockResponse(404, {"error": "User not found."})

    # Controlla se il Gacha esiste
    gacha_data = mock_database["gacha"].get(gacha_id)
    if not gacha_data:
        return MockResponse(404, {"error": "Gacha not found."})

    # Controlla che l'utente sia il proprietario del Gacha
    if gacha_data["OwnerId"] != user_data["user_id"]:
        return MockResponse(403, {"error": "User is not the owner of the Gacha."})

    # Aggiungi l'asta al mock_database
    auction_id = len(mock_database["auctions"]) + 1  # Genera un nuovo ID
    mock_database["auctions"].append({
        "auction_id": auction_id,
        "user_owner": user_data["user_id"],
        "gacha_id": gacha_id,
        "starting_price": starting_price,
        "end_date": end_date,
        "bids": [],
    })
    return MockResponse(200, {"message": "Auction created successfully.", "auction_id": auction_id})



def handle_get_auctions():
    return MockResponse(200, {"data": list(mock_database["auctions"].values())})


def handle_get_auction_bid(url):
    auction_id = int(url.split("/")[-2])
    auction = mock_database["auctions"].get(auction_id)
    if auction:
        return MockResponse(200, {"data": auction})
    return MockResponse(404, {"error": "Auction not found"})


def handle_update_actual_price(json):
    auction_id = json.get("auction_id")
    new_price = json.get("bid")

    auction = mock_database["auctions"].get(auction_id)
    if not auction:
        return MockResponse(404, {"error": "Auction not found"})

    auction["ActualPrice"] = new_price
    return MockResponse(200, {"message": "Auction price updated"})


def handle_update_amount(json):
    email = json.get("email")
    new_amount = json.get("new_amount")

    user = mock_database["users"].get(email)
    if not user:
        return MockResponse(404, {"error": "User not found"})

    user["CurrencyAmount"] = new_amount
    return MockResponse(200, {"message": "User currency updated"})


def handle_transaction_history(url):
    user_id = int(url.split("/")[-1])
    transactions = [
        tx for tx in mock_database["transactions"] if tx["user_id"] == user_id
    ]
    return MockResponse(200, {"data": transactions})

def handle_transaction():
    # Controlla se ci sono transazioni nel mock_database
    transactions = mock_database.get("transactions", [])
    if not transactions:
        return MockResponse(404, {"error": "No transactions found."})
    return MockResponse(200, {"data": transactions, "message": "Transactions retrieved successfully."})

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

patch_requests_get.start()
patch_requests_post.start()
patch_requests_put.start()
