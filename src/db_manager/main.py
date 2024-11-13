from flask import Flask, jsonify, make_response
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

CODES = {
    "200": 1,
    "404": 0,
    "500": 0
}

connection = None


def set_not_found():
    global CODES
    CODES["200"] = 0
    CODES["404"] = 1


def set_generic_error():
    global CODES
    CODES["200"] = 0
    CODES["500"] = 1


def send_response(response=""):
    global CODES
    if CODES["200"] == 1:
        return jsonify(response), 200
    elif CODES["404"] == 1:
        return jsonify("Error! Not Found."), 404
    else:
        return jsonify("Unkonwn error"), 500


# Funzione per inizializzare la connessione
def init_db_connection():
    global connection
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        if connection.is_connected():
            print("Connessione al database MySQL riuscita.")
    except Error as e:
        print(f"Errore di connessione a MySQL: {e}")


# Funzione per chiudere la connessione
def close_db_connection():
    global connection
    if connection and connection.is_connected():
        connection.close()
        print("Connessione al database MySQL chiusa.")


@app.route('/')
def roll_gacha():
    global connection
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        set_generic_error()
        return send_response()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM Gacha WHERE GachaId = 1"
        cursor.execute(query)
        result = cursor.fetchall()
        print(result)

        if not result:
            set_not_found()

        cursor.close()
        close_db_connection()
        return send_response(result)
    except Error as e:
        set_generic_error()
        return send_response()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8005)
