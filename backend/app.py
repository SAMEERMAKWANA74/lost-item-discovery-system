from flask import Flask, session, redirect, url_for
import os
# Import your Blueprint objects
from routes.auth_routes import auth
from routes.admin_routes import admin
from routes.user_routes import user
from routes.report import report_bp
from routes.search import search_bp 
from routes.claim_routes import claims_bp  

# 1. First, define the paths
template_dir = os.path.abspath("../frontend/templates")
static_dir = os.path.abspath("../frontend/static")

# 2. CREATE THE APP
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = "super_secure_secret_key"

# 3. REGISTER BLUEPRINTS
app.register_blueprint(auth) 
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(user, url_prefix="/user")
app.register_blueprint(report_bp) 
app.register_blueprint(search_bp, url_prefix="/user")

# ADD THIS LINE TO FIX THE BUILD ERROR:
app.register_blueprint(claims_bp, url_prefix="/user") 

@app.route('/')
def index():
    return redirect(url_for('auth.home'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.home'))

if __name__ == "__main__":
    app.run(debug=True)