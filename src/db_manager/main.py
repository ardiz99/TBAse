from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
# from src import utils as u
import utils as u

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
        cursor.close()
    except Error as err:
        u.generic_error(str(err))
    finally:
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


@app.route('/user/get_by_email')
def get_by_email():
    email = request.args.get('email')
    query = "SELECT * " \
            "FROM user " \
            "WHERE Email = %s"
    values = (email,)
    handle_db_operation(query, values, fetch_one=True)
    return u.send_response()


@app.route('/user/get_by_id/<int:user_id>')
def get_by_id(user_id):
    query = "SELECT * " \
            "FROM user " \
            "WHERE UserId = %s"
    values = (user_id,)
    handle_db_operation(query, values, fetch_one=True)
    return u.send_response()


# INIZIO METODI PER USER =>

@app.route('/register', methods=['POST'])
def register():
    u.reset_response()

    data = request.get_json()
    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    salt = data.get('Salt')
    currencyAmount = data.get('CurrencyAmount')

    query = "INSERT INTO user (FirstName, LastName, Email, Password, CurrencyAmount, Salt) VALUES ("""
    query = query + "'{}',".format(firstname)
    query = query + "'{}',".format(lastname)
    query = query + "'{}',".format(email)
    query = query + "'{}',".format(password)
    query = query + "'{}',".format(currencyAmount)
    query = query + "'{}');""".format(salt)
    handle_db_operation(query, commit=True)
    return u.send_response(query)


@app.route('/register_admin', methods=['POST'])
def register_admin():
    data = request.get_json()
    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    salt = data.get('Salt')

    if not email or not password or not firstname or not lastname:
        u.generic_error("All field are required")
        return u.send_response()

    u.reset_response()

    try:
        query = "INSERT INTO admin (FirstName, LastName, Email, Password, Salt) VALUES ("""
        query = query + "'{}',".format(firstname)
        query = query + "'{}',".format(lastname)
        query = query + "'{}',".format(email)
        query = query + "'{}',".format(password)
        query = query + "'{}');""".format(salt)
        handle_db_operation(query, commit=True)

        query = "SELECT * FROM admin  WHERE Email = '{}';".format(email)
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(str(e))
        return u.send_response(str(e))


@app.route('/get_all_admin', methods=['GET'])
def get_all_admin():
    query = "SELECT * FROM admin"
    handle_db_operation(query, fetch_all=True)
    return u.send_response()


@app.route('/login', methods=['GET'])
def login():
    email = request.args.get('Email')

    if not email:
        u.generic_error("email required")
        return u.send_response()

    u.reset_response()
    try:
        query = "SELECT Password, Salt FROM user WHERE Email = '{}';".format(email)
        query = query + " LIMIT 1;"
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/check_users_profile', methods=['GET'])
def check_users_profile():
    u.reset_response()

    try:
        query = "SELECT * FROM user;"
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/check_one_user', methods=['GET'])
def check_one_user():
    u.reset_response()
    email = request.args.get('Email')
    password = request.args.get('Password')
    try:
        query = "SELECT * FROM user WHERE Email = '{}'".format(email) + " and Password = '{}';".format(password)
        # query = "SELECT Salt FROM user WHERE Email = '{}'".format(email)
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/check_one_user_simple', methods=['GET'])
def check_one_user_simple():
    u.reset_response()
    Userid = request.args.get('UserId')
    try:
        query = "SELECT * FROM user WHERE UserId = '{}'".format(Userid) + " LIMIT 1;"
        # query = "SELECT Salt FROM user WHERE Email = '{}'".format(email)
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


# funzione che serve per prendere tutti i campi dell admin per l'update dinamico
@app.route('/check_one_admin', methods=['GET'])
def check_one_admin():
    u.reset_response()
    email = request.args.get('Email')
    # password = request.args.get('Password')

    try:
        query = "SELECT * FROM admin WHERE Email = '{}'".format(email) + " LIMIT 1;"""
        # query = "DELETE FROM admin WHERE Email = %s "
        # handle_db_operation(query, values=(email), commit=True)
        # query = "SELECT Salt FROM user WHERE Email = '{}'".format(email)
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
        query = "SELECT Password, Salt FROM admin WHERE Email = '{}'".format(email)
        query = query + " LIMIT 1;"
        handle_db_operation(query, fetch_all=True)
        return u.send_response()
    except Error as e:
        u.generic_error(e)
        return u.send_response()


