from flask import session, redirect, url_for, current_app, abort, request
from functools import wraps
from authlib.integrations.flask_client import OAuth
from app.models import User, Project

oauth = OAuth()

def init_oauth(app):
    """Initialize Authlib with Wikimedia OAuth 2.0 parameters."""
    oauth.init_app(app)
    oauth.register(
        name='wikimedia',
        client_id=app.config.get('OAUTH_CLIENT_ID'),
        client_secret=app.config.get('OAUTH_CLIENT_SECRET'),
        access_token_url='https://meta.wikimedia.org/w/rest.php/oauth2/access_token',
        authorize_url='https://meta.wikimedia.org/wiki/Special:OAuth2Authorize',
        api_base_url='https://meta.wikimedia.org/w/rest.php/',
        client_kwargs={'scope': 'openid'}
    )

def get_current_user():
    """Retrieve the currently authenticated user from session or MOCK_AUTH."""
    # If the user explicitly logged out, session['logged_out'] will be True
    if session.get('logged_out'):
        return None

    if current_app.config.get('MOCK_AUTH', False):
        return {
            'username': 'MoroccoVolunteer',
            'is_member': True
        }
    
    username = session.get('username')
    if not username:
        return None
    return User.query.filter_by(username=username).first()

# --- Auth Routes Blueprint / Helper Functions ---
# Note: You can register these inside your web blueprint or main app factory

def handle_login():
    """Handles /login: triggers mock login or redirects to Wikimedia OAuth."""
    if current_app.config.get('MOCK_AUTH', False):
        session['username'] = 'MoroccoVolunteer'
        session['is_member'] = True
        return redirect(url_for('web.dashboard'))
    
    redirect_uri = url_for('web.oauth_callback', _external=True)
    return oauth.wikimedia.authorize_redirect(redirect_uri)

def handle_oauth_callback():
    """Handles /oauth/callback: exchanges code and fetches profile."""
    try:
        token = oauth.wikimedia.authorize_access_token()
        # Fetch user profile using Wikimedia resource endpoint
        resp = oauth.wikimedia.get('oauth2/resource/profile', token=token)
        profile_data = resp.json()
        
        # Extract username (adjust key based on Wikimedia's actual JSON response structure)
        username = profile_data.get('username') or profile_data.get('sub')
        
        if username:
            session['username'] = username
            # Check or sync user in DB here if necessary
            user = User.query.filter_by(username=username).first()
            session['is_member'] = user.is_member if user else False
            
    except Exception as e:
        current_app.logger.error(f"OAuth callback error: {e}")
        abort(400, description="Authentication failed.")
        
    return redirect(url_for('web.dashboard'))

def handle_logout():
    """Handles /logout: clears session and redirects home."""
    session.clear()
    return redirect(url_for('web.index'))


# --- Security Decorators ---

def member_required(f):
    """Decorator to check if user is logged in and is an active Meta-Wiki group member."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('MOCK_AUTH', False):
            return f(*args, **kwargs)  # Allow mock pass-through
            
        username = session.get('username')
        if not username:
            return redirect(url_for('web.login'))
            
        user = User.query.filter_by(username=username).first()
        if not user or not user.is_member:
            abort(403, description="Access restricted: Active Meta-Wiki group membership required.")
            
        return f(*args, **kwargs)
    return decorated_function

def project_editor_required(f):
    """Decorator to check if logged-in user is the lead organizer or a co-organizer."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('MOCK_AUTH', False):
            return f(*args, **kwargs)  # Bypass for mock dev
            
        username = session.get('username')
        if not username:
            return redirect(url_for('web.login'))
            
        project_id = kwargs.get('id') or request.view_args.get('id')
        if not project_id:
            abort(400, description="Project ID required for authorization check.")
            
        project = Project.query.get_or_404(project_id)
        
        is_lead = project.lead_organizer == username
        is_co_organizer = username in (project.co_organizers or [])
        
        if not (is_lead or is_co_organizer):
            abort(403, description="Access restricted: You must be the lead organizer or a co-organizer to edit this project.")
            
        return f(*args, **kwargs)
    return decorated_function