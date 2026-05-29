import React, { useState, useEffect } from "react";
import ctfClient from "../../api/ctfClient.js";
import { useCTFAuth } from "../../context/CTFAuthContext.jsx";

const MEDALS = ["🥇", "🥈", "🥉"];

export default function CTFScoreboard() {
  const { player } = useCTFAuth();
  const [challengeMeta, setChallengeMeta] = useState([]);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      ctfClient.get("/flags/"),
      ctfClient.get("/scoreboard/"),
    ])
      .then(([flagsRes, scoreRes]) => {
        setChallengeMeta(flagsRes.data);
        setRows(scoreRes.data);
      })
      .catch(() => setError("Nie udało się załadować scoreboard"))
      .finally(() => setLoading(false));
  }, []);

  const maxPoints = challengeMeta.reduce((sum, challenge) => sum + challenge.points, 0);
  const challengeCount = challengeMeta.length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ctf-text font-mono">Scoreboard</h1>
        <p className="text-ctf-muted text-sm mt-1">
          Ranking graczy — max {loading ? "…" : maxPoints} pkt
        </p>
      </div>

      {loading && (
        <div className="text-ctf-muted text-center py-12">Ładowanie...</div>
      )}

      {error && (
        <div className="bg-red-900/30 border border-ctf-danger text-ctf-danger rounded-xl px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {!loading && !error && rows.length === 0 && (
        <div className="bg-ctf-card border border-ctf-border rounded-xl p-12 text-center">
          <p className="text-4xl mb-3">🏴</p>
          <p className="text-ctf-muted">Brak graczy. Bądź pierwszy!</p>
        </div>
      )}

      {!loading && rows.length > 0 && (
        <div className="bg-ctf-card border border-ctf-border rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-ctf-border text-ctf-muted text-xs uppercase tracking-wide">
                <th className="px-5 py-3 text-left w-12">#</th>
                <th className="px-5 py-3 text-left">Gracz</th>
                <th className="px-5 py-3 text-right">Wyzwania</th>
                <th className="px-5 py-3 text-right">Punkty</th>
                <th className="px-5 py-3 text-right hidden md:table-cell">Postęp</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const isMe = row.nickname === player?.nickname;
                return (
                  <tr
                    key={row.rank}
                    className={`border-b border-ctf-border/50 last:border-0 transition-colors ${
                      isMe ? "bg-ctf-accent/10" : "hover:bg-ctf-bg/50"
                    }`}
                  >
                    <td className="px-5 py-4 text-center">
                      {row.rank <= 3
                        ? <span className="text-lg">{MEDALS[row.rank - 1]}</span>
                        : <span className="text-ctf-muted text-sm font-mono">{row.rank}</span>
                      }
                    </td>
                    <td className="px-5 py-4">
                      <span className={`font-mono font-medium ${isMe ? "text-ctf-accent" : "text-ctf-text"}`}>
                        {row.nickname}
                      </span>
                      {isMe && (
                        <span className="ml-2 text-xs text-ctf-muted">(ty)</span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-right text-ctf-muted text-sm font-mono">
                      {row.solved_count}/{challengeCount || "?"}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <span className={`font-bold font-mono text-lg ${row.total_points > 0 ? "text-ctf-accent" : "text-ctf-muted"}`}>
                        {row.total_points}
                      </span>
                    </td>
                    <td className="px-5 py-4 hidden md:table-cell">
                      <div className="flex items-center gap-2 justify-end">
                        <div className="w-24 bg-ctf-bg rounded-full h-1.5 border border-ctf-border">
                          <div
                            className="bg-ctf-accent h-full rounded-full transition-all"
                            style={{ width: `${maxPoints > 0 ? (row.total_points / maxPoints) * 100 : 0}%` }}
                          />
                        </div>
                        <span className="text-ctf-muted text-xs font-mono w-10 text-right">
                          {Math.round(maxPoints > 0 ? (row.total_points / maxPoints) * 100 : 0)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
