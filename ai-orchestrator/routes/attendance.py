import csv
import io
from datetime import date

from flask import Blueprint, jsonify, request, session

from models import get_connection, now_iso
from routes.auth import login_required

attendance_bp = Blueprint("attendance", __name__, url_prefix="/api/attendance")


@attendance_bp.post("/upload-csv")
@login_required
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "CSV file is required"}), 400

    file = request.files["file"]
    content = file.read().decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(content))

    required_headers = {"name", "class_level", "subject"}
    if not reader.fieldnames or not required_headers.issubset(set(reader.fieldnames)):
        return jsonify({"error": "CSV must include headers: name,class_level,subject"}), 400

    inserted = 0
    with get_connection() as conn:
        for row in reader:
            name = (row.get("name") or "").strip()
            class_level = (row.get("class_level") or "General").strip()
            subject = (row.get("subject") or "").strip()
            if not name:
                continue
            conn.execute(
                "INSERT INTO students (name, class_level, subject, created_at) VALUES (?, ?, ?, ?)",
                (name, class_level, subject, now_iso()),
            )
            inserted += 1

    return jsonify({"message": f"Imported {inserted} students"})


@attendance_bp.post("/mark")
@login_required
def mark_attendance():
    payload = request.get_json(silent=True) or {}
    student_name = (payload.get("student_name") or "").strip()
    class_level = (payload.get("class_level") or "General").strip()
    status = (payload.get("status") or "Present").strip()
    record_date = (payload.get("date") or str(date.today())).strip()

    if not student_name or status not in {"Present", "Absent", "Late"}:
        return jsonify({"error": "Invalid attendance data"}), 400

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO attendance_records
            (teacher_id, student_name, class_level, date, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session["user_id"], student_name, class_level, record_date, status, now_iso()),
        )

    return jsonify({"message": "Attendance marked"})


@attendance_bp.get("/report")
@login_required
def report():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT date, status, COUNT(*) as total
            FROM attendance_records
            WHERE teacher_id = ?
            GROUP BY date, status
            ORDER BY date DESC
            """,
            (session["user_id"],),
        ).fetchall()
    return jsonify([dict(r) for r in rows])
