from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, session, flash, jsonify, url_for
from flask_wtf.csrf import CSRFError, CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from db import init_db
from forms import ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm
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
import traceback

load_dotenv()
 
app = Flask(__name__)
app.secret_key = "secret123"
csrf = CSRFProtect(app)
init_db(app)
 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
 
with app.app_context():
    load_stock_configs()
 
 
# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
 
        if user and not check_password_hash(user.password_hash, password):
            user = None
 
        if user:
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
 
        flash("Username or password incorrect.")
        return render_template("login.html", form=form)
 
    return render_template("login.html", form=form)
 
 
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if request.method == "GET":
        form.email.data = request.args.get("email", "")
 
    if form.validate_on_submit():
        email = form.email.data
 
        try:
            success, message = request_password_reset(email)
        except Exception:
            traceback.print_exc()
            success = False
            message = "Failed to send verification code. Please try again later."
 
        flash(message)
 
        if success:
            return redirect(url_for("reset_password", email=(email or "").strip()))
 
    return render_template("forgot_password.html", form=form, email=form.email.data or "")
 
 
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = request.args.get("email", "")
    form = ResetPasswordForm()
 
    if request.method == "GET":
        form.email.data = email
 
    if form.validate_on_submit():
        email = form.email.data
        code = form.code.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        success, message = confirm_password_reset(email, code, new_password, confirm_password)
        flash(message)
 
        if success:
           return redirect(url_for("login"))
 
    return render_template(
        "reset_password.html",
        form=form,
        email=email,
        code_seconds_remaining=get_reset_code_seconds_remaining(email),
        resend_seconds_remaining=get_reset_code_resend_seconds_remaining(email),
    )
 
 
# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        password_hash = generate_password_hash(password)
 
        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
 
        if existing:
            flash("Username or email already exists.")
            return render_template("register.html", form=form)
 
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            cash="10000.00"
        )
        db.session.add(new_user)
        db.session.commit()
 
        login_user(new_user)
        return redirect("/dashboard")
 
    return render_template("register.html", form=form)
 
 
@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Invalid or missing CSRF token."}), 400
 
    flash("Invalid or missing CSRF token.")
    return redirect(request.referrer or url_for("login"))
 
 
# HOME
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))
 
 
# DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
 
 
# LEADERBOARD
@app.route("/leaderboard")
@login_required
def leaderboard():
    ranking_type = request.args.get("type", "cash")
    context = get_leaderboard_context(ranking_type, current_user.username)
    return render_template("leaderboard.html", **context)
 
 
# USERS WITH PAGINATION
@app.route("/users")
@login_required
def users():
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
@login_required
def api_stocks():
    limit = request.args.get("limit", 400, type=int)
    return jsonify(get_stock_data(limit=limit))
 
 
@app.route("/api/stocks/latest")
@login_required
def api_stock_prices():
    latest_prices = update_prices_if_due()
    return jsonify({"latestPrices": latest_prices})
 
 
@app.route("/api/portfolio")
@login_required
def api_portfolio():
    portfolio = build_portfolio(current_user.id)
    return jsonify(portfolio)
 
 
@app.route("/api/trades", methods=["POST"])
@login_required
def api_trades():
    data = request.get_json(silent=True) or {}
    portfolio, error = execute_stock_trade_from_payload(current_user.id, data)
 
    if error:
        return jsonify({"error": error}), 400
 
    return jsonify(portfolio)
 
 
@app.route("/api/trades")
@login_required
def api_trade_history():
    limit = request.args.get("limit", 50, type=int)
    return jsonify({"transactions": get_transaction_history(current_user.id, limit=limit)})
 
 
# PROFILE
@app.route("/profile")
@login_required
def profile():
    user = User.query.get(current_user.id)
    return render_template("profile.html", user=user)
 
 
@app.route("/profile/update_bio", methods=["POST"])
@login_required
def update_bio():
    data = request.get_json()
    user = User.query.get(current_user.id)
    user.bio = data.get("bio", "")
    db.session.commit()
    return jsonify({"ok": True})
 
 
@app.route("/profile/update_avatar", methods=["POST"])
@login_required
def update_avatar():
    data = request.get_json()
    user = User.query.get(current_user.id)
    user.avatar_url = data.get("avatar_url", "")
    db.session.commit()
    return jsonify({"ok": True})
 
 
@app.route("/profile/update_hide_holdings", methods=["POST"])
@login_required
def update_hide_holdings():
    data = request.get_json()
    user = User.query.get(current_user.id)
    user.hide_holdings = data.get("hide_holdings", False)
    db.session.commit()
    return jsonify({"ok": True})
 
 
# DELETE ACCOUNT
@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    db.session.delete(user)
    db.session.commit()
    logout_user()
    return redirect(url_for("register"))
 
 
# LOGOUT
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))
 
 
if __name__ == "__main__":
    app.run(debug=True)
