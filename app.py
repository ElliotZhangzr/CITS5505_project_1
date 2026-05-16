from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, flash, jsonify, url_for
from flask_wtf.csrf import CSRFError, CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from db import init_db
from models import db, User, Stock, StockPrice, StockTransaction, Feedback
from forms import ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm

from user_service import get_users_paginated
from achievement_service import get_user_achievements
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
import base64
import binascii
import os
import re
import secrets
import traceback
from functools import wraps
from pathlib import Path
from forms import EmptyForm

from flask_migrate import Migrate


load_dotenv()
 
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
csrf = CSRFProtect(app)
init_db(app)
migrate = Migrate(app, db)

AVATAR_UPLOAD_DIR = Path(app.root_path) / "static" / "uploads" / "avatars"
AVATAR_DATA_URL_RE = re.compile(
    r"^data:(image/[a-zA-Z0-9.+-]+)(?:;[a-zA-Z0-9.+-]+=[^;,]+)*;base64,(.+)$",
    re.IGNORECASE,
)
 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
 
with app.app_context():
    load_stock_configs()


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))

        if not current_user.is_admin:
            flash("Admin access required.")
            return redirect(url_for("dashboard"))

        return view_func(*args, **kwargs)

    return wrapped_view


def build_admin_user_rows(users):
    return [
        {
            "user": user,
            "is_current_user": user.id == current_user.id,
            "role_label": "Admin" if user.is_admin else "Normal User",
            "action_label": "Remove Admin" if user.is_admin else "Make Admin",
        }
        for user in users
    ]


# ADMIN STOCK MANAGEMENT
@app.route("/admin/stocks", methods=["GET", "POST"])
@login_required
@admin_required
def admin_stocks():
    if request.method == "POST":
        symbol = request.form.get("symbol", "").strip().upper()
        name = request.form.get("name", "").strip()
        base_price = request.form.get("base_price", "").strip()

        if not symbol or not name or not base_price:
            flash("All fields are required.")
            return redirect("/admin/stocks")

        existing_stock = Stock.query.filter_by(symbol=symbol).first()

        if existing_stock:
            flash("Stock symbol already exists.")
            return redirect("/admin/stocks")

        try:
            base_price = float(base_price)

            new_stock = Stock(
                symbol=symbol,
                name=name,
                base_price=base_price
            )

            db.session.add(new_stock)
            db.session.flush()

            stock_price = StockPrice(
                stock_id=new_stock.id,
                price=base_price
            )

            db.session.add(stock_price)
            db.session.commit()

            flash("Stock added successfully.")

        except ValueError:
            flash("Invalid base price.")

        return redirect("/admin/stocks")

    stocks = Stock.query.order_by(Stock.symbol).all()

    return render_template(
        "admin_stocks.html",
        stocks=stocks
    )

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
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")
 
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
    search = request.args.get("q", "")
    data = get_users_paginated(page=page, search=search)
    return render_template(
        "users.html",
        users=data["users"],
        has_next=data["has_next"],
        has_prev=data["has_prev"],
        page=data["page"],
        search=data["search"],
    )


@app.route("/users/<int:user_id>")
@login_required
def public_profile(user_id):
    user = User.query.get_or_404(user_id)
    portfolio = None if user.hide_holdings else build_portfolio(user.id)

    return render_template(
        "public_profile.html",
        user=user,
        portfolio=portfolio,
        achievements=get_user_achievements(user),
    )

# ADMIN DASHBOARD
@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_stocks = Stock.query.count()
    total_transactions = StockTransaction.query.count()
    total_feedback = Feedback.query.count()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_stocks=total_stocks,
        total_transactions=total_transactions,
        total_feedback=total_feedback,
    )

# ADMIN USER MANAGEMENT
@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()

    form = EmptyForm()

    return render_template(
        "admin_users.html",
        user_rows=build_admin_user_rows(users),
        form=form
    )

@app.route("/admin/users/<int:user_id>/toggle-admin", methods=["POST"])
@login_required
@admin_required
def toggle_admin_role(user_id):
    if user_id == current_user.id:
        flash("You cannot change your own admin role.")
        return redirect(url_for("admin_users"))

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin

    db.session.commit()

    flash("User role updated successfully.")
    return redirect(url_for("admin_users"))

 
 
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
    return render_template(
        "profile.html",
        user=current_user,
        achievements=get_user_achievements(current_user),
    )


@app.route("/profile/update_bio", methods=["POST"])
@login_required
def update_bio():
    data = request.get_json()
    bio = data.get("bio", "").strip()
    if len(bio) > 200:
        return jsonify({"ok": False, "error": "Bio must be 200 characters or less."}), 400
    user = db.session.get(User, current_user.id)
    user.bio = bio
    db.session.commit()
    return jsonify({"ok": True})

@app.route("/profile/update_avatar", methods=["POST"])
@login_required
def update_avatar():
    data = request.get_json(silent=True) or {}
    avatar_data = data.get("avatar_data", "").strip()

    if not avatar_data:
        return jsonify({"ok": False, "error": "Avatar image data is required."}), 400

    match = AVATAR_DATA_URL_RE.match(avatar_data)
    if not match:
        return jsonify({"ok": False, "error": "Invalid avatar data."}), 400

    mime_type, encoded_avatar = match.groups()
    if mime_type.lower() != "image/png":
        return jsonify({"ok": False, "error": "Avatar must be saved as PNG."}), 400

    try:
        avatar_bytes = base64.b64decode(encoded_avatar, validate=True)
    except (binascii.Error, ValueError):
        return jsonify({"ok": False, "error": "Invalid avatar encoding."}), 400

    if not avatar_bytes:
        return jsonify({"ok": False, "error": "Avatar file is empty."}), 400

    AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    avatar_filename = f"user_{current_user.id}.png"
    avatar_path = AVATAR_UPLOAD_DIR / avatar_filename
    avatar_path.write_bytes(avatar_bytes)
    avatar_url = url_for("static", filename=f"uploads/avatars/{avatar_filename}")

    user = db.session.get(User, current_user.id)
    user.avatar_url = avatar_url
    db.session.commit()
    return jsonify({"ok": True, "avatar_url": user.avatar_url})


@app.route("/profile/update_hide_holdings", methods=["POST"])
@login_required
def update_hide_holdings():
    data = request.get_json()
    current_user.hide_holdings = data.get("hide_holdings", False)
    db.session.commit()
    return jsonify({"ok": True})

@app.route("/admin/feedback")
@login_required
@admin_required
def admin_feedback():
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template("admin_feedback.html", feedbacks=feedbacks)


@app.route("/api/feedback", methods=["POST"])
@login_required
def submit_feedback():
    data = request.get_json(silent=True) or {}
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"ok": False, "error": "Feedback cannot be empty."}), 400
    if len(content) > 1000:
        return jsonify({"ok": False, "error": "Feedback must be 1000 characters or less."}), 400
    db.session.add(Feedback(user_id=current_user.id, content=content))
    db.session.commit()
    return jsonify({"ok": True})


# DELETE ACCOUNT
@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    password = request.form.get("password")

    user = db.session.get(User, current_user.id)

    if not user:
        flash("User not found.")
        return redirect(url_for("login"))

    if not check_password_hash(user.password_hash, password):
        flash("Password confirmation failed.")
        return redirect(url_for("profile"))

    logout_user()

    db.session.delete(user)
    db.session.commit()

    flash("Account deleted successfully.")
    return redirect(url_for("register"))

# LOGOUT
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))
 
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
