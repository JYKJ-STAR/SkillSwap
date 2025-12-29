from flask import Blueprint
from App.db import get_db_connection

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    conn = get_db_connection()
    user_count = conn.execute('SELECT COUNT(*) FROM user').fetchone()[0]
    conn.close()
    return f"<h1>SkillSwap Application</h1><p>Welcome! SQLite Connection Successful.</p>"
