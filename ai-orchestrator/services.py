from __future__ import annotations

from typing import Dict, List, Tuple

RUBRIC_KEYWORDS = {
    "excellent": ["analyze", "evidence", "critical", "conclusion", "example"],
    "good": ["explain", "detail", "because", "reason"],
    "basic": ["answer", "fact", "simple"],
}


def score_response(text: str) -> Tuple[float, str]:
    text_lower = text.lower()
    points = 0
    for words in RUBRIC_KEYWORDS.values():
        points += sum(1 for word in words if word in text_lower)

    score = min(100, max(40, points * 12 + (len(text.split()) // 3)))
    if score >= 85:
        feedback = "Strong work with clear reasoning and supporting evidence."
    elif score >= 70:
        feedback = "Good understanding shown. Add more specific examples for depth."
    else:
        feedback = "Basic understanding detected. Encourage fuller explanations and evidence."
    return float(score), feedback


def recommend_resources(subject: str, class_level: str) -> List[str]:
    recommendations: Dict[str, Dict[str, List[str]]] = {
        "math": {
            "elementary": ["Khan Academy Kids", "Prodigy Math"],
            "middle": ["Illustrative Mathematics", "Desmos Activities"],
            "high": ["OpenStax Algebra", "Brilliant Problem Sets"],
        },
        "science": {
            "elementary": ["Mystery Science", "NASA STEM"],
            "middle": ["PhET Simulations", "CK-12 Science"],
            "high": ["HHMI BioInteractive", "LabXchange"],
        },
        "english": {
            "elementary": ["Epic!", "Storyline Online"],
            "middle": ["NoRedInk", "ReadWorks"],
            "high": ["CommonLit", "Purdue OWL"],
        },
    }

    generic = ["ReadWorks", "CommonLit", "YouTube Edu curated playlist"]
    return recommendations.get(subject.lower(), {}).get(class_level.lower(), generic)


def generate_iep_report(student_name: str, strengths: str, concerns: str, goals: str, accommodations: str) -> str:
    return f"""
Individualized Education Program (IEP)
Student: {student_name}

Strengths:
- {strengths}

Areas of Concern:
- {concerns}

Annual Goals:
- {goals}

Classroom Accommodations:
- {accommodations}

Progress Monitoring Plan:
- Teacher will monitor weekly formative assessments and adjust interventions every 4 weeks.
""".strip()
