# Guia de Implantação

Instruções para implantar a aplicação na Vercel e disponibilizá-la aos usuários.

---

## Pré-requisitos

| Ferramenta | Observação |
|---|---|
| Conta na [Vercel](https://vercel.com) | Plano Hobby (gratuito) funciona com restrições; ver seção de limitações |
| [Vercel CLI](https://vercel.com/docs/cli) | `npm install -g vercel` |
| Git | Repositório com os commits mais recentes |
| Node.js | Necessário apenas para o Vercel CLI |

---

## Arquitetura de produção

A aplicação é implantada como **dois projetos independentes na Vercel**, a partir do mesmo repositório:

| Projeto | Conteúdo | Raiz do projeto |
|---|---|---|
| `g04-backend` | API FastAPI — Python serverless | raiz do repositório |
| `g04-frontend` | SPA estática — React/Babel | `apps/frontend/` |

O banco de dados é provisionado pelo add-on **Vercel Postgres** (baseado em Neon) e vinculado ao projeto backend.

```
Usuário
   │
   ├─▶ https://g04-frontend.vercel.app     (Vercel CDN — estático)
   │
   └─▶ https://g04-backend.vercel.app/api  (Vercel Serverless — Python)
                  │
                  └─▶ Vercel Postgres (Neon)
```

---

## 1. Preparar o repositório

### 1.1 Adicionar `matplotlib` às dependências do backend

O otimizador usa `matplotlib`, que não está listado em `apps/backend/requirements.txt`. Adicione-o:

```bash
echo "matplotlib" >> apps/backend/requirements.txt
```

### 1.2 Criar o `vercel.json` na raiz do repositório

Crie o arquivo `vercel.json` na raiz do repositório. Ele instrui a Vercel a tratar `apps/backend/main.py` como ponto de entrada da API:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "apps/backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "apps/backend/main.py"
    }
  ]
}
```

> **Por que a raiz do repositório?** O backend resolve o caminho do otimizador de forma dinâmica (`credit_service.py` sobe quatro diretórios via `Path(__file__).parent` até a raiz e desce para `apps/algoritmo_simplex/`). A Vercel precisa empacotar o repositório inteiro para que esse caminho exista em tempo de execução.

### 1.3 Fazer commit das alterações

```bash
git add apps/backend/requirements.txt vercel.json
git commit -m "chore: adiciona vercel.json e matplotlib para deploy na Vercel"
git push
```

---

## 2. Deploy do backend

### 2.1 Instalar e autenticar no Vercel CLI

```bash
npm install -g vercel
vercel login
```

### 2.2 Criar o projeto backend

Na raiz do repositório:

```bash
vercel --name g04-backend
```

Responda às perguntas interativas:

| Pergunta | Resposta |
|---|---|
| Set up and deploy? | `Y` |
| Which scope? | Sua conta ou organização |
| Link to existing project? | `N` |
| In which directory is your code? | `.` (raiz do repo) |
| Want to override the settings? | `N` |

### 2.3 Provisionar o banco de dados

No painel da Vercel (vercel.com), acesse o projeto `g04-backend` e:

1. Vá em **Storage → Create Database → Postgres**
2. Escolha um nome (ex: `g04-db`) e a região mais próxima
3. Clique em **Create & Continue** — as variáveis de conexão serão adicionadas automaticamente ao projeto

Após a criação, vá em **Storage → g04-db → Quickstart** e copie os valores das variáveis `POSTGRES_HOST`, `POSTGRES_DATABASE`, `POSTGRES_USER` e `POSTGRES_PASSWORD` para a próxima etapa.

### 2.4 Configurar as variáveis de ambiente do backend

No painel do projeto `g04-backend`, vá em **Settings → Environment Variables** e adicione:

| Variável | Valor | Tipo |
|---|---|---|
| `APP_HOST` | `https://g04-backend.vercel.app` | Plain text |
| `APP_PORT` | `8000` | Plain text |
| `DB_HOST` | Valor de `POSTGRES_HOST` | Plain text |
| `DB_PORT` | `5432` | Plain text |
| `DB_DATABASE` | Valor de `POSTGRES_DATABASE` | Plain text |
| `DB_USER` | Valor de `POSTGRES_USER` | Plain text |
| `DB_PASSWORD` | Valor de `POSTGRES_PASSWORD` | **Secret** |
| `FRONTEND_ORIGINS` | `https://g04-frontend.vercel.app` | Plain text |

> `FRONTEND_ORIGINS` define quais origens podem chamar a API (CORS). Se o domínio do frontend mudar, atualize essa variável e faça um novo deploy.

### 2.5 Fazer o deploy de produção

```bash
vercel --prod
```

