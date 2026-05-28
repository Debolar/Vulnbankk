import base64
import json
import logging
import os
from typing import Any, Optional

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request

from extensions import db
from models.user import User
from models.account import Account
from models.transaction import Transaction

admin_bp = Blueprint("admin", __name__)
logger = logging.getLogger("vulnbank")

LOG_FILE = "/tmp/vulnbank.log"


def _decode_jwt_no_verify(token: str) -> Optional[dict]:
    """
    VULN: A08 — dekoduje JWT bez weryfikacji podpisu.
    Akceptuje algorytm 'none'.
    """
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None

        def pad(s: str) -> str:
            return s + "=" * (4 - len(s) % 4) if len(s) % 4 else s

        payload = json.loads(base64.urlsafe_b64decode(pad(parts[1])))
        return payload
    except Exception:
        return None


def require_admin():
    """Wymaga tokenu JWT z is_admin=True."""
    verify_jwt_in_request()
    claims = get_jwt()
    if not claims.get("is_admin", False):
        return jsonify({"error": "Brak uprawnień administratora"}), 403
    return None


@admin_bp.route("/dashboard", methods=["GET"])
def admin_dashboard() -> Any:
    """
    VULN: A08 — JWT None Algorithm Bypass
    Backend akceptuje JWT z algorytmem 'none'.
    Zmień payload JWT: is_admin: false → true, alg: HS256 → none, usuń sygnaturę.
    Flaga PWR{jwt_tampered_admin} w odpowiedzi.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Brak tokenu"}), 401

    token = auth_header.split(" ", 1)[1]

    # VULN: A08 — sprawdź nagłówek JWT i jeśli alg=none, akceptuj bez weryfikacji
    try:
        parts = token.split(".")
        if len(parts) >= 2:
            def pad(s: str) -> str:
                return s + "=" * (4 - len(s) % 4) if len(s) % 4 else s

            header = json.loads(base64.urlsafe_b64decode(pad(parts[0])))
            if header.get("alg", "").lower() == "none":
                # VULN: A08 — akceptuj token bez podpisu!
                payload = json.loads(base64.urlsafe_b64decode(pad(parts[1])))
                if not payload.get("is_admin", False):
                    return jsonify({"error": "Brak uprawnień administratora"}), 403
                # Token z alg=none i is_admin=true → dostęp przyznany
                claims = payload
            else:
                # Normalny JWT — zweryfikuj
                verify_jwt_in_request()
                claims = get_jwt()
                if not claims.get("is_admin", False):
                    return jsonify({"error": "Brak uprawnień administratora"}), 403
        else:
            return jsonify({"error": "Nieprawidłowy token"}), 401
    except Exception:
        return jsonify({"error": "Nieprawidłowy token"}), 401

    users_count = User.query.count()
    accounts_count = Account.query.count()
    tx_count = Transaction.query.count()
    total_volume = db.session.query(db.func.sum(Transaction.amount)).scalar() or 0

    return jsonify({
        "message": "Panel administratora",
        "flag": "PWR{jwt_tampered_admin}",
        "stats": {
            "users": users_count,
            "accounts": accounts_count,
            "transactions": tx_count,
            "total_volume": float(total_volume),
        }
    }), 200


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users() -> Any:
    err = require_admin()
    if err:
        return err

    users = User.query.all()
    result = []
    for u in users:
        data = u.to_dict()
        account = Account.query.filter_by(user_id=u.id).first()
        data["balance"] = float(account.balance) if account else 0
        data["iban"] = account.iban if account else None
        result.append(data)
    return jsonify(result), 200


@admin_bp.route("/users/<int:user_id>/block", methods=["POST"])
@jwt_required()
def block_user(user_id: int) -> Any:
    err = require_admin()
    if err:
        return err

    user = User.query.get_or_404(user_id)
    user.is_blocked = not user.is_blocked
    db.session.commit()
    status = "zablokowane" if user.is_blocked else "odblokowane"
    return jsonify({"message": f"Konto {status}", "is_blocked": user.is_blocked}), 200


@admin_bp.route("/transactions", methods=["GET"])
@jwt_required()
def list_all_transactions() -> Any:
    err = require_admin()
    if err:
        return err

    txs = Transaction.query.order_by(Transaction.created_at.desc()).limit(100).all()
    return jsonify([t.to_dict() for t in txs]), 200


@admin_bp.route("/backup", methods=["GET"])
@jwt_required()
def backup_users() -> Any:
    """
    VULN: A04 — backup zwraca hasła jako MD5 bez soli.
    Hashów MD5 można użyć na crackstation.net do odzyskania haseł.
    """
    err = require_admin()
    if err:
        return err

    users = User.query.all()
    return jsonify([u.to_dict(include_sensitive=True) for u in users]), 200


@admin_bp.route("/logs", methods=["GET"])
def get_logs() -> Any:
    """
    VULN: A09 — endpoint logów dostępny BEZ autoryzacji.
    Logi zawierają hasła w plaintext (logowane przy błędnym logowaniu).
    Flaga jest teraz w zmiennej środowiskowej FLAG_A09.
    """
    # VULN: A09 — brak @jwt_required() i brak require_admin()
    flag_a09 = os.environ.get("FLAG_A09", "PWR{logs_exposed_no_auth}")
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
            # Zamiast plaintext haseł, zwróć logi bez wrażliwych danych
            # ale dodaj linię z flagą jeśli istnieje
            sanitized_logs = [l.strip() for l in lines if "password" not in l.lower()]
            if flag_a09 and sanitized_logs:
                # Dodaj flagi do ostatniej linii lub jako osobną linię dla challenge'u
                sanitized_logs.append(f"2024-01-15 08:23:11 ERROR Backup admin password: {flag_a09}")
            last_100 = sanitized_logs[-100:] if len(sanitized_logs) > 100 else sanitized_logs
            return jsonify({"logs": last_100}), 200
        else:
            # Fallback - zwróć domyślne logi bez wrażliwych danych
            return jsonify({"logs": [
                "2024-01-15 08:23:11 ERROR Login failed for admin@vulnbank.pl",
                "2024-01-15 08:23:15 ERROR Login failed for alice@vulnbank.pl",
                "2024-01-15 09:01:33 INFO User 3 logged in successfully",
                "2024-01-15 09:45:22 ERROR Login failed for bob@vulnbank.pl",
                "2024-01-15 10:12:44 ERROR Login failed for admin@vulnbank.pl",
                "2024-01-15 11:30:01 INFO Transfer completed: 500.00 PLN from account 2 to account 3",
                f"2024-01-15 08:23:11 ERROR Backup admin password: {flag_a09}",
            ]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/ping", methods=["POST"])
@jwt_required()
def ping_host() -> Any:
    err = require_admin()
    if err:
        return err

    data = request.get_json()
    host = data.get("host", "127.0.0.1")
    import subprocess
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", host],
            capture_output=True, text=True, timeout=5
        )
        return jsonify({"output": result.stdout + result.stderr}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
