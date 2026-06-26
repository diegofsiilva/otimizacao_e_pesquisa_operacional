# Guia de Operações (Deploy)

Instruções para implantar a aplicação no servidor e disponibilizá-la aos usuários.

Este documento cobre o ambiente de produção. Para rodar localmente, veja o [devdoc.md](devdoc.md).

---

## Visão geral da arquitetura de deploy

A aplicação é um único processo Python que sobe, juntos, a API FastAPI e o servidor estático do frontend (via `apps/backend/run_server.py`). O deploy roda em um servidor Linux gerenciado, com:

- **Pipeline GitLab CI** (`.gitlab-ci.yml`) — testa e publica o código automaticamente.
- **Runner com a tag `g04-server`** — executa os jobs diretamente na máquina de deploy.
- **Serviço systemd `g04`** — mantém a aplicação rodando e a reinicia a cada publicação.
- **PostgreSQL** — banco de dados da aplicação, com migrations aplicadas automaticamente na inicialização.

```
Push na branch develop
        │
        ▼
GitLab CI (runner g04-server)
  ├── stage test   → roda os testes do otimizador e do backend
  └── stage deploy → rsync do código → /home/cc06-g4/g04/
                     chmod +x start.sh
                     systemctl restart g04
        │
        ▼
systemd (g04) → start.sh → run_server.py
  ├── frontend estático (FRONTEND_PORT)
  └── API FastAPI + migrations (APP_PORT)
        │
        ▼
Usuários (navegador) → domínio público
```

---

## Pré-requisitos do servidor

| Item | Versão / requisito |
|---|---|
| Sistema | Linux com systemd |
| Python | 3.11+ |
| PostgreSQL | 14+ (acessível pelo servidor da aplicação) |
| GitLab Runner | registrado com a tag `g04-server` |
| Usuário de deploy | `cc06-g4`, com permissão `sudo` para `systemctl` |
| Diretório de deploy | `/home/cc06-g4/g04/` |

---

## 1. Preparação inicial do servidor (uma vez)

Estes passos são executados manualmente apenas na primeira configuração da máquina.

### 1.1 Criar o banco de dados

```bash
sudo -u postgres psql -c "CREATE DATABASE credito;"
sudo -u postgres psql -c "CREATE USER g04 WITH PASSWORD 'senha_forte';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE credito TO g04;"
```

> As migrations em `apps/backend/db/migrations/` rodam automaticamente quando a aplicação sobe — não é necessário aplicá-las manualmente.

### 1.2 Criar o arquivo de ambiente de produção

O `.env` **não** é versionado e **não** é sobrescrito pelo deploy (o `rsync` não o remove). Crie-o uma vez em `/home/cc06-g4/g04/apps/backend/.env`:

```env
# Backend
APP_HOST=http://127.0.0.1
APP_PORT=8000
FRONTEND_PORT=5500

# Origem pública do frontend em produção (domínio próprio / túnel).
# Obrigatória quando o frontend é servido por um domínio diferente do bind local.
FRONTEND_ORIGINS=https://maiorais.com

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=credito
DB_USER=g04
DB_PASSWORD=senha_forte
```

