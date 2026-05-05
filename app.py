from flask import Flask, render_template, request, redirect, session, flash, jsonify, url_for
from dotenv import load_dotenv
from db import init_db
from models import db, User
from user_service import get_users_paginated
from leaderboard import get_leaderboard_context
from stock_data import get_stock_data
from stock_simulator import load_stock_configs, update_prices_if_due
from trading_service import build_portfolio, execute_stock_trade_from_payload, get_transaction_history
from password_reset_service import (
    confirm_password_reset,
    get_reset_code_resend_seconds_remaining,
    get_reset_code_seconds_remaining,
    request_password_reset,
)
import hashlib
import traceback

load_dotenv()

app = Flask(__name__)
app.secret_key = "secret123"
init_db(app)

with app.app_context():
    load_stock_configs()


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).filter_by(password_hash=password_hash).first()

        if user:
            session["user"] = user.username
            session["user_id"] = user.id
            session["username"] = user.username
            session["email"] = user.email
            session["cash"] = str(user.cash)
            session["logged_in"] = True
            return redirect("/dashboard")

        flash("Username or password incorrect.")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        try:
            success, message = request_password_reset(email)
        except Exception:
            traceback.print_exc()
            success = False
            message = "Failed to send verification code. Please try again later."

        flash(message)

        if success:
            return redirect(url_for("reset_password", email=(email or "").strip()))

    return render_template("forgot_password.html", email=request.args.get("email", ""))


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = request.args.get("email", "")

    if request.method == "POST":
        email = request.form.get("email")
        code = request.form.get("code")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        success, message = confirm_password_reset(email, code, new_password, confirm_password)
        flash(message)

        if success:
            return redirect("/login")

    return render_template(
        "reset_password.html",
        email=email,
        code_seconds_remaining=get_reset_code_seconds_remaining(email),
        resend_seconds_remaining=get_reset_code_resend_seconds_remaining(email),
    )


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing:
            flash("Username or email already exists.")
            return render_template("register.html")

        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            cash="10000.00"
        )
        db.session.add(new_user)
        db.session.commit()

        session["user"] = new_user.username
        session["user_id"] = new_user.id
        session["username"] = new_user.username
        session["email"] = new_user.email
        session["cash"] = str(new_user.cash)
        session["logged_in"] = True

        return redirect("/dashboard")

    return render_template("register.html")


# HOME
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")


# LEADERBOARD
@app.route("/leaderboard")
def leaderboard():
    if "user" not in session:
        return redirect("/login")
    
    ranking_type = request.args.get("type", "cash")
    context = get_leaderboard_context(ranking_type, session["user"])

    return render_template(
        "leaderboard.html",
        **context
    )


# USERS WITH PAGINATION
@app.route("/users")
def users():
    if "user" not in session:
        return redirect("/login")

    page = request.args.get("page", 1, type=int)

    data = get_users_paginated(page=page)

    return render_template(
        "users.html",
        users=data["users"],
        has_next=data["has_next"],
        has_prev=data["has_prev"],
        page=data["page"]
    )


@app.route("/api/stocks")
def api_stocks():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    limit = request.args.get("limit", 400, type=int)
    return jsonify(get_stock_data(limit=limit))


@app.route("/api/stocks/latest")
def api_stock_prices():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    latest_prices = update_prices_if_due()
    return jsonify({"latestPrices": latest_prices})


@app.route("/api/portfolio")
def api_portfolio():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    portfolio = build_portfolio(session["user_id"])
    session["cash"] = f"{portfolio['cash']:.2f}"
    return jsonify(portfolio)


@app.route("/api/trades", methods=["POST"])
def api_trades():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json(silent=True) or {}
    portfolio, error = execute_stock_trade_from_payload(session["user_id"], data)

    if error:
        return jsonify({"error": error}), 400

    session["cash"] = f"{portfolio['cash']:.2f}"
    return jsonify(portfolio)


@app.route("/api/trades")
def api_trade_history():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    limit = request.args.get("limit", 50, type=int)
    return jsonify({"transactions": get_transaction_history(session["user_id"], limit=limit)})


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host="127.0.0.1", port=5000, debug=False)
