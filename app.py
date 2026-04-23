from flask import Flask, render_template, request, redirect, session, flash
from db import init_db

app = Flask(__name__)
app.secret_key = "secret123"

# Initialize database
init_db(app)

users = {}

# login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        for user, data in users.items():
            if (username == user or username == data["email"]) and password == data["password"]:
                session["user"] = user
                return redirect("/dashboard")

        return render_template("fail.html")

    return render_template("login.html")

# register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        users[username] = {
            "email": email,
            "password": password
        }

        flash("Register success!")
        return redirect("/login")

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
