import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-replace-in-production")
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1")

    # Community Customization Variables
    COMMUNITY_NAME = os.getenv("COMMUNITY_NAME", "Wikimedia Morocco")
    META_ROSTER_PAGE = os.getenv("META_ROSTER_PAGE", "Wikimedia_MA/Members")
    DEFAULT_TARGET_WIKI = os.getenv("DEFAULT_TARGET_WIKI", "ar.wikipedia.org")
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "contact@wikimedia.ma")

    # Wikimedia API User-Agent Policy enforcement
    USER_AGENT = (
        f"AtharDashboard/1.0 (https://athar.toolforge.org; {CONTACT_EMAIL}) "
        "Python-Requests/Flask"
    )

    # Database URI: MariaDB (ToolsDB) on Toolforge; SQLite for local development
    TOOL_NAME = os.getenv("TOOL_NAME", "athar")
    TOOL_DB_USER = os.getenv("TOOL_DB_USER")
    TOOL_DB_PASS = os.getenv("TOOL_DB_PASS")

    if ENV == "production" and TOOL_DB_USER and TOOL_DB_PASS:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{TOOL_DB_USER}:{TOOL_DB_PASS}"
            f"@tools.db.svc.wikimedia.cloud:3306/s{TOOL_NAME}__main?charset=utf8mb4"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session cookie hardening
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (ENV == "production")
