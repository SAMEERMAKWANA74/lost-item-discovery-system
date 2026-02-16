import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from db import get_connection

report_bp = Blueprint('report', __name__)

# Configure upload folder for item images
UPLOAD_FOLDER = 'static/uploads/items'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@report_bp.route('/report', methods=['GET', 'POST'])
def report_item():
    # 1. Security Check: Ensure user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login to report an item.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # 2. Extract data from the form
        item_type = request.form.get('item_type')
        item_name = request.form.get('item_name')
        category = request.form.get('category')
        lost_date = request.form.get('lost_date')
        location = request.form.get('location')
        description = request.form.get('description')
        unique_mark = request.form.get('unique_mark')
        contact_info = request.form.get('contact_info')
        file = request.files.get('item_image')

        # 3. Handle Image Upload
        image_path = "default.png" # Fallback if no image is uploaded
        if file and file.filename != '':
            filename = secure_filename(f"user{user_id}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = f"uploads/items/{filename}"

        # 4. Database Insertion
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO reported_items 
                (item_type, item_name, category, lost_date, location, description, unique_mark, image_path, contact_info, reported_by, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            """
            
            cursor.execute(query, (
                item_type, item_name, category, lost_date, 
                location, description, unique_mark, image_path, 
                contact_info, user_id
            ))
            
            conn.commit()
            flash("Item reported successfully! It is now visible to others.", "success")
            return redirect(url_for('user.user_dashboard'))

        except Exception as e:
            if conn: conn.rollback()
            print(f"Insertion Error: {e}")
            flash("Error saving your report. Please check the data format.", "danger")
        finally:
            if conn:
                cursor.close()
                conn.close()

    # GET: Show the reporting form
    return render_template('users/report.html')