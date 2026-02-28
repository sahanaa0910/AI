from flask import Blueprint, jsonify, request, session

from models import get_connection, now_iso
from routes.auth import login_required, role_required
from services import generate_iep_report, recommend_resources

reports_bp = Blueprint("reports", __name__, url_prefix="/api")


@reports_bp.get("/dashboard/stats")
@login_required
def dashboard_stats():
    teacher_id = session["user_id"]
    with get_connection() as conn:
        total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        pending_grading = conn.execute(
            "SELECT COUNT(*) FROM grading_results WHERE teacher_id = ? AND score < 70", (teacher_id,)
        ).fetchone()[0]
        graded_count = conn.execute(
            "SELECT COUNT(*) FROM grading_results WHERE teacher_id = ?", (teacher_id,)
        ).fetchone()[0]
        attendance_count = conn.execute(
            "SELECT COUNT(*) FROM attendance_records WHERE teacher_id = ?", (teacher_id,)
        ).fetchone()[0]
        notifications = conn.execute(
            "SELECT id, message, level, created_at FROM notifications WHERE teacher_id = ? ORDER BY id DESC LIMIT 10",
            (teacher_id,),
        ).fetchall()

    weekly_saved = round((graded_count * 0.2) + (attendance_count * 0.08) + 1.5, 2)
    progress_pct = min(100, int((weekly_saved / 10) * 100))
    workload_reduction_pct = min(30, round((weekly_saved / 10) * 30, 1))
    return jsonify(
        {
            "total_students": total_students,
            "pending_grading": pending_grading,
            "weekly_saved_hours": weekly_saved,
            "progress_pct": progress_pct,
            "workload_reduction_pct": workload_reduction_pct,
            "notifications": [dict(r) for r in notifications],
        }
    )


@reports_bp.post("/resources/recommend")
@login_required
def resource_recommendations():
    payload = request.get_json(silent=True) or {}
    subject = (payload.get("subject") or "General").strip().lower()
    class_level = (payload.get("class_level") or "middle").strip().lower()
    picks = recommend_resources(subject, class_level)
    return jsonify({"subject": subject, "class_level": class_level, "recommendations": picks})


@reports_bp.post("/iep/generate")
@login_required
def generate_iep():
    payload = request.get_json(silent=True) or {}
    required = ["student_name", "strengths", "concerns", "goals", "accommodations"]
    missing = [f for f in required if not payload.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    report_text = generate_iep_report(
        payload["student_name"],
        payload["strengths"],
        payload["concerns"],
        payload["goals"],
        payload["accommodations"],
    )

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO iep_reports
            (teacher_id, student_name, strengths, concerns, goals, accommodations, report_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                payload["student_name"],
                payload["strengths"],
                payload["concerns"],
                payload["goals"],
                payload["accommodations"],
                report_text,
                now_iso(),
            ),
        )

    return jsonify({"report": report_text})


@reports_bp.get("/admin/teachers")
@login_required
@role_required("admin")
def admin_teachers():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, name, email, role, created_at FROM users ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])
