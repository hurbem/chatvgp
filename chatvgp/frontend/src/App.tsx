import React, { useState } from "react";
import { ChatPage } from "./pages/ChatPage";
import { AdminPage } from "./pages/AdminPage";
import IndicarProfissional from "./pages/IndicarProfissional";

function App() {
  const [isAdmin, setIsAdmin] = useState(!!localStorage.getItem("token"));
  const [currentPage, setCurrentPage] = useState<"chat" | "indicar" | "admin">("chat");
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [loginData, setLoginData] = useState({ token: "" });
  const [version, setVersion] = useState(() => {
    const saved = localStorage.getItem("appVersion");
    return saved ? parseInt(saved) : 1;
  });

  const incrementVersion = () => {
    const newVersion = version + 1;
    setVersion(newVersion);
    localStorage.setItem("appVersion", newVersion.toString());
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (loginData.token.trim()) {
      localStorage.setItem("token", loginData.token);
      setIsAdmin(true);
      setCurrentPage("admin");
      setShowLoginForm(false);
      setLoginData({ token: "" });
      incrementVersion();
    }
  };

  if (isAdmin) {
    return <AdminPage />;
  }

  return (
    <>
      {currentPage === "chat" && <ChatPage />}
      {currentPage === "indicar" && <IndicarProfissional />}

      {/* Navigation Buttons */}
      <div style={{
        position: "fixed",
        bottom: "24px",
        right: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        zIndex: 1000
      }}>
        {currentPage !== "chat" && (
          <button
            onClick={() => {
              setCurrentPage("chat");
              incrementVersion();
            }}
            style={{
              padding: "10px 16px",
              backgroundColor: "#2563eb",
              color: "white",
              border: "none",
              borderRadius: "9999px",
              fontWeight: "500",
              cursor: "pointer",
              boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
            }}
          >
            💬 Chat
          </button>
        )}
        {currentPage !== "indicar" && (
          <button
            onClick={() => {
              setCurrentPage("indicar");
              incrementVersion();
            }}
            style={{
              padding: "10px 16px",
              backgroundColor: "#16a34a",
              color: "white",
              border: "none",
              borderRadius: "9999px",
              fontWeight: "500",
              cursor: "pointer",
              boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
            }}
          >
            ⭐ Indicar
          </button>
        )}
        {!showLoginForm && (
          <button
            onClick={() => setShowLoginForm(true)}
            style={{
              padding: "10px 16px",
              backgroundColor: "#1f2937",
              color: "white",
              border: "none",
              borderRadius: "9999px",
              fontWeight: "500",
              cursor: "pointer",
              boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
            }}
          >
            🔐 Admin
          </button>
        )}

        {/* Version Display */}
        <div
          onClick={incrementVersion}
          style={{
            padding: "6px 12px",
            backgroundColor: "#6b7280",
            color: "white",
            borderRadius: "9999px",
            fontSize: "12px",
            fontWeight: "500",
            textAlign: "center",
            cursor: "pointer",
            userSelect: "none",
            marginTop: "8px"
          }}
          title="Clique para incrementar versão"
        >
          v{version}
        </div>
      </div>

      {/* Login Modal */}
      {showLoginForm && (
        <div style={{
          position: "fixed",
          inset: 0,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 2000
        }}>
          <div style={{
            backgroundColor: "white",
            borderRadius: "8px",
            boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
            padding: "24px",
            maxWidth: "448px"
          }}>
            <h2 style={{ fontSize: "18px", fontWeight: "bold", marginBottom: "16px" }}>Login Admin</h2>
            <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div>
                <label style={{ display: "block", fontSize: "14px", fontWeight: "500", marginBottom: "4px" }}>Token</label>
                <input
                  type="password"
                  value={loginData.token}
                  onChange={(e) => setLoginData({ token: e.target.value })}
                  placeholder="Cole seu token aqui"
                  style={{
                    width: "100%",
                    padding: "8px 16px",
                    border: "1px solid #d1d5db",
                    borderRadius: "8px",
                    fontSize: "14px"
                  }}
                  autoFocus
                />
              </div>
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  type="submit"
                  style={{
                    flex: 1,
                    padding: "8px 16px",
                    backgroundColor: "#2563eb",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    fontWeight: "500",
                    cursor: "pointer"
                  }}
                >
                  Entrar
                </button>
                <button
                  type="button"
                  onClick={() => setShowLoginForm(false)}
                  style={{
                    flex: 1,
                    padding: "8px 16px",
                    backgroundColor: "#e5e7eb",
                    color: "#374151",
                    border: "none",
                    borderRadius: "8px",
                    fontWeight: "500",
                    cursor: "pointer"
                  }}
                >
                  Cancelar
                </button>
              </div>
            </form>
            <p style={{ fontSize: "12px", color: "#6b7280", marginTop: "16px", textAlign: "center" }}>
              Para MVP, use qualquer token não-vazio (ex: "admin-token")
            </p>
          </div>
        </div>
      )}
    </>
  );
}

export default App;
