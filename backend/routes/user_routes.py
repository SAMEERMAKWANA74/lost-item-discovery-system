from flask import Blueprint, render_template, redirect, url_for, session

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect(url_for("auth.home"))
    return render_template("users/index.html")


@user_bp.route("/report")
def report():
    if "email" not in session:
        return redirect(url_for("auth.home"))
    return render_template("users/report.html")


@user_bp.route("/search")
def search():
    if "email" not in session:
        return redirect(url_for("auth.home"))
    return render_template("users/search.html")


@user_bp.route("/claim")
def claim():
    if "email" not in session:
        return redirect(url_for("auth.home"))
    return render_template("users/claim.html")


@user_bp.route("/contact")
def contact():
    if "email" not in session:
        return redirect(url_for("auth.home"))
    return render_template("users/contact.html")


@user_bp.route("/item_details")
def item_details():
    if "email" not in session:
        return redirect(url_for("auth.home"))
    return render_template("users/item_details.html")