Ao final, a Vercel exibirá a URL de produção (ex: `https://g04-backend.vercel.app`). Guarde essa URL para configurar o frontend.

As migrations do banco de dados são aplicadas automaticamente na primeira requisição à API (via lifespan do FastAPI).

---

## 3. Deploy do frontend

### 3.1 Criar o projeto frontend

Na raiz do repositório:

```bash
vercel --name g04-frontend
```

Responda às perguntas interativas:

| Pergunta | Resposta |
|---|---|
| Set up and deploy? | `Y` |
| Which scope? | Sua conta ou organização |
| Link to existing project? | `N` |
| In which directory is your code? | `./apps/frontend` |
| Want to override the settings? | `Y` |
| Build command? | `printf 'window.API_BASE_URL = "%s";\n' "$BACKEND_URL" > runtime-config.js` |
| Output directory? | `.` |
| Install command? | *(deixar em branco)* |

O `runtime-config.js` não é versionado no repositório — a Vercel o gera no momento do deploy usando a variável `BACKEND_URL`.

### 3.2 Configurar variável de ambiente do frontend

No painel do projeto `g04-frontend`, vá em **Settings → Environment Variables** e adicione:

| Variável | Valor |
|---|---|
| `BACKEND_URL` | `https://g04-backend.vercel.app/api` |

### 3.3 Fazer o deploy de produção

```bash
vercel --prod
```

---

## 4. Verificação pós-deploy

Após os dois deploys, confirme que cada serviço responde corretamente:

| Verificação | URL / Comando |
|---|---|
| Backend — raiz | `curl https://g04-backend.vercel.app/` |
| Backend — docs interativos | `https://g04-backend.vercel.app/docs` |
| Backend — status da API | `curl https://g04-backend.vercel.app/api/cockpit` |
| Frontend | `https://g04-frontend.vercel.app` |

A primeira requisição ao backend pode ser mais lenta (cold start do serverless).

---

## 5. Atualizar a aplicação

Após o deploy inicial, as atualizações seguem o fluxo normal de git:

```bash
git push
```

A Vercel detecta o push automaticamente e dispara um novo deploy para os projetos vinculados ao repositório. Para acionar um deploy manualmente:

```bash
vercel --prod           # backend (na raiz do repo)
cd apps/frontend && vercel --prod   # frontend
```

Para reverter para a versão anterior:

```bash
vercel rollback
```

Ou no painel: **Deployments → selecionar versão anterior → Promote to Production**.

---

## 6. Limitações em ambiente serverless

### Timeout do otimizador

A Vercel executa o backend como funções serverless com tempo de execução limitado:

| Plano | Timeout |
|---|---|
| Hobby (gratuito) | 10 segundos |
| Pro | 300 segundos |

O pipeline de otimização pode ultrapassar 10 segundos para bases de dados com muitos clientes. Para demonstrações, use bases reduzidas (`--reduced` no script de conversão) ou considere o plano Pro.

### Upload de arquivos Parquet

O sistema de arquivos das funções serverless é efêmero: arquivos enviados via upload não persistem entre invocações. O fluxo de upload e processamento funciona enquanto ocorre na mesma execução. Para persistência de arquivos em produção, seria necessário integrar um serviço externo de storage (ex: Vercel Blob, AWS S3).

### Estado local

As variáveis `UPLOAD_DIR`, `LOCAL_DATA_DIR`, `STATE_PATH` e `PARAMS_PATH` apontam para diretórios locais que não persistem no serverless. Os arquivos `state.json` e `params.json` são recriados a partir do banco de dados a cada cold start.

---

## Referência de variáveis de ambiente

### Backend (`g04-backend`)

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `APP_HOST` | Sim | `http://127.0.0.1` | URL pública do backend (com protocolo, sem porta) |
| `APP_PORT` | Não | `8000` | Porta do backend (informativo no serverless) |
| `DB_HOST` | Sim | — | Host do PostgreSQL |
| `DB_PORT` | Não | `5432` | Porta do PostgreSQL |
| `DB_DATABASE` | Sim | — | Nome do banco de dados |
| `DB_USER` | Sim | — | Usuário do banco de dados |
| `DB_PASSWORD` | Sim | — | Senha do banco de dados |
| `FRONTEND_ORIGINS` | Sim | derivado de `APP_HOST` | Origens CORS permitidas (separe múltiplas por vírgula) |
| `UPLOAD_DIR` | Não | `apps/backend/uploads` | Diretório de uploads de parquet |
| `LOCAL_DATA_DIR` | Não | `apps/backend/db/local_data` | Diretório de estado local |

### Frontend (`g04-frontend`)

| Variável | Obrigatória | Descrição |
|---|---|---|
| `BACKEND_URL` | Sim | URL completa da API do backend (ex: `https://g04-backend.vercel.app/api`) |
