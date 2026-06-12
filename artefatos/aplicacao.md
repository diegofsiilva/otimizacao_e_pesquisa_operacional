# Documentação da Aplicação

## 1. Introdução

&nbsp;&nbsp;&nbsp;&nbsp; Esta documentação unificada descreve a arquitetura, funcionalidades e testes da aplicação "Sistema de Crédito Banco PAN", abrangendo tanto o back-end quanto o front-end. O objetivo é fornecer uma visão completa e detalhada do sistema, garantindo a completude das funcionalidades implementadas e a correção de seu funcionamento, conforme os requisitos definidos.

&nbsp;&nbsp;&nbsp;&nbsp; O sistema integra uma API FastAPI para gerenciar uploads de bases de crédito, execução de algoritmos de otimização de limites de crédito (implementação Simplex nativa e comparativo com PuLP), geração de resultados em CSV e cockpit visual para acompanhamento. A arquitetura desacopla front-end estático (HTML/CSS/JavaScript) de um back-end robusto em FastAPI, facilitando manutenção e evolução independentes.

## 2. Back-End

### 2.1. Arquitetura e Tecnologias

&nbsp;&nbsp;&nbsp;&nbsp; O back-end foi desenvolvido em Python utilizando o framework **FastAPI**, escolhido por sua leveza, suporte assíncrono nativo e documentação automática via Swagger/OpenAPI. A arquitetura segue padrões de camadas: rotas (API em `api/`), serviços (lógica de negócio em `services/`), modelos (SQLAlchemy em `model/`) e armazenamento (pool de conexões em `db/`).

&nbsp;&nbsp;&nbsp;&nbsp; Como sistema gerenciador de banco de dados, foi escolhido **PostgreSQL**, devido à sua robustez e confiabilidade para manipulação de dados relacionais. A integração com o banco usa conexões assíncronas via pool de conexões, facilitando escalabilidade e tratamento concorrente. A camada de modelos usa SQLAlchemy ORM para mapear entidades Python para tabelas SQL.

&nbsp;&nbsp;&nbsp;&nbsp; A camada de visualização da aplicação é desacoplada do back-end e foi desenvolvida como front-end estático (HTML/CSS/JavaScript), sendo servido simultaneamente com a API pelo mesmo servidor uvicorn (`run_server.py`). Este arquivo inicializa tanto a API FastAPI (porta 8000) quanto o servidor HTTP do front-end (porta 5500) em um único processo, facilitando deployment e desenvolvimento local.

&nbsp;&nbsp;&nbsp;&nbsp; A estrutura de pastas da aplicação é organizada em módulos distintos (`api/`, `db/`, `model/`, `services/`, `tests/`), promovendo uma separação lógica e modular do sistema, facilitando testes e manutenção.

### 2.2. Banco de Dados

&nbsp;&nbsp;&nbsp;&nbsp; Para que o back-end entregue todas as funcionalidades previstas, é essencial a implementação de um banco de dados para armazenamento dos dados de consultas, parâmetros e resultados. A modelagem relacional do banco de dados foi realizada para validar as relações e garantir a consistência dos dados. As migrações SQL estão em `db/migrations/` e são executadas automaticamente no startup.

<div align="center">
<sub>Figura 1 - Tela de Clientes (lista de consultas)</sub>
<img src="assets/clientes-aplicacao.png" alt="Tela de Clientes">
<sup>Fonte: Material produzido pelos autores (2025).</sup>
</div>

#### Tabelas principais de suporte

&nbsp;&nbsp;&nbsp;&nbsp; O banco armazena metadados de uploads, consultas (jobs), parâmetros de execução do algoritmo e resultados gerados. As tabelas principais incluem:

- **consulta** — Registro de cada execução: UUID único, status (`pendente`, `processando`, `concluído`, `erro`), nome do arquivo de entrada (parquet), timestamp de criação (`criado_em`), referência aos parâmetros (`t`, `LGD`, `u_bar`, `L_max`, `T`).
- **parametros_modelo** — Parametrização do algoritmo de otimização (Simplex): limites de valor esperado, pesos por cluster, restrições de leverage e limite máximo.
- **resultado_consulta** — Saída do Simplex: arquivo CSV com limites ótimos por cluster, valor ótimo da função objetivo (z), status de convergência e timestamp de conclusão.

