import React, { useState } from "react";
import { ChatPage } from "./pages/ChatPage";
import { AdminPage } from "./pages/AdminPage";
import IndicarProfissional from "./pages/IndicarProfissional";

function App() {
  const [isAdmin, setIsAdmin] = useState(!!localStorage.getItem("token"));
  const [currentPage, setCurrentPage] = useState<"chat" | "indicar" | "admin">("chat");
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [loginData, setLoginData] = useState({ token: "" });

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (loginData.token.trim()) {
      localStorage.setItem("token", loginData.token);
      setIsAdmin(true);
      setCurrentPage("admin");
      setShowLoginForm(false);
      setLoginData({ token: "" });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAdmin(false);
    setCurrentPage("chat");
  };

  if (isAdmin) {
    return <AdminPage />;
  }

  return (
    <>
      {currentPage === "chat" && <ChatPage />}
      {currentPage === "indicar" && <IndicarProfissional />}

      {/* Navigation Buttons */}
      <div className="fixed bottom-6 right-6 flex flex-col gap-2">
        {currentPage !== "chat" && (
          <button
            onClick={() => setCurrentPage("chat")}
            className="px-4 py-2 bg-blue-600 text-white rounded-full font-medium hover:bg-blue-700 transition shadow-lg"
          >
            💬 Chat
          </button>
        )}
        {currentPage !== "indicar" && (
          <button
            onClick={() => setCurrentPage("indicar")}
            className="px-4 py-2 bg-green-600 text-white rounded-full font-medium hover:bg-green-700 transition shadow-lg"
          >
            ⭐ Indicar
          </button>
        )}
        {!showLoginForm && (
          <button
            onClick={() => setShowLoginForm(true)}
            className="px-4 py-2 bg-gray-800 text-white rounded-full font-medium hover:bg-gray-900 transition shadow-lg"
          >
            🔐 Admin
          </button>
        )}
      </div>

      {/* Login Modal */}
      {showLoginForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Login Admin</h2>
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Token</label>
                <input
                  type="password"
                  value={loginData.token}
                  onChange={(e) => setLoginData({ token: e.target.value })}
                  placeholder="Cole seu token aqui"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  autoFocus
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
                >
                  Entrar
                </button>
                <button
                  type="button"
                  onClick={() => setShowLoginForm(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition"
                >
                  Cancelar
                </button>
              </div>
            </form>
            <p className="text-xs text-gray-500 mt-4 text-center">
              Para MVP, use qualquer token não-vazio (ex: "admin-token")
            </p>
          </div>
        </div>
      )}
    </>
  );
}

export default App;
