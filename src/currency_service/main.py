from flask import Flask, jsonify
import requests
import random

app = Flask(__name__)

RESPONSE = {
    "code": 200,
    "data": []
}


def reset_response():
    RESPONSE["code"] = 200
    RESPONSE["data"] = []


RARITY_DISTRIBUTION = {
    "Legendary": 0.05,
    "Epic": 0.5,
    "Rare": 5,
    "Uncommon": 40,
    "Common": 54.45
}


@app.route('/roll', methods=['GET'])
def roll_gacha():
    reset_response()

    roll = random.uniform(0, 100)
    cumulative = 0
    rarity = None
    for key, chance in RARITY_DISTRIBUTION.items():
        cumulative += chance
        if roll <= cumulative:
            rarity = key
            break

    # response = requests.get('http://127.0.0.1:8005/roll', params={'rarity': 'Legendary'})
    response = requests.get('http://db-manager:8005/roll', params={'rarity': rarity})

    data = response.json()
    set = data.get("data")
    print(len(set))
    random2 = random.randint(0, len(set)-1)
    chosen = set[random2]

    RESPONSE["code"] = 200
    RESPONSE["data"] = chosen

    return jsonify(RESPONSE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)

