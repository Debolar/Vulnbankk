# Jak dodać nową podatność do VulnBank

Każda podatność to osobny Flask Blueprint w `backend/challenges/`.
Auto-discovery rejestruje go automatycznie — **nie modyfikujesz kodu core**.

---

## Architektura — dwa niezależne systemy

```
backend/core/        ← logika bankowa (cele ataków)
backend/ctf/         ← portal CTF (auth gracza, submit flag, scoreboard)
backend/challenges/  ← podatności jako osobne blueprinty (tutaj dodajesz)
```

Flaga zdobyta przez atak na `backend/challenges/` jest submitowana przez portal CTF (`POST /api/ctf/flags/check`).

---

## Krok 1: Utwórz folder wyzwania

```bash
mkdir backend/challenges/a11_twoja_nazwa
```

Konwencja nazewnictwa: `aXX_krótka_nazwa_podatności` (małe litery, podkreślniki, bez kropek w nazwie folderu).

---

## Krok 2: `__init__.py`

```python
# backend/challenges/a11_twoja_nazwa/__init__.py
from .routes import blueprint

__all__ = ["blueprint"]
```

---

## Krok 3: `routes.py` — blueprint z podatnością

```python
# Challenge: A11 - Twoja Podatność
# Difficulty: easy/medium/hard
# Flag: PWR{twoja_flaga}
# Tools: curl / Burp Suite
# Author: Twoje Imię

from typing import Any
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

blueprint = Blueprint("challenge_a11", __name__, url_prefix="/api/challenges/a11")


@blueprint.route("/", methods=["GET"])
def challenge_info() -> Any:
    return jsonify({
        "challenge": "A11",
        "name": "Twoja Podatność",
        "category": "OWASP AXX:2025",
        "difficulty": "easy",
        "points": 100,
        "description": "Opis podatności",
        "hint": "Wskazówka bez spoilerów",
        "endpoint": "GET /api/challenges/a11/vulnerable",
    }), 200


# VULN: A11 — podatny endpoint wpleciony w logikę bankową
@blueprint.route("/vulnerable", methods=["GET"])
@jwt_required()
def vulnerable_endpoint() -> Any:
    user_id = int(get_jwt_identity())
    # ... podatna logika ...
    return jsonify({"flag": "PWR{twoja_flaga}"}), 200
```

**Zasady:**
- Nazwa Blueprint musi być unikalna (`challenge_a11`)
- `url_prefix` musi być unikalny
- Komentarz `# VULN: AXX` w miejscu podatności
- Uwierzytelnienie przez **bank JWT** (`@jwt_required()`) — to jest podatny endpoint, nie portal CTF

---

## Krok 4: `CHALLENGE.md`

```markdown
# A11 — Nazwa Podatności

## Metadane
- **ID:** A11
- **Kategoria:** OWASP AXX:2025
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{twoja_flaga}`

## Opis
Co jest podatne i dlaczego.

## Podatny endpoint
GET /api/challenges/a11/vulnerable

## Exploit krok po kroku
1. Krok pierwszy
2. Krok drugi

## Jak to naprawić
Opis poprawnej implementacji.

## Referencje
- Link do OWASP
```

---

## Krok 5: Dodaj flagę do bazy

Dodaj wpis w `db/seeds/flags.sql`:

```sql
INSERT INTO flags (challenge_id, flag_value, description, difficulty, points)
VALUES ('A11', 'PWR{twoja_flaga}', 'Opis podatności', 'easy', 100);
```

Flaga jest sprawdzana przez portal CTF (`POST /api/ctf/flags/check`) — nie przez bank.

---

## Krok 6: Dodaj do metadanych CTF

Zaktualizuj tablicę `CHALLENGE_META` w `backend/ctf/flags.py` oraz wpis w `db/seeds/flags.sql`.
Frontend portalu CTF pobiera listę wyzwań z `GET /api/ctf/flags/`, więc nie duplikuj ręcznie
tej samej listy w `frontend/src/pages/ctf/CTFDashboard.jsx` ani w `CTFScoreboard.jsx`.

Jeśli dodajesz zadanie zależne od source maps, pamiętaj też o zmianach w frontendzie:
- `frontend/vite.config.js` musi generować source maps w buildzie produkcyjnym
- `frontend/nginx.conf` nie może blokować plików `*.map`
- w jednym z bundlowanych plików frontendu musi istnieć komentarz z flagą, żeby challenge był rozwiązywalny

---

## Krok 7: Weryfikacja

```bash
# Sprawdź że blueprint się załadował
docker-compose logs backend | grep "Challenge loaded"

# Test endpointu podatności (bank JWT)
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@vulnbank.pl","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/challenges/a11/

# Test submit flagi (CTF JWT)
CTF_TOKEN=$(curl -s -X POST http://localhost:5000/api/ctf/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"gracz@example.com","password":"haslo123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{twoja_flaga}"}'
```

---

## Checklist przed PR

- [ ] Folder `challenges/aXX_nazwa/` z `__init__.py`, `routes.py`, `CHALLENGE.md`
- [ ] Unikalna nazwa Blueprint i `url_prefix`
- [ ] Komentarz `# VULN: AXX` w podatnym kodzie
- [ ] Nagłówek metadanych na górze `routes.py`
- [ ] Type hints w funkcjach Pythona
- [ ] Flaga w formacie `PWR{...}` w `db/seeds/flags.sql`
- [ ] Wpis w `CHALLENGE_META` w `backend/ctf/flags.py`
- [ ] Wpis w tabeli w `README.md`
- [ ] Jeśli challenge zależy od frontendu, sprawdź build produkcyjny i nginx
- [ ] Podatność wpleciona w funkcję bankową (nie osobna demo-strona)
- [ ] Zrestartuj Docker i przetestuj exploit ręcznie

---

## Konwencje

| Element | Konwencja |
|---------|-----------|
| Folder | `aXX_krótka_nazwa` (małe litery) |
| Blueprint name | `challenge_aXX` |
| URL prefix | `/api/challenges/aXX` |
| Source maps | `a19_source_maps` / `/api/challenges/a19` |
| Flaga | `PWR{słowa_opisujące_podatność}` |
| Trudność | `easy` (100 pkt) / `medium` (150 pkt) / `hard` (200 pkt) |

---

## Szablon Git commit

```
feat(challenges): add A11 - Nazwa Podatności [easy]

- Endpoint: GET /api/challenges/a11/vulnerable
- Flag: PWR{twoja_flaga}
- Tools: curl
```
