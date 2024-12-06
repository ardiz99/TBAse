import main as main_app
from unittest.mock import patch
from datetime import datetime

flask_app = main_app.app

# Database simulato in memoria
mock_database = {
    "users": {
        "alice@example.com": {
            "UserId": 1,
            "FirstName": "Alice",
            "LastName": "Doe",
            "Email": "alice@example.com",
            "Password": "hashed_password",
            "CurrencyAmount": 500,
            "Salt": "random_salt"
        }
    },
    "gacha_items": {
        "101": {
            "GachaId": 101,
            "Name": "Legendary Sword",
            "Type1": "Steel",
            "Type2": "None",
            "Total": 600,
            "HP": 100,
            "Attack": 150,
            "Defense": 100,
            "SpAtt": 120,
            "SpDef": 100,
            "Speed": 130,
            "Rarity": "Legendary",
            "Link": "link_to_image"
        },
        "102": {
            "GachaId": 102,
            "Name": "Epic Shield",
            "Type1": "Steel",
            "Type2": "None",
            "Total": 500,
            "HP": 120,
            "Attack": 90,
            "Defense": 150,
            "SpAtt": 80,
            "SpDef": 140,
            "Speed": 50,
            "Rarity": "Epic",
            "Link": "link_to_image"
        }
    },
    "transactions": {}  # Questa tabella gestisce sia le transazioni che le aste
}


# Mock per il salvataggio delle operazioni
def mock_save_last(op, args, res):
    print(f"Mock save_last: {op} {args} {res}")


main_app.mock_save_last = mock_save_last


# Mock per le richieste GET
def mock_requests_get(url, params=None, **kwargs):
    print(f"Mock GET to {url} with params {params}")

    if "/user/get_by_email" in url:
        return handle_get_user_by_email(params)
    if "/auction" in url and "get_bid" in url:
        return handle_get_auction_bid(url)
    if "/transaction_history" in url:
        return handle_transaction_history(url)
    if "/active_auction" in url:
        return handle_get_active_auctions()
    if "/get_amount" in url:
        return handle_get_amount(params)
    if "/get_gacha_by_rarity" in url:
        return handle_get_gacha_by_rarity(params)
    if "/auction/" in url and url.endswith("/get_bid"):
        return handle_get_auction_bid(url)
    if "/transaction" in url and url.endswith("/delete"):
        return handle_delete_transaction(url)
    if "/transaction/" in url:
        return handle_get_specific_transaction(url)
    if "/auction/history" in url:
        return handle_get_old_auctions()
    if "/auction" in url:
        return handle_get_specific_auction(url)
    if "/transaction" in url:
        return handle_get_all_transactions()

    return MockResponse(404, {"error": "Endpoint not found or unsupported GET method"})


# Mock per le richieste POST
def mock_requests_post(url, json=None, **kwargs):
    print(f"Mock POST to {url} with json {json}")

    if "/roll" in url:
        return handle_roll(json)
    if "/new_auction" in url:
        return handle_new_auction(json)
    if "/register" in url:
        return handle_register_user(json)
    if "/transaction" in url:
        return handle_create_transaction(json)

    return MockResponse(404, {"error": "Endpoint not found or unsupported POST method"})


# Mock per le richieste PUT
def mock_requests_put(url, json=None, **kwargs):
    print(f"Mock PUT to {url} with json {json}")

    if "/update_amount" in url:
        return handle_update_amount(json)
    if "/auction/" in url and "update_actual_price" in url:
        return handle_update_auction_price(json)
    if "/close_auction" in url:
        return handle_close_auction(url)
    if "/transaction/" in url and "/sended_to" in url:
        return handle_update_sended_to(json)
    if "/buy_currency" in url:
        return handle_buy_currency(json)

    return MockResponse(404, {"error": "Endpoint not found or unsupported PUT method"})


# Funzioni specifiche per la gestione dei vari endpoint
def handle_get_user_by_email(params):
    email = params.get("email")
    if email not in mock_database["users"]:
        return MockResponse(400, {"error": "User not found"})
    user = mock_database["users"][email]
    return MockResponse(200, {"data": {
        "UserId": user["UserId"],
        "FirstName": user["FirstName"],
        "LastName": user["LastName"],
        "Email": user["Email"],
        "CurrencyAmount": user["CurrencyAmount"],
        "Salt": user["Salt"]
    }})


