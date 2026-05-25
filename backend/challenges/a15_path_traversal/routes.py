# Challenge: A15 - Path Traversal
# Difficulty: medium
# Flag: PWR{p4th_tr4v3rs4l_s3cr3t_r34d}
# Tools: curl / przeglądarka
# Author: VulnBank Team

import os
from typing import Any
from flask import Blueprint, jsonify, request

blueprint = Blueprint("challenge_a15", __name__, url_prefix="/api/challenges/a15")

REPORTS_DIR = "/app/reports"


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A15",
        "name": "Path Traversal - odczyt plikow poza katalogiem",
        "category": "OWASP A01:2021",
        "difficulty": "medium",
        "points": 150,
        "description": (
            "Endpoint /api/challenges/a15/report?name= serwuje pliki "
            "z katalogu /app/reports/. Brak sanityzacji sciezki pozwala "
            "wyjsc poza katalog i odczytac dowolny plik."
        ),
        "hint": (
            "Sprobuj name=../secret/flag.txt. "
            "Sekretna flaga jest w /app/secret/flag.txt."
        ),
        "endpoint": "GET /api/challenges/a15/report?name=",
    }), 200


@blueprint.route("/setup", methods=["GET"])
def setup() -> Any:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs("/app/secret", exist_ok=True)
    with open(os.path.join(REPORTS_DIR, "q1_2024.txt"), "w") as f:
        f.write("Raport Q1 2024: przychod 1.2M PLN")
    with open("/app/secret/flag.txt", "w") as f:
        f.write("PWR{p4th_tr4v3rs4l_s3cr3t_r34d}")
    return jsonify({"message": "Setup OK"}), 200


# VULN: A15 - Path Traversal, brak normalizacji sciezki
@blueprint.route("/report", methods=["GET"])
def get_report() -> Any:
    name = request.args.get("name", "")
    if not name:
        return jsonify({"error": "Podaj parametr name, np. ?name=q1_2024.txt"}), 400

    # PODATNOSC: laczemy sciezke bez sprawdzenia czy nie wychodzi poza REPORTS_DIR
    file_path = os.path.join(REPORTS_DIR, name)

    try:
        with open(file_path) as f:
            content = f.read()
        return jsonify({"file": name, "content": content}), 200
    except FileNotFoundError:
        return jsonify({"error": f"Plik nie znaleziony: {file_path}"}), 404
    except PermissionError:
        return jsonify({"error": "Brak uprawnien"}), 403