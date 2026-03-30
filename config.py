import os
from dotenv import load_dotenv
load_dotenv()

def get_db_url():
    url = os.environ.get("MYSQL_PUBLIC_URL", "")
    if url:
        if url.startswith("mysql://"):
            url = "mysql+pymysql://" + url[len("mysql://"):]
        elif not url.startswith("mysql+pymysql://"):
            url = "mysql+pymysql://" + url
        return url
    # Fallback for local development
    host     = os.environ.get("MYSQL_HOST", "localhost")
    user     = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    db       = os.environ.get("MYSQL_DB", "gaming_app_db")
    port     = os.environ.get("MYSQL_PORT", "3306")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-change-this")
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    SQLALCHEMY_DATABASE_URI = get_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    MAIL_SERVER         = "smtp.gmail.com"
    MAIL_PORT           = 465
    MAIL_USE_TLS        = False
    MAIL_USE_SSL        = True
    MAIL_USERNAME       = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD       = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "")