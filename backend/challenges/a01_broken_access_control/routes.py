# Challenge: A01 - Broken Access Control (IDOR)
# Difficulty: easy
# Flag: PWR{idor_account_takeover}
# Tools: curl / Burp Suite / przeglądarka
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify

blueprint = Blueprint("challenge_a01", __name__, url_prefix="/api/challenges/a01")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A01",
        "name": "Broken Access Control — IDOR",
        "category": "OWASP A01:2025",
        "difficulty": "easy",
        "points": 100,
        "description": (
            "Endpoint /api/accounts/<id> nie weryfikuje czy konto należy "
            "do zalogowanego użytkownika. Możesz pobrać dane KAŻDEGO konta."
        ),
        "hint": (
            "Zaloguj się, sprawdź ID swojego konta, a potem spróbuj "
            "pobrać konto o ID=1. Co widzisz w polu internal_note?"
        ),
        "endpoint": "GET /api/accounts/<account_id>",
        "vulnerable_parameter": "account_id w URL",
    }), 200
