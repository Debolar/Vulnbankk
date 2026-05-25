# Challenge: A13 - Command Injection
# Difficulty: hard
# Flag: PWR{c0mm4nd_1nj3ct10n_rce}
# Tools: curl / Burp Suite
# Author: VulnBank Team

import subprocess
from typing import Any
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

blueprint = Blueprint("challenge_a13", __name__, url_prefix="/api/challenges/a13")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A13",
        "name": "Command Injection - zdalne wykonanie kodu",
        "category": "OWASP A03:2021",
        "difficulty": "hard",
        "points": 200,
        "description": (
            "Panel diagnostyczny banku oferuje ping do adresu IP. "
            "Endpoint /api/challenges/a13/ping?host= wstrzykuje wartosc "
            "parametru bezposrednio do polecenia systemowego."
        ),
        "hint": (
            "Sprobuj host=127.0.0.1; whoami lub host=127.0.0.1 && cat /app/flag_rce.txt. "
            "Separator polecen pozwala wykonac dowolna komende."
        ),
        "endpoint": "GET /api/challenges/a13/ping?host=",
        "payload_hint": "127.0.0.1; cat /app/flag_rce.txt",
    }), 200


@blueprint.route("/setup", methods=["GET"])
def setup() -> Any:
    import os
    os.makedirs("/app", exist_ok=True)
    with open("/app/flag_rce.txt", "w") as f:
        f.write("PWR{c0mm4nd_1nj3ct10n_rce}")
    return jsonify({"message": "Setup OK - flaga zapisana w /app/flag_rce.txt"}), 200


# VULN: A13 - Command Injection przez shell=True i brak sanityzacji
@blueprint.route("/ping", methods=["GET"])
@jwt_required()
def ping_host() -> Any:
    host = request.args.get("host", "")
    if not host:
        return jsonify({"error": "Podaj parametr host"}), 400

    try:
        # PODATNOSC: shell=True + niesanityzowany input = RCE
        result = subprocess.run(
            f"ping -c 1 -W 1 {host}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        output = result.stdout + result.stderr
        return jsonify({
            "host": host,
            "output": output,
        }), 200
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Timeout"}), 408