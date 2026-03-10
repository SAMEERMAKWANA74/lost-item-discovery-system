from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import get_connection

myclaims_bp = Blueprint('myclaims', __name__)

@myclaims_bp.route('/my-claims')
def view_my_claims():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login to view your claims.", "warning")
        return redirect(url_for('auth.login'))

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetches all claims for the logged-in user
        query = """
            SELECT c.claim_status, c.claim_date, r.item_name, r.category
            FROM claims c
            JOIN reported_items r ON c.item_id = r.item_id
            WHERE c.claimant_id = %s
            ORDER BY c.claim_date DESC
        """
        cursor.execute(query, (user_id,))
        claims = cursor.fetchall()

        return render_template('users/myclaims.html', claims=claims)

    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500
    finally:
        if conn:
            cursor.close()
            conn.close()
