# Guia de Desenvolvimento

Instruções para configurar o ambiente local, executar a aplicação e rodar os testes.

---

## Pré-requisitos

| Ferramenta | Versão mínima |
|---|---|
| Python | 3.11 |
| PostgreSQL | 14 |
| Git | qualquer versão recente |

---

## 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd g04
```

---

## 2. Configurar o banco de dados

Crie um banco PostgreSQL local para a aplicação:

```sql
CREATE DATABASE credito;
```

---

## 3. Configurar o backend

### 3.1 Criar e ativar o ambiente virtual

```bash
cd apps/backend
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 3.2 Instalar as dependências

As dependências do otimizador precisam estar instaladas no mesmo ambiente que o backend, pois o worker do pipeline as importa diretamente.

```bash
pip install -r ../../apps/algoritmo_simplex/requirements.txt
pip install -r requirements.txt
```

### 3.3 Criar o arquivo `.env`

Crie o arquivo `apps/backend/.env` com as variáveis abaixo:

```env
APP_HOST=http://127.0.0.1
APP_PORT=8000
FRONTEND_PORT=5500

DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=credito
DB_USER=postgres
DB_PASSWORD=sua_senha
```

As migrations do banco são aplicadas automaticamente na primeira inicialização. Não é necessário rodá-las manualmente.

---

## 4. Subir a aplicação em desenvolvimento

A partir de `apps/backend`, o comando abaixo sobe o backend **e** o frontend juntos. O backend inicia com `--reload`, ou seja, reinicia automaticamente ao salvar qualquer arquivo Python.

```bash
python run_server.py
```

URLs disponíveis após a inicialização:

| Serviço | URL |
|---|---|
| Frontend | http://127.0.0.1:5500 |
| Backend (API) | http://127.0.0.1:8000 |
| Documentação interativa | http://127.0.0.1:8000/docs |

### Subir apenas o backend

```bash
cd apps/backend
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Subir apenas o frontend

```bash
cd apps/frontend
python -m http.server 5500
```

---

## 5. Estrutura dos módulos principais

```
apps/
├── algoritmo_simplex/     # otimizador e pipeline de otimização
│   ├── main.py            # orquestra clustering + Simplex
│   ├── simplex.py         # implementação própria do algoritmo
│   ├── clustering.py      # clusterização CART por perfil de cliente
│   ├── models.py          # estruturas Problema e Tableau
│   └── input/             # arquivos JSON de parâmetros
├── backend/
│   ├── main.py            # aplicação FastAPI
│   ├── config.py          # variáveis de ambiente e configuração
│   ├── api/               # rotas REST (routes.py, upload_routes.py)
│   ├── db/                # pool asyncpg e migrations SQL
│   ├── model/             # schemas Pydantic
│   └── services/          # lógica de negócio e integração com o otimizador
└── frontend/              # SPA React via CDN/Babel (arquivos estáticos)
```

---

## 6. Parâmetros do modelo

Os parâmetros padrão do modelo de otimização ficam em `apps/algoritmo_simplex/input/parametros.json`:

```json
{
  "T": 22,
  "t": 0.0175,
  "LGD": 0.8,
  "u_bar": 0.75,
  "L_max": 25000.0,
  "alpha": 0.05
}
```

Em ambiente de desenvolvimento, os parâmetros também podem ser sobrescritos por consulta via query params na rota `POST /api/consultas` ou persistidos via `PUT /api/config`.

---

## 7. Pipeline do otimizador via terminal

Para executar o pipeline de otimização diretamente, sem a interface web, prepare os dados primeiro (veja a seção "Preparação dos dados" no [README.md](README.md)) e então execute a partir da raiz do projeto:

```bash
python apps/algoritmo_simplex/main.py clientes_calibrado.csv parametros.json
```

---

## 8. Rodar os testes

Execute a partir da **raiz do repositório** (`g04/`), com o ambiente virtual ativado:

```bash
# Testes do otimizador (algoritmo Simplex)
python -m unittest discover -s apps/algoritmo_simplex/tests -p "test_*.py"

# Testes do backend (contratos de rotas, upload, integração HTTP e worker)
python -m unittest discover -s apps/backend/tests -p "test_*.py"
```

Os testes do backend não exigem um banco ativo: as rotas que dependem do banco são mockadas nos testes de contrato e integração HTTP.

---

## 9. Testar a API com o Bruno

As coleções de requisições para o Bruno estão em `apps/backend/bruno/backend/`. O README da pasta descreve como importar e executar as chamadas.

---

## 10. Variáveis de ambiente adicionais

| Variável | Padrão | Descrição |
|---|---|---|
| `FRONTEND_ORIGINS` | derivado de `APP_HOST:FRONTEND_PORT` | Origens CORS permitidas (separe múltiplas por vírgula) |
| `LOCAL_DATA_DIR` | `apps/backend/db/local_data` | Diretório de estado local (state.json, params.json) |
| `UPLOAD_DIR` | `apps/backend/uploads` | Diretório de uploads de parquet |


