from flask import Blueprint, render_template, request
from flask_login import login_required
from models import db, User, QuizSession
from sqlalchemy import func

leaderboard_bp = Blueprint("leaderboard", __name__)


@leaderboard_bp.route("/leaderboard")
@login_required
def leaderboard():
    # Top users by average score percentage
    results = (
        db.session.query(
            User.username,
            func.count(QuizSession.id).label("total_quizzes"),
            func.sum(QuizSession.score).label("total_score"),
            func.sum(QuizSession.total_q).label("total_questions"),
        )
        .join(QuizSession, User.id == QuizSession.user_id)
        .filter(QuizSession.completed == True)
        .group_by(User.id)
        .order_by(
            (func.sum(QuizSession.score) * 100.0 / func.sum(QuizSession.total_q)).desc()
        )
        .limit(20)
        .all()
    )

    board = []
    for row in results:
        pct = round((row.total_score / row.total_questions) * 100, 1) if row.total_questions else 0
        board.append({
            "username":     row.username,
            "total_quizzes": row.total_quizzes,
            "avg_score":    pct,
        })

    return render_template("leaderboard.html", board=board)