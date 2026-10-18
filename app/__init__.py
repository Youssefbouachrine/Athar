from flask import Flask, session, redirect, url_for, render_template_string
from config import Config
from app.models import db
from app.oauth import init_oauth, get_current_user

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set default SQLite URI if not provided in config
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'

    # Initialize extensions
    db.init_app(app)
    init_oauth(app)

    # Create local database tables automatically for development
    with app.app_context():
        db.create_all()

    # Temporary test route to verify browser access and mock login
    @app.route('/')
    def index():
        user = get_current_user()
        username = user.get('username') if isinstance(user, dict) else (user.username if user else None)
        
        return render_template_string("""
            <div style="font-family: Arial; padding: 40px; text-align: center;">
                <h1>🚀 Athar - Wikimedia Community Dashboard</h1>
                <p>Status: <strong>Running locally</strong></p>
                {% if username %}
                    <p style="color: green;">✅ Logged in as: <strong>{{ username }}</strong> (Mock Auth Active)</p>
                    <a href="/logout" style="padding: 10px 20px; background: #d33; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px;">Log Out</a>
                {% else %}
                    <p style="color: red;">❌ Not Logged In</p>
                    <a href="/login" style="padding: 10px 20px; background: #006699; color: white; text-decoration: none; border-radius: 5px;">Log In (Mock)</a>
                {% endif %}
            </div>
        """, username=username)

    @app.route('/login')
    def login():
        session.pop('logged_out', None)  # Clear logout flag on login
        session['username'] = 'MoroccoVolunteer'
        session['is_member'] = True
        return redirect(url_for('index'))

    @app.route('/logout')
    def logout():
        session.clear()
        session['logged_out'] = True  # Mark as explicitly logged out
        return redirect(url_for('index'))
    return app