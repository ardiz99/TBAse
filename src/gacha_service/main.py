from flask import Flask, jsonify, request

import requests
import utils as u

# from src import utils as u

app = Flask(__name__)


# Funzione helper per effettuare richieste verso l'API remota
def perform_request(method, endpoint, json_data=None):
    url = u.DB_MANAGER_URL + "/gacha" + endpoint
    response = requests.request(method, url, json=json_data, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code
    return response


# INIZIO METODI PER VISUALIZZARE, AGGIUNGERE, AGGIORNARE E ELIMINARE GACHA

# Endpoint per aggiungere un nuovo gacha
@app.route('/add', methods=['POST'])
def add_gacha():
    u.reset_response()
    data = request.get_json()
    response = perform_request("POST", "/add", data)
    if isinstance(response, tuple):  # In caso di errore
        return response
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha added successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per aggiornare un gacha
@app.route('/update/<int:gacha_id>', methods=['PUT'])
def update_gacha(gacha_id):
    u.reset_response()
    data = request.get_json()
    response = perform_request("PUT", f"/update/{gacha_id}", data)
    if isinstance(response, tuple):  # In caso di errore
        return response
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha modified successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per eliminare un gacha
@app.route('/delete/<int:gacha_id>', methods=['DELETE'])
def delete_gacha(gacha_id):
    u.reset_response()
    response = perform_request("DELETE", f"/delete/{gacha_id}")
    if isinstance(response, tuple):  # In caso di errore
        return response
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha deleted successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per ottenere un singolo gacha
@app.route('/get/<int:gacha_id>', methods=['GET'])
def get_gacha(gacha_id):
    u.reset_response()
    response = perform_request("GET", f"/get/{gacha_id}")

    if isinstance(response, tuple):  # In caso di errore
        return response
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    gacha = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gacha
    u.RESPONSE["message"] = "Gacha retrivied successfully!"
    return jsonify(u.RESPONSE)


@app.route('/getName/<string:gacha_name>', methods=['GET'])
def get_gacha_by_name(gacha_name):
    u.reset_response()
    response = perform_request("GET", f"/getName/{gacha_name}")
    if isinstance(response, tuple):
        return response
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    gacha = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gacha
    u.RESPONSE["message"] = "Gacha retrivied successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per ottenere tutti i gachas
@app.route('/get', methods=['GET'])
def get_all_gachas():
    u.reset_response()
    response = perform_request("GET", "/get")

    if isinstance(response, tuple):  # In caso di errore
        return response
    status_code = response.status_code
    if status_code == 404:
        u.not_found("Gacha not found")
        return u.send_response()
    if status_code == 500:
        u.generic_error("Server error occurred")
        return u.send_response()
    gacha = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gacha
    u.RESPONSE["message"] = "Gacha retrivied successfully!"
    return jsonify(u.RESPONSE)


@app.route('/mygacha/<string:email>/<int:gacha_id>', methods=['GET'])
def get_mygacha(email, gacha_id):
    u.reset_response()
    response = perform_request("GET", f"/get_gacha_of_user/{email}")
    if isinstance(response, tuple):  # In caso di errore
        return response
    gachaIds = response.json().get("data")
    if not gachaIds:
        u.RESPONSE["code"] = 404
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "No expired gacha found"
        return jsonify(u.RESPONSE)

    if gacha_id in gachaIds:
        response = perform_request("GET", f"/get/{gacha_id}")
        if isinstance(response, tuple):  # In caso di errore
            return response
        gacha = response.json().get("data")
        u.RESPONSE["data"] = gacha
        u.RESPONSE["code"] = 200
        u.RESPONSE["message"] = "Gacha retrivied succesfully"
        return jsonify(u.RESPONSE)
    else:
        u.RESPONSE["code"] = 404
        u.RESPONSE["data"] = "Gacha Not Found in Collection"
        u.RESPONSE["message"] = "Gacha Not Found in Collection!"


# Endpoint per ottenere tutti i gacha dell'utente loggato
@app.route('/mygacha/<string:email>', methods=['GET'])
def get_allmygacha(email):
    u.reset_response()
    response = perform_request("GET", f"/get_gacha_of_user/{email}")
    if isinstance(response, tuple):  # In caso di errore
        return response
    gachaIds = response.json().get("data")
    if not gachaIds:
        u.RESPONSE["code"] = 404
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "No expired gacha found"
        return jsonify(u.RESPONSE)
    if isinstance(response, tuple):  # In caso di errore
        return response
    gachaIds = response.json().get("data")
    if not gachaIds:
        u.RESPONSE["code"] = 404
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "No gacha found in your account"
        return jsonify(u.RESPONSE)
    result = []
    for gacha_id in gachaIds:
        response = perform_request("GET", f"/get/{gacha_id}")
        if isinstance(response, tuple):  # In caso di errore
            return response
        gacha = response.json().get("data")
        result.append(gacha)
    u.RESPONSE["data"] = result
    u.RESPONSE["code"] = 200
    u.RESPONSE["message"] = "Gachas retrivied succesfully"
    return jsonify(u.RESPONSE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002, debug=u.FLASK_DEBUG)
