# Challenge: A07 - Authentication Failures (Brute-force)
# Difficulty: easy
# Flag: PWR{no_ratelimit_bruteforce}
# Tools: Burp Suite Intruder / curl / hydra
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify

blueprint = Blueprint("challenge_a07", __name__, url_prefix="/api/challenges/a07")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A07",
        "name": "Authentication Failures — Brute-force bez rate limitingu",
        "category": "OWASP A07:2025",
        "difficulty": "easy",
        "points": 100,
        "description": (
            "Endpoint /api/auth/login nie ma rate limitingu ani blokady konta. "
            "Możliwe jest nieograniczone zgadywanie haseł (brute-force). "
            "Bob ma słabe hasło — znajdź je w ciągu 50 prób."
        ),
        "hint": (
            "Użyj Burp Suite Intruder lub pętli curl z listą haseł. "
            "Konto: bob@vulnbank.pl. "
            "Hasło jest w top 100 najczęstszych haseł."
        ),
        "endpoint": "POST /api/auth/login",
        "target_email": "bob@vulnbank.pl",
        "wordlist_hint": "rockyou.txt top 100",
    }), 200
