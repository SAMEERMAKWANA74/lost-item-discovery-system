from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from db import get_connection

auth = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth.record_once
def on_load(state):
    bcrypt.init_app(state.app)

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

            # Selecting the user record
            cursor.execute(
                "SELECT * FROM users WHERE LOWER(email)=%s",
                (email_input,)
            )
            user_data = cursor.fetchone()

            cursor.close()
            conn.close()

            if not user_data:
                flash("❌ Email not found.", "danger")
                return redirect(url_for("auth.login"))

            # Handle PHP-style bcrypt hashes if necessary
            stored_hash = user_data["password"].replace("$2y$", "$2b$", 1)

            if bcrypt.check_password_hash(stored_hash, password_input):
                # IMPORTANT: Set these session variables for the whole app to use
                session["user_id"] = user_data["id"]  # Match column name in your DB
                session["email"] = user_data["email"]
                session["role"] = user_data["role"].lower()

                if session["role"] == "admin":
                    return redirect(url_for("admin.admin_dashboard"))

                return redirect(url_for("user.user_dashboard"))

            flash("❌ Invalid password.", "danger")
            return redirect(url_for("auth.login"))

        except Exception as e:
            flash(f"❌ Database error: {e}", "danger")
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

            flash("✅ Signup successful. Please login.", "success")
            return redirect(url_for("auth.login"))

        except:
            flash("❌ Signup failed. Email exists.", "danger")
            return redirect(url_for("auth.signup"))

    return render_template("signup.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.home"))