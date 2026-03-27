from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import Config
from models import db, User
from extensions import csrf, limiter, mail
from routes.auth import auth_bp
from routes.quiz import quiz_bp
from routes.leaderboard import leaderboard_bp
from routes.profile import profile_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return redirect(url_for("quiz.dashboard"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])