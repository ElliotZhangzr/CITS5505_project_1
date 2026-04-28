from flask import Flask, render_template, request, redirect, session, flash

app = Flask(__name__)
app.secret_key = "secret123"

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
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")

        if username in users:
            return "User already exists!"
        
        users[username] = {
         "email": email,
         "password": password
        }

        flash("Register success!")
        return redirect("/login")

    return render_template("register.html")

# users
@app.route("/users")
def users_page():
    if "user" not in session:
        return redirect("/login")

    user_list = []

    for index, (username, data) in enumerate(users.items(), start=1):
        user_list.append({
            "id": index,
            "username": username,
            "email": data["email"],
            "joinTime": "Just now"
        })

    return render_template("users.html", users=user_list)

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
