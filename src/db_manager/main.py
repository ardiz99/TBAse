from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import os
import utils as u

# from src import utils as u

app = Flask(__name__)

connection = None


# Funzione per inizializzare la connessione
def init_db_connection():
    global connection
    try:
        if connection is None or not connection.is_connected():
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
        connection = None


# Funzione per chiudere la connessione
def close_db_connection():
    global connection
    if connection and connection.is_connected():
        connection.close()
        print("Connessione al database MySQL chiusa.")
        connection = None


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
        print(query)
        print(result)

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
        result = cursor.fetchone()
        print(query)
        print(result)

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


@app.route('/update_amount', methods=['PUT'])
def update_amount():
    data = request.get_json()
    new_amount = data.get('new_amount')
    email = data.get('email')
    # new_amount = 10
    # email = "taylor.smith@example.com"
    u.reset_response()

    global connection
    init_db_connection()

    if connection is None:
        u.generic_error()
        return jsonify(u.RESPONSE)
    try:
        cursor = connection.cursor(dictionary=True)
        query = "UPDATE user " \
                "SET CurrencyAmount = {}" \
                " WHERE Email = '{}';".format(new_amount, email)
        cursor.execute(query)

        connection.commit()

        query = "SELECT CurrencyAmount " \
                "FROM user " \
                "WHERE Email = '{}';".format(email)
        cursor.execute(query)
        result = cursor.fetchall()
        print(query)
        print(result)

        cursor.close()
        close_db_connection()

        u.reset_response()
        return jsonify(u.RESPONSE)
    except Error as e:
        u.generic_error()
        return jsonify(u.RESPONSE)


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    data = request.get_json()
    user_id = data.get('user_id')
    gacha_id = data.get('gacha_id')
    cost = data.get('cost')
    datetime = data.get('end_date')
    u.reset_response()

    global connection
    init_db_connection()

    if connection is None:
        u.generic_error()
        return jsonify(u.RESPONSE)
    try:
        cursor = connection.cursor(dictionary=True)
        query = f"INSERT INTO transaction (RequestingUser, GachaId, Cost, EndDate) " \
                f"VALUES ({user_id}, {gacha_id}, {cost}, \"{datetime}\")"

        print(query)
        cursor.execute(query)
        connection.commit()

        # query = f"SELECT * " \
        #         f"FROM transaction " \
        #         f"WHERE RequestingUser = {user_id};"
        # cursor.execute(query)
        # result = cursor.fetchall()
        # print(query)
        # print(result)

        cursor.close()
        close_db_connection()

        u.reset_response()
        return jsonify(u.RESPONSE)

    except Error as e:
        u.generic_error()
        return jsonify(u.RESPONSE)


# INIZIO METODI DEL DBMANGER PER ESEGUIRE LE QUERY DEL GACHASERVICE
@app.route('/gacha/add', methods=['POST'])
def add_gacha():
    data = request.get_json()
    u.reset_response()
    init_db_connection()
    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return jsonify(u.RESPONSE)

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO gacha (Name, Type1, Type2, Total, HP, Attack, Defense, SpAtt, SpDef, Speed, Rarity, Link) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data['Name'], data['Type1'], data['Type2'], data['Total'], data['HP'],
            data['Attack'], data['Defense'], data['SpAtt'], data['SpDef'],
            data['Speed'], data['Rarity'], data['Link']
        )
        cursor.execute(query, values)
        connection.commit()  # Conferma le modifiche nel database
        print(f"Query eseguita: {query}")

        cursor.close()
        close_db_connection()

        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "Gacha added successfully!"
        return jsonify(u.RESPONSE)

    except Error as e:
        print(f"Errore durante l'inserimento nel database: {e}")
        u.generic_error("Errore durante l'inserimento nel database.")
        return jsonify(u.RESPONSE)


