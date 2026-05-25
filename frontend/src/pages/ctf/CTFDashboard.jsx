import React, { useState, useEffect } from "react";
import FlagChecker from "../../components/FlagChecker.jsx";
import ctfClient from "../../api/ctfClient.js";
import { useCTFAuth } from "../../context/CTFAuthContext.jsx";

const CHALLENGES = [
  {
    id: "A01", name: "Broken Access Control (IDOR)", category: "OWASP A01:2021",
    difficulty: "easy", points: 100,
    hint: "Sprawdź endpoint /api/accounts/<id>. Czy możesz zobaczyć konta innych użytkowników?",
    endpoint: "GET /api/accounts/1",
  },
  {
    id: "A02", name: "Security Misconfiguration", category: "OWASP A02:2021",
    difficulty: "easy", points: 100,
    hint: "Poszukaj zapomnianego endpointu debug w /api/debug/.",
    endpoint: "GET /api/debug/config",
  },
  {
    id: "A02.1", name: "Source Maps Leak", category: "OWASP A02:2021",
    difficulty: "easy", points: 100,
    hint: "Zajrzyj do DevTools -> Sources i przeszukaj kod źródłowy",
    endpoint: "Frontend (F12 -> Sources)"
  },
  {
    id: "A03", name: "Supply Chain Failures", category: "OWASP A03:2021",
    difficulty: "easy", points: 100,
    hint: "Sprawdź listę zależności: /api/debug/dependencies. Poszukaj pakietu z polem 'flag'.",
    endpoint: "GET /api/debug/dependencies",
  },
  {
    id: "A04", name: "Cryptographic Failures (MD5)", category: "OWASP A04:2021",
    difficulty: "medium", points: 150,
    hint: "Zdobądź dostęp admina (A08), pobierz /api/admin/backup, złam hash MD5 na crackstation.net.",
    endpoint: "GET /api/admin/backup",
  },
  {
    id: "A05", name: "SQL Injection", category: "OWASP A05:2021",
    difficulty: "medium", points: 150,
    hint: "Wyszukiwarka transakcji jest podatna. Wstrzyknij UNION SELECT do parametru ?q=",
    endpoint: "GET /api/transactions/search?q=",
  },
  {
    id: "A06", name: "Insecure Design", category: "OWASP A06:2021",
    difficulty: "easy", points: 100,
    hint: "Reset hasła wymaga tylko PESELU — brak tokenu emailowego. PESEL widoczny w profilu.",
    endpoint: "POST /api/auth/forgot-password",
  },
  {
    id: "A07", name: "Authentication Failures", category: "OWASP A07:2021",
    difficulty: "easy", points: 100,
    hint: "Brak rate limitingu na logowaniu. Użyj Burp Intruder lub curl na bob@vulnbank.pl.",
    endpoint: "POST /api/auth/login",
  },
  {
    id: "A08", name: "JWT None Algorithm", category: "OWASP A08:2021",
    difficulty: "medium", points: 150,
    hint: "Czy JWT sprawdza algorytm? Spróbuj zmienić alg na 'none' i is_admin na true.",
    endpoint: "GET /api/admin/dashboard",
  },
  {
    id: "A09", name: "Logging & Alerting Failures", category: "OWASP A09:2021",
    difficulty: "easy", points: 100,
    hint: "Endpoint logów nie wymaga autoryzacji. Sprawdź GET /api/admin/logs.",
    endpoint: "GET /api/admin/logs",
  },
  {
    id: "A10", name: "Exceptional Conditions", category: "OWASP A10:2021",
    difficulty: "easy", points: 100,
    hint: "Wyślij nieprawidłowy parametr do kalkulatora kredytu. Flask DEBUG ujawni stack trace.",
    endpoint: "GET /api/loans/calculate?amount=abc&rate=2",
  },
  {
    id: "A11", name: "Open Redirect", category: "OWASP A01:2021",
    difficulty: "easy",
    points: 100,
    hint: "Parametr next= nie jest walidowany - możesz przekierować na dowolny URL",
    endpoint: "GET /api/challenges/a11/redirect?next=",
  },
  {
  id: "A12",
  name: "SSRF - falsyfikacja zapytania po stronie serwera",
  category: "OWASP A10:2021",
  difficulty: "medium",
  points: 150,
  hint: "Parametr url= nie jest walidowany - serwer wykona request do dowolnego adresu",
  endpoint: "GET /api/challenges/a12/fetch?url=",
  },
  {
  id: "A13",
  name: "Command Injection - zdalne wykonanie kodu",
  category: "OWASP A03:2021",
  difficulty: "hard",
  points: 200,
  hint: "Parametr host= trafia bezposrednio do polecenia ping - uzyj ; lub && zeby dołaczyc komende",
  endpoint: "GET /api/challenges/a13/ping?host=",
  },
  {
  id: "A14",
  name: "Mass Assignment - eskalacja uprawnien",
  category: "OWASP A01:2021",
  difficulty: "medium",
  points: 150,
  hint: "Wyslij PATCH z polem is_admin: true do /api/challenges/a14/profile/update",
  endpoint: "PATCH /api/challenges/a14/profile/update",
  },
  {
  id: "A15",
  name: "Path Traversal - odczyt plikow poza katalogiem",
  category: "OWASP A01:2021",
  difficulty: "medium",
  points: 150,
  hint: "Parametr name= nie jest sanityzowany - sprobuj ../secret/flag.txt",
  endpoint: "GET /api/challenges/a15/report?name=",
  },
  {
  id: "A16",
  name: "Insecure Deserialization - pickle RCE",
  category: "OWASP A08:2021",
  difficulty: "hard",
  points: 200,
  hint: "Zaloguj sie jako bob@vulnbank.pl / password123. Serwer robi pickle.loads() na Twoich danych - stworz obiekt z __reduce__ i zakoduj base64",
  endpoint: "POST /api/challenges/a16/preferences",
  },
];

