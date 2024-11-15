from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import os
import utils as u

app = Flask(__name__)

connection = None


# Funzione per inizializzare la connessione
def init_db_connection():
    global connection
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="diego",
            database="ase"
            # host=os.getenv('DB_HOST'),
            # user=os.getenv('DB_USER'),
            # password=os.getenv('DB_PASSWORD'),
            # database=os.getenv('DB_NAME')
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


@app.route('/get_gacha_by_rarity')
def get_gacha_by_rarity():
    rarity = request.args.get('rarity')
    # rarity = "Legendary"

    u.reset_response()

    global connection
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error()
        return jsonify(u.RESPONSE)
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM gacha WHERE Rarity = '{}';".format(rarity)
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            u.not_found()
            return jsonify(u.RESPONSE)

        cursor.close()
        close_db_connection()
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = result
        u.RESPONSE["message"] = ""
        return jsonify(u.RESPONSE)
    except Error as e:
        u.generic_error()
        return jsonify(u.RESPONSE)


@app.route('/get_amount')
def get_amount():
    email = request.args.get('email')
    # email = "taylor.smith@example.com"

    u.reset_response()

    global connection
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error()
        return jsonify(u.RESPONSE)
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT CurrencyAmount FROM user WHERE Email = '{}';".format(email)
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        close_db_connection()

        if not result:
            u.not_found()
            return jsonify(u.RESPONSE)

        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = result
        return jsonify(u.RESPONSE)
    except Error as e:
        u.generic_error()
        return jsonify(u.RESPONSE)


@app.route('/update_amount')
def update_amount():
    new_amount = request.args.get('new_amount')
    email = request.args.get('email')
    # new_amount = 10
    # email = "taylor.smith@example.com"
    u.reset_response()

    global connection
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error()
        return jsonify(u.RESPONSE)
    try:
        cursor = connection.cursor(dictionary=True)
        query = "UPDATE user " \
                "SET CurrencyAmount = {}" \
                " WHERE Email = '{}';".format(new_amount, email)
        cursor.execute(query)

        # Salva le modifiche al database
        connection.commit()

        # query = "SELECT CurrencyAmount " \
        #         "FROM user " \
        #         "WHERE Email = '{}';".format(email)
        # cursor.execute(query)
        # result = cursor.fetchall()
        # print(result)

        cursor.close()
        close_db_connection()

        u.reset_response()
        return jsonify(u.RESPONSE)
    except Error as e:
        u.generic_error()
        return jsonify(u.RESPONSE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8005)
