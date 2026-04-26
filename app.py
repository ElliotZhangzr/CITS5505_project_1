from flask import Flask, render_template, request, redirect, session, flash
from db import init_db, get_db
import hashlib

app = Flask(__name__)
app.secret_key = "secret123"
init_db(app)

# Initialize database
init_db(app)

users = {}

# login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE (username=? OR email=?) AND password=?",
            (username, username, password_hash)
        ).fetchone()

        if user:
            # Storing the full session（includes user_id, username, cash, portfolio）
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["cash"] = user["cash"]
            session["portfolio"] = user["portfolio"]
            return redirect("/dashboard")

        flash("Incorrect username or password")
        return render_template("login.html")

    return render_template("login.html")

# register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        db = get_db()
        # Check for uniqueness
        existing = db.execute(
            "SELECT id FROM users WHERE username=? OR email=?",
            (username, email)
        ).fetchone()

        if existing:
            flash("Username or email address already exists.")
            return render_template("register.html")

        # Insert new user，cash=10000
        db.execute(
            "INSERT INTO users (username, email, password, cash, portfolio) VALUES (?,?,?,?,?)",
            (username, email, password_hash, 10000, "{}")
        )
        db.commit()

        # Automatic login: Read new user and initialize session
        new_user = db.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
        session["user_id"] = new_user["id"]
        session["username"] = new_user["username"]
        session["cash"] = new_user["cash"]
        session["portfolio"] = new_user["portfolio"]

        return redirect("/dashboard")

    return render_template("register.html")



# Home page
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")


@app.route("/leaderboard")
def leaderboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("leaderboard.html")


# logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
