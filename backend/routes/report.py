import os
from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from werkzeug.utils import secure_filename
from db import get_connection

# Prefix matches the form action "/user/report"
report_bp = Blueprint("report_bp", __name__, url_prefix="/user")

# Updated UPLOAD_FOLDER to reach from backend to frontend/static/uploads
# This matches your folder structure
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/static/uploads"))

@report_bp.route("/report", methods=["GET", "POST"])
def report_item():
    # Protection: Ensure user is logged in
    if "email" not in session:
        return redirect(url_for("auth.home"))

    if request.method == "POST":
        # 1. Collect data from the HTML form
        data = {
            "type": request.form.get("item_type"),
            "name": request.form.get("item_name"),
            "cat": request.form.get("category"),
            "date": request.form.get("item_date"),
            "loc": request.form.get("location"),
            "desc": request.form.get("description"),
            "mark": request.form.get("unique_id"),
            "cont": request.form.get("contact"),
            "user_email": session.get("email")
        }

        # 2. Handle file upload logic
        file = request.files.get("image")
        image_db_name = None  # Renamed for clarity: we only store the filename
        
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            
            # Ensure the directory exists
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
                
            # Save the physical file
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            
            # IMPORTANT: Store ONLY the filename
            # This allows url_for('static', filename='uploads/' + item.image_path) to work
            image_db_name = filename

        # 3. Database Operations
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # --- STEP A: Get the numeric ID for the user ---
            # Using 'id' as per your database structure
            cursor.execute("SELECT id FROM users WHERE email = %s", (data["user_email"],))
            user_record = cursor.fetchone()
            
            if not user_record:
                flash("❌ Error: User record not found. Please log in again.")
                return redirect(url_for("auth.home"))
            
            actual_user_id = user_record['id']

            # --- STEP B: Insert into reported_items ---
            # Matches your schema: item_id(AI), item_type, item_name, category, lost_date, 
            # location, description, unique_mark, image_path, contact_info, reported_by, status
            query = """
                INSERT INTO reported_items 
                (item_type, item_name, category, lost_date, location, description, 
                 unique_mark, image_path, contact_info, reported_by, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            """
            
            cursor.execute(query, (
                data["type"], 
                data["name"], 
                data["cat"], 
                data["date"], 
                data["loc"], 
                data["desc"], 
                data["mark"], 
                image_db_name, # Storing filename like 'watch1.png'
                data["cont"], 
                actual_user_id 
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash("✅ Item reported successfully!")
            return redirect(url_for("user.user_dashboard"))

        except Exception as e:
            print(f"DATABASE INSERT ERROR: {e}") 
            flash(f"❌ Database error: {e}")
            return redirect(url_for("report_bp.report_item"))

    # If the method is GET, just show the report page
    return render_template("users/report.html")