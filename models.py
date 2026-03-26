from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id               = db.Column(db.Integer, primary_key=True)
    username         = db.Column(db.String(80), unique=True, nullable=False)
    email            = db.Column(db.String(120), unique=True, nullable=False)
    password_hash    = db.Column(db.String(255), nullable=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    bio              = db.Column(db.String(300), default="")
    avatar_color     = db.Column(db.String(20), default="#6366f1")
    fav_topics       = db.Column(db.String(500), default="")
    is_admin         = db.Column(db.Boolean, default=False)
    is_banned        = db.Column(db.Boolean, default=False)
    is_verified      = db.Column(db.Boolean, default=False)
    verify_token     = db.Column(db.String(100), nullable=True)
    reset_token      = db.Column(db.String(100), nullable=True)
    reset_token_exp  = db.Column(db.DateTime, nullable=True)

    sessions = db.relationship("QuizSession", backref="user", lazy=True)

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_verify_token(self):
        self.verify_token = secrets.token_urlsafe(32)
        return self.verify_token

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        from datetime import timedelta
        self.reset_token_exp = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

    def get_fav_topics(self):
        if not self.fav_topics:
            return []
        return [t.strip() for t in self.fav_topics.split(",") if t.strip()]

    def get_stats(self):
        completed = [s for s in self.sessions if s.completed]
        total_quizzes = len(completed)
        if total_quizzes == 0:
            return {"total_quizzes": 0, "best_score": 0, "avg_score": 0, "fav_topic": "None yet", "total_questions": 0}
        best = max(completed, key=lambda s: s.percentage)
        total_q = sum(s.total_q for s in completed)
        total_correct = sum(s.score for s in completed)
        avg = round((total_correct / total_q * 100), 1) if total_q > 0 else 0
        topic_counts = {}
        for s in completed:
            topic_counts[s.topic] = topic_counts.get(s.topic, 0) + 1
        fav_topic = max(topic_counts, key=topic_counts.get)
        return {"total_quizzes": total_quizzes, "best_score": best.percentage, "avg_score": avg, "fav_topic": fav_topic, "total_questions": total_q}


class Admin(db.Model):
    __tablename__ = "admins"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class QuizSession(db.Model):
    __tablename__ = "quiz_sessions"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    topic      = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    score      = db.Column(db.Integer, default=0)
    total_q    = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed  = db.Column(db.Boolean, default=False)

    questions = db.relationship("Question", backref="session", lazy=True)

    @property
    def percentage(self):
        if self.total_q == 0:
            return 0
        return round((self.score / self.total_q) * 100, 1)


class Question(db.Model):
    __tablename__ = "questions"

    id             = db.Column(db.Integer, primary_key=True)
    session_id     = db.Column(db.Integer, db.ForeignKey("quiz_sessions.id"), nullable=False)
    question_text  = db.Column(db.Text, nullable=False)
    option_a       = db.Column(db.String(255))
    option_b       = db.Column(db.String(255))
    option_c       = db.Column(db.String(255))
    option_d       = db.Column(db.String(255))
    correct_answer = db.Column(db.String(1))
    user_answer    = db.Column(db.String(1))
    explanation    = db.Column(db.Text)
    is_correct     = db.Column(db.Boolean, default=False)