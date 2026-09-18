import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "core"))

from flask import Flask, jsonify, request
from secret_sharing import secure_sum, threshold_check

app = Flask(__name__)

EXPECTED_INSTITUTIONS = ["bank", "nbfc", "bureau"]
THRESHOLD = 50000  # demo eligibility threshold for the summed composite score

# In-memory state for one demo "round". Cleared with POST /reset between runs.
state = {
    "received_shares": {},  # institution name -> [s1, s2, s3]
    "decision": None,       # None | "Eligible" | "Not Eligible"
}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "aggregator_service", "status": "ok"})


@app.route("/reset", methods=["POST"])
def reset():
    state["received_shares"] = {}
    state["decision"] = None
    return jsonify({"status": "reset"})


@app.route("/receive-shares", methods=["POST"])
def receive_shares():
    data = request.get_json(force=True)
    institution = data.get("institution")
    shares = data.get("shares")

    if institution not in EXPECTED_INSTITUTIONS:
        return jsonify({"error": f"unknown institution '{institution}'"}), 400
    if not isinstance(shares, list) or len(shares) != 3:
        return jsonify({"error": "shares must be a list of 3 integers"}), 400

    # This print is exactly what the network-trace panel will show later:
    # meaningless share numbers on the wire, never the raw value.
    print(f"[AGGREGATOR] Received shares from '{institution}': {shares}")

    state["received_shares"][institution] = shares

    response = {
        "status": "received",
        "institutions_received": list(state["received_shares"].keys()),
    }

    if all(inst in state["received_shares"] for inst in EXPECTED_INSTITUTIONS):
        share_sets = [state["received_shares"][inst] for inst in EXPECTED_INSTITUTIONS]
        summed_shares = secure_sum(share_sets)
        eligible = threshold_check(summed_shares, THRESHOLD)
        state["decision"] = "Eligible" if eligible else "Not Eligible"
        response["status"] = "complete"
        response["decision"] = state["decision"]
        print(f"[AGGREGATOR] All shares in. Decision: {state['decision']}")

    return jsonify(response)


@app.route("/decision", methods=["GET"])
def get_decision():
    if state["decision"] is None:
        return jsonify({
            "status": "waiting",
            "institutions_received": list(state["received_shares"].keys()),
        })
    return jsonify({"status": "complete", "decision": state["decision"]})


if __name__ == "__main__":
    app.run(port=5000, debug=True)