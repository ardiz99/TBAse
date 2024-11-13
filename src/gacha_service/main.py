from flask import Flask, jsonify
import mysql.connector
import random
import os

app = Flask(__name__)

RARITY_DISTRIBUTION = {
    "SuperUltraRare": 0.05,
    "UltraRare": 0.5,
    "SuperRare": 5,
    "Rare": 40,
    "Common": 54.45
}

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DATABASE_HOST"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        database=os.getenv("DATABASE_NAME")
    )

@app.route('/roll', methods=['GET'])
def roll_gacha():
    roll = random.uniform(0, 100)
    cumulative = 0
    rarity = None
    for key, chance in RARITY_DISTRIBUTION.items():
        cumulative += chance
        if roll <= cumulative:
            rarity = key
            break

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gacha_rolls (rarity) VALUES (%s)", (rarity,))
    conn.commit()
    conn.close()

    return jsonify({"rarity": rarity, "image": f"{rarity}.png"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