const DIFFICULTY_BADGE = {
  easy: "bg-green-900/40 text-ctf-accent border border-green-700/40",
  medium: "bg-yellow-900/40 text-ctf-warning border border-yellow-700/40",
  hard: "bg-red-900/40 text-ctf-danger border border-red-700/40",
};

export default function CTFDashboard() {
  const { player } = useCTFAuth();
  const [solved, setSolved] = useState({});
  const [expanded, setExpanded] = useState(null);
  const [loadingProgress, setLoadingProgress] = useState(true);

  useEffect(() => {
    ctfClient.get("/flags/progress")
      .then((res) => {
        const map = {};
        res.data.solved.forEach((s) => { map[s.challenge_id] = s; });
        setSolved(map);
      })
      .catch(() => {})
      .finally(() => setLoadingProgress(false));
  }, []);

  const totalPoints = Object.values(solved).reduce((sum, s) => sum + s.points, 0);
  const maxPoints = CHALLENGES.reduce((sum, c) => sum + c.points, 0);

  const handleFlagSuccess = (data) => {
    if (!data.already_solved) {
      setSolved((prev) => ({
        ...prev,
        [data.challenge_id]: { points: data.points, solved_at: new Date().toISOString() },
      }));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-ctf-text font-mono">
            Wyzwania CTF
          </h1>
          <p className="text-ctf-muted text-sm mt-1">
            OWASP Top 10 — zaloguj się do{" "}
            <a href="/login" target="_blank" rel="noopener noreferrer"
               className="text-ctf-accent hover:underline">
              VulnBank ↗
            </a>
            {" "}i atakuj!
          </p>
        </div>

        <div className="flex items-center gap-4">
          <a
            href="/login"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-ctf-border hover:bg-ctf-accent/20 border border-ctf-border hover:border-ctf-accent text-ctf-muted hover:text-ctf-accent px-4 py-2.5 rounded-xl transition-colors text-sm font-medium"
          >
            <span>🏦</span>
            <span>Uruchom VulnBank</span>
            <span className="text-xs opacity-60">↗</span>
          </a>
          <div className="bg-ctf-card border border-ctf-border rounded-xl px-6 py-4 text-center">
            <p className="text-ctf-muted text-xs">{player?.nickname}</p>
            <p className="text-3xl font-bold text-ctf-accent font-mono">
              {loadingProgress ? "—" : totalPoints}
            </p>
            <p className="text-ctf-muted text-xs">/ {maxPoints} pkt</p>
          </div>
        </div>
      </div>

      <div className="bg-ctf-card border border-ctf-border rounded-full h-3 overflow-hidden">
        <div
          className="bg-ctf-accent h-full transition-all duration-500"
          style={{ width: `${maxPoints > 0 ? (totalPoints / maxPoints) * 100 : 0}%` }}
        />
      </div>

      <div className="space-y-3">
        {CHALLENGES.map((c) => {
          const isSolved = !!solved[c.id];
          const isOpen = expanded === c.id;
          return (
            <div
              key={c.id}
              className={`bg-ctf-card border rounded-xl transition-colors ${
                isSolved ? "border-ctf-accent/40" : "border-ctf-border"
              }`}
            >
              <button
                onClick={() => setExpanded(isOpen ? null : c.id)}
                className="w-full text-left px-5 py-4 flex items-center gap-4"
              >
                <span className={`text-xl ${isSolved ? "" : "grayscale opacity-50"}`}>
                  {isSolved ? "✅" : "🔒"}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-ctf-muted text-xs font-mono font-bold">{c.id}</span>
                    <span className="text-ctf-text font-medium text-sm">{c.name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${DIFFICULTY_BADGE[c.difficulty]}`}>
                      {c.difficulty}
                    </span>
                  </div>
                  <p className="text-ctf-muted text-xs mt-0.5">{c.category}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className={`font-bold text-sm font-mono ${isSolved ? "text-ctf-accent" : "text-ctf-muted"}`}>
                    {isSolved ? `+${c.points}` : `${c.points} pkt`}
                  </p>
                  <p className="text-ctf-muted text-xs">{isOpen ? "▲" : "▼"}</p>
                </div>
              </button>

              {isOpen && (
                <div className="px-5 pb-5 border-t border-ctf-border/50 pt-4 space-y-3">
                  <div>
                    <p className="text-ctf-muted text-xs font-medium mb-1">Podatny endpoint</p>
                    <code className="bg-ctf-bg px-3 py-1.5 rounded text-ctf-accent text-xs font-mono block border border-ctf-border">
                      {c.endpoint}
                    </code>
                  </div>
                  <div>
                    <p className="text-ctf-muted text-xs font-medium mb-1">Wskazówka</p>
                    <p className="text-ctf-text text-sm">{c.hint}</p>
                  </div>
                  <div>
                    <p className="text-ctf-muted text-xs font-medium mb-1">
                      {isSolved ? "Flaga znaleziona!" : "Wprowadź flagę"}
                    </p>
                    {isSolved ? (
                      <p className="text-ctf-accent text-sm font-mono">✓ Wyzwanie ukończone</p>
                    ) : (
                      <FlagChecker challengeId={c.id} onSuccess={handleFlagSuccess} />
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
