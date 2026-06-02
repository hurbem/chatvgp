import React from "react";
import { ChatResponse } from "../types";
import { PrestadorCard } from "./PrestadorCard";

interface ChatResultProps {
  result: ChatResponse;
}

export const ChatResult: React.FC<ChatResultProps> = ({ result }) => {
  return (
    <div className="space-y-4">
      {/* Header com informações */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-gray-700">
          <span className="font-bold">Pergunta:</span> {result.pergunta}
        </p>
        {result.categoria && (
          <p className="text-sm text-gray-600 mt-1">
            <span className="font-semibold">Categoria:</span> {result.categoria}
            {result.condominio && ` • ${result.condominio}`}
          </p>
        )}
      </div>

      {/* Resultados */}
      {result.total_resultados > 0 ? (
        <div>
          <h2 className="text-lg font-bold text-gray-900 mb-3">
            {result.total_resultados} prestador{result.total_resultados !== 1 ? "es" : ""} encontrado
            {result.total_resultados !== 1 ? "s" : ""}
          </h2>
          <div className="grid gap-4">
            {result.prestadores.map((prestador) => (
              <PrestadorCard key={prestador.id} prestador={prestador} />
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
          <p className="text-gray-700">
            Nenhum prestador encontrado para sua busca. Tente com outras palavras-chave.
          </p>
        </div>
      )}
    </div>
  );
};
