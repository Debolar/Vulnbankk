# Challenge: A11 - Open Redirect
# Difficulty: easy
# Flag: PWR{open_r3d1rect_phi1sh1ng_v3ct0r}
# Tools: curl / przeglądarka
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify, request, redirect

blueprint = Blueprint("challenge_a11", __name__, url_prefix="/api/challenges/a11")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A11",
        "name": "Open Redirect - phishing przez zaufany URL",
        "category": "CWE-601",
        "difficulty": "easy",
        "points": 100,
        "description": (
            "Endpoint /api/challenges/a11/redirect?next= przekierowuje "
            "użytkownika na URL z parametru bez żadnej walidacji. "
            "Atakujący może stworzyć link phishingowy wyglądający jak vulnbank."
        ),
        "hint": (
            "Wywołaj /api/challenges/a11/redirect?next=/api/challenges/a11/flag "
            "i sprawdź gdzie jesteś po przekierowaniu."
        ),
        "endpoint": "GET /api/challenges/a11/redirect?next=",
    }), 200


# VULN: A11 — Open Redirect, brak walidacji docelowego URL
@blueprint.route("/redirect", methods=["GET"])
def open_redirect() -> Any:
    next_url = request.args.get("next", "/")
    # PODATNOŚĆ: redirect na dowolny URL bez sprawdzenia domeny
    response = redirect(next_url)
    response.set_cookie("a11_redirected", "1", max_age=60, httponly=True, samesite="Lax")
    return response


@blueprint.route("/flag", methods=["GET"])
def flag() -> Any:
    if request.cookies.get("a11_redirected") != "1":
        return jsonify({
            "error": "Flag is available only after visiting the open redirect endpoint.",
            "hint": "Use /api/challenges/a11/redirect?next=/api/challenges/a11/flag",
        }), 403

    return jsonify({
        "flag": "PWR{open_r3d1rect_phi1sh1ng_v3ct0r}",
        "info": "Link wyglądał jak vulnbank.pl - ale przekierował gdzie chciał atakujący.",
    }), 200
