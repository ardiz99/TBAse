from flask import Flask, jsonify
import requests
import random

app = Flask(__name__)

RARITY_DISTRIBUTION = {
    "Legendary": 0.05,
    "Epic": 0.5,
    "Rare": 5,
    "Uncommon": 40,
    "Common": 54.45
}


@app.route('/', methods=['GET'])
def roll_gacha():
    roll = random.uniform(0, 100)
    cumulative = 0
    rarity = None
    for key, chance in RARITY_DISTRIBUTION.items():
        cumulative += chance
        if roll <= cumulative:
            rarity = key
            break

    response = requests.get('http://127.0.0.1:8005')
    return jsonify(response.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)

