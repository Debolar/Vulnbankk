# A20 - Race Condition Double Spend

## Metadane
- **ID:** A20
- **Kategoria:** CWE-362 - Concurrent Execution using Shared Resource with Improper Synchronization
- **Trudnosc:** hard
- **Punkty:** 200
- **Flaga:** `PWR{race_condition_double_spend}`

## Opis
Specjalny endpoint przelewu dla wyzwania A20 wykonuje operacje w zlej kolejnosci:
najpierw sprawdza saldo Boba, potem czeka przez krotki czas, a dopiero na koncu
odejmuje srodki z konta.

Jesli dwa requesty zostana wyslane rownolegle, oba moga zobaczyc to samo stare
saldo i oba przejda walidacje. Nastepnie kazdy z nich odejmie kwote od aktualnego
salda w bazie. To klasyczny wariant double spend.

## Podatny endpoint
POST /api/challenges/a20/transfer-race

## Warunki
- Zaloguj sie do banku jako `bob@vulnbank.pl` / `password123`
- Wyslij przelew do Alice: `PL00100100100100100100100100`
- Doprowadz saldo Boba ponizej `0`

## Exploit krok po kroku
### Krok 1: Zaloguj sie jako Bob i pobierz token JWT
`curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"bob@vulnbank.pl\",\"password\":\"password123\"}"`

### Krok 2: Sprawdz stan challenge
`curl -H "Authorization: Bearer TWOJ_TOKEN" http://localhost:5000/api/challenges/a20/status`

Domyslnie Bob ma `2891.75 PLN`, wiec pojedynczy przelew `1500 PLN` przechodzi,
ale dwa takie przelewy lacznie powinny przekroczyc saldo.

### Krok 3: Wyslij dwa requesty rownolegle
Uzyj dwoch watkow, dwoch terminali, Burp Turbo Intruder albo `xargs -P 2`.

### Krok 4: Odczytaj flage
Request, ktory jako drugi wykona odjecie salda, zwroci flage w polu `flag`.

## Opcjonalny reset labu
Jesli wyzwanie bylo juz rozwiazane i saldo Boba jest ujemne, mozesz zresetowac
stan Boba tylko dla tego labu:

`curl -X POST http://localhost:5000/api/challenges/a20/reset -H "Authorization: Bearer TWOJ_TOKEN" -H "Content-Type: application/json" -d "{\"confirm\":\"RESET_A20\"}"`

## Jak to naprawic
- Wykonuj sprawdzenie salda i aktualizacje w jednej transakcji.
- Zablokuj wiersz konta, np. `SELECT ... FOR UPDATE`.
- Alternatywnie uzyj atomowego warunku w `UPDATE`, np. `WHERE balance >= :amount`.
- Nie rozdzielaj walidacji i zapisu opoznieniami ani osobnymi transakcjami.

## Referencje
- https://cwe.mitre.org/data/definitions/362.html
- https://portswigger.net/web-security/race-conditions
