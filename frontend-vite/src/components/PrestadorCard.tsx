interface Prestador {
  id: number;
  nome: string;
  whatsapp: string;
  score_final: number;
}

export function PrestadorCard({ prestador }: { prestador: Prestador }) {
  return (
    <div className="border rounded-lg p-4 hover:shadow-lg transition">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-bold text-gray-900">{prestador.nome}</h3>
        <div className="text-2xl font-bold text-blue-600">{prestador.score_final.toFixed(1)}</div>
      </div>
      <a
        href={`https://wa.me/55${prestador.whatsapp}?text=Olá`}
        target="_blank"
        rel="noopener noreferrer"
        className="w-full block px-4 py-2 bg-green-500 text-white rounded font-medium hover:bg-green-600 text-center"
      >
        💬 WhatsApp
      </a>
    </div>
  );
}
