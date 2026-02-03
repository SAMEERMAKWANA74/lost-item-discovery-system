from flask import Blueprint, render_template, request, session, redirect, url_for
from db import get_connection

# Define the Blueprint for search-related functionality
search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET"])
def search_item():
    """Handles item searching and filtering."""
    if "email" not in session:
        return redirect(url_for("auth.home"))

    # 1. Get search filters from the URL parameters
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '')
    item_type = request.args.get('type', '')

    # 2. Establish database connection
    conn = get_connection()
    if conn is None:
        return "Database Connection Error", 500
        
    cursor = conn.cursor(dictionary=True)

    # 3. Construct dynamic SQL query
    # Uses your table name 'reported_items'
    query = "SELECT * FROM reported_items WHERE 1=1"
    params = []

    if keyword:
        query += " AND (item_name LIKE %s OR description LIKE %s)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    
    if category:
        query += " AND category = %s"
        params.append(category)
        
    if item_type:
        query += " AND item_type = %s"
        params.append(item_type)

    # 4. Execute query and retrieve results
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()

    # 5. Render the search results page
    return render_template("users/search.html", results=results)

@search_bp.route("/item-details/<int:item_id>")
def item_details(item_id):
    """Fetches details for a specific item by its unique ID."""
    if "email" not in session:
        return redirect(url_for("auth.home"))

    conn = get_connection()
    if conn is None:
        return "Database Connection Error", 500

    cursor = conn.cursor(dictionary=True)
    
    # Select the item using 'item_id' column
    cursor.execute("SELECT * FROM reported_items WHERE item_id = %s", (item_id,))
    item = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if not item:
        # If no item is found with that ID, show a 404 error
        return "Item not found", 404

    # Render the details template with the specific item data
    return render_template("users/item_details.html", item=item)