# Deploy em Produção - ChatVGP

**Tempo estimado:** 30 minutos  
**Ferramentas:** Render (Backend) + Vercel (Frontend)  
**Custo:** Gratuito/Barato (Hobby plans)

---

## 🎯 Resumo

1. **Backend em Render** → PostgreSQL gerenciado + FastAPI
2. **Frontend em Vercel** → React/Vite automático
3. **GitHub** → Deploy automático ao fazer push

---

## ⚙️ Preparação (5 min)

### 1. Verificar Git

```bash
cd ~/Documents/Claude/Projects/Projeto\ ChatVGP

# Iniciar git (se não tiver)
git init
git add .
git commit -m "Initial ChatVGP MVP"

# Adicionar remote (usar seu repo)
git remote add origin https://github.com/SEU_USER/chatvgp.git
git branch -M main
git push -u origin main
```

### 2. Backend - Preparar Arquivos

```bash
cd chatvgp/backend

# Verificar/criar Procfile
cat > Procfile << 'EOF'
web: gunicorn -w 4 -b 0.0.0.0:$PORT app.main:app --worker-class uvicorn.workers.UvicornWorker
EOF

# Adicionar ao requirements.txt se não tiver
# gunicorn==21.2.0
# python-multipart==0.0.6

# Commit
git add Procfile requirements.txt
git commit -m "Add production files"
git push
```

---

## 🔵 Backend - Render Deployment (10 min)

### 1. Acessar Render

- Ir para https://dashboard.render.com
- Sign up com GitHub (mais fácil)

### 2. Criar PostgreSQL

1. **New +** → **PostgreSQL**
2. Preencher:
   - **Name:** `chatvgp-db`
   - **Database:** `chatvgp`
   - **User:** `postgres`
   - **Region:** São Paulo (ou mais próxima)
   - **Plan:** Free
3. **Create Database**
4. ⚠️ **Copiar connection string** (aparece após criado)

Exemplo:
```
postgresql://postgres:PASSWORD@HOST:5432/chatvgp
```

### 3. Criar Web Service (Backend)

1. **New +** → **Web Service**
2. **Connect your repository** → Seleciona `chatvgp`
3. Preencher:
   - **Name:** `chatvgp-api`
   - **Root Directory:** `chatvgp/backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** 
     ```
     gunicorn -w 4 -b 0.0.0.0:$PORT app.main:app --worker-class uvicorn.workers.UvicornWorker
     ```
   - **Plan:** Free

4. **Advanced** → Environment:
   ```
   DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/chatvgp
   SECRET_KEY=gera-algo-muito-aleatorio-aqui
   CLAUDE_API_KEY=sk-sua-chave-real-ou-placeholder
   ENVIRONMENT=production
   DEBUG=False
   CORS_ORIGINS=["https://chatvgp.vercel.app","https://seu-dominio.com"]
   ```

5. **Create Web Service**

⏳ Espera 2-5 minutos para build e deploy

### 4. Verificar Backend

Após deploy, aparece URL tipo:
```
https://chatvgp-api.onrender.com
```

Testa:
```bash
curl https://chatvgp-api.onrender.com/health
# {"status":"ok","version":"0.1.0"}
```

✅ **Backend pronto!**

---

## ⚪ Frontend - Vercel Deployment (10 min)

### 1. Acessar Vercel

- Ir para https://vercel.com/dashboard
- Sign up com GitHub

### 2. Atualizar Frontend .env

```bash
cd ~/Documents/Claude/Projects/Projeto\ ChatVGP/frontend-vite

# Editar .env para produção
cat > .env.production << 'EOF'
VITE_API_BASE_URL=https://chatvgp-api.onrender.com/api
EOF

# Copiar para .env também
cp .env.production .env

# Commit
git add .env
git commit -m "Update API URL to production"
git push
```

### 3. Deploy no Vercel

1. **Add New Project** → **Import Git Repository**
2. Selecionar `chatvgp`
3. Preencher:
   - **Project Name:** `chatvgp`
   - **Framework:** Create React App (auto-detecta)
   - **Root Directory:** `chatvgp/frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. **Environment Variables:**
   ```
   VITE_API_BASE_URL=https://chatvgp-api.onrender.com/api
   ```
5. **Deploy**

⏳ Espera 1-2 minutos para build e deploy

### 4. Verificar Frontend

