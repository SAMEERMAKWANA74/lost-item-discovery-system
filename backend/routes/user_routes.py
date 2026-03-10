from flask import Blueprint, render_template, redirect, url_for, session
from db import get_connection

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


@user.route("/contact")
def contact_us():
    if not is_logged_in():
        return redirect(url_for("auth.home"))
    return render_template("users/contact.html")

@user.route("/my-claims")
def my_claims():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query to get item info and claim status
    query = """
        SELECT c.claim_status, c.claim_date, r.item_name, r.category
        FROM claims c
        JOIN reported_items r ON c.item_id = r.item_id
        WHERE c.claimant_id = %s
        ORDER BY c.claim_date DESC
    """
    cursor.execute(query, (user_id,))
    claims = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("users/myclaims.html", claims=claims)
