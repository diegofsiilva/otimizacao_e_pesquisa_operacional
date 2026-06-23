# Deploy no Vercel

Este repositório já está preparado para o Vercel com:

- `vercel.json`: build, função Python e rotas da API.
- `api/index.py`: entrada serverless para o FastAPI.
- `scripts/build_vercel.py`: copia `apps/frontend` para `public` e cria `runtime-config.js`.
- `.env.example`: modelo das variáveis que devem ser cadastradas na Vercel.

## 1. Banco PostgreSQL

A API precisa de PostgreSQL. Crie um banco gerenciado, copie a string de conexão e cadastre na Vercel como `DATABASE_URL`.

Use uma URL no formato:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require
```

Se preferir variáveis separadas, preencha `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USER` e `DB_PASSWORD`.

## 2. Variáveis de ambiente na Vercel

No painel da Vercel, abra o projeto e vá em:

`Settings` -> `Environment Variables`

Cadastre pelo menos:

```env
FRONTEND_ORIGINS=https://SEU-PROJETO.vercel.app
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require
DB_POOL_MIN_SIZE=0
DB_POOL_MAX_SIZE=1
DB_CONNECT_TIMEOUT=5
DB_STATEMENT_CACHE_SIZE=0
LOCAL_DATA_DIR=/tmp/g04_data
UPLOAD_DIR=/tmp/g04_uploads
STATE_PATH=/tmp/g04_data/state.json
PARAMS_PATH=/tmp/g04_data/params.json
```

Depois do primeiro deploy, troque `https://SEU-PROJETO.vercel.app` pela URL real exibida pela Vercel. Se usar domínio próprio, adicione-o também em `FRONTEND_ORIGINS`, separado por vírgula.

## 3. Deploy pelo painel

1. Suba o repositório para GitHub, GitLab ou Bitbucket.
2. Na Vercel, clique em `Add New` -> `Project`.
3. Importe o repositório.
4. Mantenha a raiz do projeto como root directory.
5. Confirme as variáveis de ambiente.
6. Clique em `Deploy`.

## 4. Deploy pela CLI

```bash
npm i -g vercel
vercel login
vercel
vercel --prod
```

## 5. Testes após publicar

Abra:

- `https://SEU-PROJETO.vercel.app`
- `https://SEU-PROJETO.vercel.app/api/health`
- `https://SEU-PROJETO.vercel.app/docs`

O frontend usa `/api` automaticamente em produção.

## Observação importante

O Vercel executa o backend como função serverless. O upload em chunks usa `/tmp`, que é temporário e não é armazenamento persistente. Para bases grandes e pipelines longos, o caminho mais robusto é manter o frontend no Vercel e hospedar o backend em um serviço com processo persistente, como Render, Railway, Fly.io ou uma VM.
