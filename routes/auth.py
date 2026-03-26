from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models import db, User
from extensions import limiter
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


def validate_password(password):
    errors = []
    if len(password) < 8:
        errors.append("at least 8 characters")
    if not any(c.isupper() for c in password):
        errors.append("at least one uppercase letter")
    if not any(c.isdigit() for c in password):
        errors.append("at least one number")
    return errors


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        errors = validate_password(password)
        if errors:
            flash(f"Password must have: {chr(44).join(errors)}.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))

        user = User(username=username, email=email)
        user.set_password(password)
        user.generate_verify_token()
        db.session.add(user)
        db.session.commit()

        try:
            from email_service import send_welcome_email
            verify_url = url_for("auth.verify_email", token=user.verify_token, _external=True)
            send_welcome_email(user, verify_url)
            flash("Account created! Check your inbox and spam folder to verify your account.", "success")
        except Exception as e:
            print(f"EMAIL FAILED: {type(e).__name__}: {str(e)}")
            flash(f"Email error: {str(e)}", "danger")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/verify/<token>")
def verify_email(token):
    user = User.query.filter_by(verify_token=token).first()
    if not user:
        flash("Invalid or expired verification link.", "danger")
        return redirect(url_for("auth.login"))
    user.is_verified  = True
    user.verify_token = None
    db.session.commit()
    flash("Email verified! You can now log in.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and user.is_banned:
            flash("Your account has been banned. Contact support.", "danger")
            return redirect(url_for("auth.login"))

        if user and not user.is_verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for("auth.login"))

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("quiz.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user  = User.query.filter_by(email=email).first()
        if user:
            user.generate_reset_token()
            db.session.commit()
            try:
                from email_service import send_password_reset_email
                reset_url = url_for("auth.reset_password", token=user.reset_token, _external=True)
                send_password_reset_email(user, reset_url)
            except Exception as e:
                print(f"EMAIL FAILED: {type(e).__name__}: {str(e)}")
                flash(f"Email error: {str(e)}", "danger")
                return redirect(url_for("auth.forgot_password"))
        flash("If that email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user or user.reset_token_exp < datetime.utcnow():
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth.forgot_password"))
    if request.method == "POST":
        password = request.form.get("password", "")
        errors = validate_password(password)
        if errors:
            flash(f"Password must have: {chr(44).join(errors)}.", "danger")
            return redirect(request.url)
        user.set_password(password)
        user.reset_token     = None
        user.reset_token_exp = None
        db.session.commit()
        flash("Password reset successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("reset_password.html", token=token)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/resend-verification", methods=["POST"])
@limiter.limit("5 per hour")
def resend_verification():
    email = request.form.get("email", "").strip()
    user  = User.query.filter_by(email=email).first()
    if user and not user.is_verified:
        user.generate_verify_token()
        db.session.commit()
        try:
            from email_service import send_welcome_email
            verify_url = url_for("auth.verify_email", token=user.verify_token, _external=True)
            send_welcome_email(user, verify_url)
            flash("Verification email resent! Check your inbox and spam folder.", "success")
        except Exception as e:
            print(f"EMAIL FAILED: {type(e).__name__}: {str(e)}")
            flash(f"Email error: {str(e)}", "danger")
    else:
        flash("If that email exists and is unverified, we sent a new link.", "info")
    return redirect(url_for("auth.login")) 