from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
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
                host=u.HOST,
                user=u.USER,
                password=u.PASSWORD,
                database=u.DATABASE
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


def handle_db_operation(query, values=None, fetch_one=False, fetch_all=False, commit=False):
    result = []
    u.reset_response()
    init_db_connection()

    if connection is None:
        u.generic_error('Database connection failed')
        return result

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, values)
        if commit:
            connection.commit()
        else:
            if fetch_one:
                result = cursor.fetchone()
            if fetch_all:
                result = cursor.fetchall()
            if not result:
                u.not_found()
            u.RESPONSE["data"] = result
    except Error as err:
        u.generic_error(str(err))
    finally:
        cursor.close()
        close_db_connection()


@app.route('/get_gacha_by_rarity')
def get_gacha_by_rarity():
    rarity = request.args.get('rarity')

    query = "SELECT * FROM gacha WHERE Rarity = %s"
    values = (rarity,)
    handle_db_operation(query, values, fetch_all=True)
    return u.send_response()


@app.route('/get_amount')
def get_amount():
    email = request.args.get('email')
    query = "SELECT CurrencyAmount FROM user WHERE Email = '{}';".format(email)
    handle_db_operation(query, fetch_one=True)
    return u.send_response()


@app.route('/update_amount', methods=['PUT'])
def update_amount():
    data = request.get_json()
    email = data.get('email')
    new_amount = data.get('new_amount')
    if not email or not new_amount:
        u.bad_request()
        return u.send_response()

    query = "UPDATE user " \
            "SET CurrencyAmount = %s" \
            " WHERE Email = %s;"
    values = (new_amount, email)
    handle_db_operation(query, values, commit=True)

    query = "SELECT CurrencyAmount " \
            "FROM user " \
            "WHERE Email = %s"
    values = (email,)
    handle_db_operation(query, values, fetch_one=True)
    return u.send_response()


@app.route('/get_id_by_email')
def get_id_by_email():
    email = request.args.get('email')
    query = "SELECT UserId " \
            "FROM user " \
            "WHERE Email = %s"
    values = (email,)
    handle_db_operation(query, values, fetch_one=True)
    return u.send_response()


# INIZIO METODI DEL DBMANGER PER ESEGUIRE LE QUERY DEL GACHASERVICE
@app.route('/gacha/add', methods=['POST'])
def add_gacha():
    data = request.get_json()
    u.reset_response()
    init_db_connection()
    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return u.send_response()

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
        return u.send_response()

    except Error as e:
        print(f"Errore durante l'inserimento nel database: {e}")
        u.generic_error("Errore durante l'inserimento nel database.")
        return u.send_response()


@app.route('/gacha/update/<int:gacha_id>', methods=['PUT'])
def update_gacha(gacha_id):
    data = request.get_json()
    u.reset_response()
    init_db_connection()
    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return u.send_response()

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM gacha WHERE GachaId = %s", (gacha_id,))
        gacha = cursor.fetchone()
        if not gacha:
            u.not_found
            return u.send_response()

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
        return u.send_response()

    except Error as e:
        print(f"Errore durante la modifica nel database: {e}")
        u.generic_error("Errore durante la modifica nel database.")
        return u.send_response()


@app.route('/gacha/delete/<int:gacha_id>', methods=['DELETE'])
def delete_gacha(gacha_id):
    u.reset_response()
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return u.send_response()

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM gacha WHERE GachaId = %s", (gacha_id,))
        gacha = cursor.fetchone()
        if not gacha:
            u.not_found()
            return u.send_response()

        cursor.execute("DELETE FROM gacha WHERE GachaId = %s", (gacha_id,))
        connection.commit()
        print(f"Gacha con ID {gacha_id} eliminato correttamente.")
        cursor.close()
        close_db_connection()

        u.RESPONSE["code"] = 200
        u.RESPONSE["message"] = "Gacha deleted successfully!"
        return u.send_response()

    except Error as e:
        print(f"Errore durante l'eliminazione del gacha: {e}")
        u.generic_error("Errore durante l'eliminazione del gacha.")
        return u.send_response()


@app.route('/gacha/<int:gacha_id>', methods=['GET'])
def get_gacha(gacha_id):
    u.reset_response()
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return u.send_response()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gacha WHERE GachaId = %s", (gacha_id,))
        gacha = cursor.fetchone()
        if gacha is None:
            u.not_found()
            return u.send_response()

        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = gacha
        u.RESPONSE["message"] = "Gacha retrieved successfully!"
        cursor.close()
        close_db_connection()
        return u.send_response()

    except Error as e:
        print(f"Errore durante il recupero del gacha: {e}")
        u.generic_error("Errore durante il recupero del gacha.")
        return u.send_response()