def handle_get_auction_bid(url):
    transaction_id = int(url.split("/")[-2])
    if transaction_id not in mock_database["transactions"]:
        return MockResponse(404, {"error": "Auction not found"})
    transaction = mock_database["transactions"][transaction_id]
    if transaction["UserOwner"] is None:
        return MockResponse(404, {"error": "Auction not found"})
    return MockResponse(200, {"data": transaction})


def handle_transaction_history(url):
    user_id = int(url.split("/")[-1])
    transactions = []
    for transaction in mock_database["transactions"].values():
        if transaction["RequestingUser"] == user_id or transaction.get("UserOwner") == user_id:
            transactions.append(transaction)
    return MockResponse(200, {"data": transactions})


def handle_get_active_auctions():
    active_auctions = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for auction in mock_database["transactions"].values():
        if auction["UserOwner"] is not None and auction["EndDate"] > current_time:
            active_auctions.append(auction)
    return MockResponse(200, {"data": active_auctions})


def handle_roll(data):
    # Simula la creazione di una transazione di "roll"
    required_fields = ["user_id", "gacha_id", "cost", "end_date"]
    for field in required_fields:
        if field not in data:
            return MockResponse(400, {"error": f"Bad request, missing parameter: {field}"})

    transaction_id = len(mock_database["transactions"]) + 1
    mock_database["transactions"][transaction_id] = {
        "RequestingUser": data["user_id"],
        "GachaId": data["gacha_id"],
        "StartingPrice": data["cost"],
        "ActualPrice": data["cost"],
        "EndDate": data["end_date"]
    }
    return MockResponse(200, {"message": "Roll transaction created successfully"})


def handle_new_auction(data):
    # Simula la creazione di una nuova asta
    required_fields = ["user_owner", "gacha_id", "starting_price", "end_date"]
    for field in required_fields:
        if field not in data:
            return MockResponse(400, {"error": f"Bad request, missing parameter: {field}"})

    auction_id = len(mock_database["transactions"]) + 1
    mock_database["transactions"][auction_id] = {
        "UserOwner": data["user_owner"],
        "GachaId": data["gacha_id"],
        "StartingPrice": data["starting_price"],
        "EndDate": data["end_date"],
        "ActualPrice": data["starting_price"],
        "RequestingUser": None
    }
    return MockResponse(200, {"message": "Auction created successfully"})


def handle_update_amount(data):
    email = data.get("email")
    new_amount = data.get("new_amount")

    if email not in mock_database["users"]:
        return MockResponse(400, {"error": "User not found"})
    if new_amount < 0:
        return MockResponse(400, {"error": "Amount cannot be negative"})

    mock_database["users"][email]["CurrencyAmount"] = new_amount
    return MockResponse(200, {"message": "Amount updated successfully"})


def handle_update_auction_price(data):
    bid = data.get("bid")
    requesting_user = data.get("requesting_user")
    auction_id = int(data.get("auction_id"))

    if auction_id not in mock_database["transactions"]:
        return MockResponse(404, {"error": "Auction not found"})

    mock_database["transactions"][auction_id]["ActualPrice"] = bid
    mock_database["transactions"][auction_id]["RequestingUser"] = requesting_user
    return MockResponse(200, {"message": "Auction price updated successfully"})


def handle_get_amount(params):
    email = params.get("email")
    if email not in mock_database["users"]:
        return MockResponse(400, {"error": "User not found"})
    user = mock_database["users"][email]
    return MockResponse(200, {"data": {"CurrencyAmount": user["CurrencyAmount"]}})


def handle_buy_currency(data):
    email = data.get("email")
    quantity = data.get("quantity")

    # Controllo parametri
    if not email or quantity is None:
        return MockResponse(400, {"error": "Email and quantity are required"})

    if quantity <= 0:
        return MockResponse(400, {"error": "You can't add a negative or zero quantity."})

    # Controllo esistenza utente
    if email not in mock_database["users"]:
        return MockResponse(404, {"error": "User not found"})

    # Aggiorno il valore della valuta
    current_amount = mock_database["users"][email]["CurrencyAmount"]
    new_amount = current_amount + quantity
    mock_database["users"][email]["CurrencyAmount"] = new_amount

    return MockResponse(200, {"message": f"Currency amount updated successfully. New amount: {new_amount}"})


