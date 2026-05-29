# Challenge: A04 - Cryptographic Failures
# Difficulty: medium
# Flag: PWR{md5_no_salt_cracked}
# Tools: crackstation.net / hashcat / Burp Suite
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify

blueprint = Blueprint("challenge_a04", __name__, url_prefix="/api/challenges/a04")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A04",
        "name": "Cryptographic Failures — MD5 bez soli",
        "category": "OWASP A04:2025",
        "difficulty": "medium",
        "points": 150,
        "description": (
            "Hasła w bazie są hashowane algorytmem MD5 bez soli. "
            "Endpoint /api/admin/backup zwraca listę użytkowników z hashami "
            "(wymaga dostępu admina — zdobądź go przez A08). "
            "Wklej hash MD5 użytkownika charlie na crackstation.net, "
            "uzyskaj hasło i zaloguj się jako charlie."
        ),
        "hint": (
            "1. Zdobądź dostęp admina przez A08 (JWT None alg). "
            "2. GET /api/admin/backup → skopiuj password_hash dla charlie. "
            "3. Wejdź na crackstation.net i wklej hash. "
            "4. Zaloguj się jako charlie, sprawdź profil."
        ),
        "endpoint": "GET /api/admin/backup",
        "charlie_md5_hint": "MD5('charlie2024') = ?",
    }), 200
