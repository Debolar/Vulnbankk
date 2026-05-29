# Challenge: A18 - Server-Side Template Injection
# Difficulty: hard
# Flag: PWR{t1mpl4t3_inj3ct10n}
# Tools: curl / Python / Burp Suite
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify, request, render_template_string
from flask_jwt_extended import jwt_required

blueprint = Blueprint("challenge_a18", __name__, url_prefix="/api/challenges/a18")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A18",
        "name": "Server-Side Template Injection",
        "category": "OWASP A05:2025",
        "difficulty": "hard",
        "points": 200,
        "description": (
            "Endpoint /api/challenges/a18/render renderuje szablon Jinja2 dostarczony "
            "jako parametr template. Aplikacja nie sanitizuje wejścia, więc można "
            "wykonać złośliwe wyrażenie w szablonie i odczytać plik z flagą."
        ),
        "hint": (
            "Podaj parametr template jako wyrażenie Jinja. "
            "Spróbuj uzyskać dostęp do modułu os i przeczytać plik z flagą."
        ),
        "endpoint": "GET /api/challenges/a18/render?template=",
        "payload_hint": "{{ ''.__class__.__mro__[1].__subclasses__()[40]('flag_a18.txt').read() }}",
    }), 200


@blueprint.route("/setup", methods=["GET"])
def setup_flag() -> Any:
    with open("flag_a18.txt", "w", encoding="utf-8") as f:
        f.write("PWR{t1mpl4t3_inj3ct10n}")
    return jsonify({"message": "Setup OK - flag_a18.txt created"}), 200


@blueprint.route("/render", methods=["GET"])
@jwt_required()
def render_template() -> Any:
    template = request.args.get("template", "")
    if not template:
        return jsonify({"error": "Podaj parametr template"}), 400

    try:
        rendered = render_template_string(template, user="alice", role="user")
        return jsonify({
            "template": template,
            "rendered": rendered,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