@app.route('/gacha', methods=['GET'])
def get_all_gachas():
    u.reset_response()
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return u.send_response()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gacha")
        gachas = cursor.fetchall()

        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = gachas
        u.RESPONSE["message"] = "All gachas retrieved successfully!"
        cursor.close()
        close_db_connection()
        return u.send_response()

    except Error as e:
        print(f"Errore durante il recupero di tutti i gachas: {e}")
        u.generic_error("Errore durante il recupero di tutti i gachas.")
        return u.send_response()


# INIZIO METODI PER USER =>

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    currencyAmount = data.get('CurrencyAmount')

    if not email or not password or not firstname or not lastname or not currencyAmount:
        u.generic_error("All field are required")
        return u.send_response()

    u.reset_response()

    try:
        # Connessione al database
        query = "INSERT INTO user (FirstName, LastName, Email, Password, CurrencyAmount) VALUES ("""
        query = query + "'{}',".format(firstname)
        query = query + "'{}',".format(lastname)
        query = query + "'{}',".format(email)
        query = query + "'{}',".format(password)
        query = query + "'{}');""".format(currencyAmount)
        handle_db_operation(query, commit=True)

        query = "SELECT * FROM user  WHERE Email = '{}';".format(email)
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/register_admin', methods=['POST'])
def register_admin():
    data = request.get_json()
    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    # currencyAmount = data.get('CurrencyAmount')

    if not email or not password or not firstname or not lastname:
        u.generic_error("All field are required")
        return u.send_response()

    u.reset_response()

    try:
        # Connessione al database
        query = "INSERT INTO admin (FirstName, LastName, Email, Password) VALUES ("""
        query = query + "'{}',".format(firstname)
        query = query + "'{}',".format(lastname)
        query = query + "'{}',".format(email)
        query = query + "'{}');""".format(password)
        handle_db_operation(query, commit=True)

        query = "SELECT * FROM user  WHERE Email = '{}';".format(email)
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/login', methods=['GET'])
def login():
    email = request.args.get('Email')

    if not email:
        u.bad_request("email required")
        return u.send_response()

    u.reset_response()
    try:
        query = "SELECT Password FROM user WHERE Email = '{}';".format(email)
        handle_db_operation(query, fetch_one=True)
        return u.send_response()
    except Error as e:
        u.generic_error(str(e))
        return u.send_response()


