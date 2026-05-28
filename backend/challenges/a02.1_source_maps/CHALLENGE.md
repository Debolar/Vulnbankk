# A02 — Source Maps Leak

## Metadane
- **ID:** A02-2
- **Kategoria:** OWASP A05:2021 - Security Misconfiguration
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** PWR{S0urc3_M4ps_L34k}

## Opis
Proces budowania aplikacji frontendowej (Vite/React) został błędnie skonfigurowany, z włączonym generowaniem plików map źródłowych (Source Maps) na środowisku produkcyjnym. Pozwala to na pełne odtworzenie oryginalnego, niezminifikowanego kodu źródłowego w przeglądarce, w którym deweloper pozostawił wrażliwy komentarz z awaryjną flagą dostępową.

## Podatny endpoint
```HTTP
GET /assets/index-[hash].js.map
# Pliki mapowania źródeł są serwowane publicznie i podpinane pod główne skrypty aplikacji
```

## Exploit
Rozwiązanie manualne w przeglądarce:
- Otwórz stronę aplikacji.
- Wciśnij F12, aby otworzyć Narzędzia deweloperskie.
- Przejdź do zakładki Sources (Źródła).
- Rozwiń drzewo plików (np. src/App.jsx).
- Przeczytaj oryginalny kod i znajdź komentarz z flagą.

Rozwiązanie CLI (zakładając, że sprawdziliśmy nazwę pliku z w zakładce Network/Inspektorze):
```bash
curl -s http://localhost:5173/assets/index-jakishash123.js.map | grep "PWR{"
Wyjście (zrekonstruowany kod źródłowy) będzie zawierać:
```

```JavaScript
// TODO: [Ważne] Usunąć przed wdrożeniem na produkcję!
// Awaryjna flaga dostępowa dla testerów QA omijająca SSO w panelu Admina:
// PWR{S0urc3_M4ps_L34k}
```

## Jak to naprawić
- W pliku vite.config.js ustaw generowanie map źródeł na wyłączone (sourcemap: false) dla środowiska produkcyjnego.
- Skonfiguruj serwer WWW (np. Nginx), aby domyślnie blokował żądania do plików z rozszerzeniem *.map na produkcji.
- Nigdy nie przechowuj sekretów, haseł ani tokenów w komentarzach w kodzie źródłowym — minifikacja/obfuskacja kodu nie jest metodą zabezpieczania danych (Security through obscurity).