Após deploy, aparece URL tipo:
```
https://chatvgp.vercel.app
```

Acessa no navegador → Deve carregar e conectar ao backend!

✅ **Frontend pronto!**

---

## 🎯 Testar Produção

### 1. Acessar Sistema

**Frontend:** https://chatvgp.vercel.app

### 2. Criar Dados

Acessa Swagger do backend:
```
https://chatvgp-api.onrender.com/docs
```

Login com token: `admin-token`

Cria:
1. Categoria (Encanaria)
2. Condominio (Vargem Grande)
3. Prestador (João Silva)
4. Feedback (teste)

### 3. Testar Busca

No frontend:
```
Digita: "Preciso de um encanador"
Clica: Buscar
Resultado: João Silva aparece com score
```

✅ **Sistema em produção funcionando!**

---

## 🔧 Domínio Personalizado (Opcional)

### Backend - Render

1. Dashboard → `chatvgp-api` → **Settings**
2. **Custom Domain**
3. Adicionar: `api.seu-dominio.com`
4. Seguir instruções de DNS

### Frontend - Vercel

1. Dashboard → `chatvgp` → **Settings** → **Domains**
2. Adicionar: `chatvgp.seu-dominio.com`
3. Seguir instruções de DNS

---

## 📊 Monitoramento

### Backend (Render)

- Dashboard → `chatvgp-api` → **Logs**
- Ver requisições em tempo real

### Frontend (Vercel)

- Dashboard → `chatvgp` → **Analytics**
- Ver tráfego, performance

### Uptime Monitor (Gratuito)

1. Ir para https://updown.io
2. Adicionar monitores:
   - `https://chatvgp-api.onrender.com/health`
   - `https://chatvgp.vercel.app`
3. Receber alertas se cair

---

## 🚨 Troubleshooting

### Backend não inicia em Render

1. Verificar logs: Dashboard → Logs
2. Erros comuns:
   - **MODULE_NOT_FOUND:** Falta dependência em requirements.txt
   - **CONNECTION_REFUSED:** DATABASE_URL incorreta
   - **PERMISSION_DENIED:** Procfile inválido

**Solução:** Edita arquivo, faz push, Render redeploy automático

### Frontend mostra "Backend offline"

1. Verifica se VITE_API_BASE_URL está correto
2. Verifica CORS_ORIGINS no backend .env
3. Render pode estar em cold start (leva 30s)

**Solução:** Aguarda ou edita env variable e redeploy

### Banco de dados vazio

- Dados são criados via Swagger: `/docs`
- Ou cria via API direto

### Mudar CLAUDE_API_KEY

1. Render Dashboard → `chatvgp-api` → **Environment**
2. Edita `CLAUDE_API_KEY`
3. **Auto-redeploy** ativado = atualiza sozinho

---

## 📈 Próximas Melhorias

Após deploy em produção:

### Segurança
- [ ] Ativar HTTPS (automático em Render/Vercel)
- [ ] Implementar JWT (não apenas token simples)
- [ ] Adicionar rate limiting
- [ ] Logs de auditoria

### Performance
- [ ] Upgrade Render para Standard ($12/mês) = remove cold starts
- [ ] CDN no frontend (Vercel já incluso)
- [ ] Cache HTTP headers

### Features
- [ ] Admin panel completo
- [ ] Sistema de feedback público
- [ ] Dashboard de estatísticas
- [ ] Mobile app (React Native)

---

## 💡 Checklist Final

- [ ] Backend deploiado em Render
- [ ] PostgreSQL em Render
- [ ] Frontend deploiado em Vercel
- [ ] Backend conectado ao PostgreSQL
- [ ] Frontend conectado ao Backend
- [ ] Dados de teste criados
- [ ] Busca funcionando em produção
- [ ] CORS configurado
- [ ] Domínios personalizados (opcional)
- [ ] Uptime monitoring (opcional)

---

## 🎉 Pronto!

Seu ChatVGP está em produção!

**URLs:**
- Frontend: https://chatvgp.vercel.app
- Backend: https://chatvgp-api.onrender.com
- Docs: https://chatvgp-api.onrender.com/docs

**Próximo passo:** Coletar feedback de usuários reais e iterar!

---

**Documentação:** DEPLOY-PRODUCAO.md  
**Data:** Junho 2, 2026  
**Versão:** 1.0.0
