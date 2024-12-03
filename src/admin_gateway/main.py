from flask import Flask, jsonify, request, Response
import requests
import utils as u

# from src import utils as u

app = Flask(__name__)


@app.route('/')
def index():
    return {"message": "API Gateway is running for admin"}


# INIZIO ENDPOINT PER IL MARKET-SERVICE ==>
@app.route('/auction')
def get_all_auctions():
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()

    path = u.MARKET_SERVICE_URL + "/auction"
    response = requests.get(path,
                            verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/auction/<int:transaction_id>')
def get_specific_auction(transaction_id):
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()

    path = u.MARKET_SERVICE_URL + f"/auction/{transaction_id}"
    response = requests.get(path,
                            verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/end_auction/<int:transaction_id>', methods=['PUT'])
def end_auction(transaction_id):
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()

    path = u.MARKET_SERVICE_URL + f"/close_auction/{transaction_id}"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


@app.route('/auction/history', methods=['GET'])
def get_old_transaction():
    u.reset_response()
    enc_token = request.headers.get("token")
    if not u.check_token_admin(enc_token):
        return u.send_response()

    path = u.MARKET_SERVICE_URL + f"/auction/history"
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        u.handle_error(response.status_code)
        return u.send_response()

    u.set_response(response)
    return u.send_response()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=u.FLASK_DEBUG)
