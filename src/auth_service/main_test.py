from flask import Flask, jsonify, request
import bcrypt
import base64
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

# Configurazione segreta per il JWT
SECRET_KEY = "your_secret_key"

# Simulazione di un database in memoria
mock_db = {
    "user@example.com": {
        "Email": "user@example.com",
        "Password": bcrypt.hashpw("securepassword".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "Salt": base64.b64encode(bcrypt.gensalt()).decode('utf-8'),
        "FirstName": "John",
        "LastName": "Doe",
        "CurrencyAmount": 100,
        "Role": "user",
    }
}

blacklisted_tokens = set()  # Per simulare i token revocati


def generate_tokens(email, role):
    """Genera access_token e id_token."""
    payload = {
        "sub": email,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    id_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"access_token": access_token, "id_token": id_token}


@app.route("/register", methods=["POST"])
def register():
    """Endpoint per la registrazione."""
    data = request.get_json()
    email = data.get("Email")
    password = data.get("Password")
    if email in mock_db:
        return jsonify({"error": "User already exists"}), 400

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    mock_db[email] = {
        "Email": email,
        "Password": hashed_password.decode('utf-8'),
        "Salt": base64.b64encode(salt).decode('utf-8'),
        "FirstName": data.get("FirstName"),
        "LastName": data.get("LastName"),
        "CurrencyAmount": data.get("CurrencyAmount", 0),
        "Role": "user",
    }
    return jsonify({"message": "Registration successful"}), 200


@app.route("/login", methods=["POST"])
def login():
    """Endpoint per il login."""
    data = request.get_json()
    email = data.get("Email")
    password = data.get("Password")
    user = mock_db.get(email)

    if not user:
        return jsonify({"error": "User not found"}), 400

    stored_hash = user["Password"].encode('utf-8')
    if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        return jsonify({"error": "Invalid credentials"}), 400

    tokens = generate_tokens(email, user["Role"])
    return jsonify({"data": tokens, "message": "Login successful"}), 200


@app.route("/update_user", methods=["PUT"])
def update_user():
    """Endpoint per aggiornare un utente."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    email = decoded.get("sub")
    user = mock_db.get(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    user.update({
        "FirstName": data.get("FirstName", user["FirstName"]),
        "LastName": data.get("LastName", user["LastName"]),
        "CurrencyAmount": data.get("CurrencyAmount", user["CurrencyAmount"]),
    })
    if data.get("Password"):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(data["Password"].encode('utf-8'), salt)
        user["Password"] = hashed_password.decode('utf-8')
        user["Salt"] = base64.b64encode(salt).decode('utf-8')

    return jsonify({"message": "User updated successfully"}), 200


@app.route("/delete_user", methods=["DELETE"])
def delete_user():
    """Endpoint per eliminare un utente."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    email = decoded.get("sub")
    if email in mock_db:
        del mock_db[email]
        return jsonify({"message": "User deleted successfully"}), 200

    return jsonify({"error": "User not found"}), 404


@app.route("/check_users_profile", methods=["GET"])
def check_users_profile():
    """Endpoint per controllare il profilo degli utenti."""
    return jsonify({"data": list(mock_db.values()), "message": "Profiles retrieved successfully"}), 200


@app.route("/logout", methods=["GET"])
def logout():
    """Endpoint per il logout."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]
    if token in blacklisted_tokens:
        return jsonify({"error": "Token already blacklisted"}), 401

    blacklisted_tokens.add(token)
    return jsonify({"message": "Logout successful"}), 200


if __name__ == "__main_test__":
    app.run(host="0.0.0.0", port=5001, debug=True)
