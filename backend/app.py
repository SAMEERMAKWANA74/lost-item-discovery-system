from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_connection
from flask_bcrypt import Bcrypt
import os

# --- CONFIGURE PATHS ---
template_dir = os.path.abspath("../frontend/templates")
static_dir = os.path.abspath("../frontend/static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = "super_secure_secret_key"
bcrypt = Bcrypt(app)

# --- ROUTES ---

@app.route('/')
def home():
    """Maps to the login page."""
    return render_template('login.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Clean the user input
        email_input = request.form.get("email").strip().lower()
        password_input = request.form.get("password").strip()

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Fetch everyone so we can manually strip the hidden \n found in your log
            cursor.execute("SELECT * FROM users")
            all_users = cursor.fetchall()
            
            user = None
            for row in all_users:
                # This specifically removes the 'invisible' enter key at the end of the email
                clean_db_email = row['email'].strip().lower().replace('\n', '').replace('\r', '')
                if clean_db_email == email_input:
                    user = row
                    break

            cursor.close()
            conn.close()

            if not user:
                flash("❌ Email not found.")
                return redirect(url_for("login"))

            # Convert PHP-style hashes ($2y$)
            stored_hash = user['password'].strip().replace('$2y$', '$2b$', 1)

            if bcrypt.check_password_hash(stored_hash, password_input):
                session['email'] = user['email'].strip()
                session['role'] = user['role'].strip().lower()
                
                # Role-based redirection
                if session['role'] == 'admin':
                    return redirect(url_for("admin_dashboard"))
                return redirect(url_for("user_dashboard"))
            else:
                flash("❌ Invalid password.")
                return redirect(url_for("login"))
                
        except Exception as e:
            flash(f"❌ Database error: {e}")
            return redirect(url_for("login"))
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password").strip()
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)", (email, hashed_pw, 'user'))
            conn.commit()
            cursor.close()
            conn.close()
            flash("✅ Success! Please login.")
            return redirect(url_for("home"))
        except:
            flash("❌ Signup failed.")
            return redirect(url_for("signup"))
    return render_template("signup.html")

# --- ADMIN ROUTES ---

@app.route("/admin/dashboard")
def admin_dashboard():
    if 'email' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template("admin/adminhome.html")

@app.route("/admin/reported-items")
def reported_items_page():
    """Fixes BuildError for 'reported_items_page'."""
    if 'email' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template("admin/reported_item.html")

@app.route("/admin/users")
def users_page():
    """Fixes BuildError for 'users_page'."""
    if 'email' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template("admin/users.html")

# --- USER ROUTES ---
# --- USER ROUTES ---

@app.route("/user/dashboard")
def user_dashboard():
    if 'email' not in session:
        return redirect(url_for('home'))
    return render_template("users/index.html")

@app.route("/user/report")
def report_item():
    if 'email' not in session:
        return redirect(url_for('home'))
    return render_template("users/report.html") # Matches image_d7c332.png

@app.route("/user/search")
def search_item():
    if 'email' not in session:
        return redirect(url_for('home'))
    return render_template("users/search.html") # Matches image_d7c332.png

@app.route("/user/claim")
def claim_item():
    if 'email' not in session:
        return redirect(url_for('home'))
    return render_template("users/claim.html") # Matches image_d7c332.png

@app.route("/user/contact")
def contact_us():
    if 'email' not in session:
        return redirect(url_for('home'))
    return render_template("users/contact.html") # Matches image_d7c332.png

@app.route("/user/item_details")
def item_details():
    if 'email' not in session:
        return redirect(url_for('home'))
    # Change the underscore to a dash to match your file name exactly
    return render_template("users/item_details.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)