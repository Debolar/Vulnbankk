# Challenge: A12 - Server-Side Request Forgery (SSRF)
# Difficulty: medium
# Flag: PWR{ss4f_int3rnal_s3rvice_expos3d}
# Tools: curl / Burp Suite
# Author: VulnBank Team

from typing import Any
from flask import Blueprint, jsonify, request
import urllib.request

blueprint = Blueprint("challenge_a12", __name__, url_prefix="/api/challenges/a12")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A12",
        "name": "SSRF - falsyfikacja zapytania po stronie serwera",
        "category": "OWASP A10:2021",
        "difficulty": "medium",
        "points": 150,
        "description": (
            "Endpoint /api/challenges/a12/fetch przyjmuje parametr url "
            "i pobiera jego zawartosc po stronie serwera. "
            "Brak walidacji pozwala odpytac wewnetrzne adresy."
        ),
        "hint": (
            "Sprobuj url=http://localhost/api/challenges/a12/internal. "
            "Serwer wykona request do samego siebie."
        ),
        "endpoint": "GET /api/challenges/a12/fetch?url=",
    }), 200


@blueprint.route("/internal", methods=["GET"])
def internal_resource() -> Any:
    remote_addr = request.remote_addr
    if remote_addr not in ("127.0.0.1", "::1"):
        return jsonify({"error": "Internal endpoint - brak dostepu"}), 403
    return jsonify({
        "secret": "internal-service-key-9f3a",
        "flag": "PWR{ss4f_int3rnal_s3rvice_expos3d}",
    }), 200


# VULN: A12 - SSRF, brak walidacji adresow wewnetrznych
@blueprint.route("/fetch", methods=["GET"])
def fetch_url() -> Any:
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "Podaj parametr url"}), 400

    try:
        # podatnosc: serwer wykonuje request do dowolnego URL podanego przez uzytkownika
        with urllib.request.urlopen(url, timeout=3) as resp:
            body = resp.read(4096).decode("utf-8", errors="replace")
        return jsonify({"url": url, "response": body}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500