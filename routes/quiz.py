from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from models import db, QuizSession, Question
from ai_engine import generate_questions

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/dashboard")
@login_required
def dashboard():
    recent = (
        QuizSession.query
        .filter_by(user_id=current_user.id, completed=True)
        .order_by(QuizSession.started_at.desc())
        .limit(5)
        .all()
    )
    return render_template("dashboard.html", recent=recent)


@quiz_bp.route("/start", methods=["POST"])
@login_required
def start():
    topic      = request.form.get("topic", "").strip()
    difficulty = request.form.get("difficulty", "medium")
    num_q      = int(request.form.get("num_questions", 5))

    if not topic:
        flash("Please enter a topic.", "warning")
        return redirect(url_for("quiz.dashboard"))

    try:
        raw_questions = generate_questions(topic, difficulty, num_q)
    except Exception as e:
        flash(f"AI generation failed: {str(e)}", "danger")
        return redirect(url_for("quiz.dashboard"))

    quiz_session = QuizSession(
        user_id=current_user.id,
        topic=topic,
        difficulty=difficulty,
        total_q=len(raw_questions)
    )
    db.session.add(quiz_session)
    db.session.flush()

    for q in raw_questions:
        question = Question(
            session_id=quiz_session.id,
            question_text=q["question"],
            option_a=q["options"].get("A"),
            option_b=q["options"].get("B"),
            option_c=q["options"].get("C"),
            option_d=q["options"].get("D"),
            correct_answer=q["correct_answer"],
            explanation=q.get("explanation", "")
        )
        db.session.add(question)

    db.session.commit()

    session["quiz_session_id"] = quiz_session.id
    session["question_index"]  = 0

    return redirect(url_for("quiz.question"))


@quiz_bp.route("/question", methods=["GET"])
@login_required
def question():
    quiz_session_id = session.get("quiz_session_id")
    q_index         = session.get("question_index", 0)

    if not quiz_session_id:
        return redirect(url_for("quiz.dashboard"))

    quiz_session = QuizSession.query.get_or_404(quiz_session_id)
    questions    = quiz_session.questions

    if q_index >= len(questions):
        return redirect(url_for("quiz.results"))

    current_q = questions[q_index]
    return render_template(
        "quiz.html",
        question=current_q,
        q_number=q_index + 1,
        total=len(questions),
        topic=quiz_session.topic,
        difficulty=quiz_session.difficulty
    )


@quiz_bp.route("/answer", methods=["POST"])
@login_required
def answer():
    quiz_session_id = session.get("quiz_session_id")
    q_index         = session.get("question_index", 0)

    if not quiz_session_id:
        return redirect(url_for("quiz.dashboard"))

    quiz_session = QuizSession.query.get_or_404(quiz_session_id)
    questions    = quiz_session.questions

    if q_index < len(questions):
        current_q             = questions[q_index]
        user_answer           = request.form.get("answer", "").upper()
        current_q.user_answer = user_answer
        current_q.is_correct  = (user_answer == current_q.correct_answer.upper())

        if current_q.is_correct:
            quiz_session.score += 1

        db.session.commit()
        session["question_index"] = q_index + 1

    return redirect(url_for("quiz.question"))


@quiz_bp.route("/results")
@login_required
def results():
    quiz_session_id = session.get("quiz_session_id")
    if not quiz_session_id:
        return redirect(url_for("quiz.dashboard"))

    quiz_session           = QuizSession.query.get_or_404(quiz_session_id)
    quiz_session.completed = True
    db.session.commit()

    session.pop("quiz_session_id", None)
    session.pop("question_index", None)

    return render_template("results.html", quiz_session=quiz_session)


@quiz_bp.route("/history")
@login_required
def history():
    all_sessions = (
        QuizSession.query
        .filter_by(user_id=current_user.id, completed=True)
        .order_by(QuizSession.started_at.desc())
        .all()
    )
    return render_template("history.html", sessions=all_sessions)