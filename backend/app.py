from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

ADMIN_EMAIL = "admin@gmail.com"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]

        if email == ADMIN_EMAIL:
            return redirect(url_for("admin"))
        else:
            return redirect(url_for("user"))

    return render_template("login.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/user")
def user():
    return render_template("user.html")

if __name__ == "__main__":
    app.run(debug=True)
