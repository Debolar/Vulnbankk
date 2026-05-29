# Challenge: A06 - Insecure Design (Password Reset Logic Flaw)
# Difficulty: easy
# Flag: PWR{insecure_password_reset}
# Tools: curl / Burp Suite
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify

blueprint = Blueprint("challenge_a06", __name__, url_prefix="/api/challenges/a06")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A06",
        "name": "Insecure Design — błędna logika resetu hasła",
        "category": "OWASP A06:2025",
        "difficulty": "easy",
        "points": 100,
        "description": (
            "Reset hasła wymaga tylko PESELU zamiast bezpiecznego tokenu na email. "
            "PESEL jest widoczny w GET /api/profile (podatność A01 + A06). "
            "Możesz przejąć konto alice znając jej PESEL."
        ),
        "hint": (
            "1. Pobierz PESEL alice przez IDOR: GET /api/accounts/1 lub "
            "zaloguj się jako bob i sprawdź profil alice przez /api/profile/ z ID. "
            "2. POST /api/auth/forgot-password z emailem alice i jej PESELem. "
            "Flaga jest w odpowiedzi resetu."
        ),
        "endpoint": "POST /api/auth/forgot-password",
        "body": '{"email": "alice@vulnbank.pl", "pesel": "???", "new_password": "hacked"}',
    }), 200
