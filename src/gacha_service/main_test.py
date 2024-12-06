import main as main_app
from unittest.mock import patch
from flask import request

flask_app = main_app.app

# Simulazione di un database
mock_database = {
    "gacha": {  # Gacha items nel sistema
        1: {"GachaId": 1, "Name": "Legendary Sword", "Rarity": "Legendary"},
        2: {"GachaId": 2, "Name": "Epic Shield", "Rarity": "Epic"},
    },
    "user_gachas": {  # Relazione tra utenti e i loro Gacha
        "alice@example.com": [1, 2],  # L'utente con ID 2 possiede i Gacha con ID 1 e 2
    },
}

def mock_save_last(op, args, res):
    print(f"Mock save_last: {op} {args} {res}")

main_app.save_last = mock_save_last

# Mock della funzione `perform_request`
def mock_perform_request(method, endpoint, json_data=None):
    print(f"Mock {method} to {endpoint} with data {json_data}")

    if "/add" in endpoint and method == "POST":
        new_id = max(mock_database["gacha"].keys()) + 1
        mock_database["gacha"][new_id] = json_data
        return MockResponse(200, {"message": "Gacha added successfully!"})

    if "/update" in endpoint and method == "PUT":
        gacha_id = int(endpoint.split("/")[-1])
        if gacha_id in mock_database["gacha"]:
            mock_database["gacha"][gacha_id].update(json_data)
            return MockResponse(200, {"message": "Gacha updated successfully!"})
        return MockResponse(404, {"error": "Gacha not found"})

    if "/delete" in endpoint and method == "DELETE":
        gacha_id = int(endpoint.split("/")[-1])
        if gacha_id in mock_database["gacha"]:
            del mock_database["gacha"][gacha_id]
            return MockResponse(200, {"message": "Gacha deleted successfully!"})
        return MockResponse(404, {"error": "Gacha not found"})

    if "/get/" in endpoint:
        try:
            gacha_id = int(endpoint.split("/")[-1])
        except ValueError:
            return MockResponse(400, {"error": "Invalid Gacha ID"})

        gacha = mock_database["gacha"].get(gacha_id)
        if not gacha:
            return MockResponse(404, {"error": f"Gacha with ID {gacha_id} not found"})
        return MockResponse(200, {"data": gacha})

    if "/getName/" in endpoint and method == "GET":
        gacha_name = endpoint.split("/")[-1]
        for gacha in mock_database["gacha"].values():
            if gacha["Name"] == gacha_name:
                return MockResponse(200, {"data": gacha})
        return MockResponse(404, {"error": "Gacha not found"})

    if "/get" in endpoint and method == "GET":
        return MockResponse(200, {"data": list(mock_database["gacha"].values())})

    if "/get_gacha_of_user/" in endpoint:
        email = endpoint.split("/")[-1]
        user_gachas = mock_database["user_gachas"].get(email, [])
        return MockResponse(200, {"data": user_gachas})


# Classe per simulare una risposta
class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json


# Applicazione dei mock
patch_perform_request = patch("main.perform_request", side_effect=mock_perform_request)
patch_perform_request.start()
