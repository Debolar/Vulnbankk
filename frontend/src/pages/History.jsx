import React, { useState, useEffect } from "react";
import apiClient from "../api/client.js";

export default function History() {
  const [transactions, setTransactions] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [accountId, setAccountId] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [accRes, txRes] = await Promise.all([
          apiClient.get("/accounts/"),
          apiClient.get("/transactions/"),
        ]);
        if (accRes.data.length > 0) setAccountId(accRes.data[0].id);
        setTransactions(txRes.data);
      } catch {}
      setLoading(false);
    };
    fetchData();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    setSearching(true);
    try {
      // VULN: A05 — q parametr wysyłany bezpośrednio do podatnego backendu
      const res = await apiClient.get(`/transactions/search?q=${encodeURIComponent(searchQuery)}`);
      setTransactions(res.data);
    } catch {}
    setSearching(false);
  };

  const formatDate = (iso) => new Date(iso).toLocaleString("pl-PL");

  if (loading) return <div className="text-bank-muted text-center py-12">Ładowanie...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-bank-text">Historia transakcji</h1>
          <p className="text-bank-muted text-sm mt-1">Wszystkie Twoje przelewy</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Szukaj po tytule przelewu..."
          className="flex-1 bg-bank-card border border-bank-border rounded-md px-4 py-2.5 text-bank-text placeholder-bank-muted focus:outline-none focus:border-bank-accent"
        />
        <button type="submit" disabled={searching}
          className="bg-bank-accent hover:bg-bank-accent-hover text-white px-4 py-2.5 rounded-md transition-colors disabled:opacity-50">
          {searching ? "..." : "Szukaj"}
        </button>
      </form>

      <div className="bg-bank-card border border-bank-border rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-bank-border">
              <th className="text-left text-bank-muted text-sm font-medium px-4 py-3">Tytuł</th>
              <th className="text-left text-bank-muted text-sm font-medium px-4 py-3 hidden md:table-cell">Z konta</th>
              <th className="text-left text-bank-muted text-sm font-medium px-4 py-3 hidden md:table-cell">Na konto</th>
              <th className="text-right text-bank-muted text-sm font-medium px-4 py-3">Kwota</th>
              <th className="text-right text-bank-muted text-sm font-medium px-4 py-3 hidden sm:table-cell">Data</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center text-bank-muted py-8 text-sm">
                  Brak transakcji
                </td>
              </tr>
            ) : (
              transactions.map((tx) => {
                const isIncoming = tx.to_account_id === accountId;
                return (
                  <tr key={tx.id} className="border-b border-bank-border/50 hover:bg-bank-bg/30 transition-colors">
                    <td className="px-4 py-3 text-sm text-bank-text">{tx.title}</td>
                    <td className="px-4 py-3 text-xs text-bank-muted font-mono hidden md:table-cell">
                      {tx.from_iban || "—"}
                    </td>
                    <td className="px-4 py-3 text-xs text-bank-muted font-mono hidden md:table-cell">
                      {tx.to_iban || "—"}
                    </td>
                    <td className={`px-4 py-3 text-sm font-semibold text-right ${isIncoming ? "text-bank-success" : "text-bank-danger"}`}>
                      {isIncoming ? "+" : "-"}{tx.amount.toFixed(2)} PLN
                    </td>
                    <td className="px-4 py-3 text-xs text-bank-muted text-right hidden sm:table-cell">
                      {formatDate(tx.created_at)}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
