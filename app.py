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
                return redirect("/")

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
        return f'''
            <h2>Welcome {session["user"]}</h2>
            <a href="/logout"><button>Logout</button></a>
        '''
    return redirect("/login")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)