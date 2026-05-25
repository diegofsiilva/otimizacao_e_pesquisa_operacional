# Backend (FastAPI) + Supabase

Este backend expõe uma API para as telas de Dashboard, Gerar Limites e Resultados.

## Rodar local

```powershell
cd apps/backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Docs: `http://localhost:8000/docs`

## Supabase

1. Crie a tabela `app_kv` no Supabase executando `apps/backend/db/schema.sql` no SQL editor.
2. Configure as variaveis no ambiente (use `apps/backend/.env.example` como base):
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY` (recomendado no backend) ou `SUPABASE_ANON_KEY`

Checagem rapida: `GET /api/supabase/health`.
