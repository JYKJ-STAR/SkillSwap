from flask import Blueprint, render_template
from app.db import get_db_connection

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    conn = get_db_connection()
    user_count = conn.execute('SELECT COUNT(*) FROM user').fetchone()[0]
    conn.close()
    return render_template("guestview.html")

@home_bp.route("/login")
def login():
    return render_template("login.html")