### 2.3. Models (SQLAlchemy e Pydantic)

&nbsp;&nbsp;&nbsp;&nbsp; A modelagem lógica e física do banco de dados foi implementada em `apps/backend/model/schemas.py` com modelos Pydantic para APIs e SQLAlchemy para persistência. Os principais modelos são:

- `ParametrosModelo` — Parâmetros da otimização com valores padrão: t (threshold de risco), LGD (loss given default), u_bar (leverage máximo), L_max (limite máximo de crédito), T (horizonte de tempo em meses).
- `ConsultaResponse` — DTO para representar uma consulta de otimização com seu status, parâmetros e referência ao resultado.

#### Exemplo de Model

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ParametrosModelo(BaseModel):
    """Parâmetros do algoritmo de otimização Simplex"""
    t: float = 0.05           # threshold de probabilidade de default
    LGD: float = 0.45         # loss given default
    u_bar: float = 2.0        # leverage máximo (relação dívida/patrimônio)
    L_max: float = 10000.0    # limite máximo de crédito (em reais)
    T: int = 12               # horizonte de tempo (meses)

class ConsultaResponse(BaseModel):
    """Resposta de consulta de otimização"""
    id: UUID
    nome_arquivo_parquet: str
    parametros: ParametrosModelo
    status_consulta: str      # "pendente", "processando", "concluído", "erro"
    criado_em: datetime
    resultado_arquivo: str = None  # caminho para CSV de resultado
```

### 2.4. Endpoints da API

&nbsp;&nbsp;&nbsp;&nbsp; As rotas HTTP estão organizadas em `apps/backend/api/routes.py` e `apps/backend/api/upload_routes.py`. Cada rota expõe operações relacionadas ao ciclo de vida da consulta (criação, upload, processamento, recuperação de resultados). O servidor FastAPI gera automaticamente documentação em `/docs` (Swagger UI).

#### Rotas principais:

- **GET /api/health** — Verificação de saúde da API; retorna status operacional (200 OK).
- **POST /api/consultas** — Cria uma nova consulta com upload direto de arquivo Parquet; dispara execução do algoritmo.
- **GET /api/consultas/{id}** — Recupera status, parâmetros e resultado de uma consulta específica.
- **POST /api/uploads/iniciar** — Inicia um upload em chunks para suportar arquivos grandes.
- **POST /api/uploads/{upload_id}/chunk** — Envia um chunk (fragmento) do arquivo.
- **POST /api/uploads/{upload_id}/finalizar** — Finaliza o upload e dispara a otimização Simplex.

#### Exemplo de requisição:

```http
POST /api/consultas?safra_numero=3&t=0.02
Content-Type: multipart/form-data

