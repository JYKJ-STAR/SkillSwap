import os
from flask import Flask
from dotenv import load_dotenv

def create_app():
    # Force loading of .env file to override system variables if valid
    load_dotenv(override=True)

    app = Flask(__name__, template_folder='HTML_Files', static_folder='Styling')
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    # Register blueprints
    from .Python_Files.Home import home_bp
    from .Python_Files.Dashboard import dashboard_bp
    from .Python_Files.Admin import admin_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    return app
