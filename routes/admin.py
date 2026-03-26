from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, User, Admin, QuizSession
from sqlalchemy import func
from functools import wraps
from extensions import csrf

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ── Admin session guard ──────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Admin login required.", "warning")
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated


# ── Login ────────────────────────────────────────────────────
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session["admin_logged_in"] = True
            session["admin_username"]  = admin.username
            return redirect(url_for("admin.dashboard"))
        flash("Invalid admin credentials.", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    flash("Admin logged out.", "info")
    return redirect(url_for("admin.login"))


# ── Dashboard / Site Stats ───────────────────────────────────
@admin_bp.route("/")
@admin_required
def dashboard():
    total_users   = User.query.count()
    total_quizzes = QuizSession.query.filter_by(completed=True).count()
    banned_users  = User.query.filter_by(is_banned=True).count()

    # Most popular topics
    top_topics = (
        db.session.query(QuizSession.topic, func.count(QuizSession.id).label("count"))
        .filter_by(completed=True)
        .group_by(QuizSession.topic)
        .order_by(func.count(QuizSession.id).desc())
        .limit(5)
        .all()
    )

    # Recent activity
    recent_sessions = (
        QuizSession.query
        .filter_by(completed=True)
        .order_by(QuizSession.started_at.desc())
        .limit(10)
        .all()
    )

    # Avg score across platform
    all_sessions = QuizSession.query.filter_by(completed=True).all()
    if all_sessions:
        total_score = sum(s.score for s in all_sessions)
        total_q     = sum(s.total_q for s in all_sessions)
        platform_avg = round((total_score / total_q * 100), 1) if total_q > 0 else 0
    else:
        platform_avg = 0

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_quizzes=total_quizzes,
        banned_users=banned_users,
        top_topics=top_topics,
        recent_sessions=recent_sessions,
        platform_avg=platform_avg
    )


# ── Users ────────────────────────────────────────────────────
@admin_bp.route("/users")
@admin_required
def users():
    search = request.args.get("search", "").strip()
    if search:
        all_users = User.query.filter(User.username.ilike(f"%{search}%")).all()
    else:
        all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users, search=search)


@admin_bp.route("/users/delete/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    # Delete all related data first
    for s in user.sessions:
        for q in s.questions:
            db.session.delete(q)
        db.session.delete(s)
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user.username}' deleted.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/ban/<int:user_id>")
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_banned = True
    db.session.commit()
    try:
        from email_service import send_ban_email
        send_ban_email(user)
    except Exception:
        pass
    flash(f"User '{user.username}' banned and notified by email.", "warning")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/unban/<int:user_id>")
@admin_required
def unban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    flash(f"User '{user.username}' unbanned.", "success")
    return redirect(url_for("admin.users"))


# ── All Quizzes ──────────────────────────────────────────────
@admin_bp.route("/quizzes")
@admin_required
def quizzes():
    all_sessions = (
        QuizSession.query
        .filter_by(completed=True)
        .order_by(QuizSession.started_at.desc())
        .all()
    )
    return render_template("admin/quizzes.html", sessions=all_sessions)


# ── Create first admin ───────────────────────────────────────
@admin_bp.route("/setup", methods=["GET", "POST"])
@csrf.exempt 
def setup():
    if Admin.query.count() > 0:
        return redirect(url_for("admin.login"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        flash("Admin account created! Please log in.", "success")
        return redirect(url_for("admin.login"))
    return render_template("admin/setup.html")