from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, QuizSession

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    stats = current_user.get_stats()
    completed = (
        QuizSession.query
        .filter_by(user_id=current_user.id, completed=True)
        .order_by(QuizSession.started_at.desc())
        .all()
    )
    # Chart data — last 10 quizzes scores for line chart
    chart_labels = [f"#{i+1}" for i, _ in enumerate(completed[-10:])]
    chart_scores = [s.percentage for s in completed[-10:]]
    fav_topics   = current_user.get_fav_topics()

    return render_template(
        "profile.html",
        stats=stats,
        sessions=completed,
        chart_labels=chart_labels,
        chart_scores=chart_scores,
        fav_topics=fav_topics
    )


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        bio          = request.form.get("bio", "").strip()
        avatar_color = request.form.get("avatar_color", "#6366f1")

        # Check username not taken by someone else
        from models import User
        existing = User.query.filter_by(username=new_username).first()
        if existing and existing.id != current_user.id:
            flash("Username already taken.", "danger")
            return redirect(url_for("profile.edit_profile"))

        current_user.username     = new_username
        current_user.bio          = bio
        current_user.avatar_color = avatar_color
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("profile.profile"))

    return render_template("edit_profile.html")


@profile_bp.route("/profile/topics", methods=["POST"])
@login_required
def save_topics():
    topics = request.form.get("topics", "").strip()
    current_user.fav_topics = topics
    db.session.commit()
    flash("Favourite topics saved!", "success")
    return redirect(url_for("profile.profile"))


@profile_bp.route("/profile/topics/remove/<topic>")
@login_required
def remove_topic(topic):
    topics = current_user.get_fav_topics()
    topics = [t for t in topics if t != topic]
    current_user.fav_topics = ",".join(topics)
    db.session.commit()
    return redirect(url_for("profile.profile"))