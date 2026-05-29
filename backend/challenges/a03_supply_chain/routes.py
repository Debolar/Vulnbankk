# Challenge: A03 - Software Supply Chain Failures
# Difficulty: easy
# Flag: PWR{vulnerable_dependency_found}
# Tools: curl / przeglądarka
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify

blueprint = Blueprint("challenge_a03", __name__, url_prefix="/api/challenges/a03")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A03",
        "name": "Software Supply Chain Failures",
        "category": "OWASP A03:2025",
        "difficulty": "easy",
        "points": 100,
        "description": (
            "Aplikacja używa podatnych bibliotek. "
            "Endpoint /api/debug/dependencies ujawnia pełną listę "
            "zainstalowanych pakietów z wersjami i znane CVE."
        ),
        "hint": "Sprawdź GET /api/debug/dependencies i poszukaj pakietu z polem 'flag'",
        "endpoint": "GET /api/debug/dependencies",
    }), 200
