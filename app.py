from flask import Flask, render_template, request, redirect, session, flash
from db import init_db
from models import db, User
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
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Check existing user in DB
        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing:
            flash("Username or email already exists.")
            return render_template("register.html")

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            cash=10000.0
        )

        db.session.add(new_user)
        db.session.commit()

        # Store session
        session["user"] = new_user.username
        session["user_id"] = new_user.id
        session["username"] = new_user.username
        session["email"] = new_user.email
        session["cash"] = str(new_user.cash)
        session["logged_in"] = True

        return redirect("/dashboard")

    return render_template("register.html")


# USERS PAGE (UPDATED TO DATABASE)
@app.route("/users")
def users_page():
    if "user" not in session:
        return redirect("/login")

    users = User.query.all()

    user_list = []
    for u in users:
        user_list.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "joinTime": u.created_at.strftime("%Y-%m-%d %H:%M")
        })

    return render_template("users.html", users=user_list)


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


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)