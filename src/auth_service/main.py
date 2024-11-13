from flask import Flask, request, jsonify
from authlib.jose import JsonWebToken, JWTClaims, JoseError
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure JWT with Authlib
jwt = JsonWebToken(['HS256'])
SECRET_KEY = "your-secret-key"  # This should be kept secure

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DATABASE_HOST"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        database=os.getenv("DATABASE_NAME")
    )

# User registration route
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    hashed_password = generate_password_hash(password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    conn.commit()
    conn.close()
    return jsonify(message="User registered"), 201

# User login route
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        # Create JWT token using Authlib
        header = {'alg': 'HS256'}
        payload = {'sub': username}
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
