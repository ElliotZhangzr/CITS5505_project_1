from flask import Flask, render_template, request, redirect, session, flash
from db import init_db
from models import db, User
from user_service import get_users_paginated
import hashlib

app = Flask(__name__)
app.secret_key = "secret123"
init_db(app)


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
            cash=10000.0
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
    return render_template("leaderboard.html")


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


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)