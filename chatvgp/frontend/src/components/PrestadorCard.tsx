import React from "react";
import { PrestadorResult } from "../types";

interface PrestadorCardProps {
  prestador: PrestadorResult;
  posicao?: number;
}

const renderScore = (score: number) => {
  const barWidth = (score / 10) * 100;
  let color = "bg-green-500";
  if (score < 4) color = "bg-red-500";
  else if (score < 6) color = "bg-yellow-500";
  else if (score < 8) color = "bg-blue-500";

  return (
    <div className="w-full bg-gray-200 rounded h-2 overflow-hidden">
      <div className={`${color} h-full transition-all`} style={{ width: `${barWidth}%` }} />
    </div>
  );
};

const renderPercentage = (value?: number) => {
  if (!value) return "—";
  return `${Math.round(value * 100)}%`;
};

export const PrestadorCard: React.FC<PrestadorCardProps> = ({ prestador, posicao }) => {
  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition">
      <div className="flex items-start justify-between mb-3">
        <div>
          {posicao && <span className="text-sm font-bold text-blue-600">#{posicao}</span>}
          <h3 className="text-lg font-bold text-gray-900">{prestador.nome}</h3>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">{prestador.score_final.toFixed(1)}</div>
          <div className="text-xs text-gray-500">de 10</div>
        </div>
      </div>

      {/* Score visual */}
      <div className="mb-3">
        {renderScore(prestador.score_final)}
      </div>

      {/* Contato */}
      <a
        href={prestador.link_whatsapp}
        target="_blank"
        rel="noopener noreferrer"
        className="w-full block mb-3 px-4 py-2 bg-green-500 text-white rounded font-medium hover:bg-green-600 transition text-center"
      >
        💬 Contatar via WhatsApp
      </a>

      {/* Stats */}
      {prestador.feedback_count > 0 && (
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="bg-gray-50 p-2 rounded">
            <div className="text-xs text-gray-600">Material</div>
            <div className="font-bold">{renderPercentage(prestador.material_acertou_pct)}</div>
          </div>
          <div className="bg-gray-50 p-2 rounded">
            <div className="text-xs text-gray-600">Prazo</div>
            <div className="font-bold">{renderPercentage(prestador.prazo_cumprido_pct)}</div>
          </div>
          <div className="bg-gray-50 p-2 rounded">
            <div className="text-xs text-gray-600">Custo</div>
            <div className="font-bold">{renderPercentage(prestador.custo_mantido_pct)}</div>
          </div>
          <div className="bg-gray-50 p-2 rounded">
            <div className="text-xs text-gray-600">Qualidade</div>
            <div className="font-bold">
              {prestador.qualidade_media ? prestador.qualidade_media.toFixed(1) : "—"} ⭐
            </div>
          </div>
        </div>
      )}

      {/* Feedbacks */}
      <div className="mt-3 text-xs text-gray-500">
        {prestador.feedback_count > 0 ? (
          <>
            ✓ {prestador.feedback_count} avaliação{prestador.feedback_count !== 1 ? "ções" : ""}
          </>
        ) : (
          "Sem avaliações ainda"
        )}
      </div>
    </div>
  );
};
