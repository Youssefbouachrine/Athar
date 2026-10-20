from flask import Flask
from config import Config
from app.models import db
from app.oauth import init_oauth
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    init_oauth(app)

    # Register Blueprints
    from app.routes.web import web_bp
    from app.routes.api import api_bp
    from app.oauth import oauth_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(oauth_bp)

    return app