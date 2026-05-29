import React, { useState } from "react";
import PropTypes from "prop-types";
import ctfClient from "../api/ctfClient.js";

export default function FlagChecker({ challengeId, onSuccess }) {
  const [flag, setFlag] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!flag.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await ctfClient.post("/flags/check", { flag: flag.trim() });
      const { correct, message, points, already_solved } = res.data;
      setResult({ success: correct, message, points });
      if (correct && !already_solved && onSuccess) onSuccess(res.data);
    } catch (err) {
      const data = err.response?.data;
      const message = data?.error || data?.message || err.message || "Błąd połączenia";
      setResult({ success: false, message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-center mt-2">
      <input
        type="text"
        value={flag}
        onChange={(e) => setFlag(e.target.value)}
        placeholder="PWR{...}"
        className="flex-1 bg-ctf-bg border border-ctf-border rounded-md px-3 py-2 text-sm text-ctf-text placeholder-ctf-muted focus:outline-none focus:border-ctf-accent font-mono"
      />
      <button
        type="submit"
        disabled={loading}
        className="bg-ctf-accent hover:bg-ctf-accent-hover text-white text-sm px-4 py-2 rounded-md transition-colors disabled:opacity-50"
      >
        {loading ? "..." : "Sprawdź"}
      </button>
      {result && (
        <span
          className={`text-sm font-medium ${
            result.success ? "text-bank-success" : "text-ctf-danger"
          }`}
        >
          {result.success ? `✓ ${result.message}` : `✗ ${result.message}`}
        </span>
      )}
    </form>
  );
}

FlagChecker.propTypes = {
  challengeId: PropTypes.string,
  onSuccess: PropTypes.func,
};
