from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DATABASE_HOST"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        database=os.getenv("DATABASE_NAME")
    )

@app.route('/auctions', methods=['POST'])
def create_auction():
    gacha_id = request.json.get("gacha_id")
    starting_bid = request.json.get("starting_bid")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO auctions (gacha_id, starting_bid) VALUES (%s, %s)", (gacha_id, starting_bid))
    conn.commit()
    auction_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Auction created", "auction_id": auction_id}), 201

@app.route('/auctions/<int:auction_id>/bid', methods=['POST'])
def place_bid(auction_id):
    bid_amount = request.json.get("bid_amount")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auctions WHERE id=%s", (auction_id,))
    auction = cursor.fetchone()
    if not auction:
        conn.close()
        return jsonify({"error": "Auction not found"}), 404
    cursor.execute("INSERT INTO bids (auction_id, bid_amount) VALUES (%s, %s)", (auction_id, bid_amount))
    conn.commit()
    conn.close()
    return jsonify({"message": "Bid placed"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)
