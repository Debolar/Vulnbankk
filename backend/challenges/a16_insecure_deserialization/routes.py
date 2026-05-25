# Challenge: A16 - Insecure Deserialization
# Difficulty: hard
# Flag: PWR{p1ckl3_d3s3r14l1z4t10n_rce}
# Tools: curl / Python
# Author: VulnBank Team

import pickle
import base64
from typing import Any
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

blueprint = Blueprint("challenge_a16", __name__, url_prefix="/api/challenges/a16")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A16",
        "name": "Insecure Deserialization - pickle RCE",
        "category": "OWASP A08:2021",
        "difficulty": "hard",
        "points": 200,
        "description": (
            "Endpoint /api/challenges/a16/preferences wczytuje preferencje "
            "uzytkownika z base64-encoded pickle. "
            "pickle.loads() na niezaufanych danych = zdalne wykonanie kodu."
        ),
        "hint": (
            "Stworz obiekt pickle ktory zwraca flage przez __reduce__. "
            "Zakoduj go base64 i wyslij jako parametr data. "
            "Przyklad exploita w Python ponizej."
        ),
        "endpoint": "POST /api/challenges/a16/preferences",
        "payload_hint": (
            "import pickle, base64\n"
            "class Exploit(object):\n"
            "    def __reduce__(self):\n"
            "        return (str, ('PWR{p1ckl3_d3s3r14l1z4t10n_rce}',))\n"
            "print(base64.b64encode(pickle.dumps(Exploit())).decode())"
        ),
    }), 200


# VULN: A16 - Insecure Deserialization, pickle.loads() na danych od uzytkownika
@blueprint.route("/preferences", methods=["POST"])
@jwt_required()
def load_preferences() -> Any:
    data = request.get_json() or {}
    encoded = data.get("data", "")

    if not encoded:
        return jsonify({"error": "Podaj pole data z base64-encoded pickle"}), 400

    try:
        raw = base64.b64decode(encoded)
        # PODATNOSC: deserializacja niezaufanych danych
        prefs = pickle.loads(raw)
        return jsonify({
            "preferences": str(prefs),
            "flag": "PWR{p1ckl3_d3s3r14l1z4t10n_rce}",
        }), 200
    except Exception as e:
        return jsonify({"error": f"Blad deserializacji: {e}"}), 400