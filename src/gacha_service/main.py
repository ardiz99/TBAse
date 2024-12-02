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



# Endpoint per ottenere un singolo gacha dell'utente loggato
@app.route('/mygacha/<int:gacha_id>', methods=['GET'])
def get_mygacha(gacha_id):
    u.reset_response()
    user_id = 2  # Passiamo l'user_id come 0 per testing
    response = perform_request("GET", f"/get_gacha_of_user/{user_id}")
    if isinstance(response, tuple):  # In caso di errore
        return response
    gachaIds = response.json().get("data")
    if not gachaIds:
        u.RESPONSE["code"] = 404
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "No expired gacha found"
        return jsonify(u.RESPONSE)

    if gacha_id in gachaIds:
        response = perform_request("GET", f"/admin_gacha/get/{gacha_id}")
        if isinstance(response, tuple):  # In caso di errore
            return response
        gacha = response.json().get("data")
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = gacha
        u.RESPONSE["message"] = "Gacha retrieved successfully!"
        return jsonify(u.RESPONSE)
    else:
        u.RESPONSE["code"] = 404
        u.RESPONSE["data"] = "Gacha Not Found in Collection"
        u.RESPONSE["message"] = "Gacha Not Found in Collection!"


# Endpoint per ottenere tutti i gacha dell'utente loggato
@app.route('/mygacha', methods=['GET'])
def get_allmygacha():
    u.reset_response()
    user_id = 2  # Passiamo l'user_id come 0 per testing
    response = perform_request("GET", f"/get_gacha_of_user/{user_id}")
    if isinstance(response, tuple):  # In caso di errore
        return response
    gachaIds = response.json().get("data")
    if not gachaIds:
        u.RESPONSE["code"] = 404
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "No expired gacha found"
        return jsonify(u.RESPONSE)
    result = []
    for gacha_id in gachaIds:
        response = perform_request("GET", f"/admin_gacha/get/{gacha_id}")
        if isinstance(response, tuple):  # In caso di errore
            return response
        gacha = response.json().get("data")
        result.append(gacha)
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = result
    u.RESPONSE["message"] = "Gacha retrieved successfully!"
    return jsonify(u.RESPONSE)    



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002, debug=u.FLASK_DEBUG)