@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    # Recupera i dati dal corpo della richiesta
    data = request.get_json()
    email = data.get('Email')
    password = data.get('Password')

    if not email or not password:
        u.generic_error("Email and Password are required")
        return u.send_response()

    u.reset_response()
    try:
        # Costruisci la query SQL per eliminare l'utente
        query = "DELETE FROM user WHERE Email = %s AND Password = %s"
        handle_db_operation(query, values=(email, password), commit=True)

        # Verifica se l'utente è stato eliminato
        # query = "SELECT * FROM user WHERE Email = %s"
        # handle_db_operation(query, values=(email,), fetch_one=True)

        if u.RESPONSE["data"]:
            u.generic_error("Failed to delete user")
        else:
            u.RESPONSE["message"] = "User deleted successfully"
        return u.send_response()
    except Error as e:
        u.generic_error(str(e))
        return u.send_response()


@app.route('/delete_admin', methods=['DELETE'])
def delete_admin():
    # Recupera i dati dal corpo della richiesta
    data = request.get_json()
    email = data.get('Email')
    password = data.get('Password')

    if not email or not password:
        u.generic_error("Email and Password are required")
        return u.send_response()

    u.reset_response()
    try:
        # Costruisci la query SQL per eliminare l'amministratore
        query = "DELETE FROM admin WHERE Email = %s AND Password = %s"
        handle_db_operation(query, values=(email, password), commit=True)

        # Verifica se l'amministratore è stato eliminato
        # query = "SELECT * FROM admin WHERE Email = %s"
        # handle_db_operation(query, values=(email,), fetch_one=True)

        if u.RESPONSE["data"]:
            u.generic_error("Failed to delete admin")
        else:
            u.RESPONSE["message"] = "Admin deleted successfully"
        return u.send_response()
    except Error as e:
        u.generic_error(str(e))
        return u.send_response()


@app.route('/update_user', methods=['PUT'])
def update_user():
    # Estrai i dati dalla richiesta
    data = request.get_json()
    if not data:
        u.generic_error("Missing fields")
        return u.send_response()

    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    currency_amount = data.get('CurrencyAmount')

    u.reset_response()
    try:
        # Costruisci dinamicamente la query SQL
        updates = []
        if firstname:
            updates.append(f"FirstName = '{firstname}'")
        if lastname:
            updates.append(f"LastName = '{lastname}'")
        if password:
            updates.append(f"Password = '{password}'")
        if currency_amount:
            updates.append(f"CurrencyAmount = '{currency_amount}'")

        if not updates:
            u.generic_error("No fields to update")
            return u.send_response()

        query = f"UPDATE user SET {', '.join(updates)} WHERE Email = '{email}';"
        handle_db_operation(query, commit=True)

        query = f"SELECT * FROM user WHERE Email = '{email}';"
        handle_db_operation(query, fetch_one=True)
        return u.send_response()
    except Error as e:
        u.generic_error(str(e))
        return u.send_response()


@app.route('/update_admin', methods=['PUT'])
def update_admin():
    # fare il controllo in caso di cambio di email
    # Estrai i dati dalla richiesta
    data = request.get_json()
    if not data:
        u.generic_error("Missing fields")
        return u.send_response()

    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    salt = data.get('Salt')
    tmp_email = data.get('tmp_email')
    u.reset_response()
    try:
        # Costruisci dinamicamente la query SQL
        updates = []
        if firstname:
            updates.append(f"FirstName = '{firstname}'")
        if lastname:
            updates.append(f"LastName = '{lastname}'")
        if email:
            updates.append(f"Email = '{email}'")
        if password:
            updates.append(f"Password = '{password}'")
        if salt:
            updates.append(f"Salt = '{salt}'")

        if not updates:
            u.generic_error("No fields to update")
            return u.send_response()

        query = f"UPDATE admin SET {', '.join(updates)} WHERE Email = '{tmp_email}';"
        handle_db_operation(query, commit=True)

        query = f"SELECT * FROM admin WHERE Email = '{email}';"
        handle_db_operation(query, fetch_one=True)
        return u.send_response()
    except Error as e:
        u.generic_error(str(e))
        return u.send_response()


@app.route('/update_specific_user', methods=['PUT'])
def update_specific_user():
    # Estrai i dati dalla richiesta
    data = request.get_json()
    if not data:
        u.generic_error("Missing fields")
        return u.send_response()

    firstname = data.get('FirstName')
    lastname = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    currency_amount = data.get('CurrencyAmount')

    if not email or not any([firstname, lastname, password, currency_amount]):
        u.generic_error("At least one field is required")
        return u.send_response()

    u.reset_response()
    try:
        # Costruisci dinamicamente la query SQL
        updates = []
        if firstname:
            updates.append(f"FirstName = '{firstname}'")
        if lastname:
            updates.append(f"LastName = '{lastname}'")
        if password:
            updates.append(f"Password = '{password}'")
        if currency_amount:
            updates.append(f"CurrencyAmount = '{currency_amount}'")

        if not updates:
            u.generic_error("No fields to update")
            return u.send_response()

        query = f"UPDATE user SET {', '.join(updates)} WHERE Email = '{email}';"
        handle_db_operation(query, commit=True)

        query = f"SELECT * FROM user WHERE Email = '{email}';"
        handle_db_operation(query, fetch_one=True)
        return u.send_response()
    except Error as e:
        u.generic_error(str(e))
        return u.send_response()


