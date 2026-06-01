from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.account import Account
from models.transaction import Transaction

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/", methods=["GET"])
@jwt_required()
def get_transactions() -> Any:
    user_id = int(get_jwt_identity())
    account = Account.query.filter_by(user_id=user_id).first()
    if not account:
        return jsonify([]), 200

    txs = Transaction.query.filter(
        (Transaction.from_account_id == account.id) |
        (Transaction.to_account_id == account.id)
    ).order_by(Transaction.created_at.desc()).all()

    return jsonify([t.to_dict() for t in txs]), 200


@transactions_bp.route("/recent", methods=["GET"])
@jwt_required()
def get_recent_transactions() -> Any:
    user_id = int(get_jwt_identity())
    account = Account.query.filter_by(user_id=user_id).first()
    if not account:
        return jsonify([]), 200

    txs = Transaction.query.filter(
        (Transaction.from_account_id == account.id) |
        (Transaction.to_account_id == account.id)
    ).order_by(Transaction.created_at.desc()).limit(5).all()

    return jsonify([t.to_dict() for t in txs]), 200


@transactions_bp.route("/transfer", methods=["POST"])
@jwt_required()
def transfer() -> Any:
    user_id = int(get_jwt_identity())
    data = request.get_json()

    to_iban = data.get("to_iban", "")
    amount = data.get("amount")
    title = data.get("title", "Przelew")

    if not to_iban or amount is None:
        return jsonify({"error": "Wymagane pola: to_iban, amount"}), 400

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Nieprawidłowa kwota"}), 400

    if amount <= 0:
        return jsonify({"error": "Kwota musi być większa od 0"}), 400

    from_account = Account.query.filter_by(user_id=user_id).first()
    if not from_account:
        return jsonify({"error": "Nie masz konta bankowego"}), 404

    to_account = Account.query.filter_by(iban=to_iban).first()
    if not to_account:
        return jsonify({"error": "Konto odbiorcy nie istnieje"}), 404

    if from_account.id == to_account.id:
        return jsonify({"error": "Nie możesz przelać środków na własne konto"}), 400

    if float(from_account.balance) < amount:
        return jsonify({"error": "Niewystarczające saldo"}), 400

    from_account.balance = float(from_account.balance) - amount
    to_account.balance = float(to_account.balance) + amount

    tx = Transaction(
        from_account_id=from_account.id,
        to_account_id=to_account.id,
        amount=amount,
        title=title,
    )
    db.session.add(tx)
    db.session.commit()

    return jsonify({"message": "Przelew wykonany pomyślnie", "transaction": tx.to_dict()}), 200


@transactions_bp.route("/search", methods=["GET"])
@jwt_required()
def search_transactions() -> Any:
    """
    VULN: A05 — SQL Injection przez string concatenation
    Payload: ' UNION SELECT id,flag_value,3,4,5,6 FROM flags WHERE challenge_id='A05'--
    """
    user_id = int(get_jwt_identity())
    account = Account.query.filter_by(user_id=user_id).first()
    if not account:
        return jsonify([]), 200

    q = request.args.get("q", "")

    # VULN: A05 — string concatenation zamiast parametryzowanego zapytania
    raw_sql = (
        f"SELECT id, from_account_id, to_account_id, amount, title, created_at "
        f"FROM transactions "
        f"WHERE (from_account_id = {account.id} OR to_account_id = {account.id}) "
        f"AND title LIKE '%{q}%' "
        f"ORDER BY created_at DESC"
    )

    try:
        result = db.session.execute(db.text(raw_sql))
        rows = result.fetchall()
        transactions = []
        for row in rows:
            transactions.append({
                "id": row[0],
                "from_account_id": row[1],
                "to_account_id": row[2],
                "amount": float(row[3]) if row[3] else 0,
                "title": str(row[4]),
                "created_at": str(row[5]),
            })
        return jsonify(transactions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

