import React, { useState } from "react";
import api from "../services/api";
import { ChatResponse } from "../types";
import { ChatInput } from "../components/ChatInput";
import { ChatResult } from "../components/ChatResult";

export const ChatPage: React.FC = () => {
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchHistory, setSearchHistory] = useState<ChatResponse[]>([]);

  const handleBuscar = async (pergunta: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.buscar({ pergunta });
      setResult(response);
      setSearchHistory([response, ...searchHistory]);
    } catch (err: any) {
      setError(err.message || "Erro ao buscar prestadores. Tente novamente.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">ChatVGP</h1>
          <p className="text-gray-600 mt-1">Encontre prestadores de serviços na sua região</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Chat Input */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">O que você está procurando?</h2>
          <ChatInput onSend={handleBuscar} isLoading={isLoading} />

          {/* Exemplos de perguntas */}
          {!result && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-600 mb-3">Exemplos de buscas:</p>
              <div className="flex flex-wrap gap-2">
                {[
                  "Preciso de um encanador em Vargem Grande",
                  "Eletricista em Cotia",
                  "Limpeza residencial",
                  "Pintura de casa",
                ].map((exemplo) => (
                  <button
                    key={exemplo}
                    onClick={() => handleBuscar(exemplo)}
                    className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded transition"
                  >
                    {exemplo}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-700 font-medium">⚠️ {error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <ChatResult result={result} />
          </div>
        )}

        {/* Search History */}
        {searchHistory.length > 1 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Buscas Anteriores</h2>
            <div className="space-y-2">
              {searchHistory.slice(1, 5).map((history, idx) => (
                <button
                  key={idx}
                  onClick={() => setResult(history)}
                  className="block w-full text-left px-4 py-2 hover:bg-blue-50 rounded border border-gray-200 transition"
                >
                  <p className="text-gray-700 text-sm">📌 {history.pergunta}</p>
                  <p className="text-gray-500 text-xs">
                    {history.total_resultados} prestador{history.total_resultados !== 1 ? "es" : ""} encontrado
                    {history.total_resultados !== 1 ? "s" : ""}
                  </p>
                </button>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
