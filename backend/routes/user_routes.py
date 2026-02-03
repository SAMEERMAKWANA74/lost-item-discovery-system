from flask import Blueprint, render_template, redirect, url_for, session

user = Blueprint("user", __name__, url_prefix="/user")

# Helper function to check login
def is_logged_in():
    return "email" in session

@user.route("/dashboard")
def user_dashboard():
    if not is_logged_in():
        return redirect(url_for("auth.home")) 
    return render_template("users/index.html")

@user.route("/report")
def report_item():
    if not is_logged_in():
        return redirect(url_for("auth.home"))
    return render_template("users/report.html")

@user.route("/claim")
def claim_item():
    if not is_logged_in():
        return redirect(url_for("auth.home"))
    return render_template("users/claim.html")

@user.route("/contact")
def contact_us():
    if not is_logged_in():
        return redirect(url_for("auth.home"))
    return render_template("users/contact.html")