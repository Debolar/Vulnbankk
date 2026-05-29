# Challenge: A09 - Security Logging & Alerting Failures
# Difficulty: easy
# Flag: PWR{logs_exposed_no_auth}
# Tools: curl / przeglądarka
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify

blueprint = Blueprint("challenge_a09", __name__, url_prefix="/api/challenges/a09")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A09",
        "name": "Logging & Alerting Failures — logi bez autoryzacji",
        "category": "OWASP A09:2025",
        "difficulty": "easy",
        "points": 100,
        "description": (
            "Endpoint /api/admin/logs zwraca logi aplikacji BEZ autoryzacji. "
            "Logi zawierają hasła w plaintext (logowane przy błędnym logowaniu). "
            "W logach zaseedowany wpis z flagą jako 'hasłem' admina."
        ),
        "hint": (
            "Wejdź na GET /api/admin/logs bez tokenu. "
            "Przejrzyj logi i znajdź wpis z wartością PWR{...}."
        ),
        "endpoint": "GET /api/admin/logs",
        "auth_required": False,
    }), 200