@app.route('/check_users_profile', methods=['GET'])
def check_users_profile():
    u.reset_response()

    try:
        query = "SELECT * FROM user"
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/login_admin', methods=['GET'])
def login_admin():
    email = request.args.get('Email')

    if not email:
        u.generic_error("email required")
        return u.send_response()

    u.reset_response()

    try:
        query = "SELECT Password FROM admin WHERE Email = '{}'".format(email)
        handle_db_operation(query, fetch_one=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/delete_user', methods=['GET'])
def delete_user():
    email = request.args.get('Email')
    password = request.args.get('Password')

    if not email or not password:
        u.generic_error("email and password are required")
        return u.send_response()

    u.reset_response()
    try:
        # Cancella l'utente dal database
        query = "DELETE FROM user WHERE Email = '{}'".format(email)
        query = query + "and Password='{}';".format(password)
        handle_db_operation(query, commit=True)

        query = "SELECT * FROM user  WHERE Email = '{}';".format(email)
        handle_db_operation(query, fetch_one=True)
        return u.send_response()

    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/delete_admin', methods=['GET'])
def delete_admin():
    email = request.args.get('Email')
    password = request.args.get('Password')

    if not email or not password:
        u.generic_error("email and password are required")
        return u.send_response()

    u.reset_response()
    try:
        # Cancella l'utente dal database
        query = "DELETE FROM admin WHERE Email = '{}'".format(email)
        query = query + "and Password='{}';".format(password)
        handle_db_operation(query, commit=True)

        query = "SELECT * FROM admin  WHERE Email = '{}';".format(email)
        handle_db_operation(query, fetch_one=True)
        return u.send_response()

    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/update_user', methods=['PUT'])
def update_user():
    userid = ""
    firstname = ""
    lastname = ""
    email = ""
    password = ""
    currencyAmount = ""

    firstname = request.args.get('FirstName')
    lastname = request.args.get('LastName')
    email = request.args.get('Email')
    password = request.args.get('Password')
    currencyAmount = request.args.get('CurrencyAmount')

    if not email and not password and not firstname and not lastname and not currencyAmount:
        u.generic_error("almost one field are required")
        return u.send_response()

    u.reset_response()
    try:

        query = "UPDATE user SET "
        if firstname:
            query = query + "FirstName ='{}'".format(firstname)
        if lastname:
            query = query + ",LastName ='{}'".format(lastname)
        if email:
            query = query + ",Email ='{}'".format(email)
        if password:
            query = query + ",Password ='{}'".format(password)
        if currencyAmount:
            query = query + ",CurrencyAmount ='{}'".format(currencyAmount)
        if userid:
            query = query + "' WHERE UserId ='{}';".format(userid)
        handle_db_operation(query, commit=True)

        query = "SELECT * FROM user WHERE UserId ='{}';".format(userid)
        handle_db_operation(query, fetch_one=True)
        return u.send_response()

    except Error as e:
        u.generic_error(e)
        return u.send_response()


# only for admin
@app.route('/update_specific_user', methods=['PUT'])
def update_specific_user():
    userid = ""
    firstname = ""
    lastname = ""
    email = ""
    password = ""
    currencyAmount = ""

    firstname = request.args.get('FirstName')
    lastname = request.args.get('LastName')
    email = request.args.get('Email')
    password = request.args.get('Password')
    currencyAmount = request.args.get('CurrencyAmount')

    if not email and not password and not firstname and not lastname and not currencyAmount:
        u.generic_error("almost one field are required")
        return u.send_response()

    u.reset_response()
    try:

        query = "UPDATE user SET "
        if firstname:
            query = query + "FirstName ='{}'".format(firstname)
        if lastname:
            query = query + ",LastName ='{}'".format(lastname)
        if email:
            query = query + ",Email ='{}'".format(email)
        if password:
            query = query + ",Password ='{}'".format(password)
        if currencyAmount:
            query = query + ",CurrencyAmount ='{}'".format(currencyAmount)
        if userid:
            query = query + "' WHERE UserId ='{}';".format(userid)
        handle_db_operation(query, commit=True)

        query = "SELECT * FROM user WHERE UserId ='{}';".format(userid)
        handle_db_operation(query, fetch_one=True)
        return u.send_response()

    except Error as e:
        u.generic_error(e)
        return u.send_response()


# per i gatcha non venduti
@app.route('/see_auction_market', methods=['GET'])
def see_auction_market():
    u.reset_response()

    try:
        query = "SELECT * FROM transaction WHERE SendedTo is NULL"
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


# per tutti i gatcha  (solo per gli ADMIN)
@app.route('/see_history_auction_market', methods=['GET'])
def see_history_auction_market():
    u.reset_response()

    try:
        query = "SELECT * FROM transaction WHERE EndDate is not NULL"
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/see_specific_auction', methods=['GET'])
def see_specific_auction():
    u.reset_response()
    tra_id = request.args.get('Transaction')
    try:
        query = "SELECT * FROM transaction WHERE TransactionId='{}'".format(tra_id)
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/see_transaction_history', methods=['GET'])
def see_transaction_history():
    email = request.args.get('Email')

    if not email:
        u.generic_error("email are required")
        return u.send_response()

    u.reset_response()

    try:
        query = "SELECT * FROM transaction WHERE RequestingUser='{}';".format(email)
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    data = request.get_json()
    user_id = data.get('user_id')
    gacha_id = data.get('gacha_id')
    cost = data.get('cost')
    datetime = data.get('end_date')
    if not user_id or not gacha_id or not cost or not datetime:
        u.bad_request()
        return u.send_response()
    u.reset_response()

    query = "INSERT INTO transaction (RequestingUser, GachaId, Cost, EndDate) " \
            "VALUES (%s, %s, %s, %s)"
    values = (user_id, gacha_id, cost, datetime)
    handle_db_operation(query, values, commit=True)

    return u.send_response()


@app.route('/update_transaction/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    data = request.get_json()
    sended_to = data.get('SendedTo')
    if not sended_to:
        u.bad_request()
        return u.send_response()
    u.reset_response()

    query = "UPDATE transaction " \
            "SET SendedTo = %s " \
            "WHERE TransactionId = %s"
    values = (sended_to, transaction_id)
    handle_db_operation(query, values, commit=True)

    return u.send_response()


@app.route('/transaction')
def get_all_transactions():
    u.reset_response()

    query = "SELECT * FROM transaction"
    handle_db_operation(query, fetch_all=True)
    return u.send_response()


@app.route('/transaction/<int:requesting_user>')
def get_transaction_by_user(requesting_user):
    u.reset_response()

    query = "SELECT * FROM transaction WHERE RequestingUser = %s"
    values = (requesting_user,)
    handle_db_operation(query, values, fetch_all=True)
    return u.send_response()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8005, debug=u.FLASK_DEBUG)
