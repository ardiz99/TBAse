from flask import Flask, request, make_response, jsonify
from sqlalchemy import create_engine
import random, time, os, threading, hashlib
import pandas as pd

app = Flask(__name__)
engine = create_engine('sqlite:///ase.db')


@app.route('/login')
def login():
    email = request.args.get('email', type=str)
    password = request.args.get('password', type=str)
    if email and password:
        query = f"SELECT Password FROM Users WHERE Email = '{email}'"
        result = pd.read_sql(query, con=engine)
        if result.empty:
            return make_response("Error! Wrong e-mail", 404)
        else:
            hash_passw = hashlib.sha256(password.encode()).hexdigest()[:16]
            if hash_passw != result['Password'][0]:
                return make_response("Error! Wrong password", 404)
        return make_response("Login successful", 200)
    else:
        return make_response('Invalid input\n', 400)


if __name__ == '__main__':
    app.run(debug=True)
