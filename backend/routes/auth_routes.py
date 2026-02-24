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

            cursor.execute("SELECT * FROM users WHERE LOWER(email)=%s", (email_input,))
            user_data = cursor.fetchone()

            cursor.close()
            conn.close()

            if not user_data:
                flash("❌ Email not found.", "danger")
                return redirect(url_for("auth.login"))

            # --- SECURITY CHECK: IS THE USER BLOCKED? ---
            if user_data.get("status") == "blocked":
                flash("🚫 Your account has been blocked. Please contact the administrator.", "danger")
                return redirect(url_for("auth.login"))

            stored_hash = user_data["password"].replace("$2y$", "$2b$", 1)

            if bcrypt.check_password_hash(stored_hash, password_input):
                session["user_id"] = user_data["id"]
                session["full_name"] = user_data.get("full_name") # Store name in session
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
        # Capture all 4 fields from your new signup.html
        full_name = request.form.get("full_name").strip()
        email = request.form.get("email").strip().lower()
        phone = request.form.get("phone").strip()
        password = request.form.get("password").strip()

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Updated query to include full_name, phone, and default status
            cursor.execute(
                "INSERT INTO users (full_name, email, phone, password, role, status) VALUES (%s, %s, %s, %s, %s, %s)",
                (full_name, email, phone, hashed_pw, "user", "active")
            )
            conn.commit()

            cursor.close()
            conn.close()

            flash("✅ Signup successful. Please login.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            # Most likely a duplicate email error
            flash("❌ Signup failed. Email may already be registered.", "danger")
            return redirect(url_for("auth.signup"))

    return render_template("signup.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.home"))