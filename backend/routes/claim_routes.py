import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from db import get_connection

claims_bp = Blueprint('claims', __name__)

# Folder to save proof files - ensure path matches your structure
UPLOAD_FOLDER = os.path.abspath("../frontend/static/uploads/proofs")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
@claims_bp.route('/claim/<int:item_id>', methods=['GET', 'POST'])
def claim_item(item_id):
    claimant_id = session.get('user_id')
    
    if not claimant_id:
        flash("Please login first to claim an item.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # Get data from the form fields
        claimant_name = request.form.get('fullName')
        claimant_email = request.form.get('email')
        claimant_phone = request.form.get('phone')
        # Note: You have 'description' in the form, but no column for it in the 'claims' table screenshot.
        # If you want to save description, you should add a column to your DB first.

        file = request.files.get('identityProof')

        # File Upload Logic
        proof_file_path = "No file uploaded"
        if file and file.filename != '':
            filename = secure_filename(f"item{item_id}_user{claimant_id}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            proof_file_path = f"uploads/proofs/{filename}"

        # Insert into Database
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Updated query to match your screenshot columns exactly
            query = """
                INSERT INTO claims (
                    item_id, 
                    claimant_id, 
                    claimant_name, 
                    claimant_email, 
                    claimant_phone, 
                    identity_proof_path, 
                    claim_status
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, 'pending')
            """
            
            # Execute with all the details from the form
            cursor.execute(query, (
                item_id, 
                claimant_id, 
                claimant_name, 
                claimant_email, 
                claimant_phone, 
                proof_file_path
            ))
            
            conn.commit()
            flash("Claim submitted successfully!", "success")
            return redirect(url_for('user.user_dashboard'))

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error: {e}")
            flash("An error occurred while submitting your claim.", "danger")
        finally:
            if conn:
                cursor.close()
                conn.close()

    return render_template('users/claim.html', item_id=item_id)