Referência completa das variáveis: [devdoc.md](devdoc.md#10-variáveis-de-ambiente-adicionais) e `apps/backend/config.py`.

> **CORS:** em produção com domínio próprio é obrigatório definir `FRONTEND_ORIGINS` com a origem exata do frontend (esquema + host, ex.: `https://maiorais.com`). Sem isso, o navegador bloqueia as chamadas à API. Múltiplas origens podem ser separadas por vírgula.

### 1.3 Criar o serviço systemd

Crie `/etc/systemd/system/g04.service`:

```ini
[Unit]
Description=Sistema de Credito Banco PAN (G04)
After=network.target postgresql.service

[Service]
Type=exec
User=cc06-g4
WorkingDirectory=/home/cc06-g4/g04/apps/backend
ExecStart=/home/cc06-g4/g04/apps/backend/start.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Habilite e inicie:

```bash
sudo systemctl daemon-reload
sudo systemctl enable g04
sudo systemctl start g04
```

O `start.sh` cria a virtualenv (se não existir), instala as dependências do otimizador e do backend e executa `run_server.py`.

### 1.4 Permitir o restart sem senha (para o CI)

O job de deploy roda `sudo systemctl restart g04`. Para que isso funcione sem prompt de senha, conceda ao usuário do runner a permissão específica via `sudoers` (`sudo visudo`):

```
cc06-g4 ALL=(ALL) NOPASSWD: /bin/systemctl restart g04
```

---

## 2. Deploy automático (fluxo padrão)

O deploy é disparado pelo pipeline definido em [.gitlab-ci.yml](../.gitlab-ci.yml) e roda em dois estágios:

| Estágio | Quando roda | O que faz |
|---|---|---|
| `test` | Em todo push/merge request | Cria venv, instala dependências e roda os testes do otimizador e do backend |
| `deploy` | Apenas na branch `develop` | `rsync` do código para `/home/cc06-g4/g04/`, `chmod +x` no `start.sh` e `systemctl restart g04` |

### Como publicar uma nova versão

1. Garanta que os testes passam localmente:

   ```bash
   python -m unittest discover -s apps/algoritmo_simplex/tests -p "test_*.py"
   python -m unittest discover -s apps/backend/tests -p "test_*.py"
   ```

2. Faça merge das alterações na branch **`develop`**.
3. O pipeline roda `test` e, se passar, executa `deploy` automaticamente.
4. Acompanhe o pipeline no GitLab (**CI/CD → Pipelines**) até o job `deploy` ficar verde.

> Apenas a branch `develop` publica em produção (regra `only: develop`). Pushes em outras branches só rodam os testes.

O passo de `deploy` usa `rsync -a --exclude='.git'`, ou seja, **copia** arquivos novos/alterados mas **não apaga** o que já existe no destino. Arquivos locais não versionados (como `.env`, `uploads/` e caches) são preservados entre deploys.

---

## 3. Deploy manual (contingência)

Caso o CI esteja indisponível, é possível publicar manualmente a partir do servidor:

```bash
# A partir de um checkout do repositório no servidor
rsync -a --exclude='.git' /caminho/do/checkout/ /home/cc06-g4/g04/
chmod +x /home/cc06-g4/g04/apps/backend/start.sh
sudo systemctl restart g04
```

---

## 4. Disponibilizar para os usuários (acesso externo)

`run_server.py` faz o bind em `APP_HOST_BIND` (derivado de `APP_HOST`). Para tornar a aplicação acessível pela internet, exponha-a por um domínio público. Há duas abordagens comuns:

### Opção A — Túnel (ex.: Cloudflare Tunnel)

Indicado quando o servidor não tem IP/porta pública. O túnel aponta o domínio público para a porta local do frontend:

- Frontend (`FRONTEND_PORT`, ex. `5500`) → `https://maiorais.com`
- API (`APP_PORT`, ex. `8000`) → caminho `/api` consumido pelo frontend

Defina `FRONTEND_ORIGINS=https://maiorais.com` no `.env` (passo 1.2) para liberar o CORS.

### Opção B — Reverse proxy (ex.: Nginx)

Em um servidor com porta pública, coloque um Nginx à frente, servindo o frontend e encaminhando `/api` para o backend, com TLS terminado no proxy. Mantenha `FRONTEND_ORIGINS` apontando para o domínio público.

> **`runtime-config.js`:** o frontend descobre a URL da API em tempo de execução a partir de `window.API_BASE_URL`, escrito por `run_server.py` com base em `APP_HOST`/`APP_PORT`. Ao publicar atrás de um domínio próprio, ajuste `APP_HOST`/`APP_PORT` no `.env` para que o arquivo aponte para a URL pública da API (ex.: `https://maiorais.com/api`).

---

## 5. Verificação pós-deploy

Após cada publicação, confirme que a aplicação está saudável:

```bash
# Estado do serviço
sudo systemctl status g04

# Health check da API (no servidor)
curl http://127.0.0.1:8000/api/health

# Acesso público (de fora)
curl https://maiorais.com
```

Verificações funcionais:

- A documentação interativa responde em `{APP_HOST}:{APP_PORT}/docs`.
- O frontend abre no domínio público e carrega o Cockpit.
- Um upload de teste em **Gerar Limites** cria uma consulta e o pipeline avança de `pendente` até concluído.

---

## 6. Operação e manutenção

### Logs

```bash
# Acompanhar em tempo real
sudo journalctl -u g04 -f

# Últimas 200 linhas
sudo journalctl -u g04 -n 200
```

### Controle do serviço

```bash
sudo systemctl restart g04   # reiniciar
sudo systemctl stop g04      # parar
sudo systemctl start g04     # iniciar
```

### Atualizar dependências

O `start.sh` reinstala as dependências (`requirements.txt` do otimizador e do backend) a cada inicialização. Para forçar a recriação da virtualenv:

```bash
rm -rf /home/cc06-g4/g04/apps/backend/.venv
sudo systemctl restart g04
```

### Migrations de banco

São aplicadas automaticamente na inicialização. Para adicionar uma nova, inclua o arquivo `.sql` numerado em `apps/backend/db/migrations/` e publique normalmente — a aplicação roda as pendentes no próximo restart.

### Backup

Faça backup periódico de:

- **Banco PostgreSQL** (`pg_dump credito`) — dados de safras, consultas e resultados.
- **`apps/backend/.env`** — configuração de produção (não versionada).
- **`apps/backend/uploads/`** — parquets enviados, se precisarem ser reprocessados.

---

## 7. Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| Serviço não sobe (`systemctl status g04` em falha) | Erro no `.env`, banco inacessível ou porta ocupada | Ver `journalctl -u g04 -n 200`; checar credenciais e conectividade do PostgreSQL |
| Frontend abre mas as chamadas à API falham (erro de CORS no console) | `FRONTEND_ORIGINS` não inclui o domínio público | Ajustar `FRONTEND_ORIGINS` no `.env` e reiniciar |
| Frontend chama URL de API errada | `APP_HOST`/`APP_PORT` não refletem o domínio público | Ajustar no `.env` e reiniciar (regenera `runtime-config.js`) |
| Frontend não sobe, mas a API responde | Porta do frontend ocupada ou diretório ausente | Aviso `[warn]` no log; liberar `FRONTEND_PORT` ou ajustar no `.env` |
| Deploy do CI falha em `systemctl restart g04` | Permissão `sudo` ausente para o runner | Conferir a regra `NOPASSWD` em `sudoers` (passo 1.4) |
| Pipeline para no estágio `test` | Teste quebrado | Reproduzir localmente os comandos do `.gitlab-ci.yml` e corrigir antes de publicar |
