# A19 - Source Maps Leak

## Metadane
- **ID:** A19
- **Kategoria:** OWASP A02:2025 - Security Misconfiguration
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{S0urc3_M4ps_L34k}`

## Opis
Frontend jest budowany z publicznie dostępnymi source maps. Dzięki temu
z przeglądarki można odtworzyć oryginalny kod źródłowy i znaleźć w nim
ukryty komentarz z flagą.

## Podatny endpoint
`Frontend (F12 -> Sources)`

## Exploit
1. Otwórz aplikację na `http://localhost:3000`
2. Wejdź w `DevTools`
3. Otwórz zakładkę `Sources`
4. Przeszukaj oryginalne pliki frontendu albo załaduj mapę źródeł z `assets/*.map`
5. Znajdź komentarz zawierający `PWR{S0urc3_M4ps_L34k}`

## Jak to naprawić
- Wyłącz source maps w buildzie produkcyjnym
- Zablokuj publiczne serwowanie plików `.map`
- Nigdy nie umieszczaj sekretów ani flag w komentarzach w kodzie