@app.route('/gacha/update/<int:gacha_id>', methods=['PUT'])
def update_gacha(gacha_id):
    data = request.get_json()
    u.reset_response()
    init_db_connection()
    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return jsonify(u.RESPONSE)

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM gacha WHERE GachaId = %s", (gacha_id,))
        gacha = cursor.fetchone()
        if not gacha:
            u.not_found
            return jsonify(u.RESPONSE)

        query = "UPDATE gacha " \
                "SET Name = %s, Type1 = %s, Type2 = %s, Total = %s, HP = %s, Attack = %s, Defense = %s, SpAtt = %s, " \
                "SpDef = %s, Speed = %s, Rarity = %s, Link = %s" \
                "WHERE GachaId = %s"
        values = (
            data.get('Name', gacha[1]), data.get('Type1', gacha[2]), data.get('Type2', gacha[3]),
            data.get('Total', gacha[4]), data.get('HP', gacha[5]), data.get('Attack', gacha[6]),
            data.get('Defense', gacha[7]), data.get('SpAtt', gacha[8]), data.get('SpDef', gacha[9]),
            data.get('Speed', gacha[10]), data.get('Rarity', gacha[11]), data.get('Link', gacha[12]),
            gacha_id
        )
        cursor.execute(query, values)
        connection.commit()
        print(f"Query eseguita: {query}")
        cursor.close()
        close_db_connection()
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "Gacha modified successfully!"
        return jsonify(u.RESPONSE)

    except Error as e:
        print(f"Errore durante la modifica nel database: {e}")
        u.generic_error("Errore durante la modifica nel database.")
        return jsonify(u.RESPONSE)


@app.route('/gacha/delete/<int:gacha_id>', methods=['DELETE'])
def delete_gacha(gacha_id):
    u.reset_response()
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return jsonify(u.RESPONSE)

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM gacha WHERE GachaId = %s", (gacha_id,))
        gacha = cursor.fetchone()
        if not gacha:
            u.not_found()
            return jsonify(u.RESPONSE)

        cursor.execute("DELETE FROM gacha WHERE GachaId = %s", (gacha_id,))
        connection.commit()
        print(f"Gacha con ID {gacha_id} eliminato correttamente.")
        cursor.close()
        close_db_connection()

        u.RESPONSE["code"] = 200
        u.RESPONSE["message"] = "Gacha deleted successfully!"
        return jsonify(u.RESPONSE)

    except Error as e:
        print(f"Errore durante l'eliminazione del gacha: {e}")
        u.generic_error("Errore durante l'eliminazione del gacha.")
        return jsonify(u.RESPONSE)


@app.route('/gacha/<int:gacha_id>', methods=['GET'])
def get_gacha(gacha_id):
    u.reset_response()
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return jsonify(u.RESPONSE)

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gacha WHERE GachaId = %s", (gacha_id,))
        gacha = cursor.fetchone()
        if gacha is None:
            u.not_found()
            return jsonify(u.RESPONSE)

        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = gacha
        u.RESPONSE["message"] = "Gacha retrieved successfully!"
        cursor.close()
        close_db_connection()
        return jsonify(u.RESPONSE)

    except Error as e:
        print(f"Errore durante il recupero del gacha: {e}")
        u.generic_error("Errore durante il recupero del gacha.")
        return jsonify(u.RESPONSE)


@app.route('/gacha', methods=['GET'])
def get_all_gachas():
    u.reset_response()
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return jsonify(u.RESPONSE)

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gacha")
        gachas = cursor.fetchall()

        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = gachas
        u.RESPONSE["message"] = "All gachas retrieved successfully!"
        cursor.close()
        close_db_connection()
        return jsonify(u.RESPONSE)

    except Error as e:
        print(f"Errore durante il recupero di tutti i gachas: {e}")
        u.generic_error("Errore durante il recupero di tutti i gachas.")
        return jsonify(u.RESPONSE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8005, debug=u.FLASK_DEBUG)
