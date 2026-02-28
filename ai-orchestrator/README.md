# AI Orchestrator

Full-stack Flask + SQLite dashboard for teachers to reduce non-instructional workload with automated grading, attendance workflows, resource recommendations, and IEP drafting.

## Features
- Authentication with hashed passwords and session management
- Smart dashboard (students, pending grading, time-saved tracker, notifications)
- AI-simulated grading (keyword/NLP-style rule engine)
- Attendance CSV import + marking + reporting
- Rule-based learning resource recommendations
- IEP report generator
- Responsive UI with dark/light mode, toast notifications, and loading overlay
- Basic role-based access endpoint for admins

## Run locally

```bash
cd ai-orchestrator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open: `http://localhost:5000`

Demo account:
- Email: `teacher@example.com`
- Password: `password123`

Optional env vars:
- `SECRET_KEY`
- `DATABASE_PATH`
- `FLASK_DEBUG=1`
- `SESSION_COOKIE_SECURE=1`

## CSV format for attendance import

```csv
name,class_level,subject
John Doe,Grade 7,Math
Jane Smith,Grade 7,Science
```
