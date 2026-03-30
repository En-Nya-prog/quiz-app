import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-change-this")
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
MYSQL_HOST     = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER     = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DB       = os.environ.get("MYSQL_DB", "gaming_app_db")
MYSQL_PORT     = os.environ.get("MYSQL_PORT", "3306")
SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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