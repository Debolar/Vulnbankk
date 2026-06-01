# Challenge: A02 - Security Misconfiguration
# Difficulty: easy
# Flag: PWR{debug_config_exposed}
# Tools: curl / przeglądarka
# Author: VulnBank Team

import os
from typing import Any
from flask import Blueprint, jsonify, current_app

blueprint = Blueprint("challenge_a02", __name__, url_prefix="/api/debug")


@blueprint.route("/config", methods=["GET"])
def debug_config() -> Any:
    """
    VULN: A02 — Security Misconfiguration
    Endpoint zapomniany przez dewelopera. Zwraca pełne os.environ() jako JSON.
    Dostępny bez autoryzacji. Ujawnia klucze, hasła, connection stringi i flagę.
    """
    # VULN: A02 — os.environ() bez autoryzacji, bez filtrowania
    env_vars = dict(os.environ)
    return jsonify({
        "warning": "DEBUG ENDPOINT — REMOVE BEFORE PRODUCTION",
        "environment": env_vars,
    }), 200


@blueprint.route("/dependencies", methods=["GET"])
def list_dependencies() -> Any:
    """
    VULN: A03 — Supply Chain Failures
    Zwraca listę zainstalowanych pakietów. Jeden z nich ma znane CVE
    i ukrytą flagę w polu 'flag'.
    """
    import pkg_resources

    packages = []
    for dist in pkg_resources.working_set:
        pkg = {
            "name": dist.project_name,
            "version": dist.version,
        }
        # VULN: A03 — podatna biblioteka z flagą
        if dist.project_name.lower() == "pyyaml" and dist.version == "5.3.1":
            pkg["cve"] = "CVE-2020-14343"
            pkg["severity"] = "CRITICAL"
            pkg["description"] = "Arbitrary code execution via yaml.load() without Loader"
            pkg["flag"] = "PWR{vulnerable_dependency_found}"
        elif dist.project_name.lower() == "pillow" and dist.version == "9.0.0":
            pkg["cve"] = "CVE-2022-22817"
            pkg["severity"] = "HIGH"
            pkg["description"] = "PIL.ImageMath.eval allows evaluation of arbitrary expressions"
        packages.append(pkg)

    return jsonify({
        "total": len(packages),
        "packages": sorted(packages, key=lambda x: x["name"].lower()),
    }), 200


@blueprint.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok", "service": "VulnBank API"}), 200
