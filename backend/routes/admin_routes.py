from flask import Blueprint, render_template, redirect, url_for, session, flash
from functools import wraps

# Define the blueprint with the prefix /admin
admin = Blueprint("admin", __name__, url_prefix="/admin")

# --- Decorator to protect admin routes ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Checks if user is logged in and is an admin
        if "email" not in session or session.get("role") != "admin":
            flash("❌ Admin access required.")
            # Redirecting to 'home' because it is in your main app.py
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

# --- Admin Routes ---

@admin.route("/dashboard")
@admin_required
def admin_dashboard():
    # Renders the admin dashboard template
    return render_template("admin/adminhome.html")

@admin.route("/reported-items")
@admin_required
def reported_items_page():
    # Renders the reported items template
    return render_template("admin/reported_item.html")

@admin.route("/users")
@admin_required
def users_page():
    # Renders the user management template
    return render_template("admin/users.html")