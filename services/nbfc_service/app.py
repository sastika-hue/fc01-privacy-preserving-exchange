import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "core"))

import requests
from flask import Flask, jsonify, request
from secret_sharing import split

app = Flask(__name__)

INSTITUTION_NAME = "nbfc"
AGGREGATOR_URL = "http://127.0.0.1:5000/receive-shares"

# Configurable private value: the customer's existing debt.
private_value = 15000


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "nbfc_service", "status": "ok"})


@app.route("/set-value", methods=["POST"])
def set_value():
    global private_value
    data = request.get_json(force=True)
    value = data.get("value")
    if not isinstance(value, int) or value < 0:
        return jsonify({"error": "value must be a non-negative integer"}), 400
    private_value = value
    return jsonify({"service": INSTITUTION_NAME, "private_value_set_to": private_value})


@app.route("/submit", methods=["POST"])
def submit():
    shares = split(private_value)
    print(f"[{INSTITUTION_NAME.upper()}] Splitting private value into shares: {shares}")

    payload = {"institution": INSTITUTION_NAME, "shares": shares}
    resp = requests.post(AGGREGATOR_URL, json=payload, timeout=5)

    return jsonify({
        "service": INSTITUTION_NAME,
        "shares_sent": shares,
        "aggregator_response": resp.json(),
    })


if __name__ == "__main__":
    app.run(port=5002, debug=True)