from flask import Flask, jsonify, request, Response
import requests
import utils as u

app = Flask(__name__)


@app.route('/')
def index():
    return {"message": "API Gateway is running"}


@app.route('/roll', methods=['GET'])
def roll():
    path = u.CURRENCY_SERVICE_URL + "/roll_info"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    data = response.json().get("data")
    url = data["Link"]
    path = u.CURRENCY_SERVICE_URL + "/roll_img"
    response = requests.get(path,
                            verify=False,
                            params={"url": url})
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE)

    return Response(
        response.content,
        content_type=response.headers['Content-Type'],
        status=response.status_code
    )


@app.route('/buy_currency', methods=['PUT'])
def buy_currency():
    data = request.get_json()
    quantity = data.get('quantity')
    if quantity is None:
        u.bad_request()
        return jsonify(u.RESPONSE)

    path = u.CURRENCY_SERVICE_URL + "/buy_currency"
    response = requests.put(path,
                            verify=False,
                            json={"quantity": quantity})
    return jsonify(response.json())


# INIZIO ENDPOINT DEL GACHASERVICE_URL ==>

# Endpoint per aggiungere un nuovo gacha
@app.route('/gacha/add', methods=['POST'])
def add_gacha():
    u.reset_response()

    # Recupera i dati JSON dalla richiesta
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Missing or invalid JSON payload")
    except Exception as e:
        u.RESPONSE["code"] = 400
        u.RESPONSE["message"] = f"Invalid request: {str(e)}"
        return jsonify(u.RESPONSE), 400

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + "gacha/add"

    # Effettua la richiesta POST al servizio remoto
    response = requests.post(url,
                             verify=False,
                             json=data,
                             headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha added successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per aggiornare un gacha
@app.route('/gacha/update/<int:gacha_id>', methods=['PUT'])
def update_gacha(gacha_id):
    u.reset_response()

    # Recupera i dati JSON dalla richiesta
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Missing or invalid JSON payload")
    except Exception as e:
        u.RESPONSE["code"] = 400
        u.RESPONSE["message"] = f"Invalid request: {str(e)}"
        return jsonify(u.RESPONSE), 400

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + f"gacha/update/{gacha_id}"

    # Effettua la richiesta PUT al servizio remoto
    response = requests.put(url,
                            verify=False,
                            json=data,
                            headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha updated successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per eliminare un gacha
@app.route('/gacha/delete/<int:gacha_id>', methods=['DELETE'])
def delete_gacha(gacha_id):
    u.reset_response()

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + f"gacha/delete/{gacha_id}"

    # Effettua la richiesta DELETE al servizio remoto
    response = requests.delete(url)

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code

    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = []
    u.RESPONSE["message"] = "Gacha deleted successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per ottenere un singolo gacha
@app.route('/gacha/<int:gacha_id>', methods=['GET'])
def get_gacha(gacha_id):
    u.reset_response()

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + f"/gacha/{gacha_id}"

    # Effettua la richiesta GET al servizio remoto
    response = requests.get(url, verify=False)

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code

    gacha = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gacha
    u.RESPONSE["message"] = "Gacha retrieved successfully!"
    return jsonify(u.RESPONSE)


# Endpoint per ottenere tutti i gachas
@app.route('/gacha', methods=['GET'])
def get_all_gachas():
    u.reset_response()

    # URL completo del servizio remoto
    url = u.GACHA_SERVICE_URL + "/gacha"

    # Effettua la richiesta GET al servizio remoto
    response = requests.get(url, verify=False)

    if response.status_code != 200:
        u.handle_error(response.status_code)
        return jsonify(u.RESPONSE), response.status_code

    gachas = response.json().get("data")
    u.RESPONSE["code"] = 200
    u.RESPONSE["data"] = gachas
    u.RESPONSE["message"] = "All gachas retrieved successfully!"
    return jsonify(u.RESPONSE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=u.FLASK_DEBUG)
