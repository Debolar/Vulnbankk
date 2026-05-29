import hashlib
from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.user import User
from models.account import Account

profile_bp = Blueprint("profile", __name__)


def md5_hash(password: str) -> str:
    # VULN: A04
    return hashlib.md5(password.encode()).hexdigest()


@profile_bp.route("/", methods=["GET"])
@jwt_required()
def get_profile() -> Any:
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    # VULN: A06 — PESEL zwracany w odpowiedzi (można go użyć do reset-password)
    profile = user.to_dict(include_sensitive=True)

    account = Account.query.filter_by(user_id=user_id).first()
    if account:
        profile["account"] = account.to_dict()

    # Flaga A04 dostępna dla charlie po złamaniu hasła
    if user.email == "charlie@vulnbank.pl":
        profile["flag"] = "PWR{md5_no_salt_cracked}"

    # Flaga A07 dostępna dla boba po brute-force
    if user.email == "bob@vulnbank.pl":
        profile["flag"] = "PWR{no_ratelimit_bruteforce}"

    return jsonify(profile), 200


@profile_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password() -> Any:
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if user.password_hash != md5_hash(old_password):
        return jsonify({"error": "Nieprawidłowe aktualne hasło"}), 401

    user.password_hash = md5_hash(new_password)
    db.session.commit()
    return jsonify({"message": "Hasło zostało zmienione"}), 200
