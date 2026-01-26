from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
import datetime

support_bp = Blueprint('support', __name__)

# --- 1. SIMULATED DATABASE (Place this at the top level) ---
# This list acts as your database. Since it's global, both the Youth page
# and Admin page can access it as long as the server is running.
all_tickets = [
    {
        "id": "T-100",
        "user": "John Doe",
        "type": "Harassment",
        "date": "2025-08-26",
        "priority": "High",
        "event": "Artistic Workshop",
        "status": "In Progress",
        "description": "User was spamming chat."
    }
]

# --- 2. EXISTING ROUTE: SUPPORT CENTER ---
@support_bp.route('/support')
def support():
    """Route to Support Center."""
    if 'user_id' not in session:
        flash("Please log in to access support.", "warning")
        return redirect(url_for('home.login_page'))
        
    role = session.get('user_role')
    
    if role == 'admin':
        # If admin goes here, we can redirect them to the ticket manager
        # or back to the dashboard.
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'senior':
        return render_template('senior/senior_support.html')
    elif role == 'youth':
        return render_template('youth/youth_support.html')
    else:
        return render_template('youth/youth_support.html')

# --- 3. NEW ROUTE: SUBMIT TICKET (Called by JavaScript) ---
@support_bp.route('/submit-ticket', methods=['POST'])
def submit_ticket():
    data = request.json
    
    # Create the new ticket
    new_ticket = {
        "id": f"T-{len(all_tickets) + 101}", 
        "user": session.get('user_name', 'Current User'), # Try to get real name from session
        "type": data.get('issueType'),
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "priority": "Medium",
        "event": data.get('eventName'),
        "status": "In Progress",
        "description": data.get('description')
    }
    
    # Save it to the global list
    all_tickets.append(new_ticket)
    
    return jsonify({"message": "Ticket submitted successfully!", "ticket": new_ticket})

# --- 4. NEW ROUTE: ADMIN VIEW TICKETS ---
# Even though this is for admins, we keep it here so it can access 'all_tickets' easily.
@support_bp.route('/admin/tickets')
def admin_tickets():
    # Check if user is actually admin
    if session.get('user_role') != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('home.login_page'))

    # Send the 'all_tickets' list to the HTML
    return render_template('admin/support_tickets.html', tickets=all_tickets)