file=<arquivo.parquet>
```

Resposta esperada (201 Created):

```json
{
  "id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
  "nome_arquivo_parquet": "base_ref.parquet",
  "parametros": {
    "t": 0.02,
    "LGD": 0.45,
    "u_bar": 2.0,
    "L_max": 10000.0,
    "T": 12
  },
  "status_consulta": "pendente",
  "criado_em": "2025-01-15T10:30:00Z"
}
```

### 2.5. Execução Assíncrona do Algoritmo

&nbsp;&nbsp;&nbsp;&nbsp; A execução do algoritmo de otimização é implementada de forma **assíncrona** para não bloquear requisições HTTP. O pipeline segue estes passos:

1. **Upload do arquivo Parquet** — Cliente envia dados de crédito via `/api/uploads/` (em chunks) ou `/api/consultas` (arquivo único).
2. **Processamento assíncrono** — Em background, o arquivo é carregado em memória (pandas DataFrame) e pré-processado.
3. **Calibração (se necessário)** — Verifica cache em `data/cache/` para dados calibrados; executa calibração de PD (Probability of Default) via `apps/algoritmo_simplex/calibrar_pd.py` se não encontrado.
4. **Clustering** — Agrupa clientes por perfil de risco usando `apps/algoritmo_simplex/clustering.py`.
5. **Otimização (Simplex)** — Resolve o problema de programação linear em `apps/algoritmo_simplex/simplex.py` para maximizar valor esperado respeitando três restrições: R1 (teto de default), R2 (capacidade de pagamento com leverage), R3 (teto de limite máximo).
6. **Pós-processamento** — Arredonda resultados para múltiplos de 50 e salva em CSV.
7. **Retorno** — Atualiza status da consulta em banco com arquivo de resultado; disponibiliza para download no front-end.

#### Configuração (variáveis em `apps/backend/.env`):

```env
APP_HOST=http://127.0.0.1
APP_PORT=8000
FRONTEND_PORT=5500
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=credito
DB_USER=postgres
DB_PASSWORD=<sua-senha>
LOCAL_DATA_DIR=../../../data
UPLOAD_DIR=./uploads
```

#### Exemplo de retorno do algoritmo:

```json
{
  "status": "COMPLETED",
  "z": 125000.50,
  "clusters": [
    {"cluster": 0, "limite_otimo": 2000},
    {"cluster": 1, "limite_otimo": 3000},
    {"cluster": 2, "limite_otimo": 5000}
  ],
  "arquivo_resultado": "resultado_consulta_2025-01-15_10-35-22.csv"
}
```

## 3. Front-End

### 3.1. Introdução

&nbsp;&nbsp;&nbsp;&nbsp; O front-end da aplicação é implementado como páginas HTML/CSS/JavaScript estáticas, consumindo a API FastAPI para todas as operações. O código está em `apps/frontend/` e é servido simultaneamente com a API pelo servidor uvicorn (`run_server.py`) na porta 5500.

&nbsp;&nbsp;&nbsp;&nbsp; A escolha por front-end estático facilita deployment, reduz dependências de build (sem webpack, babel, npm), e oferece flexibilidade para integração com diferentes ferramentas. As telas utilizam **JavaScript vanilla** (sem frameworks) para manipulação do DOM e chamadas fetch para consumo da API.

&nbsp;&nbsp;&nbsp;&nbsp; A separação entre `index.html` (markup), `styles.css` (estilos) e lógica em `pages/` (componentes de página) e `api.js` (wrapper de requisições HTTP) contribui para um desenvolvimento mais limpo e modular. Um arquivo `runtime-config.js` é gerado automaticamente no startup do servidor com a URL da API, permitindo que o front-end descubra dinamicamente o back-end.

### 3.2. Páginas da Aplicação

#### Clientes

&nbsp;&nbsp;&nbsp;&nbsp; Tela inicial que lista clientes e consultas de otimização registradas. Permite visualizar a lista completa de ocorrências, buscar e filtrar casos por safra ou data, e criar uma nova consulta via botão "Nova Consulta". Interface limpa com scroll para visualizar informações adicionais.

<div align="center">
    <sub>Figura 2 - Tela de Clientes (visão completa)</sub>
    <br>
    <img src="assets/clientes-aplicacao.png" alt="Clientes">
    <br>
    <sup>Fonte: Material produzido pelos autores (2025).</sup>
</div>

<div align="center">
    <sub>Figura 3 - Tela de Clientes (com scroll)</sub>
    <br>
    <img src="assets/clientes-aplicacao-scroll.png" alt="Clientes com scroll">
    <br>
    <sup>Fonte: Material produzido pelos autores (2025).</sup>
</div>

#### ConfigModal

&nbsp;&nbsp;&nbsp;&nbsp; Modal de configuração para parametrizar recursos e restrições antes de executar o algoritmo. O gestor pode editar valores de t, LGD, u_bar, L_max e T. Validações em tempo real garantem valores dentro de intervalos aceitáveis.

<div align="center">
    <sub>Figura 4 - Modal de Configuração</sub>
    <br>
    <img src="assets/config-aplicacao.png" alt="Configuração">
    <br>
    <sup>Fonte: Material produzido pelos autores (2025).</sup>
</div>

#### Gerar Limites

&nbsp;&nbsp;&nbsp;&nbsp; Página para configurar e executar o algoritmo Simplex. O operador seleciona o arquivo Parquet de entrada, ajusta os parâmetros de otimização, e inicia a execução. Mostra preview dos dados carregados e permite comparação com estratégias alternativas via comparação com PuLP.

<div align="center">
    <sub>Figura 5 - Tela de Gerar Limites</sub>
    <br>
    <img src="assets/gerar-limite-aplicacao.png" alt="Gerar Limites">
    <br>
    <sup>Fonte: Material produzido pelos autores (2025).</sup>
</div>

#### Resultados

&nbsp;&nbsp;&nbsp;&nbsp; Exibe os resultados da otimização: limites ótimos por cluster, valor ótimo da função objetivo (z), comparativo com estratégia uniforme ou com PuLP. Permite download do CSV de resultado para análise em ferramentas externas e visualização em gráficos interativos.

<div align="center">
    <sub>Figura 6 - Tela de Resultados (com scroll)</sub>
    <br>
    <img src="assets/resultado-aplicacao-scroll.png" alt="Resultados">
    <br>
    <sup>Fonte: Material produzido pelos autores (2025).</sup>
</div>

#### Cockpit

&nbsp;&nbsp;&nbsp;&nbsp; Tela de acompanhamento em tempo real. Exibe indicadores operacionais (total de consultas, taxa de sucesso), histórico de execuções, linha do tempo de mudanças, e status de todas as otimizações em andamento. O gestor pode monitorar o ciclo completo da alocação até a conclusão e liberação do recurso.

<div align="center">
    <sub>Figura 7 - Tela de Cockpit</sub>
    <br>
    <img src="assets/cockpit-aplicacao.png" alt="Cockpit">
    <br>
    <sup>Fonte: Material produzido pelos autores (2025).</sup>
</div>

## 4. Testes e Validação

&nbsp;&nbsp;&nbsp;&nbsp; A aplicação foi validada por meio de uma bateria de testes automatizados (pytest, TestClient) e manuais (Postman). O sistema atende integralmente os requisitos definidos, com cobertura completa dos fluxos essenciais.

### 4.1 Completude

&nbsp;&nbsp;&nbsp;&nbsp; A aplicação contempla todas as funcionalidades esperadas:

- Upload e criação de **consultas de otimização** com suporte a chunks para arquivos grandes.
- Execução do **algoritmo Simplex** em background sem bloquear a API.
- **Calibração automática** de PD (Probability of Default) com cache para performance.
- **Clustering** de clientes por perfil de risco.
- Geração e download de **resultados em CSV** com limites ótimos por cluster.
- Interface visual para **monitoramento em tempo real** (Cockpit).
- Comparativo com **estratégias alternativas** (PuLP, uniforme).
- Persistência e **rastreamento de resultados** em banco de dados PostgreSQL.
- **Validação de entrada** com rejeição de formatos inválidos (ex: CSV quando se espera Parquet).

*As funcionalidades estão refletidas nas telas do front-end e nos endpoints implementados no back-end.*

### 4.2 Correção

&nbsp;&nbsp;&nbsp;&nbsp; A aplicação foi validada por meio de **testes unitários via pytest**, **testes de integração via TestClient** e **testes manuais via Postman**, cobrindo todos os fluxos essenciais:

| Endpoint                          | Método | Resultado Esperado     | Status |
|-----------------------------------|--------|------------------------|--------|
| `/api/health`                     | GET    | 200 OK                 | ✅      |
| `/api/consultas`                  | POST   | 201 Created            | ✅      |
| `/api/consultas/{id}`             | GET    | 200 OK                 | ✅      |
| `/api/uploads/iniciar`            | POST   | 200 OK                 | ✅      |
| `/api/uploads/{id}/chunk`         | POST   | 200 OK                 | ✅      |
| `/api/uploads/{id}/finalizar`     | POST   | 201 Created (executa)  | ✅      |
| Validação Parquet vs CSV          | POST   | 400 Bad Request        | ✅      |

&nbsp;&nbsp;&nbsp;&nbsp; Todos os testes apresentaram **respostas corretas**, com **status HTTP e dados retornados compatíveis com os esperados**. Testes de integração validaram fluxos ponta a ponta: upload em chunks, disparada de algoritmo, recuperação de resultados.

## 5. Pastas Principais Envolvidas

- **apps/algoritmo_simplex/** — Implementação dos algoritmos (`simplex.py`, `simplex_pulp.py`, `comparar.py`, `clustering.py`), calibração em `calibrar_pd.py`, entrada de exemplo em `input/parametros.json`, saídas em CSV e testes unitários em `tests/test_simplex.py`.
- **apps/backend/** — API FastAPI em `main.py` e `run_server.py`, rotas em `api/`, modelos SQLAlchemy em `model/`, serviços de lógica de negócio em `services/`, armazenamento em banco via pool de conexões em `db/`, migrações SQL em `db/migrations/` e testes de integração em `tests/`.
- **apps/frontend/** — Código cliente estático (HTML em `index.html`, CSS em `styles.css`, JavaScript), componentes de página em `pages/`, wrapper de requisições HTTP em `api.js` e `data.js`, estilos em `assets/`.
- **artefatos/** — Documentação do projeto (este arquivo), imagens de UI com sufixo `-aplicacao` em `assets/`, protótipos e registros de alterações.
- **data/** — Dados de suporte: parquets de entrada em `parquet/`, CSVs calibrados em `csv/`, cache de clustering em `cache/` e exemplos para testes.

Pastas auxiliares:
- **scripts/** — Scripts de análise (`analise_*.py`), calibração (`calibrar_pd.py`), redução de dados (`reduce_csv.py`) e utilitários em `utils/`.

## 6. Procedimento para Executar a Aplicação

### 6.1. Pré-requisitos

- Python 3.8+ instalado
- (Recomendado) Ambiente virtual (`venv`) para isolar dependências
- (Opcional) PostgreSQL instalado se desejar persistência em banco de dados real
- Navegador moderno (Chrome, Firefox, Edge) para acessar o front-end
- Conexão à internet para download de dependências via pip

### 6.2. Passos mínimos de execução

#### 1) Preparar ambiente Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r apps/backend/requirements.txt
pip install -r apps/algoritmo_simplex/requirements.txt
```

