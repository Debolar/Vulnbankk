# Challenge: A14 - Mass Assignment
# Difficulty: medium
# Flag: PWR{m4ss_4ss1gnm3nt_pr1v_3sc}
# Tools: curl / Burp Suite
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User

blueprint = Blueprint("challenge_a14", __name__, url_prefix="/api/challenges/a14")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A14",
        "name": "Mass Assignment - eskalacja uprawnien",
        "category": "OWASP A01:2021",
        "difficulty": "medium",
        "points": 150,
        "description": (
            "Endpoint /api/challenges/a14/profile/update przyjmuje JSON "
            "i przypisuje WSZYSTKIE pola bezposrednio do modelu uzytkownika. "
            "Mozesz nadpisac pole is_admin=true i uzyskac flage."
        ),
        "hint": (
            "Wyslij PATCH z JSON zawierajacym is_admin: true. "
            "Nastepnie wywolaj /api/challenges/a14/secret."
        ),
        "endpoint": "PATCH /api/challenges/a14/profile/update",
    }), 200


# VULN: A14 - Mass Assignment, brak whitelisty pol
@blueprint.route("/profile/update", methods=["PATCH"])
@jwt_required()
def update_profile() -> Any:
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}

    # PODATNOSC: przypisujemy wszystko co przyjdzie w JSON-ie
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    db.session.commit()
    return jsonify({"message": "Profile updated", "is_admin": user.is_admin}), 200


@blueprint.route("/secret", methods=["GET"])
@jwt_required()
def admin_secret() -> Any:
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "Admins only"}), 403
    return jsonify({"flag": "PWR{m4ss_4ss1gnm3nt_pr1v_3sc}"}), 200