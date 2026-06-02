import { useState, useEffect } from "react";
import api from "./services/api";

function App() {
  const [status, setStatus] = useState("Conectando ao backend...");

  useEffect(() => {
    api.get("/health")
      .then(() => setStatus("✅ Backend conectado!"))
      .catch(() => setStatus("❌ Backend offline"));
  }, []);

  return (
    <div className="min-h-screen bg-blue-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">ChatVGP</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Status do Sistema</h2>
          <p className="text-lg text-gray-700">{status}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Teste</h2>
          <input 
            type="text" 
            placeholder="Teste aqui (em breve)"
            className="w-full px-4 py-2 border rounded"
            disabled
          />
        </div>
      </div>
    </div>
  );
}

export default App;
