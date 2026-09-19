import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "core"))

import requests
from flask import Flask, jsonify, request
from secret_sharing import split

app = Flask(__name__)

INSTITUTION_NAME = "nbfc"
AGGREGATOR_URL = "http://127.0.0.1:5000/receive-shares"

CUSTOMER_DB = {
    "CUST001": {"name": "Arjun Menon", "debt": 8000},
    "CUST002": {"name": "Divya Rao", "debt": 18000},
    "CUST003": {"name": "Karthik Iyer", "debt": 12000},
    "CUST004": {"name": "Meena Pillai", "debt": 9000},
}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "nbfc_service", "status": "ok"})


@app.route("/customers", methods=["GET"])
def list_customers():
    return jsonify([
        {"customer_id": cid, "name": rec["name"]}
        for cid, rec in CUSTOMER_DB.items()
    ])


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(force=True)
    customer_id = data.get("customer_id")

    if customer_id not in CUSTOMER_DB:
        return jsonify({"error": f"unknown customer_id '{customer_id}'"}), 404

    private_value = CUSTOMER_DB[customer_id]["debt"]
    shares = split(private_value)
    print(f"[{INSTITUTION_NAME.upper()}] Splitting debt for {customer_id} into shares: {shares}")

    payload = {"institution": INSTITUTION_NAME, "customer_id": customer_id, "shares": shares}
    resp = requests.post(AGGREGATOR_URL, json=payload, timeout=5)

    return jsonify({
        "service": INSTITUTION_NAME,
        "customer_id": customer_id,
        "shares_sent": shares,
        "aggregator_response": resp.json(),
    })


if __name__ == "__main__":
    app.run(port=5002, debug=True)