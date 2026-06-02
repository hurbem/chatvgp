import axios, { AxiosInstance } from "axios";
import {
  Categoria,
  Condominio,
  Prestador,
  Feedback,
  ChatRequest,
  ChatResponse,
  FeedbackStats,
  RankingItem,
} from "../types";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api";

class APIClient {
  client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Interceptor para adicionar token em requisições
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers.Authorization = token;
      }
      return config;
    });
  }

  // Categorias
  getCategorias(): Promise<Categoria[]> {
    return this.client.get("/categorias").then((res) => res.data);
  }

  createCategoria(data: { nome: string; descricao?: string }): Promise<Categoria> {
    return this.client.post("/categorias", data).then((res) => res.data);
  }

  // Condomínios
  getCondominios(cidade?: string): Promise<Condominio[]> {
    return this.client
      .get("/condominios", { params: { cidade } })
      .then((res) => res.data);
  }

  createCondominio(data: { nome: string; cidade: string }): Promise<Condominio> {
    return this.client.post("/condominios", data).then((res) => res.data);
  }

  // Prestadores
  getPrestadores(
    categoria_id?: number,
    condominio_id?: number,
    status_filter?: string
  ): Promise<Prestador[]> {
    return this.client
      .get("/prestadores", {
        params: { categoria_id, condominio_id, status_filter },
      })
      .then((res) => res.data);
  }

  getPrestador(id: number): Promise<Prestador> {
    return this.client.get(`/prestadores/${id}`).then((res) => res.data);
  }

  createPrestador(data: any): Promise<Prestador> {
    return this.client.post("/prestadores", data).then((res) => res.data);
  }

  updatePrestador(id: number, data: any): Promise<Prestador> {
    return this.client.put(`/prestadores/${id}`, data).then((res) => res.data);
  }

  deletePrestador(id: number): Promise<void> {
    return this.client.delete(`/prestadores/${id}`);
  }

  // Feedback
  getFeedbacks(
    prestador_id?: number,
    condominio_id?: number,
    seu_feedback?: boolean
  ): Promise<Feedback[]> {
    return this.client
      .get("/feedback", {
        params: { prestador_id, condominio_id, seu_feedback },
      })
      .then((res) => res.data);
  }

  getFeedbacksPrestador(prestador_id: number): Promise<Feedback[]> {
    return this.client.get(`/feedback/prestador/${prestador_id}`).then((res) => res.data);
  }

  getFeedbackStats(prestador_id: number, condominio_id?: number): Promise<FeedbackStats> {
    return this.client
      .get(`/feedback/stats/${prestador_id}`, { params: { condominio_id } })
      .then((res) => res.data);
  }

  createFeedback(data: any): Promise<Feedback> {
    return this.client.post("/feedback", data).then((res) => res.data);
  }

  updateFeedback(id: number, data: any): Promise<Feedback> {
    return this.client.put(`/feedback/${id}`, data).then((res) => res.data);
  }

  deleteFeedback(id: number): Promise<void> {
    return this.client.delete(`/feedback/${id}`);
  }

  // Ranking
  getRankingCondominio(
    condominio_id: number,
    categoria_id?: number,
    limit?: number
  ): Promise<RankingItem[]> {
    return this.client
      .get(`/feedback/ranking/por-condominio/${condominio_id}`, {
        params: { categoria_id, limit },
      })
      .then((res) => res.data);
  }

  // Chat
  buscar(request: ChatRequest): Promise<ChatResponse> {
    return this.client.post("/chat/buscar", request).then((res) => res.data);
  }

  // Health check
  healthCheck(): Promise<{ status: string; version: string }> {
    return this.client.get("/health").then((res) => res.data);
  }
}

export default new APIClient();
