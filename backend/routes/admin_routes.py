from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from functools import wraps
from db import get_connection

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

# --- Admin Dashboard ---
@admin.route("/dashboard") # Fixed: Moved to a new line
@admin_required
def admin_dashboard():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    

    cursor.execute("SELECT COUNT(*) as users FROM users WHERE role='user'")
    total_users = cursor.fetchone()['users']
    # Statistics for the dashboard cards
    cursor.execute("SELECT COUNT(*) as total FROM reported_items")
    total_reports = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as pending FROM claims WHERE claim_status='pending'")
    pending_claims = cursor.fetchone()['pending']
    
    cursor.execute("SELECT COUNT(*) as resolved FROM reported_items WHERE status='claimed'")
    resolved_items = cursor.fetchone()['resolved']
    
    cursor.execute("SELECT COUNT(*) as users FROM users WHERE role='user'")
    total_users = cursor.fetchone()['users']
    
    # Fetch 5 most recent reported items for Recent Activity
    cursor.execute("SELECT item_name, created_at FROM reported_items ORDER BY created_at DESC LIMIT 5")
    recent_items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("admin/adminhome.html", 
                           total_reports=total_reports, 
                           pending_claims=pending_claims, 
                           resolved_items=resolved_items, 
                           total_users=total_users,
                           recent_items=recent_items)

# --- Item Management ---
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
    cursor.execute("SELECT * FROM reported_items WHERE item_id = %s", (item_id,))
    item = cursor.fetchone()
    cursor.execute("SELECT * FROM claims WHERE item_id = %s", (item_id,))
    claims = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/item_details.html", item=item, claims=claims)

@admin.route("/delete-item/<int:item_id>", methods=["POST"])
@admin_required
def delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM claims WHERE item_id = %s", (item_id,))
        cursor.execute("DELETE FROM reported_items WHERE item_id = %s", (item_id,))
        conn.commit()
        flash("🗑️ Item and associated claims deleted.", "warning")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.reported_items_page'))

# --- Claim Management ---
@admin.route("/claims")
@admin_required
def claims_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM claims WHERE claim_status = 'pending' ORDER BY claim_date DESC")
    all_claims = cursor.fetchall() 
    cursor.close()
    conn.close()
    return render_template("admin/claimrequest.html", claims=all_claims)

@admin.route("/approve_claim/<int:claim_id>/<int:item_id>", methods=["POST"])
@admin_required
def approve_claim(claim_id, item_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE claims SET claim_status = 'approved' WHERE claim_id = %s", (claim_id,))
        cursor.execute("UPDATE claims SET claim_status = 'rejected' WHERE item_id = %s AND claim_id != %s", (item_id, claim_id))
        cursor.execute("UPDATE reported_items SET status = 'claimed' WHERE item_id = %s", (item_id,))
        conn.commit()
        flash("✅ Claim approved and item successfully closed!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.reported_items_page'))

@admin.route("/reject_claim/<int:claim_id>/<int:item_id>", methods=["POST"])
@admin_required
def reject_claim(claim_id, item_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE claims SET claim_status = 'rejected' WHERE claim_id = %s", (claim_id,))
        conn.commit()
        flash("🚫 Claim rejected successfully.", "warning")
    except Exception as e:
        flash(f"❌ Error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.item_details', item_id=item_id))

# --- User Management ---
@admin.route("/users")
@admin_required
def users_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, email, phone, role, status FROM users")
    all_users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/users.html", users=all_users)

@admin.route("/block-user/<int:user_id>", methods=["POST"])
@admin_required
def block_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET status = 'blocked' WHERE id = %s", (user_id,))
        conn.commit()
        flash("🚫 User blocked successfully.", "success")
    except Exception as e:
        flash(f"❌ Error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.users_page'))

@admin.route("/unblock-user/<int:user_id>", methods=["POST"])
@admin_required
def unblock_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET status = 'active' WHERE id = %s", (user_id,))
        conn.commit()
        flash("✅ User unblocked successfully.", "success")
    except Exception as e:
        flash(f"❌ Error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.users_page'))

@admin.route("/delete-user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM claims WHERE claimant_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash("🗑️ User and their claims have been permanently deleted.", "warning")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error deleting user: {e}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.users_page'))