import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext.jsx";
import { CTFAuthProvider } from "./context/CTFAuthContext.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import ProtectedCTFRoute from "./components/ProtectedCTFRoute.jsx";
import Navbar from "./components/Navbar.jsx";
import CTFNavbar from "./components/CTFNavbar.jsx";

import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Transfer from "./pages/Transfer.jsx";
import History from "./pages/History.jsx";
import Profile from "./pages/Profile.jsx";
import Admin from "./pages/Admin.jsx";

import CTFLogin from "./pages/ctf/CTFLogin.jsx";
import CTFRegister from "./pages/ctf/CTFRegister.jsx";
import CTFDashboard from "./pages/ctf/CTFDashboard.jsx";
import CTFScoreboard from "./pages/ctf/CTFScoreboard.jsx";

function BankLayout({ children }) {
  return (
    <div className="min-h-screen bg-bank-bg text-bank-text">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
    </div>
  );
}

function CTFLayout({ children }) {
  return (
    <div className="min-h-screen bg-ctf-bg text-ctf-text">
      <CTFNavbar />
      <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <CTFAuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Bank routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <BankLayout><Dashboard /></BankLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/transfer"
              element={
                <ProtectedRoute>
                  <BankLayout><Transfer /></BankLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <BankLayout><History /></BankLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <BankLayout><Profile /></BankLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute adminOnly>
                  <BankLayout><Admin /></BankLayout>
                </ProtectedRoute>
              }
            />
            {/* Stary link do wyzwań → przekierowanie do portalu CTF */}
            <Route path="/challenges" element={<Navigate to="/ctf" replace />} />

            {/* CTF Portal routes */}
            <Route path="/ctf/login" element={<CTFLogin />} />
            <Route path="/ctf/register" element={<CTFRegister />} />
            <Route
              path="/ctf"
              element={
                <ProtectedCTFRoute>
                  <CTFLayout><CTFDashboard /></CTFLayout>
                </ProtectedCTFRoute>
              }
            />
            <Route
              path="/ctf/scoreboard"
              element={
                <ProtectedCTFRoute>
                  <CTFLayout><CTFScoreboard /></CTFLayout>
                </ProtectedCTFRoute>
              }
            />

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </CTFAuthProvider>
    </AuthProvider>
  );
}
