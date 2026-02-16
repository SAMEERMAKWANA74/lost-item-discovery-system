from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from functools import wraps
from db import get_connection

# Define the blueprint
admin = Blueprint("admin", __name__, url_prefix="/admin")

# --- Decorator to protect admin routes ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session or session.get("role") != "admin":
            flash("❌ Admin access required.", "danger")
            return redirect(url_for("auth.home"))
        return f(*args, **kwargs)
    return decorated_function

# --- Admin Routes ---

@admin.route("/dashboard")
@admin_required
def admin_dashboard():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as total FROM reported_items")
    total_reports = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as pending FROM claims WHERE claim_status='pending'")
    pending_claims = cursor.fetchone()['pending']
    
    cursor.execute("SELECT COUNT(*) as resolved FROM reported_items WHERE status='claimed'")
    resolved_items = cursor.fetchone()['resolved']
    
    cursor.execute("SELECT COUNT(*) as users FROM users WHERE role='user'")
    total_users = cursor.fetchone()['users']
    
    cursor.close()
    conn.close()
    
    return render_template("admin/adminhome.html", 
                           total_reports=total_reports, 
                           pending_claims=pending_claims, 
                           resolved_items=resolved_items, 
                           total_users=total_users)

@admin.route("/reported-items")
@admin_required
def reported_items_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reported_items ORDER BY item_id DESC")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/reported_item.html", items=items)

@admin.route("/item-details/<int:item_id>")
@admin_required
def item_details(item_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch item data
    cursor.execute("SELECT * FROM reported_items WHERE item_id = %s", (item_id,))
    item = cursor.fetchone()

    # JOIN with users using email (since username column doesn't exist)
    query = """
        SELECT c.*, u.email 
        FROM claims c
        JOIN users u ON c.claimant_id = u.id
        WHERE c.item_id = %s
    """
    cursor.execute(query, (item_id,))
    claims = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("admin/item_details.html", item=item, claims=claims)

@admin.route("/approve-claim/<int:claim_id>/<int:item_id>", methods=["POST"])
@admin_required
def approve_claim(claim_id, item_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE claims SET claim_status = 'approved' WHERE claim_id = %s", (claim_id,))
        cursor.execute("UPDATE claims SET claim_status = 'rejected' WHERE item_id = %s AND claim_id != %s", (item_id, claim_id))
        cursor.execute("UPDATE reported_items SET status = 'claimed' WHERE item_id = %s", (item_id,))
        conn.commit()
        flash("✅ Claim approved!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.reported_items_page'))

@admin.route("/delete-item/<int:item_id>", methods=["POST"])
@admin_required
def delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM claims WHERE item_id = %s", (item_id,))
        cursor.execute("DELETE FROM reported_items WHERE item_id = %s", (item_id,))
        conn.commit()
        flash("🗑️ Item deleted.", "warning")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.reported_items_page'))

@admin.route("/users")
@admin_required
def users_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, email, role FROM users")
    all_users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/users.html", users=all_users)