from flask import Blueprint

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    return "<h1>SkillSwap Application</h1><p>Welcome! This is the Home page served from Python_Files/Home.py</p>"
