# Challenge: A05 - Injection (SQL Injection)
# Difficulty: medium
# Flag: PWR{sqli_transactions_leaked}
# Tools: curl / Burp Suite / sqlmap
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify

blueprint = Blueprint("challenge_a05", __name__, url_prefix="/api/challenges/a05")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A05",
        "name": "SQL Injection — wyszukiwarka transakcji",
        "category": "OWASP A05:2025",
        "difficulty": "medium",
        "points": 150,
        "description": (
            "Endpoint /api/transactions/search?q= buduje zapytanie SQL "
            "przez string concatenation. Możliwe UNION-based SQL Injection "
            "do wyciągnięcia flagi z tabeli flags."
        ),
        "hint": (
            "Wstrzyknij UNION SELECT do pola q. "
            "Tabela flags ma kolumny: id, challenge_id, flag_value, description, difficulty, points"
        ),
        "endpoint": "GET /api/transactions/search?q=",
        "payload_hint": "' UNION SELECT ...",
    }), 200
