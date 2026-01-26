from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from app.db import get_db_connection # This ensures we use the SAME database as Admin
import datetime

support_bp = Blueprint('support', __name__)

# --- ROUTES ---

@support_bp.route('/support')
def support():
    # Ensure user is logged in (optional, based on your logic)
    # return render_template('youth/youth_support.html')
    # Based on your structure it seems you might just be rendering the template:
    return render_template('youth/youth_support.html')

@support_bp.route('/submit-ticket', methods=['POST'])
def submit_ticket():
    data = request.json
    print(f"--- RECEIVED DATA: {data} ---") # Debug print

    user_id = session.get('user_id')
    # Fallback for testing if no user is logged in
    if not user_id:
        print("Warning: No user_id in session. Using placeholder ID 1.")
        user_id = 1 

    # 1. Map frontend data to variables
    issue_type = data.get('issueType')
    event_name = data.get('eventName', 'N/A')
    raw_desc = data.get('description')
    
    # Combine Event Name into description so Admin sees it clearly
    full_description = f"Event: {event_name}\n\nDetails: {raw_desc}"

    # 2. Connect to the Database
    conn = get_db_connection()

    try:
        # --- SELF-REPAIR: Create Table if it doesn't exist ---
        # This prevents "Table not found" errors
        conn.execute("""
            CREATE TABLE IF NOT EXISTS support_ticket (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (user_id)
            );
        """)

        # 3. INSERT the ticket into the database
        conn.execute(
            "INSERT INTO support_ticket (user_id, subject, description, status) VALUES (?, ?, ?, 'open')",
            (user_id, issue_type, full_description)
        )
        conn.commit()
        print("--> SUCCESS: Saved to SQLite Database 'support_ticket' table.")
        return jsonify({"message": "Ticket submitted successfully!"}), 200

    except Exception as e:
        print(f"--> ERROR SAVING TO DB: {e}")
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()