# Challenge: A10 - Mishandling of Exceptional Conditions
# Difficulty: easy
# Flag: PWR{stacktrace_db_url_leaked}
# Tools: curl / przeglądarka
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify

blueprint = Blueprint("challenge_a10", __name__, url_prefix="/api/challenges/a10")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A10",
        "name": "Exceptional Conditions — stack trace z connection stringiem",
        "category": "OWASP A10:2025",
        "difficulty": "easy",
        "points": 100,
        "description": (
            "Kalkulator rat kredytowych nie obsługuje wyjątków. "
            "Flask DEBUG=True → przy błędnym parametrze zwracany jest "
            "pełny stack trace Werkzeug z wartościami zmiennych lokalnych. "
            "Zmienna db_url zawiera flagę w connection stringu."
        ),
        "hint": (
            "Wyślij GET /api/loans/calculate?amount=abc&rate=2 "
            "i znajdź zmienną db_url w stack trace."
        ),
        "endpoint": "GET /api/loans/calculate?amount=abc&rate=2",
        "vulnerable_parameter": "amount=abc (nie-numeryczna wartość)",
    }), 200
