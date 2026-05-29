# Challenge Template

## Metadane
- **ID:** AXX
- **Kategoria:** OWASP AXX:2025 - Nazwa Kategorii
- **Trudność:** easy / medium / hard
- **Punkty:** 100 / 150 / 200
- **Flaga:** `PWR{twoja_flaga_tutaj}`

## Opis
Krótki opis podatności wplecionej w funkcję bankową.

## Podatny endpoint
```
METODA /api/ścieżka/do/endpointu
```

## Hint
Wskazówka dla uczestnika bez spoilera.

## Submit flagi
Flagi submituje się przez **portal CTF** (`/ctf`), nie przez bank:
```bash
curl -X POST http://localhost:5000/api/ctf/flags/check \
  -H "Authorization: Bearer $CTF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"PWR{twoja_flaga_tutaj}"}'
```

## Jak to naprawić
Krótki opis jak wyeliminować podatność.

## Referencje
- OWASP AXX:2025
- [CWE-XXX](https://cwe.mitre.org/data/definitions/XXX.html)