@app.route('/user', methods=['GET'])
def get_all_user():
    u.reset_response()
    query = "SELECT * FROM user"
    handle_db_operation(query, fetch_all=True)
    return u.send_response()


# TRANSACTION ===>

@app.route('/roll', methods=['POST'])
def roll():
    data = request.get_json()
    user_id = data.get('user_id')
    gacha_id = data.get('gacha_id')
    cost = data.get('cost')
    datetime = data.get('end_date')
    if not user_id or not gacha_id or not cost or not datetime:
        u.bad_request()
        return u.send_response()

    query = "INSERT INTO transaction (RequestingUser, GachaId, StartingPrice, ActualPrice, EndDate) " \
            "VALUES (%s, %s, %s, %s, %s)"
    values = (user_id, gacha_id, cost, cost, datetime)
    handle_db_operation(query, values, commit=True)

    return u.send_response()


@app.route('/transaction/<int:transaction_id>/sended_to', methods=['PUT'])
def update_transaction(transaction_id):
    data = request.get_json()
    sended_to = data.get('sended_to')
    if not sended_to:
        u.bad_request()
        return u.send_response()

    query = "UPDATE transaction " \
            "SET SendedTo = %s " \
            "WHERE TransactionId = %s"
    values = (sended_to, transaction_id)
    handle_db_operation(query, values, commit=True)

    return u.send_response()


@app.route('/transaction')
def get_all_transactions():
    query = "SELECT * FROM transaction"
    handle_db_operation(query, fetch_all=True)
    return u.send_response()


@app.route('/transaction_history/<int:user_id>', methods=['GET'])
def transaction_history(user_id):
    query = "SELECT * FROM transaction WHERE RequestingUser = %s OR UserOwner = %s"
    values = (user_id, user_id)
    handle_db_operation(query, values, fetch_all=True)
    return u.send_response()


@app.route('/transaction/requesting_user/<int:requesting_user>')
def get_transaction_by_user(requesting_user):
    query = "SELECT * FROM transaction WHERE RequestingUser = %s"
    values = (requesting_user,)
    handle_db_operation(query, values, fetch_all=True)
    return u.send_response()


@app.route('/transaction/<int:transaction_id>/delete')
def delete_transaction(transaction_id):
    query = "DELETE FROM transaction WHERE TransactionId = %s"
    values = (transaction_id,)
    handle_db_operation(query, values, commit=True)
    return u.send_response()


# =======> AUCTION METHODS


@app.route('/new_auction', methods=['POST'])
def new_auction():
    data = request.get_json()
    user_owner = data.get('user_owner')
    gacha_id = data.get('gacha_id')
    starting_price = data.get('starting_price')
    end_date = data.get('end_date')
    if not user_owner or not gacha_id or not starting_price or not end_date:
        u.bad_request()
        return u.send_response()

    query = "INSERT INTO transaction (UserOwner, GachaId, StartingPrice, ActualPrice, EndDate) " \
            "VALUES (%s, %s, %s, %s, %s)"
    values = (user_owner, gacha_id, starting_price, starting_price, end_date)
    handle_db_operation(query, values, commit=True)

    return u.send_response()


@app.route('/auction')
def get_all_auctions():
    query = "SELECT * FROM transaction WHERE UserOwner IS NOT NULL"
    handle_db_operation(query, fetch_all=True)
    return u.send_response()


@app.route('/active_auction')
def get_all_active_auction():
    query = "SELECT * " \
            "FROM transaction " \
            "WHERE UserOwner IS NOT NULL " \
            "   AND STR_TO_DATE(EndDate, '%Y-%m-%d %H:%i:%s') > NOW()"
    handle_db_operation(query, fetch_all=True)
    return u.send_response()


@app.route('/auction/gacha/<int:gacha>')
def get_auction_by_user(gacha):
    query = "SELECT * FROM transaction WHERE GachaId = %s AND UserOwner IS NOT NULL"
    values = (gacha,)
    handle_db_operation(query, values, fetch_all=True)
    return u.send_response()


