from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "nbfc_service", "status": "ok"})


if __name__ == "__main__":
    app.run(port=5002, debug=True)