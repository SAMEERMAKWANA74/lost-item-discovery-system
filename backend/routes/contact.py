from flask import Blueprint, render_template, request, flash, redirect, url_for
from db import get_connection

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = "INSERT INTO contact_messages (name, email, subject, message) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, subject, message))
            conn.commit()
            flash("✅ Your message has been sent! We will get back to you soon.", "success")
        except Exception as e:
            print(f"Error: {e}")
            flash("❌ Something went wrong. Please try again.", "danger")
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('contact.contact_page'))

    return render_template('users/contact.html')
