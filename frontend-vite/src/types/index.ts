export interface Prestador {
  id: number;
  nome: string;
  whatsapp: string;
  score_final: number;
}

export interface ChatResponse {
  pergunta: string;
  prestadores: Prestador[];
  total_resultados: number;
}
