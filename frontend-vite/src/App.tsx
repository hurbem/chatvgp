import { useState } from "react";
import { ChatInput } from "./components/ChatInput";
import { PrestadorCard } from "./components/PrestadorCard";

interface Prestador {
  id: number;
  nome: string;
  whatsapp: string;
  score_final: number;
}

function App() {
  const [results, setResults] = useState<Prestador[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [pergunta, setPergunta] = useState("");

  const handleBuscar = async (texto: string) => {
    setPergunta(texto);
    setIsLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
      const res = await fetch(`${apiUrl}/chat/buscar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pergunta: texto })
      });
      const data = await res.json();
      setResults(data.prestadores || []);
    } catch (error) {
      console.error(error);
      alert("Erro ao buscar. Verifique o backend.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-blue-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">ChatVGP</h1>
        <p className="text-gray-600 mb-8">Encontre prestadores de serviços</p>

        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <ChatInput onSend={handleBuscar} isLoading={isLoading} />
        </div>

        {pergunta && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <p className="text-gray-700 mb-4"><strong>Pergunta:</strong> {pergunta}</p>
            {results.length > 0 ? (
              <div className="grid gap-4">
                {results.map((p) => (
                  <PrestadorCard key={p.id} prestador={p} />
                ))}
              </div>
            ) : (
              <p className="text-gray-600">Nenhum prestador encontrado</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
