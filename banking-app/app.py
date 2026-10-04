from flask import Flask, jsonify, request, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "banking.db"


# -------------------------
# Database connection
# -------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# Create database tables
# -------------------------

def init_db():

    conn = get_db()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Accounts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_number TEXT UNIQUE NOT NULL,
            balance REAL NOT NULL DEFAULT 10000,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Transactions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_after REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
    """)

    # Create demo user if it doesn't exist
    user = conn.execute(
        "SELECT id FROM users WHERE username = ?",
        ("shilpi",)
    ).fetchone()

    if user is None:

        cursor = conn.execute(
            """
            INSERT INTO users (username, password)
            VALUES (?, ?)
            """,
            ("shilpi", "bank123")
        )

        user_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO accounts
            (user_id, account_number, balance)
            VALUES (?, ?, ?)
            """,
            (user_id, "10001", 10000)
        )

    conn.commit()
    conn.close()


# -------------------------
# Get logged-in user's account
# -------------------------

def get_account(username):

    conn = get_db()

    account = conn.execute(
        """
        SELECT
            accounts.id,
            accounts.account_number,
            accounts.balance
        FROM accounts
        JOIN users
        ON accounts.user_id = users.id
        WHERE users.username = ?
        """,
        (username,)
    ).fetchone()

    conn.close()

    return account


# -------------------------
# Get transaction history
# -------------------------

def get_transactions(account_id):

    conn = get_db()

    transactions = conn.execute(
        """
        SELECT
            transaction_type,
            amount,
            balance_after,
            transaction_date
        FROM transactions
        WHERE account_id = ?
        ORDER BY id DESC
        """,
        (account_id,)
    ).fetchall()

    conn.close()

    return transactions


# -------------------------
# Home / Login
# -------------------------

@app.route("/")
def home():
    return render_template("login.html")


# -------------------------
# Login
# -------------------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db()

    user = conn.execute(
        """
        SELECT id, username
        FROM users
        WHERE username = ?
        AND password = ?
        """,
        (username, password)
    ).fetchone()

    conn.close()

    if user:

        account = get_account(username)

        transactions = get_transactions(account["id"])

        return render_template(
            "dashboard.html",
            account=account,
            username=username,
            transactions=transactions
        )

    return "Invalid username or password", 401


# -------------------------
# Deposit from Website
# -------------------------

@app.route("/deposit-web", methods=["POST"])
def deposit_web():

    username = "shilpi"

    try:
        amount = float(request.form.get("amount"))
    except (TypeError, ValueError):
        return "Invalid amount", 400

    if amount <= 0:
        return "Invalid amount", 400

    conn = get_db()

    account = conn.execute(
        """
        SELECT accounts.id, accounts.balance
        FROM accounts
        JOIN users
        ON accounts.user_id = users.id
        WHERE users.username = ?
        """,
        (username,)
    ).fetchone()

    new_balance = account["balance"] + amount

    conn.execute(
        """
        UPDATE accounts
        SET balance = ?
        WHERE id = ?
        """,
        (new_balance, account["id"])
    )

    conn.execute(
        """
        INSERT INTO transactions
        (
            account_id,
            transaction_type,
            amount,
            balance_after,
            transaction_date
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            account["id"],
            "Deposit",
            amount,
            new_balance,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        )
    )

    conn.commit()
    conn.close()

    account = get_account(username)
    transactions = get_transactions(account["id"])

    return render_template(
        "dashboard.html",
        account=account,
        username=username,
        transactions=transactions,
        message=f"Deposit successful: ₹{amount:.2f}"
    )


# -------------------------
# Withdraw from Website
# -------------------------

@app.route("/withdraw-web", methods=["POST"])
def withdraw_web():

    username = "shilpi"

    try:
        amount = float(request.form.get("amount"))
    except (TypeError, ValueError):
        return "Invalid amount", 400

    if amount <= 0:
        return "Invalid amount", 400

    conn = get_db()

    account = conn.execute(
        """
        SELECT accounts.id, accounts.balance
        FROM accounts
        JOIN users
        ON accounts.user_id = users.id
        WHERE users.username = ?
        """,
        (username,)
    ).fetchone()

    if amount > account["balance"]:

        conn.close()

        account = get_account(username)
        transactions = get_transactions(account["id"])

        return render_template(
            "dashboard.html",
            account=account,
            username=username,
            transactions=transactions,
            message="Insufficient balance"
        )

    new_balance = account["balance"] - amount

    conn.execute(
        """
        UPDATE accounts
        SET balance = ?
        WHERE id = ?
        """,
        (new_balance, account["id"])
    )

    conn.execute(
        """
        INSERT INTO transactions
        (
            account_id,
            transaction_type,
            amount,
            balance_after,
            transaction_date
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            account["id"],
            "Withdrawal",
            amount,
            new_balance,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        )
    )

    conn.commit()
    conn.close()

    account = get_account(username)
    transactions = get_transactions(account["id"])

    return render_template(
        "dashboard.html",
        account=account,
        username=username,
        transactions=transactions,
        message=f"Withdrawal successful: ₹{amount:.2f}"
    )


# -------------------------
# Balance API
# -------------------------

@app.route("/balance")
def balance():

    account = get_account("shilpi")

    return jsonify({
        "account_number": account["account_number"],
        "balance": account["balance"]
    })


# -------------------------
# Deposit API
# -------------------------

@app.route("/deposit", methods=["POST"])
def deposit():

    data = request.get_json()

    if not data or "amount" not in data:
        return jsonify({
            "error": "Amount is required"
        }), 400

    amount = data["amount"]

    if amount <= 0:
        return jsonify({
            "error": "Invalid amount"
        }), 400

    conn = get_db()

    account = conn.execute(
        """
        SELECT id, balance
        FROM accounts
        WHERE account_number = ?
        """,
        ("10001",)
    ).fetchone()

    new_balance = account["balance"] + amount

    conn.execute(
        """
        UPDATE accounts
        SET balance = ?
        WHERE id = ?
        """,
        (new_balance, account["id"])
    )

    conn.execute(
        """
        INSERT INTO transactions
        (
            account_id,
            transaction_type,
            amount,
            balance_after,
            transaction_date
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            account["id"],
            "Deposit",
            amount,
            new_balance,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Deposit successful",
        "balance": new_balance
    })


# -------------------------
# Withdraw API
# -------------------------

@app.route("/withdraw", methods=["POST"])
def withdraw():

    data = request.get_json()

    if not data or "amount" not in data:
        return jsonify({
            "error": "Amount is required"
        }), 400

    amount = data["amount"]

    if amount <= 0:
        return jsonify({
            "error": "Invalid amount"
        }), 400

    conn = get_db()

    account = conn.execute(
        """
        SELECT id, balance
        FROM accounts
        WHERE account_number = ?
        """,
        ("10001",)
    ).fetchone()

    if amount > account["balance"]:

        conn.close()

        return jsonify({
            "error": "Insufficient balance"
        }), 400

    new_balance = account["balance"] - amount

    conn.execute(
        """
        UPDATE accounts
        SET balance = ?
        WHERE id = ?
        """,
        (new_balance, account["id"])
    )

    conn.execute(
        """
        INSERT INTO transactions
        (
            account_id,
            transaction_type,
            amount,
            balance_after,
            transaction_date
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            account["id"],
            "Withdrawal",
            amount,
            new_balance,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Withdrawal successful",
        "balance": new_balance
    })


# -------------------------
# Initialize database
# -------------------------

init_db()


# -------------------------
# Start application
# -------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)