**Descrição**

Esta aplicação implementa um sistema de apoio à alocação de recursos para ocorrências operacionais. O conjunto inclui:
- um front-end (interface do operador/gestor) com telas para criar ocorrências, editar recursos, executar algoritmos e aceitar recomendações;
- um back-end REST que expõe as APIs usadas pelo front-end e integra os algoritmos e o armazenamento de dados;
- módulos de algoritmos (implementações do Simplex e comparativo com Pulp) usados para gerar propostas de alocação e comparativos entre estratégias.

O objetivo é permitir ao operador criar uma ocorrência, executar diferentes algoritmos de alocação, comparar resultados e acompanhar o fluxo da ocorrência até sua finalização e liberação de recursos.

**Pastas principais envolvidas**

- **apps/algoritmo_simplex/**: implementação dos algoritmos (`simplex.py`, `simplex_pulp.py`, `comparar.py`, `clustering.py`), entradas de exemplo em `input/parametros.json` e testes unitários em `tests/`.
- **backend/**: aplicação servidor (API), modelos, serviços, armazenamento e migrações SQL. Contém `run_server.py` para iniciar a API, `requirements.txt` com dependências e testes de integração em `tests/`.
- **frontend/**: código cliente estático (HTML/CSS/JS) e componentes em `pages/` que implementam as telas do operador e do gestor (Clientes, Cockpit, Resultados, ConfigModal, etc.).
- **artefatos/**: documentação do projeto (este arquivo), imagens, protótipos e registros de alterações do front-end.
- **data/**: dados de apoio, caches e exemplos (parquet/csv) usados em análises e visualizações.

Outras pastas auxiliares:
- **scripts/**: scripts de análise, geração de dados e utilitários usados no desenvolvimento.

**Pré-requisitos**

- Python 3.8+ instalado
- Recomenda-se criar e ativar um ambiente virtual (`venv`)
- Navegador moderno para abrir o front-end local
- (Opcional) Serviços adicionais conforme instruções do README (ex.: Neo4j, MongoDB) se for utilizar integrações específicas do projeto

**Procedimento para executar a aplicação (passos mínimos)**

1) Preparar ambiente Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install -r apps/algoritmo_simplex/requirements.txt
```

2) Iniciar o back-end (API)

```powershell
python backend/run_server.py
```

O servidor expõe as rotas definidas em `backend/api/` e é consumido pelo front-end.

3) Servir o front-end localmente

Opção A — abrir `frontend/index.html` diretamente no navegador (modo estático).

Opção B — servir via um servidor HTTP simples (recomendado para evitar problemas de CORS):

```powershell
cd frontend
python -m http.server 8000
# acessar http://localhost:8000
```

**Navegação principal da aplicação**

1) Página inicial / Clientes

- Ao abrir o front-end, o usuário chega na tela de clientes e ocorrências.
- É possível visualizar a lista de ocorrências, buscar e filtrar casos, e criar uma nova ocorrência.
- A imagem abaixo mostra a tela principal de clientes no fluxo da aplicação.

![Clientes](assets/clientes-aplicacao.png)

- A tela também permite mais detalhes e rolagem para visualizar outras informações da ocorrência.

![Clientes rolando](assets/clientes-aplicacao-scroll.png)

2) Tela de Configuração de recursos

- Nesta etapa, o gestor pode editar e parametrizar os recursos disponíveis antes de rodar o algoritmo.
- A edição de recursos está acessível para definir quantidades, tipos e limites de alocação.

![Configuração](assets/config-aplicacao.png)

3) Tela de geração de limite / execução do algoritmo

- A página de geração de limite permite escolher as regras de alocação, acionar o cálculo e comparar resultados.
- O operador visualiza rapidamente os valores de entrada e inicia a execução do algoritmo.

![Gerar limite](assets/gerar-limite-aplicacao.png)

4) Tela de resultados e comparação de algoritmos

- Após a execução, o front-end apresenta as recomendações e comparativos entre alternativas.
- A navegação permite aceitar a sugestão, analisar alocação e seguir para a etapa de liberação de recurso.

![Resultado](assets/resultado-aplicacao-scroll.png)

5) Cockpit e acompanhamento de ocorrência

- A tela de cockpit reúne indicadores operacionais, histórico e a linha do tempo da ocorrência.
- Aqui o gestor pode acompanhar o ciclo da alocação até a conclusão e liberação do recurso.

![Cockpit](assets/cockpit-aplicacao.png)

4) Executar os algoritmos localmente (modo standalone)

Os módulos de algoritmo ficam em `apps/algoritmo_simplex/`.

Exemplos:

```powershell
python apps/algoritmo_simplex/main.py --input apps/algoritmo_simplex/input/parametros.json
python apps/algoritmo_simplex/simplex_pulp.py --input apps/algoritmo_simplex/input/parametros.json
python apps/algoritmo_simplex/comparar.py --input apps/algoritmo_simplex/input/parametros.json
```

Esses scripts geram saídas que também podem ser carregadas no front-end para visualização e comparação.

5) Testes

Preparação:

```powershell
# ativar ambiente (PowerShell)
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install -r apps/algoritmo_simplex/requirements.txt
pip install pytest pytest-cov
```

Executar testes unitários do back-end:

```powershell
pytest backend/tests -q
```

Executar testes dos módulos de algoritmo:

```powershell
pytest apps/algoritmo_simplex/tests -q
```

Executar um arquivo de teste específico (útil para depuração):

```powershell
pytest apps/algoritmo_simplex/tests/test_simplex.py -q
```

Testes de integração (requer servidor em execução):

1. Em um terminal, inicie a API:

```powershell
python backend/run_server.py
```

2. Em outro terminal, execute os testes de integração:

```powershell
pytest backend/tests/test_api_integration.py -q
```

Relatório de cobertura (opcional):

```powershell
pytest --cov=backend --cov=apps/algoritmo_simplex --cov-report=term-missing
```

Dicas de solução de problemas:
- Se os testes de integração falharem por dependências externas (BD, serviços), execute primeiro os testes unitários isolados.
- Verifique fixtures em `backend/tests/fixtures/` para dados necessários; alguns testes usam bases sintéticas que estão na pasta de fixtures.
- Para rodar apenas testes rápidos, especifique a pasta do projeto: `pytest apps/algoritmo_simplex/tests -q`.

Registro de execução dos testes (exemplo):
- `pytest apps/algoritmo_simplex/tests -q` — todos os testes de algoritmo passaram localmente.
- `pytest backend/tests -q` — maioria dos testes unitários passou; alguns testes de integração requereram iniciar o servidor e dados de fixtures.
