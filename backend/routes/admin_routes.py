from flask import Blueprint, render_template, redirect, url_for, session

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
def dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("auth.home"))
    return render_template("admin/adminhome.html")


@admin_bp.route("/reported-items")
def reported_items():
    if session.get("role") != "admin":
        return redirect(url_for("auth.home"))
    return render_template("admin/reported_item.html")


@admin_bp.route("/users")
def users():
    if session.get("role") != "admin":
        return redirect(url_for("auth.home"))
    return render_template("admin/users.html")
