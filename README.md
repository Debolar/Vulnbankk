# VulnBank — PWr CTF Edition

> Celowo podatna aplikacja bankowa do nauki bezpieczeństwa web.  
> **TYLKO DO UŻYTKU LOKALNEGO**

---

## Szybki start

```bash
git clone <repo-url>
cd vulnbank
docker-compose up --build
```

Pierwsze uruchomienie trwa ~2 minuty (build + migracja bazy).

| Adres | Co to |
|-------|-------|
| **http://localhost:3000/ctf/register** | Zarejestruj się jako gracz CTF — zacznij tutaj |
| **http://localhost:3000/login** | VulnBank — podatna aplikacja bankowa (cel ataków) |

---

## Jak to działa — dwa osobne systemy

```
┌─────────────────────────┐        ┌──────────────────────────┐
│      CTF Portal         │        │       VulnBank           │
│  localhost:3000/ctf/*   │ ──────▶│  localhost:3000/*        │
│                         │  atak  │                          │
│  • Twoje konto gracza   │        │  • Konta alice/bob/admin │
│  • Lista wyzwań + hinty │        │  • Podatne endpointy API │
│  • Submit flag          │        │  • Cel wszystkich ataków │
│  • Scoreboard           │        │                          │
└─────────────────────────┘        └──────────────────────────┘
```

**Przepływ:**
1. Otwórz `/ctf/register` → utwórz konto gracza (nick + email + hasło)
2. Kliknij **"Uruchom VulnBank ↗"** → bank otwiera się w nowej karcie
3. Zaloguj się do banku jako alice/bob/admin i atakuj
4. Zdobytą flagę `PWR{...}` wklej w portalu CTF → wynik zapisuje się w scoreboard

---

## Mapa portów

| Port | Serwis | Opis |
|------|--------|------|
| 3000 | Frontend | React UI — bank i portal CTF (przez nginx) |
| 5000 | Backend | Flask API (bezpośredni dostęp do `/api/*`) |
| 6379 | Redis | Cache (bez hasła — podatność A02) |
| 5432 | PostgreSQL | Baza danych (wewnętrzna) |

---

## Konta bankowe (cele ataków)

| Email | Hasło | Uwagi |
|-------|-------|-------|
| alice@vulnbank.pl | qwerty123 | Ofiara IDOR i przejęcia konta |
| bob@vulnbank.pl | password123 | Cel brute-force (A07) |
| charlie@vulnbank.pl | charlie2024 | Hash MD5 do złamania (A04) |
| admin@vulnbank.pl | admin123 | Panel admina |

Konta bankowe są **osobne** od kont w portalu CTF. Gracz rejestruje się sam w `/ctf/register`.

---

## Wyzwania CTF (10 flag, 1150 punktów)

| ID | Nazwa | Trudność | Punkty |
|----|-------|----------|--------|
| A01 | Broken Access Control (IDOR) | 🟢 easy | 100 |
| A02 | Security Misconfiguration | 🟢 easy | 100 |
| A03 | Supply Chain Failures | 🟢 easy | 100 |
| A04 | Cryptographic Failures (MD5) | 🟡 medium | 150 |
| A05 | SQL Injection | 🟡 medium | 150 |
| A06 | Insecure Design | 🟢 easy | 100 |
| A07 | Authentication Failures | 🟢 easy | 100 |
| A08 | JWT None Algorithm | 🟡 medium | 150 |
| A09 | Logging & Alerting Failures | 🟢 easy | 100 |
| A10 | Exceptional Conditions | 🟢 easy | 100 |
| A11 | Open Redirect | 🟢 easy | 100 |
| A12 | Falsyfikacja zapytania po stronie serwera (SSRF) | 🟡 medium | 150 |
| A13 | Command Injection - zdalne wykonanie kodu | 🔴 hard | 200 |
| A14 | Mass Assignment - eskalacja uprawnień | 🟡 medium | 150 |
| A15 | Path Traversal - odczyt plikow poza katalogiem | 🟡 medium | 150 |
| A16 | Insecure Deserialization - pickle RCE | 🔴 hard | 200 |

Hinty i submit flag dostępne po zalogowaniu do portalu CTF (`/ctf`).

---

## API — endpointy CTF portalu

```
POST /api/ctf/auth/register   Rejestracja gracza
POST /api/ctf/auth/login      Logowanie gracza (zwraca CTF JWT)
GET  /api/ctf/auth/me         Dane zalogowanego gracza

GET  /api/ctf/flags/          Lista wyzwań (publiczna)
POST /api/ctf/flags/check     Submit flagi (wymaga CTF JWT)
GET  /api/ctf/flags/progress  Postęp gracza (wymaga CTF JWT)

GET  /api/ctf/scoreboard/     Ranking (wymaga CTF JWT)
```

> **CTF JWT ≠ bank JWT.** Token z `/api/ctf/auth/login` nie działa na bankowych endpointach i odwrotnie.

---

## Narzędzia potrzebne do wyzwań

- **Przeglądarka + DevTools** — większość wyzwań easy
- **curl** — testy API z wiersza poleceń
- **[Burp Suite Community](https://portswigger.net/burp/communitydownload)** — proxy do A05, A07, A08
- **[jwt.io](https://jwt.io)** — analiza i modyfikacja tokenów (A08)
- **[crackstation.net](https://crackstation.net)** — łamanie hashy MD5 (A04)

---

## Struktura projektu

```
vulnbank/
├── docker-compose.yml
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── ctf/          # Portal CTF (Login, Register, Dashboard, Scoreboard)
│       │   └── ...           # Strony bankowe (Dashboard, Transfer, ...)
│       ├── context/
│       │   ├── AuthContext.jsx     # Stan konta bankowego
│       │   └── CTFAuthContext.jsx  # Stan konta gracza CTF
│       └── api/
│           ├── client.js     # Axios dla banku (vulnbank_token)
│           └── ctfClient.js  # Axios dla CTF portalu (ctf_token)
└── backend/
    ├── core/          # Logika bankowa (auth, accounts, transactions...)
    ├── ctf/           # CTF portal (auth, flags, scoreboard)
    ├── models/
    │   ├── user.py, account.py, ...  # Modele bankowe
    │   ├── player.py                  # Gracz CTF (bcrypt, osobna tabela)
    │   └── player_solve.py            # Rozwiązane wyzwania gracza
    └── challenges/    # Blueprinty podatności (auto-discovery)
```

---

## Dodawanie własnych podatności

Zobacz [CONTRIBUTING.md](CONTRIBUTING.md) — krok po kroku jak dodać nowe wyzwanie.

---

## Rozwiązania

Pełne write-upy: [SOLUTIONS.md](SOLUTIONS.md)

---

## Ostrzeżenie bezpieczeństwa

```
⚠️  Ta aplikacja jest CELOWO PODATNA na ataki.
⚠️  Uruchamiaj TYLKO lokalnie w izolowanym środowisku Docker.
⚠️  NIE wystawiaj na publiczny internet.
⚠️  NIE używaj prawdziwych danych osobowych.
```

---

*VulnBank — projekt edukacyjny, Politechnika Wrocławska*
