// Tipos da API

export interface Categoria {
  id: number;
  nome: string;
  descricao?: string;
}

export interface Condominio {
  id: number;
  nome: string;
  cidade: string;
  criado_em: string;
}

export interface Prestador {
  id: number;
  nome: string;
  whatsapp: string;
  categoria_id: number;
  condominio_ids: number[];
  status: string;
  notas?: string;
  criado_em: string;
  categoria: Categoria;
}

export interface PrestadorComScore extends Prestador {
  score_final: number;
  feedback_count: number;
  qualidade_media?: number;
  material_acertou_pct?: number;
  prazo_cumprido_pct?: number;
  custo_mantido_pct?: number;
}

export interface Feedback {
  id: number;
  prestador_id: number;
  condominio_id: number;
  categoria_id: number;
  data_feedback: string;
  qualidade: number;
  material_estimativa: string;
  prazo_manteve: boolean;
  custo_manteve: boolean;
  observacoes?: string;
  seu_feedback: boolean;
  criado_em: string;
}

export interface FeedbackStats {
  qualidade_media?: number;
  material_acertou_pct?: number;
  prazo_cumprido_pct?: number;
  custo_mantido_pct?: number;
  total_feedbacks: number;
  score_material: number;
  score_prazo: number;
  score_custo: number;
  score_qualidade: number;
  score_final: number;
}

export interface ChatRequest {
  pergunta: string;
  condominio_id?: number;
}

export interface PrestadorResult {
  id: number;
  nome: string;
  whatsapp: string;
  link_whatsapp: string;
  score_final: number;
  feedback_count: number;
  qualidade_media?: number;
  material_acertou_pct?: number;
  prazo_cumprido_pct?: number;
  custo_mantido_pct?: number;
}

export interface ChatResponse {
  pergunta: string;
  categoria?: string;
  condominio?: string;
  prestadores: PrestadorResult[];
  total_resultados: number;
}

export interface RankingItem extends PrestadorResult {
  categoria: string;
  posicao: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
}
