from typing import Any

from flask import Blueprint, jsonify, request

from extensions import db
from models.flag import Flag
from models.player_solve import PlayerSolve
from ctf.decorators import ctf_jwt_required, get_ctf_player_id

ctf_flags_bp = Blueprint("ctf_flags", __name__)

CHALLENGE_META = [
    {"id": "A01", "name": "Broken Access Control (IDOR)", "category": "OWASP A01:2021", "difficulty": "easy", "points": 100,
     "hint": "Sprawdź endpoint /api/accounts/<id>. Czy możesz zobaczyć konta innych użytkowników?",
     "endpoint": "GET /api/accounts/1"},
    {"id": "A02", "name": "Security Misconfiguration", "category": "OWASP A02:2021", "difficulty": "easy", "points": 100,
     "hint": "Poszukaj zapomnianego endpointu debug w /api/debug/.",
     "endpoint": "GET /api/debug/config"},
     {"id": "A02.1", "name": "Source Maps Leak", "category": "OWASP A02:2021", "difficulty": "easy", "points": 100, 
      "hint": "Jak przeglądarki radzą sobie z mapowaniem zminifikowanego kodu? Zbadaj oryginalne pliki w DevToolsach w zakładce Sources.",
      "endpoint": "Frontend (F12 -> Sources)"},
    {"id": "A03", "name": "Supply Chain Failures", "category": "OWASP A03:2021", "difficulty": "easy", "points": 100,
     "hint": "Sprawdź listę zależności: /api/debug/dependencies. Poszukaj pakietu z polem 'flag'.",
     "endpoint": "GET /api/debug/dependencies"},
    {"id": "A04", "name": "Cryptographic Failures (MD5)", "category": "OWASP A04:2021", "difficulty": "medium", "points": 150,
     "hint": "Zdobądź dostęp admina (A08), pobierz /api/admin/backup, złam hash MD5 na crackstation.net.",
     "endpoint": "GET /api/admin/backup"},
    {"id": "A05", "name": "SQL Injection", "category": "OWASP A05:2021", "difficulty": "medium", "points": 150,
     "hint": "Wyszukiwarka transakcji jest podatna. Wstrzyknij UNION SELECT do parametru ?q=",
     "endpoint": "GET /api/transactions/search?q="},
    {"id": "A06", "name": "Insecure Design", "category": "OWASP A06:2021", "difficulty": "easy", "points": 100,
     "hint": "Reset hasła wymaga tylko PESELU — brak tokenu emailowego. PESEL widoczny w profilu.",
     "endpoint": "POST /api/auth/forgot-password"},
    {"id": "A07", "name": "Authentication Failures", "category": "OWASP A07:2021", "difficulty": "easy", "points": 100,
     "hint": "Brak rate limitingu na logowaniu. Użyj Burp Intruder lub curl na bob@vulnbank.pl.",
     "endpoint": "POST /api/auth/login"},
    {"id": "A08", "name": "JWT None Algorithm", "category": "OWASP A08:2021", "difficulty": "medium", "points": 150,
     "hint": "Czy JWT sprawdza algorytm? Spróbuj zmienić alg na 'none' i is_admin na true.",
     "endpoint": "GET /api/admin/dashboard"},
    {"id": "A09", "name": "Logging & Alerting Failures", "category": "OWASP A09:2021", "difficulty": "easy", "points": 100,
     "hint": "Endpoint logów nie wymaga autoryzacji. Sprawdź GET /api/admin/logs.",
     "endpoint": "GET /api/admin/logs"},
    {"id": "A10", "name": "Exceptional Conditions", "category": "OWASP A10:2021", "difficulty": "easy", "points": 100,
     "hint": "Wyślij nieprawidłowy parametr do kalkulatora kredytu. Flask DEBUG ujawni stack trace.",
     "endpoint": "GET /api/loans/calculate?amount=abc&rate=2"},
     {"id": "A11","name": "Open Redirect","category": "OWASP A01:2021","difficulty": "easy","points": 100,
      "hint": "Parametr next= nie jest walidowany — możesz przekierować na dowolny URL",
      "endpoint": "GET /api/challenges/a11/redirect?next="},
    {"id": "A12", "name": "SSRF", "category": "OWASP A10:2021", "difficulty": "medium", "points": 150,
     "hint": "Endpoint /api/challenges/a12/fetch pozwala pobrać zawartość URL. Spróbuj pobrać wewnętrzne zasoby.",
     "endpoint": "GET /api/challenges/a12/fetch?url="},
    {"id": "A13", "name": "Command Injection", "category": "CWE-78", "difficulty": "hard", "points": 200,
     "hint": "Parametr komendy jest przekazywany do shell'a bez sanityzacji. Wstrzyknij ; ls",
     "endpoint": "GET /api/challenges/a13/execute?cmd="},
    {"id": "A14", "name": "Mass Assignment", "category": "CWE-915", "difficulty": "medium", "points": 150,
     "hint": "Endpoint pozwala na masowe przypisanie pól. Spróbuj ustawić is_admin=true",
     "endpoint": "POST /api/challenges/a14/user"},
    {"id": "A15", "name": "Path Traversal", "category": "CWE-22", "difficulty": "medium", "points": 150,
     "hint": "Parametr file nie waliduje ścieżki. Spróbuj ../../../etc/passwd",
     "endpoint": "GET /api/challenges/a15/file?name="},
    {"id": "A16", "name": "Insecure Deserialization", "category": "CWE-502", "difficulty": "hard", "points": 200,
     "hint": "Endpoint deserializuje pickle bez walidacji. Wstrzyknij RCE payload",
     "endpoint": "POST /api/challenges/a16/deserialize"},
    {"id": "A17", "name": "Sensitive Information Disclosure", "category": "Data Exposure", "difficulty": "easy", "points": 100,
     "hint": "Zaloguj się i pobierz swój profil. Czy widzisz coś, co wygląda na flagę?",
     "endpoint": "GET /api/challenges/a17/profile"},
    {"id": "A18", "name": "Server-Side Template Injection", "category": "CWE-94", "difficulty": "hard", "points": 200,
     "hint": "Renderyzowany jest Twój szablon Jinja2. Spróbuj odczytać plik z flagą przez SSTI.",
     "endpoint": "GET /api/challenges/a18/render?template="},
]

