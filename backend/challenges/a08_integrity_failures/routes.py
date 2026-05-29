# Challenge: A08 - Software/Data Integrity Failures (JWT None Algorithm)
# Difficulty: medium
# Flag: PWR{jwt_tampered_admin}
# Tools: jwt.io / Burp Suite / Python (base64)
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify

blueprint = Blueprint("challenge_a08", __name__, url_prefix="/api/challenges/a08")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A08",
        "name": "Integrity Failures — JWT None Algorithm Bypass",
        "category": "OWASP A08:2025",
        "difficulty": "medium",
        "points": 150,
        "description": (
            "Backend akceptuje JWT z algorytmem 'none' — token bez podpisu. "
            "Możliwa jest modyfikacja payload'u JWT bez znajomości klucza tajnego. "
            "Zmień is_admin: false → true żeby uzyskać dostęp do panelu admina."
        ),
        "hint": (
            "1. Zaloguj się jako zwykły user, skopiuj JWT. "
            "2. Zdekoduj na jwt.io. "
            "3. Zmień alg na 'none', is_admin na true. "
            "4. Usuń sygnaturę (zostaw końcową kropkę). "
            "5. Wyślij do GET /api/admin/dashboard."
        ),
        "endpoint": "GET /api/admin/dashboard",
        "target": "Zmień payload JWT: is_admin: false → true",
    }), 200
