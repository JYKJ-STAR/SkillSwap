from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from app.db import get_db_connection # This ensures we use the SAME database as Admin
import datetime

support_bp = Blueprint('support', __name__)

# --- ROUTES ---

@support_bp.route('/support')
def support():
    # Fetch tickets from database to display on My Tickets page
    conn = get_db_connection()
    
    user_id = session.get('user_id')
    
    # If user is logged in, fetch their tickets; otherwise fetch all for debugging
    if user_id:
        tickets = conn.execute("""
            SELECT st.*, u.name as user_name 
            FROM support_ticket st
            LEFT JOIN user u ON st.user_id = u.user_id
            WHERE st.user_id = ?
            ORDER BY st.created_at DESC
        """, (user_id,)).fetchall()
    else:
        # Debug mode: fetch all tickets
        print("Warning: No user_id in session. Fetching all tickets for display.")
        tickets = conn.execute("""
            SELECT st.*, u.name as user_name 
            FROM support_ticket st
            LEFT JOIN user u ON st.user_id = u.user_id
            ORDER BY st.created_at DESC
        """).fetchall()
    
    conn.close()
    
    print(f"--- DEBUG: Loaded {len(tickets)} tickets for support page ---")
    
    return render_template('youth/youth_support.html', tickets=tickets)

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

@support_bp.route('/my-tickets')
def my_tickets():
    conn = get_db_connection()
    
    # --- DEBUG MODE: FETCH ALL TICKETS (Ignores User ID) ---
    print("--- DEBUG: Fetching ALL tickets for display ---")
    
    tickets = conn.execute("""
        SELECT st.*, u.name as user_name 
        FROM support_ticket st
        LEFT JOIN user u ON st.user_id = u.user_id
        ORDER BY st.created_at DESC
    """).fetchall()
    
    conn.close()
    
    # Debug print to confirm data is found
    print(f"--- DEBUG: Found {len(tickets)} tickets total. ---")

    return render_template('youth/youth_my_tickets.html', tickets=tickets)

@support_bp.route('/adopt-tickets')
def adopt_tickets():
    # Assign ALL tickets to the currently logged-in user
    user_id = session.get('user_id')
    if not user_id:
        return "Please log in first!"
        
    conn = get_db_connection()
    conn.execute("UPDATE support_ticket SET user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return f"Success! All tickets now belong to User ID {user_id}. Go back to My Tickets."

@support_bp.route('/fix-my-tickets')
def fix_my_tickets():
    # 1. Get your current ID (e.g., maybe you are ID 1 or 2)
    current_user_id = session.get('user_id')
    
    if not current_user_id:
        return "You are not logged in! Please log in first."

    conn = get_db_connection()
    
    # 2. Force all tickets in the DB to belong to YOU
    conn.execute("UPDATE support_ticket SET user_id = ?", (current_user_id,))
    conn.commit()
    conn.close()
    
    return f"Fixed! All tickets have been moved to User ID {current_user_id}. Go back to 'My Tickets' to see them."