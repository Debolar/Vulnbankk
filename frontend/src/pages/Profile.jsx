import React, { useState, useEffect } from "react";
import apiClient from "../api/client.js";

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [passwordForm, setPasswordForm] = useState({ old_password: "", new_password: "" });
  const [resetForm, setResetForm] = useState({ email: "", pesel: "", new_password: "" });
  const [msg, setMsg] = useState({ type: "", text: "" });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get("/profile/").then((res) => {
      setProfile(res.data);
      setLoading(false);
    });
  }, []);

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setMsg({ type: "", text: "" });
    try {
      await apiClient.post("/profile/change-password", passwordForm);
      setMsg({ type: "success", text: "Hasło zostało zmienione" });
      setPasswordForm({ old_password: "", new_password: "" });
    } catch (err) {
      setMsg({ type: "error", text: err.response?.data?.error || "Błąd" });
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setMsg({ type: "", text: "" });
    try {
      const res = await apiClient.post("/auth/forgot-password", resetForm);
      const flagText = res.data?.flag ? ` Flaga: ${res.data.flag}` : "";
      setMsg({ type: "success", text: `Hasło zmienione przez reset (VULN A06).${flagText}` });
      setResetForm({ email: "", pesel: "", new_password: "" });
    } catch (err) {
      setMsg({ type: "error", text: err.response?.data?.error || "Błąd" });
    }
  };

  if (loading) return <div className="text-bank-muted text-center py-12">Ładowanie...</div>;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-bank-text">Profil użytkownika</h1>

      <div className="bg-bank-card border border-bank-border rounded-xl p-6">
        <h2 className="text-bank-text font-semibold mb-4">Dane osobowe</h2>
        <div className="grid grid-cols-2 gap-4">
          {[
            ["Imię", profile?.first_name],
            ["Nazwisko", profile?.last_name],
            ["Email", profile?.email],
            ["PESEL", profile?.pesel],
          ].map(([label, value]) => (
            <div key={label}>
              <p className="text-bank-muted text-xs mb-1">{label}</p>
              <p className="text-bank-text font-medium font-mono">{value}</p>
            </div>
          ))}
        </div>
        {profile?.account && (
          <div className="mt-4 pt-4 border-t border-bank-border">
            <p className="text-bank-muted text-xs mb-1">IBAN</p>
            <p className="text-bank-text font-mono">{profile.account.iban}</p>
          </div>
        )}
        {profile?.flag && (
          <div className="mt-4 pt-4 border-t border-bank-border bg-yellow-900/20 rounded-md p-3">
            <p className="text-bank-warning text-xs font-medium">CTF Flag</p>
            <p className="text-bank-text font-mono text-sm mt-1">{profile.flag}</p>
          </div>
        )}
      </div>

      {msg.text && (
        <div className={`border rounded-md px-4 py-3 text-sm ${
          msg.type === "success"
            ? "bg-green-900/30 border-bank-success text-bank-success"
            : "bg-red-900/30 border-bank-danger text-bank-danger"
        }`}>
          {msg.text}
        </div>
      )}

      <div className="bg-bank-card border border-bank-border rounded-xl p-6">
        <h2 className="text-bank-text font-semibold mb-4">Zmiana hasła</h2>
        <form onSubmit={handleChangePassword} className="space-y-3">
          <div>
            <label className="block text-bank-muted text-sm mb-1">Obecne hasło</label>
            <input type="password" value={passwordForm.old_password}
              onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })}
              required className="w-full bg-bank-bg border border-bank-border rounded-md px-3 py-2.5 text-bank-text focus:outline-none focus:border-bank-accent"
              placeholder="••••••••" />
          </div>
          <div>
            <label className="block text-bank-muted text-sm mb-1">Nowe hasło</label>
            <input type="password" value={passwordForm.new_password}
              onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
              required className="w-full bg-bank-bg border border-bank-border rounded-md px-3 py-2.5 text-bank-text focus:outline-none focus:border-bank-accent"
              placeholder="••••••••" />
          </div>
          <button type="submit"
            className="bg-bank-accent hover:bg-bank-accent-hover text-white px-4 py-2 rounded-md transition-colors text-sm">
            Zmień hasło
          </button>
        </form>
      </div>

      <div className="bg-bank-card border border-bank-warning/40 rounded-xl p-6">
        <h2 className="text-bank-warning font-semibold mb-1">Reset hasła przez PESEL</h2>
        <p className="text-bank-muted text-xs mb-4">Funkcja awaryjnego resetu hasła — wymaga tylko PESELU</p>
        <form onSubmit={handleResetPassword} className="space-y-3">
          <div>
            <label className="block text-bank-muted text-sm mb-1">Email</label>
            <input type="email" value={resetForm.email}
              onChange={(e) => setResetForm({ ...resetForm, email: e.target.value })}
              required className="w-full bg-bank-bg border border-bank-border rounded-md px-3 py-2.5 text-bank-text focus:outline-none focus:border-bank-accent"
              placeholder="email@example.com" />
          </div>
          <div>
            <label className="block text-bank-muted text-sm mb-1">PESEL</label>
            <input type="text" value={resetForm.pesel}
              onChange={(e) => setResetForm({ ...resetForm, pesel: e.target.value })}
              required maxLength={11} className="w-full bg-bank-bg border border-bank-border rounded-md px-3 py-2.5 text-bank-text font-mono focus:outline-none focus:border-bank-accent"
              placeholder="00000000000" />
          </div>
          <div>
            <label className="block text-bank-muted text-sm mb-1">Nowe hasło</label>
            <input type="password" value={resetForm.new_password}
              onChange={(e) => setResetForm({ ...resetForm, new_password: e.target.value })}
              required className="w-full bg-bank-bg border border-bank-border rounded-md px-3 py-2.5 text-bank-text focus:outline-none focus:border-bank-accent"
              placeholder="••••••••" />
          </div>
          <button type="submit"
            className="bg-bank-warning hover:bg-yellow-600 text-white px-4 py-2 rounded-md transition-colors text-sm">
            Zresetuj hasło
          </button>
        </form>
      </div>
    </div>
  );
}
