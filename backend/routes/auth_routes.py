from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from db import get_connection

auth = Blueprint("auth", __name__)
bcrypt = Bcrypt()   # ✅ CREATE HERE


@auth.record_once
def on_load(state):
    bcrypt.init_app(state.app)   # ✅ ATTACH TO APP


@auth.route("/", methods=["GET"])
def home():
    return render_template("login.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_input = request.form.get("email").strip().lower()
        password_input = request.form.get("password").strip()

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM users WHERE LOWER(email)=%s",
                (email_input,)
            )
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if not user:
                flash("❌ Email not found.")
                return redirect(url_for("auth.login"))

            stored_hash = user["password"].replace("$2y$", "$2b$", 1)

            if bcrypt.check_password_hash(stored_hash, password_input):
                session["email"] = user["email"]
                session["role"] = user["role"].lower()

                if session["role"] == "admin":
                    return redirect(url_for("admin.admin_dashboard"))

                return redirect(url_for("user.user_dashboard"))

            flash("❌ Invalid password.")
            return redirect(url_for("auth.login"))

        except Exception as e:
            flash(f"❌ Database error: {e}")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password").strip()

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (email, password, role) VALUES (%s,%s,%s)",
                (email, hashed_pw, "user")
            )
            conn.commit()

            cursor.close()
            conn.close()

            flash("✅ Signup successful. Please login.")
            return redirect(url_for("auth.login"))

        except:
            flash("❌ Signup failed. Email exists.")
            return redirect(url_for("auth.signup"))

    return render_template("signup.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.home"))