def handle_get_gacha_by_rarity(params):
    rarity = params.get("rarity")
    gacha_items = [item for item in mock_database["gacha_items"].values() if item["Rarity"] == rarity]
    if not gacha_items:
        return MockResponse(400, {"error": "Invalid rarity"})
    return MockResponse(200, {"data": gacha_items})


def handle_register_user(data):
    required_fields = ["FirstName", "LastName", "Email", "Password", "Salt", "CurrencyAmount"]
    for field in required_fields:
        if field not in data:
            return MockResponse(400, {"error": f"Missing registration data: {field}"})

    email = data['Email']
    if email in mock_database['users']:
        return MockResponse(400, {"error": "User already exists"})

    user_id = len(mock_database['users']) + 1
    mock_database['users'][email] = {
        "UserId": user_id,
        "FirstName": data['FirstName'],
        "LastName": data['LastName'],
        "Email": data['Email'],
        "Password": data['Password'],
        "Salt": data['Salt'],
        "CurrencyAmount": data['CurrencyAmount']
    }
    return MockResponse(200, {"message": "User registered successfully"})


def handle_create_transaction(data):
    required_fields = ["user_id", "gacha_id", "cost", "end_date"]
    for field in required_fields:
        if field not in data:
            return MockResponse(400, {"error": f"Missing transaction data: {field}"})

    transaction_id = len(mock_database['transactions']) + 1
    mock_database['transactions'][transaction_id] = {
        "RequestingUser": data['user_id'],
        "GachaId": data['gacha_id'],
        "StartingPrice": data['cost'],
        "ActualPrice": data['cost'],
        "EndDate": data['end_date']
    }
    return MockResponse(200, {"message": "Transaction created successfully"})


def handle_close_auction(url):
    transaction_id = int(url.split("/")[-2])
    if transaction_id not in mock_database['transactions']:
        return MockResponse(404, {"error": "Auction not found"})
    mock_database['transactions'][transaction_id]['EndDate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return MockResponse(200, {"message": "Auction closed successfully"})


def handle_update_sended_to(data):
    transaction_id = data.get("transaction_id")
    sended_to = data.get("sended_to")
    if transaction_id not in mock_database['transactions']:
        return MockResponse(404, {"error": "Transaction not found"})
    mock_database['transactions'][transaction_id]['SendedTo'] = sended_to
    return MockResponse(200, {"message": "Transaction updated with SendedTo"})


def handle_delete_transaction(url):
    transaction_id = int(url.split("/")[-2])
    if transaction_id not in mock_database['transactions']:
        return MockResponse(404, {"error": "Transaction not found"})
    del mock_database['transactions'][transaction_id]
    return MockResponse(200, {"message": "Transaction deleted successfully"})


def handle_get_specific_transaction(url):
    transaction_id = int(url.split("/")[-1])
    if transaction_id not in mock_database['transactions']:
        return MockResponse(404, {"error": "Transaction not found"})
    return MockResponse(200, {"data": mock_database['transactions'][transaction_id]})


def handle_get_all_transactions():
    return MockResponse(200, {"data": list(mock_database['transactions'].values())})


def handle_get_specific_auction(url):
    transaction_id = int(url.split("/")[-1])
    if transaction_id not in mock_database['transactions'] or mock_database['transactions'][transaction_id][
        'UserOwner'] is None:
        return MockResponse(404, {"error": "Auction not found"})
    return MockResponse(200, {"data": mock_database['transactions'][transaction_id]})


def handle_get_old_auctions():
    old_auctions = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for auction in mock_database['transactions'].values():
        if auction['UserOwner'] is not None and auction['EndDate'] < current_time:
            old_auctions.append(auction)
    return MockResponse(200, {"data": old_auctions})


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

patch_requests_get.start()
patch_requests_post.start()
patch_requests_put.start()