_SPECIAL_FLAGS = {
    "PWR{jwt_tampered_admin}": ("A08", 150),
}


@ctf_flags_bp.route("/", methods=["GET"])
def list_challenges() -> Any:
    return jsonify(CHALLENGE_META), 200


@ctf_flags_bp.route("/check", methods=["POST"])
@ctf_jwt_required
def check_flag() -> Any:
    player_id = get_ctf_player_id()
    data = request.get_json() or {}
    submitted = data.get("flag", "").strip()

    if not submitted:
        return jsonify({"correct": False, "message": "Flaga nie może być pusta"}), 200

    # Resolve challenge_id and points
    if submitted in _SPECIAL_FLAGS:
        challenge_id, points = _SPECIAL_FLAGS[submitted]
    else:
        flag = Flag.query.filter_by(flag_value=submitted).first()
        if not flag:
            return jsonify({"correct": False, "message": "Nieprawidłowa flaga"}), 200
        challenge_id, points = flag.challenge_id, flag.points

    # Idempotent — don't error if already solved, just inform
    existing = PlayerSolve.query.filter_by(player_id=player_id, challenge_id=challenge_id).first()
    if existing:
        return jsonify({
            "correct": True,
            "already_solved": True,
            "challenge_id": challenge_id,
            "points": 0,
            "message": "Wyzwanie już było rozwiązane!",
        }), 200

    solve = PlayerSolve(player_id=player_id, challenge_id=challenge_id, points=points)
    db.session.add(solve)
    db.session.commit()

    return jsonify({
        "correct": True,
        "already_solved": False,
        "challenge_id": challenge_id,
        "points": points,
        "message": f"Poprawna flaga! +{points} punktów",
    }), 200


@ctf_flags_bp.route("/progress", methods=["GET"])
@ctf_jwt_required
def get_progress() -> Any:
    player_id = get_ctf_player_id()
    solves = PlayerSolve.query.filter_by(player_id=player_id).all()
    return jsonify({
        "solved": [
            {
                "challenge_id": s.challenge_id,
                "points": s.points,
                "solved_at": s.solved_at.isoformat(),
            }
            for s in solves
        ]
    }), 200