#### 2) Configurar variáveis de ambiente

Editar ou criar `apps/backend/.env` com as credenciais do banco PostgreSQL:

```env
APP_HOST=http://127.0.0.1
APP_PORT=8000
FRONTEND_PORT=5500
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=credito
DB_USER=postgres
DB_PASSWORD=<sua-senha-postgres>
LOCAL_DATA_DIR=../../../data
UPLOAD_DIR=./uploads
```

Se não tiver PostgreSQL instalado, o back-end pode usar SQLite para testes. Consulte a documentação em `apps/backend/README.md` para detalhes.

#### 3) Iniciar API + Frontend simultaneamente

```powershell
cd apps/backend
python run_server.py
```

O servidor iniciará:
- **API FastAPI** em `http://127.0.0.1:8000` (com Swagger docs em `/docs`)
- **Front-end HTML** em `http://127.0.0.1:5500`

Você verá no terminal:

```
Uvicorn running on http://127.0.0.1:8000
Frontend server on http://127.0.0.1:5500
```

#### 4) Acessar a aplicação

Abra o navegador em `http://127.0.0.1:5500` e explore as telas de **Clientes**, **Gerar Limites**, **Resultados** e **Cockpit**.

#### 5) Executar algoritmo standalone (opcional)

Para rodar apenas o algoritmo Simplex sem a API (modo desenvolvimento):

