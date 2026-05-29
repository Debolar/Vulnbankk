# Challenge: A17 - Sensitive Information Disclosure
# Difficulty: easy
# Flag: PWR{exposed_internal_token}
# Tools: curl / Burp Suite / przeglądarka
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

blueprint = Blueprint("challenge_a17", __name__, url_prefix="/api/challenges/a17")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    """Opis wyzwania."""
    return jsonify({
        "challenge": "A17",
        "name": "Sensitive Information Disclosure",
        "category": "Data Exposure",
        "difficulty": "easy",
        "points": 100,
        "description": (
            "Endpoint /api/challenges/a17/profile zwraca dane użytkownika. "
            "Problem: odpowiedź zawiera poufne pola, które nie powinny być widoczne dla klienta."
        ),
        "hint": (
            "Zaloguj się i pobierz swój profil. Czy w odpowiedzi widzisz coś, "
            "co wygląda na flagę? Zwróć uwagę na pola, które zwykle powinny być ukryte."
        ),
        "endpoint": "GET /api/challenges/a17/profile",
        "vulnerable_parameter": "Całkowita odpowiedź zawiera wrażliwe dane",
    }), 200


@blueprint.route("/profile", methods=["GET"])
@jwt_required()
def get_profile() -> Any:
    """
    VULN: A17 — Sensitive Information Disclosure
    
    Endpoint zwraca profil zalogowanego użytkownika, ALE zawiera pole 'internal_token'
    które jest przeznaczone wyłącznie dla administratorów i systemów wewnętrznych.
    
    Aplikacja "zapomina" filtrować wrażliwe pola, dlatego flaga jest dostępna dla każdego
    zalogowanego użytkownika.
    
    FIX: Zwrócić tylko pola dozwolone dla użytkownika, np. id, name, email, role
    (bez internal_token, api_key, password_hash, secret_answer, itp.)
    """
    user_id = get_jwt_identity()
    
    # VULN: A17 — Zwracamy ALL pola, w tym wrażliwe 'internal_token'
    # W rzeczywistości dane mogłyby pochodzić z bazy danych
    user_data = {
        "id": user_id,
        "name": "User Account",
        "email": f"user{user_id}@vulnbank.pl",
        "role": "user",
        # VULN: To pole NIGDY nie powinno być w odpowiedzi dla klienta
        "internal_token": "PWR{exposed_internal_token}",
        # VULN: To również poufne
        "api_key": "secret_api_key_12345",
        "is_admin": False,
    }
    
    return jsonify(user_data), 200


@blueprint.route("/admin-only", methods=["GET"])
@jwt_required()
def admin_endpoint() -> Any:
    """
    Endpoint dostępny tylko dla administratorów.
    Wymaga internal_token z poprzedniego endpointu.
    """
    user_id = get_jwt_identity()
    
    return jsonify({
        "message": "Gratulacje! Zdobyłeś flagę.",
        "flag": "PWR{exposed_internal_token}",
        "description": "Podatność: Wrażliwe dane były widoczne w publicznym API.",
    }), 200
