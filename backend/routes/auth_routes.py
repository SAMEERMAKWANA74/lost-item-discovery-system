from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_connection
from flask_bcrypt import Bcrypt

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/")
def home():
    return render_template("login.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_input = request.form.get("email").strip().lower()
        password_input = request.form.get("password").strip()

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            cursor.close()
            conn.close()

            user = None
            for u in users:
                if u["email"].strip().lower() == email_input:
                    user = u
                    break

            if not user:
                flash("❌ Email not found")
                return redirect(url_for("auth.login"))

            stored_hash = user["password"].replace("$2y$", "$2b$", 1)

            if bcrypt.check_password_hash(stored_hash, password_input):
                session["email"] = user["email"]
                session["role"] = user["role"].lower()

                if session["role"] == "admin":
                    return redirect(url_for("admin.dashboard"))
                return redirect(url_for("user.dashboard"))

            flash("❌ Invalid password")
            return redirect(url_for("auth.login"))

        except Exception as e:
            flash(f"❌ Error: {e}")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password").strip()
        hashed_pw = bcrypt.generate_password_hash(password).decode()

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

            flash("✅ Signup successful")
            return redirect(url_for("auth.home"))

        except:
            flash("❌ Signup failed")
            return redirect(url_for("auth.signup"))

    return render_template("signup.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.home"))
