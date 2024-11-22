from flask import Flask, jsonify, request

import requests
import utils as u
# from src import utils as u

app = Flask(__name__)


# Funzione helper per effettuare richieste verso l'API remota
def perform_request(method, endpoint, json_data=None):
    url = u.DB_MANAGER_URL + endpoint
    response = requests.request(method, url, json=json_data, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code
    return response


# INIZIO METODI PER VISUALIZZARE, AGGIUNGERE, AGGIORNARE E ELIMINARE GACHA


# Endpoint per aggiungere un nuovo gacha
@app.route('/gacha/add', methods=['POST'])
def add_gacha():
    u.reset_response()
    data = request.get_json()
    response = perform_request("POST", "/gacha/add", data)

    if isinstance(response, tuple):  # In caso di errore
        return response

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha added successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per aggiornare un gacha
@app.route('/gacha/update/<int:gacha_id>', methods=['PUT'])
def update_gacha(gacha_id):
    u.reset_response()
    data = request.get_json()
    response = perform_request("PUT", f"/gacha/update/{gacha_id}", data)

    if isinstance(response, tuple):  # In caso di errore
        return response

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha updated successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per eliminare un gacha
@app.route('/gacha/delete/<int:gacha_id>', methods=['DELETE'])
def delete_gacha(gacha_id):
    u.reset_response()
    response = perform_request("DELETE", f"/gacha/delete/{gacha_id}")

    if isinstance(response, tuple):  # In caso di errore
        return response

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha deleted successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per ottenere un singolo gacha
@app.route('/gacha/<int:gacha_id>', methods=['GET'])
def get_gacha(gacha_id):
    u.reset_response()
    response = perform_request("GET", f"/gacha/{gacha_id}")

    if isinstance(response, tuple):  # In caso di errore
        return response

    gacha = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gacha
    u.RESPONSE["message"] = "Gacha retrieved successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per ottenere tutti i gachas
@app.route('/gacha', methods=['GET'])
def get_all_gachas():
    u.reset_response()
    response = perform_request("GET", "/gacha")

    if isinstance(response, tuple):  # In caso di errore
        return response

    gachas = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gachas
    u.RESPONSE["message"] = "All gachas retrieved successfully!"
    return jsonify(u.RESPONSE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002, debug=u.FLASK_DEBUG)
