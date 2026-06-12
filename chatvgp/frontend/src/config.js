// URL base da API do backend.
// Em desenvolvimento usa o backend local; em produção, defina a variável de
// ambiente REACT_APP_API_URL no provedor de deploy (ex: Vercel) apontando
// para a URL do backend (ex: https://chatvgp-api.onrender.com).
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
