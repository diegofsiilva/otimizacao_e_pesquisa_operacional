# Inteli - Instituto de Tecnologia e Liderança

<p align="center">
  <a href="https://www.inteli.edu.br/">
    <img src="https://res.cloudinary.com/dwewomj84/image/upload/v1761355911/inteli_lfuayp.png" alt="Inteli" width=35%>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://www.bancopan.com.br/">
    <img src="./banco_pan.png" alt="Banco Pan" width=35%>
  </a>
</p>

<br>

<p align="center">
  <a href="https://www.inteli.edu.br/ciencia-da-computacao/">
    <img src="https://img.shields.io/badge/Inteli-Ciência_da_Computação-6B2FBF?style=flat-square" alt="Curso">
  </a>
  <img src="https://img.shields.io/badge/Módulo-6-6B2FBF?style=flat-square" alt="Módulo">
  <img src="https://img.shields.io/badge/Sprint-4_de_5-blue?style=flat-square" alt="Sprint">
  <img src="https://img.shields.io/badge/Status-Em_desenvolvimento-yellow?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Linguagem-Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Parceiro-Banco_Pan-E8440A?style=flat-square" alt="Parceiro">
</p>

<br>

# G04

## 👨‍🎓 Integrantes

- Diego Figueiredo Silva
- Lucas Garcia Rodrigues Lopes
- Luiz Gustavo Borges Oliveira
- Maria Clara Oliveira Santos
- Rebeca Namura Sbroglio
- Richard Dias Alves
- Teodoro Borges de Carvalho Neira

## 👩‍🏫 Professores

### Orientador

