from flask import Blueprint, jsonify, request, session

from models import get_connection, now_iso
from routes.auth import login_required
from services import score_response

grading_bp = Blueprint("grading", __name__, url_prefix="/api/grading")


@grading_bp.post("/auto-grade")
@login_required
def auto_grade():
    payload = request.get_json(silent=True) or {}
    required = ["student_name", "assignment_title", "response_text"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    student_name = payload["student_name"].strip()
    assignment_title = payload["assignment_title"].strip()
    response_text = payload["response_text"].strip()
    if len(response_text.split()) < 3:
        return jsonify({"error": "Response text must contain at least 3 words"}), 400

    score, feedback = score_response(response_text)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO grading_results
            (teacher_id, student_name, assignment_title, response_text, score, feedback, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (session["user_id"], student_name, assignment_title, response_text, score, feedback, now_iso()),
        )

        conn.execute(
            "INSERT INTO notifications (teacher_id, message, level, created_at) VALUES (?, ?, ?, ?)",
            (session["user_id"], f"Auto-graded {student_name}'s assignment.", "success", now_iso()),
        )

    return jsonify({"score": score, "feedback": feedback})


@grading_bp.get("/results")
@login_required
def results():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, student_name, assignment_title, score, feedback, created_at FROM grading_results WHERE teacher_id = ? ORDER BY id DESC LIMIT 20",
            (session["user_id"],),
        ).fetchall()
    return jsonify([dict(row) for row in rows])
