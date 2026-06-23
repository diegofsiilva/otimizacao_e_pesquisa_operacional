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

