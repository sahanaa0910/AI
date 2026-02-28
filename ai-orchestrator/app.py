from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, session, url_for
from werkzeug.security import generate_password_hash

from config import Config
from models import get_connection, init_db, now_iso
from routes.attendance import attendance_bp
from routes.auth import auth_bp
from routes.grading import grading_bp
from routes.reports import reports_bp

BASE_DIR = Path(__file__).resolve().parent


def create_app():
    app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
    app.config.from_object(Config)

    app.register_blueprint(auth_bp)
    app.register_blueprint(grading_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)

    @app.get("/")
    def home():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login_page"))

    @app.get("/login")
    def login_page():
        return render_template("login.html")

    @app.get("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return render_template("dashboard.html", user_name=session.get("name", "Teacher"), role=session.get("role", "teacher"))

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"error": "Internal server error"}), 500

    return app


def seed_default_user():
    with get_connection() as conn:
        exists = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
        if exists:
            return

        conn.execute(
            "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("Demo Teacher", "teacher@example.com", generate_password_hash("password123"), "teacher", now_iso()),
        )


app = create_app()

if __name__ == "__main__":
    init_db()
    seed_default_user()
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
