import hashlib
import logging
import random
from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db
from models.user import User
from models.account import Account

auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger("vulnbank")


def md5_hash(password: str) -> str:
    # VULN: A04 — MD5 bez soli (powinno być bcrypt)
    return hashlib.md5(password.encode()).hexdigest()


def generate_iban(user_id: int) -> str:
    base = f"PL{user_id:04d}{random.randint(100000000000000000000000, 999999999999999999999999)}"
    return base[:32]


@auth_bp.route("/register", methods=["POST"])
def register() -> Any:
    data = request.get_json()
    required = ["first_name", "last_name", "email", "password", "pesel"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Pole {field} jest wymagane"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email już istnieje"}), 409

    user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        password_hash=md5_hash(data["password"]),  # VULN: A04
        pesel=data["pesel"],
    )
    db.session.add(user)
    db.session.flush()

    iban = generate_iban(user.id)
    starting_balance = random.uniform(1000, 9999)
    account = Account(
        user_id=user.id,
        iban=iban,
        balance=round(starting_balance, 2),
    )
    db.session.add(account)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"is_admin": user.is_admin, "email": user.email},
    )
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login() -> Any:
    data = request.get_json()
    email = data.get("email", "")
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()

    # VULN: A09 — hasło logowane w plaintext przy błędzie
    if not user or user.password_hash != md5_hash(password):
        logger.error(f"Login failed for {email} with password {password}")
        return jsonify({"error": "Nieprawidłowy email lub hasło"}), 401

    if user.is_blocked:
        return jsonify({"error": "Konto jest zablokowane"}), 403

    # VULN: A07 — brak rate limitingu, token ważny bez ograniczeń czasowych
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"is_admin": user.is_admin, "email": user.email},
    )
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout() -> Any:
    # VULN: A07 — token NIE jest unieważniany (brak blacklisty w Redis)
    return jsonify({"message": "Wylogowano pomyślnie"}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password() -> Any:
    """
    VULN: A06 — Insecure Design
    Reset hasła wymaga tylko PESELU zamiast bezpiecznego tokenu na email.
    PESEL można zdobyć przez IDOR (A01) z /api/accounts/<id> lub /api/profile
    po zalogowaniu jako inny użytkownik.
    """
    data = request.get_json()
    email = data.get("email", "")
    pesel = data.get("pesel", "")
    new_password = data.get("new_password", "")

    if not all([email, pesel, new_password]):
        return jsonify({"error": "Wymagane pola: email, pesel, new_password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Użytkownik nie istnieje"}), 404

    # VULN: A06 — weryfikacja tylko przez PESEL, brak tokenu, brak wygaśnięcia
    if user.pesel != pesel:
        return jsonify({"error": "Nieprawidłowy PESEL"}), 401

    user.password_hash = md5_hash(new_password)
    db.session.commit()

    response = {"message": "Hasło zostało zmienione"}
    if user.email == "alice@vulnbank.pl":
        response["flag"] = "PWR{insecure_password_reset}"
    return jsonify(response), 200
