# Challenge: A19 - Source Maps Leak
# Difficulty: easy
# Flag: PWR{S0urc3_M4ps_L34k}
# Tools: przeglądarka (Narzędzia Deweloperskie / F12)
# Author: VulnBank Team

from typing import Any

from flask import Blueprint, jsonify

blueprint = Blueprint("challenge_a19", __name__, url_prefix="/api/challenges/a19")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A19",
        "name": "Source Maps Leak",
        "category": "OWASP A02:2025",
        "difficulty": "easy",
        "points": 100,
        "description": (
            "Frontend został zbudowany z publicznie dostępnymi source maps. "
            "Po otwarciu DevTools -> Sources można odtworzyć oryginalny kod źródłowy "
            "i znaleźć komentarz z flagą."
        ),
        "hint": "Otwórz DevTools -> Sources i przeszukaj oryginalne pliki frontendu.",
        "endpoint": "Frontend (F12 -> Sources)",
    }), 200
