import React, { useState, useEffect } from "react";
import FlagChecker from "../../components/FlagChecker.jsx";
import ctfClient from "../../api/ctfClient.js";
import { useCTFAuth } from "../../context/CTFAuthContext.jsx";

const DIFFICULTY_BADGE = {
  easy: "bg-green-900/40 text-ctf-accent border border-green-700/40",
  medium: "bg-yellow-900/40 text-ctf-warning border border-yellow-700/40",
  hard: "bg-red-900/40 text-ctf-danger border border-red-700/40",
};

export default function CTFDashboard() {
  const { player } = useCTFAuth();
  const [challenges, setChallenges] = useState([]);
  const [solved, setSolved] = useState({});
  const [expanded, setExpanded] = useState(null);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    Promise.all([
      ctfClient.get("/flags/"),
      ctfClient.get("/flags/progress"),
    ])
      .then(([challengeRes, progressRes]) => {
        setChallenges(challengeRes.data);
        const map = {};
        progressRes.data.solved.forEach((s) => {
          map[s.challenge_id] = s;
        });
        setSolved(map);
      })
      .catch(() => {})
      .finally(() => setLoadingData(false));
  }, []);

  const totalPoints = Object.values(solved).reduce((sum, s) => sum + s.points, 0);
  const maxPoints = challenges.reduce((sum, c) => sum + c.points, 0);

  const bankAccounts = [
    { email: "alice@vulnbank.pl", password: "qwerty123" },
    { email: "bob@vulnbank.pl", password: "password123" },
  ];

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
              {loadingData ? "—" : totalPoints}
            </p>
            <p className="text-ctf-muted text-xs">/ {maxPoints} pkt</p>
          </div>
        </div>
      </div>

      <div className="bg-ctf-card border border-ctf-border rounded-xl p-4">
        <p className="text-ctf-muted text-xs font-medium uppercase tracking-wide mb-2">
          Konta bankowe do ataków
        </p>
        <div className="grid gap-2 md:grid-cols-2">
          {bankAccounts.map((account) => (
            <div key={account.email} className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-ctf-border/70 bg-ctf-bg px-3 py-2">
              <p className="text-ctf-text text-sm font-medium">{account.email}</p>
              <code className="text-ctf-accent text-xs font-mono">{account.password}</code>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-ctf-card border border-ctf-border rounded-full h-3 overflow-hidden">
        <div
          className="bg-ctf-accent h-full transition-all duration-500"
          style={{ width: `${maxPoints > 0 ? (totalPoints / maxPoints) * 100 : 0}%` }}
        />
      </div>

      <div className="space-y-3">
        {challenges.map((c) => {
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