- [Tomaz Mikio Sasaki](https://www.linkedin.com/in/tmsasaki/)

### Instrutores

- [Bruna Mayer Costa](https://www.linkedin.com/in/bruna-mayer/)
- [Fillipe Manoel Xavier Resina](https://www.linkedin.com/in/fillipe-resina-b2211a22/)
- [Laíza Ribeiro Silva](https://www.linkedin.com/in/laizaribeiro/)
- [Maria Cristina Nogueira Gramani](https://www.linkedin.com/in/cristinagramani/)
- [Natalia Varela da Rocha Kloeckner](https://www.linkedin.com/in/natalia-k-37a62052/)
- [Rodolfo Goya](https://www.linkedin.com/in/rodolfo-goya-6ab187/)

## 📜 Descrição

O Banco Pan oferece cartões de crédito pré-aprovados a clientes correntistas. A decisão de qual limite oferecer a cada cliente é hoje tomada com base em tabelas fixas, que não consideram a heterogeneidade entre perfis e não controlam o risco agregado da carteira.

Este projeto substitui essa regra empírica por um modelo de otimização linear: dado um conjunto de restrições de risco e capacidade de pagamento definidas pelo parceiro, o modelo encontra os limites de crédito que maximizam o retorno líquido esperado do banco, entendido como a receita de interchange menos a perda esperada por inadimplência.

A solução agrupa os clientes elegíveis em clusters com perfis semelhantes e resolve um Problema de Programação Linear (PL) para cada conjunto de clusters, atribuindo a cada grupo o limite ótimo a ser ofertado. O algoritmo Simplex, implementado do zero em Python, é o motor de decisão do modelo.

## 📁 Estrutura do Projeto

```
g04/
├── apps/
│   ├── algoritmo_simplex/        # otimizador e pipeline de otimizacao
│   │   ├── clustering.py         # clusterizacao CART e agregacao por cluster
│   │   ├── main.py               # orquestra calibracao, clustering e Simplex
│   │   ├── models.py             # estruturas Problema e Tableau
│   │   ├── simplex.py            # implementacao propria do algoritmo Simplex
│   │   ├── simplex_pulp.py       # solver de referencia para comparacao
│   │   ├── comparar.py           # comparacao Simplex proprio x PuLP
│   │   ├── input/                # parametros JSON do modelo
│   │   └── tests/                # testes automatizados do otimizador
│   ├── backend/                  # API FastAPI usada pelo frontend
│   │   ├── api/                  # rotas REST e upload em chunks
│   │   ├── db/                   # conexao PostgreSQL e migrations
│   │   ├── model/                # schemas Pydantic
│   │   ├── services/             # regras de negocio e integracao com otimizador
│   │   ├── tests/                # testes unitarios, integracao HTTP e background worker
│   │   ├── main.py               # aplicacao FastAPI
│   │   ├── run_server.py         # sobe backend e frontend estatico juntos
│   │   ├── requirements.txt      # dependencias do backend
│   │   └── start.sh              # inicializacao no ambiente de deploy
│   └── frontend/                 # SPA React via CDN/Babel
│       ├── pages/                # telas Cockpit, Gerar Limites, Resultados, Clientes e Config
│       ├── assets/               # logo e fontes
│       ├── api.js                # cliente HTTP do backend
│       ├── data.js               # helpers e metadados de UI
│       ├── index.html            # ponto de entrada da aplicacao
│       └── styles.css            # estilos globais
├── artefatos/                    # documentacao tecnica das entregas
│   ├── back-end.md               # documentacao do backend e otimizador
│   ├── frontend.md               # documentacao do frontend
│   ├── entendimento_negocio.md
│   ├── entendimento_ux.md
│   ├── modelagem_matematica.md
│   ├── prototipo_frontend.md
│   └── comparacao_simplex.md
├── apresentacoes/                # apresentacoes das sprints
├── data/                         # dados do projeto e caches locais
│   ├── parquet/                  # arquivos Parquet de entrada
│   ├── csv/                      # tabelas intermediarias e auxiliares
│   └── cache/                    # parquets calibrados/clusterizados gerados
├── scripts/                      # utilitarios de preparacao, calibracao e analise
├── .gitlab-ci.yml                # pipeline de teste e deploy
└── README.md
```

## 🚀 Como executar

### Backend e frontend da aplicação

O modo recomendado para a entrega atual é subir o backend FastAPI e o frontend estático juntos pelo script do backend.

#### Pré-requisitos

- Python 3.11+
- PostgreSQL 14+
- Banco PostgreSQL criado para a aplicação
- Credenciais do banco configuradas em `apps/backend/.env`

#### 1. Configurar o backend

Na raiz do repositório:

```bash
cd apps/backend
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o arquivo de ambiente:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/macOS
cp .env.example .env
```

Edite `apps/backend/.env` com as credenciais do PostgreSQL:

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

#### 2. Subir backend e frontend juntos

Ainda dentro de `apps/backend`:

```bash
python run_server.py
```

Esse comando:

- sobe o backend em `http://127.0.0.1:8000`;
- executa as migrations automaticamente;
- sobe o frontend estático em `http://127.0.0.1:5500`;
- disponibiliza a documentação interativa em `http://127.0.0.1:8000/docs`.

#### 3. Executar somente o backend

Caso queira subir apenas a API:

```bash
cd apps/backend
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### 4. Executar somente o frontend

Caso queira subir apenas a interface:

```bash
cd apps/frontend
python -m http.server 5500
```

Abra no navegador:

```text
http://127.0.0.1:5500
```

Observação: para consumir um backend local, confira se `window.API_BASE_URL` em `apps/frontend/index.html` aponta para `http://127.0.0.1:8000/api`. Em ambiente publicado, esse valor pode apontar para a URL do deploy.

#### 5. Rodar os testes do backend e otimizador

Na raiz do repositório:

```bash
python -m unittest discover -s apps/algoritmo_simplex/tests -p "test_*.py"
python -m unittest discover -s apps/backend/tests -p "test_*.py"
```

Os testes cobrem o Simplex, contratos das rotas, upload em chunks, integração HTTP e execução do worker em background.

#### 6. Testar API via Bruno

As instruções para a utilização do Bruno estão presentes no arquivo README.md na pasta apps/backend/bruno/backend/.

### Pipeline do otimizador via terminal

### Pré-requisitos

Instale as dependências a partir do diretório `apps/algoritmo_simplex/`:

```bash
pip install -r apps/algoritmo_simplex/requirements.txt
```

### Preparação dos dados

Os arquivos `.parquet` fornecidos pelo parceiro devem ser colocados em `data/parquet/`. Todos os scripts abaixo devem ser executados a partir do diretório `scripts/`.

```bash
cd scripts
```

**Passo 1 - Calcular os fatores de calibração da PD**

Este script lê os três parquets (M1, M2, M3) diretamente de `data/parquet/`, calcula empiricamente os fatores de correção da probabilidade de inadimplência por decil de risco e salva o resultado em `data/csv/tabela_gamma_decil.csv`. Só precisa ser rodado uma vez, ou quando os dados de entrada forem atualizados.

```bash
python analise_09_calibracao_final.py
```

**Passo 2 - Converter o parquet para CSV**

Converte um arquivo `.parquet` de `data/parquet/` para `.csv` em `data/csv/`. Para a execução completa, use a safra desejada (M1, M2 ou M3):

```bash
python convert_parquet_to_csv.py base_ref_M1_v2.parquet clientes.csv
```

Para gerar uma versão reduzida (útil para testes rápidos):

```bash
python convert_parquet_to_csv.py base_ref_M1_v2.parquet clientes.csv --reduced 10
```

**Passo 3 - Calibrar a PD dos clientes**

Aplica os fatores de correção calculados no Passo 1 a cada cliente, adicionando a coluna `pd_calibrada` ao CSV. O arquivo de saída é salvo em `data/csv/` com o sufixo `_calibrado`:

```bash
python calibrar_pd.py clientes.csv
# gera → data/csv/clientes_calibrado.csv
```

**Passo 4 - Executar o modelo de otimização**

A partir da raíz do projeto (`g04/`), execute o pipeline completo passando o CSV calibrado e o arquivo de parâmetros:

```bash
cd ..
python apps/algoritmo_simplex/main.py clientes_calibrado.csv parametros.json
```

Na primeira execução, a clusterização é gerada automaticamente e salva em `data/csv/clientes_calibrado_clusters.csv`. Nas execuções seguintes, o arquivo clusterizado é reutilizado, tornando a execução significativamente mais rápida.

Os arquivos JSON de parâmetros devem estar em `apps/algoritmo_simplex/input/`.

## 📅 Histórico de versões

- 0.1.0 - 30/04/2026
  - Sprint 1 - Definição do contexto de negócio e modelagem matemática inicial

- 0.2.0 - 15/05/2026
  - Sprint 2 - Refinamento do modelo matemático, implementação do algoritmo Simplex e protótipo do front-end

- 0.3.0 - 29/05/2026
  - Sprint 3 - Clusterização do algoritmo, desenvolvimento do front-end, back-end e artigo
- 0.4.0 - xx/xx/xxxx

- 0.5.0 - xx/xx/xxxx

## 📋 Licença/License

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://git.inteli.edu.br/graduacao/2026-1b/t15/g04">G04</a> by <a href="https://www.inteli.edu.br/">Inteli</a>, Diego Figueiredo Silva, Lucas Garcia Rodrigues Lopes, Luiz Gustavo Borges Oliveira, Maria Clara Oliveira Santos, Rebeca Namura Sbroglio, Richard Dias Alves, Teodoro Borges de Carvalho Neira is licensed under <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>