@app.route('/auction/<int:transaction_id>')
def get_specific_auction(transaction_id):
    query = "SELECT * FROM transaction WHERE TransactionId = %s AND UserOwner IS NOT NULL"
    values = (transaction_id,)
    handle_db_operation(query, values, fetch_one=True)
    return u.send_response()


@app.route('/auction/<int:transaction_id>/get_bid')
def get_actual_price(transaction_id):
    query = "SELECT * " \
            "FROM transaction " \
            "WHERE TransactionId = %s AND UserOwner IS NOT NULL " \
            "LIMIT 1"
    values = (transaction_id,)
    handle_db_operation(query, values, fetch_one=True)
    return u.send_response()


@app.route('/auction/<int:transaction_id>/update_actual_price', methods=['PUT'])
def update_actual_price(transaction_id):
    bid = request.get_json().get("bid")
    requesting_user = request.get_json().get("requesting_user")
    query = "UPDATE transaction " \
            "SET ActualPrice = %s, RequestingUser = %s " \
            "WHERE TransactionId = %s"
    values = (bid, requesting_user, transaction_id)
    handle_db_operation(query, values, commit=True)
    return u.send_response()


@app.route('/auction/<int:transaction_id>/close_auction', methods=['PUT'])
def close_auction(transaction_id):
    query = "UPDATE transaction " \
            "SET EndDate = DATE_FORMAT(NOW(), \'%Y-%m-%d %H:%i:%s\') " \
            f"WHERE TransactionId = {transaction_id}"
    handle_db_operation(query, commit=True)
    return u.send_response()


@app.route('/auction/history>', methods=['GET'])
def get_old_transaction():
    query = "SELECT * " \
            "FROM transaction " \
            "WHERE RequestingUser IS NOT NULL " \
            "   AND STR_TO_DATE(EndDate, '%Y-%m-%d %H:%i:%s') < NOW() "
    handle_db_operation(query, fetch_all=True)

    return u.send_response()


@app.route('/gacha/UserId_by_email/<string:email>')
def get_id_by_email_gacha(email):
    query = "SELECT UserId FROM user WHERE Email = %s LIMIT 1"
    values = (email,)
    handle_db_operation(query, values, fetch_one=True)
    return u.send_response()


# INIZIO METODI DEL DBMANGER PER ESEGUIRE LE QUERY DEL GACHASERVICE

@app.route('/gacha/get_gacha_of_user/<string:email>', methods=['GET'])
def get_gacha_of_user(email):
    u.reset_response()
    global connection
    init_db_connection()

    if connection is None:
        u.generic_error("Errore di connessione al database.")
        return jsonify(u.RESPONSE)

    try:
        # Esegui la prima query per ottenere UserId
        cursor = connection.cursor(dictionary=True)
        query = f"SELECT UserId FROM user WHERE Email = '{email}' LIMIT 1"  # Concatenazione manuale
        print(f"Query eseguita: {query}")  # Stampa la query per il debug
        cursor.execute(query)
        res = cursor.fetchone()

        if not res:
            u.not_found()
            return jsonify(u.RESPONSE)

        user_id = res.get("UserId")
        cursor.close()  # Chiudi il cursore dopo la prima query

        # Esegui la seconda query per ottenere GachaId
        query = f"""
            SELECT GachaId
            FROM transaction
            WHERE RequestingUser = {user_id}
              AND STR_TO_DATE(EndDate, '%Y-%m-%d %H:%i:%s') < NOW()
              AND SendedTo IS NULL
        """  # Concatenazione manuale
        print(f"Query eseguita: {query}")  # Stampa la query per il debug
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            u.not_found()
            return jsonify(u.RESPONSE)

        cursor.close()  # Chiudi il cursore dopo la seconda query
        close_db_connection()  # Chiudi la connessione al database

        # Estrai solo gli GachaId dalla query e invia come risposta
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = [row['GachaId'] for row in result]
        u.RESPONSE["message"] = "Expired gacha IDs retrieved successfully!"
        return jsonify(u.RESPONSE)

    except Error as e:
        u.generic_error("Errore durante il recupero dei gacha IDs: " + str(e))
        return jsonify(u.RESPONSE)

    finally:
        # Chiudi sempre la connessione e il cursore, anche in caso di errore
        if cursor:
            cursor.close()
        close_db_connection()


