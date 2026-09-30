from flask import Flask, jsonify, request

app = Flask(__name__)

account = {
    "account_number": "10001",
    "balance": 10000
}

@app.route("/")
def home():
    return "Banking Application is running"

@app.route("/balance")
def balance():
    return jsonify({
        "account_number": account["account_number"],
        "balance": account["balance"]
    })

@app.route("/deposit", methods=["POST"])
def deposit():
    amount = request.json["amount"]

    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    account["balance"] += amount

    return jsonify({
        "message": "Deposit successful",
        "balance": account["balance"]
    })

@app.route("/withdraw", methods=["POST"])
def withdraw():
    amount = request.json["amount"]

    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    if amount > account["balance"]:
        return jsonify({"error": "Insufficient balance"}), 400

    account["balance"] -= amount

    return jsonify({
        "message": "Withdrawal successful",
        "balance": account["balance"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)