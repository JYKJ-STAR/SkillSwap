from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from app.db import get_db_connection # This ensures we use the SAME database as Admin
import datetime
import os
import uuid
from werkzeug.utils import secure_filename

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
    # Handle FormData instead of JSON
    print(f"--- RECEIVED FORM DATA ---") # Debug print

    user_id = session.get('user_id')
    # Fallback for testing if no user is logged in
    if not user_id:
        print("Warning: No user_id in session. Using placeholder ID 1.")
        user_id = 1 

    # 1. Map frontend data to variables from FormData
    issue_type = request.form.get('issueType')
    event_name = request.form.get('eventName', 'N/A')
    raw_desc = request.form.get('description', '')
    
    # Handle screenshot upload
    screenshot_path = None
    if 'screenshot' in request.files:
        screenshot = request.files['screenshot']
        if screenshot and screenshot.filename:
            # Create uploads directory if it doesn't exist
            
            upload_folder = os.path.join('app', 'Styling', 'uploads', 'screenshots')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Generate unique filename
            
            ext = os.path.splitext(screenshot.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            filepath = os.path.join(upload_folder, filename)
            
            # Save the file
            screenshot.save(filepath)
            screenshot_path = f"/uploads/screenshots/{filename}"
            print(f"DEBUG: Using Styling folder - Screenshot saved: {screenshot_path}")
    
    # Parse the description to extract "Involved:" and actual details
    # Frontend sends: "Involved: Name \n\n Actual description"
    # Normalize line endings (handle both \r\n and \n)
    raw_desc = raw_desc.replace('\r\n', '\n')
    print(f"DEBUG: Raw description received (normalized): {repr(raw_desc)}")
    
    involved_person = 'N/A'
    actual_details = raw_desc
    
    if raw_desc.startswith('Involved:'):
        parts = raw_desc.split('\n\n', 1)
        print(f"DEBUG: Split into {len(parts)} parts: {parts}")
        
        if len(parts) >= 1:
            # Extract the involved person (everything after "Involved:" on the first line)
            involved_line = parts[0].replace('Involved:', '').strip()
            involved_person = involved_line if involved_line else 'N/A'
            print(f"DEBUG: Involved person: {repr(involved_person)}")
            
            # Get the actual details (everything after the first \n\n)
            if len(parts) == 2:
                actual_details = parts[1].strip()
                print(f"DEBUG: Actual details: {repr(actual_details)}")
            else:
                actual_details = ''
                print(f"DEBUG: No details found (only 1 part)")
    
    # Combine into a well-formatted description
    full_description = f"Event: {event_name}\n\nInvolved: {involved_person}\n\nDetails:\n{actual_details}"
    print(f"DEBUG: Final description: {repr(full_description)}")

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
        
        # Add screenshot column if it doesn't exist
        try:
            conn.execute("ALTER TABLE support_ticket ADD COLUMN screenshot_path TEXT")
        except:
            pass  # Column already exists

        # 3. INSERT the ticket into the database
        conn.execute(
            "INSERT INTO support_ticket (user_id, subject, description, status, screenshot_path) VALUES (?, ?, ?, 'open', ?)",
            (user_id, issue_type, full_description, screenshot_path)
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

# =====================================================
# LIVE CHAT ROUTES
# =====================================================

@support_bp.route('/start-chat', methods=['POST'])
def start_chat():
    """Create a new live chat session"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db_connection()
    
    # Check if user already has an active chat
    existing = conn.execute(
        "SELECT session_id FROM live_chat_session WHERE user_id = ? AND status = 'active'",
        (user_id,)
    ).fetchone()
    
    if existing:
        conn.close()
        return jsonify({'session_id': existing['session_id'], 'status': 'existing'})
    
    # Create new chat session
    cursor = conn.execute(
        "INSERT INTO live_chat_session (user_id, status, last_message_at) VALUES (?, 'active', CURRENT_TIMESTAMP)",
        (user_id,)
    )
    session_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    print(f"New chat session created: {session_id} for user {user_id}")
    return jsonify({'session_id': session_id, 'status': 'created'})

@support_bp.route('/send-message', methods=['POST'])
def send_message():
    """Send a message in a chat session"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    session_id = data.get('session_id')
    message_text = data.get('message')
    
    if not session_id or not message_text:
        return jsonify({'error': 'Missing session_id or message'}), 400
    
    conn = get_db_connection()
    
    # Verify user owns this chat session
    chat = conn.execute(
        "SELECT * FROM live_chat_session WHERE session_id = ? AND user_id = ?",
        (session_id, user_id)
    ).fetchone()
    
    if not chat:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Insert message
    conn.execute(
        "INSERT INTO live_chat_message (session_id, sender_type, sender_id, message_text) VALUES (?, 'user', ?, ?)",
        (session_id, user_id, message_text)
    )
    
    # Update last_message_at
    conn.execute(
        "UPDATE live_chat_session SET last_message_at = CURRENT_TIMESTAMP WHERE session_id = ?",
        (session_id,)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'sent'})

@support_bp.route('/get-messages/<int:session_id>')
def get_messages(session_id):
    """Fetch all messages for a chat session"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db_connection()
    
    # Verify user owns this chat session and get admin_connected status
    chat = conn.execute(
        "SELECT * FROM live_chat_session WHERE session_id = ? AND user_id = ?",
        (session_id, user_id)
    ).fetchone()
    
    if not chat:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get admin_connected status
    admin_connected = bool(chat['admin_connected']) if chat else False
    
    # Fetch messages
    messages = conn.execute(
        """SELECT m.*, u.name as sender_name
           FROM live_chat_message m
           LEFT JOIN user u ON m.sender_id = u.user_id AND m.sender_type = 'user'
           WHERE m.session_id = ?
           ORDER BY m.created_at ASC""",
        (session_id,)
    ).fetchall()
    
    conn.close()
    
    return jsonify({
        'messages': [dict(m) for m in messages],
        'admin_connected': admin_connected,
        'status': chat['status']  # Add chat status (active/closed)
    })

@support_bp.route('/get-active-chat')
def get_active_chat():
    """Check if user has an active chat session"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db_connection()
    
    active_chat = conn.execute(
        "SELECT session_id, created_at FROM live_chat_session WHERE user_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    
    conn.close()
    
    if active_chat:
        return jsonify({'has_active': True, 'session_id': active_chat['session_id']})
    else:
        return jsonify({'has_active': False})

@support_bp.route('/get-chat-history')
def get_chat_history():
    """Get all chat sessions for the current user"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db_connection()
    
    chats = conn.execute(
        """SELECT cs.session_id, cs.status, cs.created_at, cs.last_message_at,
                  (SELECT message_text FROM live_chat_message WHERE session_id = cs.session_id ORDER BY created_at DESC LIMIT 1) as last_message,
                  (SELECT COUNT(*) FROM live_chat_message WHERE session_id = cs.session_id) as message_count
           FROM live_chat_session cs
           WHERE cs.user_id = ?
           ORDER BY cs.last_message_at DESC""",
        (user_id,)
    ).fetchall()
    
    conn.close()
    
    return jsonify({'chats': [dict(c) for c in chats]})