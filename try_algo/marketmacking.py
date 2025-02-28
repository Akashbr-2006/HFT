from flask import Flask, jsonify
from flask_cors import CORS
import random
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Simulated market data
market_data = {
    "best_bid": 100.00,
    "bid_size": 5,
    "best_ask": 100.10,
    "ask_size": 5
}

def update_market_data():
    """ Continuously updates the mock market data """
    while True:
        mid_price = 100 + random.uniform(-1, 1)  # Simulated mid-price fluctuations
        spread = random.uniform(0.05, 0.2)  # Simulated spread variation
        market_data["best_bid"] = round(mid_price - spread / 2, 2)
        market_data["best_ask"] = round(mid_price + spread / 2, 2)
        market_data["bid_size"] = round(random.uniform(1, 10), 2)
        market_data["ask_size"] = round(random.uniform(1, 10), 2)
        time.sleep(0.1)  # Updates every 100ms

@app.route('/market_data', methods=['GET'])
def get_market_data():
    """ API endpoint to fetch live market data """
    return jsonify(market_data)

# Start the market data simulation in the background
threading.Thread(target=update_market_data, daemon=True).start()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