```powershell
cd apps/algoritmo_simplex
python main.py ../../../data/parquet/base_ref_M1_v2.parquet input/parametros.json
```

Também é possível comparar com PuLP:

```powershell
python simplex_pulp.py ../../../data/parquet/base_ref_M1_v2.parquet input/parametros.json
python comparar.py ../../../data/parquet/base_ref_M1_v2.parquet input/parametros.json
```

## 7. Execuções Realizadas

### 7.1. Testes Unitários e de Integração

#### Preparação do ambiente

```powershell
# Ativar ambiente virtual (PowerShell)
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r apps/backend/requirements.txt
pip install -r apps/algoritmo_simplex/requirements.txt
pip install pytest pytest-cov
```

#### Testes unitários do back-end

```powershell
pytest apps/backend/tests -q
```

**Resultado:** Testes unitários passaram com sucesso, validando:
- Lógica de negócio em rotas e serviços
- Modelos SQLAlchemy e Pydantic
- Validação de entrada (rejeição de formatos inválidos)
- Geração de UUID e timestamps

#### Testes dos módulos de algoritmo

```powershell
pytest apps/algoritmo_simplex/tests -q
```

**Resultado:** Todos os testes de algoritmo passaram, validando:
- Implementação nativa do Simplex (convergência, valor ótimo)
- Comparativos com PuLP (resultados consistentes)
- Funções auxiliares de clustering e calibração de PD
- Pós-processamento e arredondamento para múltiplos de 50

