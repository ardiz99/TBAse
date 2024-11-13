from flask import Flask, request, jsonify
from authlib.jose import JsonWebToken, JoseError
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure JWT with Authlib
jwt = JsonWebToken(['HS256'])
SECRET_KEY = "your-secret-key"  # This should be stored securely

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DATABASE_HOST", "localhost"),
        user=os.getenv("DATABASE_USER", "root"),
        password=os.getenv("DATABASE_PASSWORD", "password"),
        database=os.getenv("DATABASE_NAME", "ase")
    )

# User registration route
@app.route('/register', methods=['POST'])
def register():
    data = request.json
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
        INSERT INTO users ( FirstName, LastName, Email, Password, CurrencyAmount)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (first_name, last_name, email, hashed_password, currency_amount)
    )
    conn.commit()
    conn.close()
    return jsonify(message="User registered"), 201

# User login route
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
        # Create JWT token using Authlib
        header = {'alg': 'HS256'}
        payload = {'sub': email}
        token = jwt.encode(header, payload, SECRET_KEY)
        return jsonify(access_token=token.decode('utf-8')), 200
    else:
        return jsonify(error="Invalid credentials"), 401

# Protected endpoint example
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
