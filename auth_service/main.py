from flask import Flask, request, jsonify
from authlib.jose import JsonWebToken, JoseError
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)  # Abilita CORS per l'intera app consentendo la gestione del server Flask per consentire richieste da altre origini.


# Configura JWT con Authlib
jwt = JsonWebToken(['HS256'])
SECRET_KEY = "your-secret-key"  # Questo valore deve essere mantenuto sicuro

# Funzione di connessione al database
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DATABASE_HOST", "localhost"),
        user=os.getenv("DATABASE_USER", "gachauser"),
        password=os.getenv("DATABASE_PASSWORD", "123456"),
        database=os.getenv("DATABASE_NAME", "ase")
    )


# Endpoint per la registrazione
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user_id = data.get('UserId')
    first_name = data.get('FirstName')
    last_name = data.get('LastName')
    email = data.get('Email')
    password = data.get('Password')
    currency_amount = data.get('CurrencyAmount')

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (UserId, FirstName, LastName, Email, Password, CurrencyAmount)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (user_id, first_name, last_name, email, hashed_password, currency_amount)
    )
    conn.commit()
    conn.close()
    return jsonify(message="User registered"), 201

# Endpoint per il login
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('Email')
    password = request.json.get('Password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Password FROM users WHERE Email=%s", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        # Crea il token JWT
        header = {'alg': 'HS256'}
        payload = {'sub': email}
        token = jwt.encode(header, payload, SECRET_KEY)
        return jsonify(access_token=token.decode('utf-8')), 200
    else:
        return jsonify(error="Invalid credentials"), 401

# Endpoint di accesso protetto
@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization').split()[1]
    try:
        claims = jwt.decode(token, SECRET_KEY)
        return jsonify(message="Access granted", user=claims['sub']), 200
    except JoseError:
        return jsonify(error="Invalid or expired token"), 401

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8001)
