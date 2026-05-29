# Challenge: A20 - Race Condition Double Spend
# Difficulty: hard
# Flag: PWR{race_condition_double_spend}
# Tools: curl / Python threads / Burp Suite Turbo Intruder
# Author: VulnBank Team

from decimal import Decimal, InvalidOperation
from time import sleep
from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models.account import Account
from models.transaction import Transaction

blueprint = Blueprint("challenge_a20", __name__, url_prefix="/api/challenges/a20")

BOB_USER_ID = 2
BOB_ACCOUNT_ID = 2
ALICE_IBAN = "PL00100100100100100100100100"
BOB_START_BALANCE = Decimal("2891.75")
FLAG = "PWR{race_condition_double_spend}"


def _parse_amount(raw_amount: Any) -> Decimal | None:
    try:
        amount = Decimal(str(raw_amount))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return amount.quantize(Decimal("0.01"))


def _get_bob_account() -> Account | None:
    user_id = int(get_jwt_identity())
    if user_id != BOB_USER_ID:
        return None
    return Account.query.filter_by(user_id=user_id, id=BOB_ACCOUNT_ID).first()


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A20",
        "name": "Race Condition - Double Spend",
        "category": "CWE-362",
        "difficulty": "hard",
        "points": 200,
        "description": (
            "Specjalny endpoint przelewu sprawdza saldo, czeka przez krotki czas, "
            "a dopiero potem odejmuje srodki. Dwa rownolegle requesty moga przejsc "
            "walidacje na tym samym starym saldzie i doprowadzic konto Boba ponizej zera."
        ),
        "hint": (
            "Zaloguj sie jako bob i wyslij dwa przelewy do Alice w tym samym momencie. "
            "Kazdy pojedynczy przelew musi miescic sie w saldzie Boba."
        ),
        "endpoint": "POST /api/challenges/a20/transfer-race",
        "recipient_iban": ALICE_IBAN,
    }), 200


@blueprint.route("/status", methods=["GET"])
@jwt_required()
def status() -> Any:
    account = _get_bob_account()
    if not account:
        return jsonify({"error": "To wyzwanie wykonaj jako bob@vulnbank.pl"}), 403

    return jsonify({
        "account_id": account.id,
        "balance": float(account.balance),
        "currency": account.currency,
        "suggested_amount": 1500,
        "recipient_iban": ALICE_IBAN,
    }), 200


@blueprint.route("/reset", methods=["POST"])
@jwt_required()
def reset_lab_state() -> Any:
    account = _get_bob_account()
    if not account:
        return jsonify({"error": "To wyzwanie wykonaj jako bob@vulnbank.pl"}), 403

    data = request.get_json() or {}
    if data.get("confirm") != "RESET_A20":
        return jsonify({"error": "Wyslij confirm=RESET_A20, aby zresetowac saldo Boba dla labu"}), 400

    account.balance = BOB_START_BALANCE
    db.session.commit()
    return jsonify({
        "message": "Stan A20 zresetowany",
        "balance": float(account.balance),
        "recipient_iban": ALICE_IBAN,
    }), 200


# VULN: A20 - race condition, check-then-act bez blokady/wspolnej transakcji
@blueprint.route("/transfer-race", methods=["POST"])
@jwt_required()
def transfer_race() -> Any:
    from_account = _get_bob_account()
    if not from_account:
        return jsonify({"error": "To wyzwanie wykonaj jako bob@vulnbank.pl"}), 403

    data = request.get_json() or {}
    to_iban = data.get("to_iban", "")
    amount = _parse_amount(data.get("amount"))
    title = data.get("title", "A20 race transfer")

    if not to_iban or amount is None:
        return jsonify({"error": "Wymagane pola: to_iban, amount"}), 400
    if amount <= 0:
        return jsonify({"error": "Kwota musi byc wieksza od 0"}), 400

    to_account = Account.query.filter_by(iban=to_iban).first()
    if not to_account:
        return jsonify({"error": "Konto odbiorcy nie istnieje"}), 404
    if to_account.id == from_account.id:
        return jsonify({"error": "Nie mozesz przelac srodkow na wlasne konto"}), 400

    checked_balance = Decimal(str(from_account.balance))
    if checked_balance < amount:
        return jsonify({
            "error": "Niewystarczajace saldo",
            "checked_balance": float(checked_balance),
        }), 400

    # Celowe okno race: po sprawdzeniu salda request spi, ale nie blokuje konta.
    # Rownolegly request moze przejsc ten sam check na identycznym starym saldzie.
    sleep(0.55)

    try:
        db.session.execute(
            db.text("UPDATE accounts SET balance = balance - :amount WHERE id = :account_id"),
            {"amount": amount, "account_id": from_account.id},
        )
        db.session.execute(
            db.text("UPDATE accounts SET balance = balance + :amount WHERE id = :account_id"),
            {"amount": amount, "account_id": to_account.id},
        )

        tx = Transaction(
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            amount=amount,
            title=title,
        )
        db.session.add(tx)

        new_balance = Decimal(str(db.session.execute(
            db.text("SELECT balance FROM accounts WHERE id = :account_id"),
            {"account_id": from_account.id},
        ).scalar_one()))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    response = {
        "message": "Przelew A20 wykonany",
        "checked_balance": float(checked_balance),
        "new_balance": float(new_balance),
        "transaction": tx.to_dict(),
    }
    if new_balance < 0:
        response["flag"] = FLAG
        response["message"] = "Double spend udany - konto Boba zeszlo ponizej zera"
    else:
        response["hint"] = "Wyslij drugi identyczny request rownolegle, nie po zakonczeniu pierwszego."

    return jsonify(response), 200