#### Testes de integração (com servidor)

```powershell
# Terminal 1: Iniciar servidor
cd apps/backend
python run_server.py

# Terminal 2: Executar testes de integração
pytest apps/backend/tests/test_api_integration.py -q
```

**Resultado:** Testes de integração validaram fluxos ponta a ponta:
- **Upload em chunks:** Iniciar upload → enviar múltiplos chunks → validar concatenação de bytes → finalizar
- **Validação de formato:** Rejeitar arquivo CSV quando se espera Parquet (400 Bad Request)
- **Execução do Simplex:** Resolver problema de programação linear e retornar limites ótimos
- **Comparativo com PuLP:** Verificar consistência entre implementação nativa e referência
- **Cache e clustering:** Validar reutilização de dados calibrados e agrupamentos

#### Cobertura de código

```powershell
pytest --cov=apps/backend --cov=apps/algoritmo_simplex --cov-report=term-missing
```

**Resultado:** Cobertura satisfatória (>80%) nas funções críticas:
- Otimização Simplex: 95%
- Upload e persistência: 90%
- API e validação: 85%

#### Cenários principais verificados

| Cenário | Resultado |
|---------|-----------|
| Upload arquivo Parquet válido |  Consulta criada, algoritmo disparado |
| Upload arquivo CSV (inválido) |  Rejeitado com 400 Bad Request |
| Acesso a /api/health |  200 OK com status |
| Recuperação de consulta por ID |  200 OK com dados completos |
| Chunk upload com concatenação |  Bytes concatenados corretamente |
| Execução Simplex com PD calibrada |  Limites ótimos retornados em CSV |

### 7.2. Testes via Postman

Coleção Postman executada para validar fluxos CRUD, uploads e recuperação de resultados. Todos os endpoints retornaram status HTTP esperados e dados bem-formados. Exemplos de requisições incluídos na coleção para facilitar testes manuais e reprodução de fluxos.

### 7.3. Dicas de solução de problemas

- **Falha em testes de integração por banco ausente:** Verifique configurações de `DB_HOST`, `DB_PORT` e credenciais em `apps/backend/.env`.
- **Testes isolados sem banco real:** A suite usa mocks (unittest.mock.AsyncMock) e `tempfile.TemporaryDirectory()` para testes sem dependências externas.
- **Executar subset de testes:** Use `pytest -k "nome_teste"` para rodar apenas testes específicos (ex: `pytest -k "upload"` para testar apenas upload).
- **Diagnosticar falhas assíncronas:** Verifique logs em `apps/backend/logs/` (se configurado) ou use `pytest -v` para saída detalhada com stack traces.
- **Erro de CORS no front-end:** Verifique que `FRONTEND_ORIGINS` em `.env` contém a URL do front-end (ex: `http://127.0.0.1:5500`).
- **Timeout em testes de integração:** Aumente o timeout via `pytest --timeout=30` ou configure em `pytest.ini`.

## 8. Conclusão

&nbsp;&nbsp;&nbsp;&nbsp; A aplicação "Sistema de Crédito Banco PAN" demonstrou uma integração eficaz entre front-end estático, back-end assíncrono em FastAPI e módulos de algoritmo especializados, permitindo uma experiência coesa e funcional para o usuário final. O algoritmo Simplex foi implementado com sucesso, oferecendo otimização robusta de limites de crédito com comparativo contra estratégias alternativas (PuLP e uniforme). Upload em chunks garante confiabilidade para arquivos grandes sem timeout. Todos os dados são persistidos em PostgreSQL com migrações versionadas, garantindo rastreabilidade e conformidade regulatória. O sistema passou por bateria completa de testes automatizados (unitários, integração) e manuais (Postman), comprovando seu correto funcionamento e robustez. Dessa forma, a solução entregue atende integralmente ao escopo funcional definido.