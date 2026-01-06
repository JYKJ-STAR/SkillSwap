from datetime import timedelta
import os
from flask import Flask
from dotenv import load_dotenv

from authlib.integrations.flask_client import OAuth

oauth = OAuth()

def create_app():
    # Force loading of .env file to override system variables if valid
    load_dotenv(override=True)

    app = Flask(__name__, template_folder='HTML_Files', static_folder='Styling')
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
    
    # OAuth Configuration
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET')

    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    # Register blueprints
    from .Python_Files.Home import home_bp
    from .Python_Files.Dashboard import dashboard_bp
    from .Python_Files.Admin import admin_bp
    from .Python_Files.Support import support_bp
    from .Python_Files.Events import events_bp
    from .Python_Files.Rewards import rewards_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(rewards_bp)

    return app

