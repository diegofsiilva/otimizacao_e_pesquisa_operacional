# Backend (FastAPI)

API do sistema de otimização de limites de crédito. Expõe endpoints para o Cockpit, Gerar Limites e Resultados.

## Requisitos

- Python 3.11+
- PostgreSQL 14+

## Setup

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # editar com as credenciais do banco
python run_server.py
```

O comando `run_server.py` sobe o backend e o servidor estático do frontend juntos. As URLs aparecem no terminal ao iniciar.

## Configuração (.env)

| Variável        | Descrição                              | Exemplo            |
| --------------- | -------------------------------------- | ------------------ |
| `APP_HOST`      | URL base do backend, com protocolo     | `http://127.0.0.1` |
| `APP_PORT`      | Porta do backend                       | `8000`             |
| `FRONTEND_PORT` | Porta do servidor estático do frontend | `5500`             |
| `DB_HOST`       | Host do PostgreSQL                     | `localhost`        |
| `DB_PORT`       | Porta do PostgreSQL                    | `5432`             |
| `DB_DATABASE`   | Nome do banco                          | `credito`          |
| `DB_USER`       | Usuário do banco                       | `postgres`         |
| `DB_PASSWORD`   | Senha do banco                         | -                  |

`FRONTEND_ORIGINS` não precisa ser configurado: é derivado automaticamente de `APP_HOST` e `FRONTEND_PORT`.

Sem `.env`, o backend usa os valores padrão de `config.py`.

## Banco de dados

O backend usa PostgreSQL via `asyncpg`. As migrations ficam em `db/migrations/` e rodam automaticamente na inicialização. Não é necessário rodar nenhum comando separado.

## Endpoints

| Método | Rota                                  | Descrição                           |
| ------ | ------------------------------------- | ----------------------------------- |
| GET    | `/api/health`                         | Status da API                       |
| GET    | `/api/safras`                         | Lista todas as safras               |
| GET    | `/api/consultas`                      | Lista todas as consultas            |
| POST   | `/api/consultas`                      | Cria consulta e dispara o pipeline  |
| GET    | `/api/consultas/{id}`                 | Detalhe de uma consulta             |
| GET    | `/api/consultas/{id}/clusters`        | Clusters de uma consulta            |
| GET    | `/api/consultas/{id}/clientes`        | Clientes de uma consulta (paginado) |
| GET    | `/api/consultas/{id}/clientes/export` | Exporta clientes como CSV           |
| GET    | `/api/clientes/{token}`               | Histórico de um cliente             |
| GET    | `/api/config`                         | Parâmetros do modelo                |
| PUT    | `/api/config`                         | Atualiza parâmetros do modelo       |

Documentação interativa disponível em `{APP_HOST}:{APP_PORT}/docs` com o servidor rodando.

## Pipeline

O endpoint `POST /api/consultas` recebe um arquivo `.parquet`, registra a consulta com status `pendente` e dispara o pipeline em background. O frontend consulta `GET /api/consultas/{id}` periodicamente para acompanhar o progresso.

Etapas do pipeline: calibração de PD, clustering via CART e otimização por programação linear (Simplex).
