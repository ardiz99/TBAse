from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

RESPONSE = {
    "code": 200,
    "data": []
}

connection = None


#
# def set_not_found():
#     global CODES
#     CODES["200"] = 0
#     CODES["404"] = 1
#
#
# def set_generic_error():
#     global CODES
#     CODES["200"] = 0
#     CODES["500"] = 1


# def send_response(response=""):
#     global CODES
#     if CODES["200"] == 1:
#         return jsonify(response), 200
#     elif CODES["404"] == 1:
#         return jsonify("Error! Not Found."), 404
#     else:
#         return jsonify("Unkonwn error"), 500


def reset_response():
    RESPONSE["code"] = 200
    RESPONSE["data"] = []


# Funzione per inizializzare la connessione
def init_db_connection():
    global connection
    try:
        connection = mysql.connector.connect(
            # host="localhost",
            # user="root",
            # password="diego",
            # database="ase"
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        if connection.is_connected():
            print("Connessione al database MySQL riuscita.")
            print(connection.server_host)
            print(connection.server_port)
            print(os.getenv('DB_HOST'))
            print(os.getenv('DB_USER'))
            print(os.getenv('DB_PASSWORD'))
            print(os.getenv('DB_NAME'))
    except Error as e:
        print(f"Errore di connessione a MySQL: {e}")


# Funzione per chiudere la connessione
def close_db_connection():
    global connection
    if connection and connection.is_connected():
        connection.close()
        print("Connessione al database MySQL chiusa.")


@app.route('/roll')
def roll_gacha():
    rarity = request.args.get('rarity')
    # rarity = "Legendary"

    reset_response()

    global connection
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        return jsonify("Unkonwn error"), 505
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM gacha WHERE Rarity = '{}';".format(rarity)
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            jsonify("Error! Not Found."), 404

        cursor.close()
        close_db_connection()
        RESPONSE["code"] = 200
        RESPONSE["data"] = result
        return jsonify(RESPONSE)
    except Error as e:
        return jsonify("Unkonwn error"), 505


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8005)
