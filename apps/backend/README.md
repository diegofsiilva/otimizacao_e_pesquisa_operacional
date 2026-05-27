# Backend (FastAPI) - Servidor local

Este backend expoe uma API para as telas de Dashboard, Gerar Limites e Resultados.

## Rodar local

```powershell
cd apps/backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python run_server.py
```

Docs: `http://localhost:8000/docs`

## Onde configurar o servidor

Copie `apps/backend/.env.example` para `apps/backend/.env` e preencha:

- `APP_HOST`: host do backend local, por exemplo `127.0.0.1`.
- `APP_PORT`: porta do backend local, por exemplo `8000`.
- `FRONTEND_ORIGINS`: URLs do frontend que podem acessar a API, separadas por virgula.
- `LOCAL_DATA_DIR`: pasta onde ficam os JSONs locais do backend.
- `UPLOAD_DIR`: pasta onde ficam os arquivos enviados por upload.
- `STATE_PATH`: arquivo JSON de estado da aplicacao.
- `PARAMS_PATH`: arquivo JSON de parametros do modelo.

Sem `.env`, o backend usa os valores padrao do `apps/backend/config.py`.

## Persistencia local

O backend nao usa Supabase. Ele salva dados em arquivos JSON no servidor local:

- `state.json`: estado da aplicacao, clusters e ultimo resultado.
- `params.json`: parametros do modelo.