# INIZIO METODI DEL DBMANGER PER ESEGUIRE LE QUERY DEL ADMINGACHASERVICE
# Il metodo add richiede di inserire anche
# l'id: Creare la chiave autoincrement, e andare a prendere dal db NEXTVAL(GachaId)+1, e fare la insert
@app.route('/gacha/add', methods=['POST'])
def add_gacha():
    data = request.get_json()

    # Inizializza la risposta
    u.reset_response()

    # Inizializza la connessione al database
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return jsonify(u.RESPONSE)

    try:
        # Verifica che tutti i dati necessari siano presenti nel corpo della richiesta
        required_fields = ['GachaId', 'Name', 'Type1', 'Type2', 'Total', 'HP', 'Attack', 'Defense', 'SpAtt', 'SpDef',
                           'Speed', 'Rarity', 'Link']
        for field in required_fields:
            if field not in data:
                print(f"Errore: campo mancante {field}")
                u.generic_error(f"Campo mancante: {field}")
                return jsonify(u.RESPONSE)

        # Esegui l'inserimento dei dati nel database
        cursor = connection.cursor()
        query = """
            INSERT INTO gacha (GachaId, Name, Type1, Type2, Total, HP, Attack, Defense, SpAtt, SpDef, Speed, Rarity, Link) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data['GachaId'], data['Name'], data['Type1'], data['Type2'], data['Total'], data['HP'],
            data['Attack'], data['Defense'], data['SpAtt'], data['SpDef'],
            data['Speed'], data['Rarity'], data['Link']
        )

        # Esegui la query
        cursor.execute(query, values)
        connection.commit()  # Conferma le modifiche nel database
        print(f"Query eseguita: {query}")

        cursor.close()

        # Chiudi la connessione
        close_db_connection()

        # Imposta la risposta di successo
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = []
        u.RESPONSE["message"] = "Gacha added successfully!"
        return jsonify(u.RESPONSE)
    except Error as e:
        print(f"Errore durante l'inserimento nel database: {e}")
        u.generic_error("Errore durante l'inserimento nel database.")
        close_db_connection()  # Assicurati di chiudere la connessione anche in caso di errore
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


@app.route('/gacha/get/<int:gacha_id>', methods=['GET'])
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


@app.route('/gacha/getName/<string:gacha_name>', methods=['GET'])
def get_gacha_by_name(gacha_name):
    u.reset_response()
    init_db_connection()

    if connection is None:
        print("Errore: connessione al database non riuscita.")
        u.generic_error("Errore di connessione al database.")
        return jsonify(u.RESPONSE)

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gacha WHERE Name = %s", (gacha_name,))
        gacha = cursor.fetchone()

        if gacha is None:
            u.not_found()
            return jsonify(u.RESPONSE)

        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = gacha
        u.RESPONSE["message"] = f"Gacha with name '{gacha_name}' retrieved successfully!"
        cursor.close()
        close_db_connection()
        return jsonify(u.RESPONSE)

    except Error as e:
        print(f"Errore durante il recupero del gacha: {e}")
        u.generic_error("Errore durante il recupero del gacha.")
        return jsonify(u.RESPONSE)


@app.route('/gacha/get', methods=['GET'])
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
        if gachas is None:
            u.not_found()
            return jsonify(u.RESPONSE)
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


@app.route('/transaction', methods=['GET'])
def view_transaction():
    u.reset_response()

    global connection
    init_db_connection()

    if connection is None:
        u.generic_error()
        return jsonify(u.RESPONSE)
    try:
        cursor = connection.cursor(dictionary=True)
        query = f"SELECT * FROM transaction"
        cursor.execute(query)
        result = cursor.fetchall()
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = result
        u.RESPONSE["message"] = "All gachas retrieved successfully!"
        cursor.close()
        close_db_connection()
        return jsonify(u.RESPONSE)

    except Error as e:
        print(f"Errore durante il recupero di tutti i gachas: {e}")
        u.generic_error("Errore durante il recupero di tutti i gachas.")
        return jsonify(u.RESPONSE)


@app.route('/transaction/<int:user_id>', methods=['GET'])
def view_transaction_user(user_id):
    u.reset_response()

    global connection
    init_db_connection()

    if connection is None:
        u.generic_error()
        return jsonify(u.RESPONSE)
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transaction WHERE RequestingUser = %s", (user_id,))
        result = cursor.fetchall()
        if result is None:
            u.not_found()
            return jsonify(u.RESPONSE)
        u.RESPONSE["code"] = 200
        u.RESPONSE["data"] = result
        u.RESPONSE["message"] = "Transaction retrieved successfully!"
        cursor.close()
        close_db_connection()
        return jsonify(u.RESPONSE)

    except Error as e:
        print(f"Errore durante il recupero del gacha: {e}")
        u.generic_error("Errore durante il recupero del gacha.")
        return jsonify(u.RESPONSE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8005, debug=u.FLASK_DEBUG)

