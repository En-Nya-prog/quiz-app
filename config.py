import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-change-this")
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "MYSQL_PUBLIC_URL",
        "mysql+pymysql://root@localhost/gaming_app_db"
    ).replace("mysql://", "mysql+pymysql://")
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