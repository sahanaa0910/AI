import re
from functools import wraps

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from models import get_connection, now_iso

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return fn(*args, **kwargs)

    return wrapper


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = session.get("role")
            if role not in roles:
                return jsonify({"error": "Permission denied"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    required = ["name", "email", "password"]
    missing = [f for f in required if not payload.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    name = payload["name"].strip()
    email = payload["email"].strip().lower()
    password = payload["password"]

    if len(name) < 2:
        return jsonify({"error": "Name must be at least 2 characters"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Invalid email format"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    role = payload.get("role", "teacher")
    if role not in {"teacher", "admin"}:
        return jsonify({"error": "Invalid role"}), 400

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
                (name, email, generate_password_hash(password), role, now_iso()),
            )
        return jsonify({"message": "Account created"}), 201
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            return jsonify({"error": "Email already registered"}), 409
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    with get_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    session.clear()
    session["user_id"] = user["id"]
    session["name"] = user["name"]
    session["role"] = user["role"]
    return jsonify({"message": "Login successful", "user": {"name": user["name"], "role": user["role"]}})


@auth_bp.post("/logout")
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@auth_bp.get("/me")
def me():
    if "user_id" not in session:
        return jsonify({"authenticated": False})
    return jsonify(
        {
            "authenticated": True,
            "user": {
                "id": session.get("user_id"),
                "name": session.get("name"),
                "role": session.get("role"),
            },
        }
    )
