# A03 — Software Supply Chain Failures

## Metadane
- **ID:** A03
- **Kategoria:** OWASP A03:2025 - Software Supply Chain Failures
- **Trudność:** easy
- **Punkty:** 100
- **Flaga:** `PWR{vulnerable_dependency_found}`

## Opis
Aplikacja używa podatnej wersji biblioteki **PyYAML 5.3.1** (CVE-2020-14343).
Endpoint `/api/debug/dependencies` zwraca listę zainstalowanych pakietów.
Dla podatnej biblioteki odpowiedź zawiera pole `flag`.

## Exploit
```bash
curl http://localhost:5000/api/debug/dependencies \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data['packages']:
    if 'flag' in p:
        print(p)
"
```

Wynik:
```json
{
  "name": "PyYAML",
  "version": "5.3.1",
  "cve": "CVE-2020-14343",
  "severity": "CRITICAL",
  "flag": "PWR{vulnerable_dependency_found}"
}
```

## CVE-2020-14343
PyYAML 5.3.1 jest podatna na wykonanie dowolnego kodu przez `yaml.load()` bez parametru `Loader`.
Naprawiono w wersji 5.4 przez wymuszenie `yaml.safe_load()`.

## Jak to naprawić
1. Zaktualizuj `PyYAML` do wersji `>=6.0`
2. Zawsze używaj `yaml.safe_load()` zamiast `yaml.load()`
3. Regularnie skanuj zależności narzędziami: `safety check`, `pip-audit`, Dependabot

## Referencje
- [CVE-2020-14343](https://nvd.nist.gov/vuln/detail/CVE-2020-14343)
- OWASP A03:2025 - Software Supply Chain Failures
