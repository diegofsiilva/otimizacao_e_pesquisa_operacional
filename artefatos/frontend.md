# Entrega Parcial — Front-end da Aplicação

## 1. User Stories Priorizadas

As User Stories abaixo foram priorizadas para esta primeira entrega com base no valor direto ao usuário final e na viabilidade de implementação sem integração ao back-end. A priorização seguiu a ordem de criticidade do fluxo principal: carregar dados → gerar limites → visualizar resultados → exportar.

| Prioridade | ID | Título | Persona |
|---|---|---|---|
| 1 | US01 | Carregar base de dados | Larissa (Data Science) |
| 2 | US04 | Gerar limite por cluster | Rodinei (Estratégia de Crédito) |
| 3 | US06 | Visualizar distribuição dos limites | Rodinei (Estratégia de Crédito) |
| 4 | US07 | Exportar resultados | Larissa (Data Science) |
| 5 | US02 | Ajustar clusterização | Larissa (Data Science) |
| 6 | US03 | Configurar metas de produção | Rodinei (Estratégia de Crédito) |
| 7 | US05 | Consultar restrições ativas | Rodinei (Estratégia de Crédito) |

### Implementação por User Story

**US01 — Carregar base de dados**
Implementada na página *Gerar Limites*. A interface apresenta uma dropzone com suporte a arrastar-e-soltar e seleção manual de arquivos `.csv` e `.xlsx`. Após o upload, o nome do arquivo é exibido com feedback visual na própria zona. A tabela de estrutura esperada do CSV orienta o usuário sobre as colunas obrigatórias antes do envio. A validação real das colunas será conectada ao back-end na próxima entrega.

**US04 — Gerar limite por cluster**
Após o upload, o botão *Executar Simplex* dispara a simulação (com delay de 1,2s simulando o processamento). O resultado exibe três mini-cards (Total de Clusters, Com Solução Viável, Sem Solução) e uma tabela com Cluster ID, Limite Sugerido e Status por cluster. Status "Solução Viável" aparece em verde com ícone de check; "Sem Solução" em vermelho com ícone X.

**US06 — Visualizar distribuição dos limites**
Implementada na página *Resultados*. Contém quatro visualizações em SVG puro: gráfico de barras (Limites por Cluster), gráfico de rosca (Distribuição por Status), gráfico de linha (Evolução Temporal de Limites) e gráfico de área (Distribuição por Faixa de Score). Todos renderizam dados mock interativamente.

**US07 — Exportar resultados**
O botão *Exportar CSV* na página *Resultados* gera e baixa um arquivo `limites_clusters.csv` com as colunas `cluster_id`, `limite_simplex`, `limite_pulp`, `status`. O botão só aparece quando há dados gerados (`hasData = true`). No Dashboard, o botão *Exportar* gera `clientes.csv` com ID, Score, Status, Limite e Cadastro via `Blob` e `URL.createObjectURL`.

**US02 / US03 — Ajustar clusterização e Configurar metas**
Parcialmente implementadas via modal de *Configurações*. O modal exibe parâmetros editáveis (Taxa de Interchange, LGD, Utilização Esperada, Teto Máximo de Limite) com sliders interativos e campos numéricos. Salvar/cancelar estão funcionais no front-end; a persistência ao back-end é prevista para a próxima entrega.

**US05 — Consultar restrições ativas**
Não implementada nesta entrega. Prevista para integração com o back-end, que retornará as restrições ativas por cluster.

---

## 2. Como Executar o Projeto

O front-end não possui dependências de build. Roda diretamente no browser via `file://` ou qualquer servidor HTTP estático.

### Opção A — Abrir direto no browser

```bash
# Navegue até a pasta do front-end
cd apps/frontend

# Abra o index.html no browser
# Windows
start index.html

# macOS
open index.html

# Linux
xdg-open index.html
```

### Opção B — Servidor HTTP local (recomendado para evitar erros de CORS)

**Com Python (sem instalação adicional):**

```bash
cd apps/frontend
python -m http.server 8080
# Acesse: http://localhost:8080
```

**Com Node.js:**

```bash
cd apps/frontend
npx serve .
# Acesse a URL exibida no terminal
```

**Com VS Code:**
Instale a extensão *Live Server*, clique com botão direito em `index.html` → *Open with Live Server*.

### Dependências (todas via CDN, sem instalação)

| Biblioteca | Versão | Finalidade |
|---|---|---|
| React | 18 | UI reativa |
| ReactDOM | 18 | Renderização no DOM |
| Babel Standalone | latest | Transpilação de JSX |
| Tailwind CSS | CDN | Estilização utilitária |
| Inter (Google Fonts) | — | Tipografia base |
| DrukHeavy (local) | — | Títulos e valores numéricos |

A fonte Druk Heavy é carregada de `assets/druk/Druk Family/Druk-Heavy-Trial.otf`. Caso o arquivo não esteja presente, os títulos fazem fallback para `Arial Black` sem impacto funcional.

### Estrutura de arquivos

```
apps/frontend/
├── index.html              # Entry point — carrega dados, páginas e monta o App
├── data.js                 # Dados mock globais (CLIENTS, CLUSTERS_UPLOAD, SOLVER_COMPARISON)
├── assets/
│   ├── Logo_PAN.jpg
│   └── druk/               # Fonte Druk Heavy (necessário colocar os .otf manualmente)
└── pages/
    ├── Navbar.js            # Navbar fixa com scroll-shrink
    ├── Dashboard.js         # Visão geral da carteira + tabela de clientes
    ├── GerarLimites.js      # Upload de base + execução do Simplex
    ├── Resultados.js        # Visualizações gráficas + comparação Simplex vs PuLP
    └── ConfigModal.js       # Modal de configuração de parâmetros
```

---

## 3. Diferenças em Relação ao Protótipo (Wireframes)

### 3.1 Melhorias implementadas

#### Paleta de cores — Midnight & Slate

**Wireframe:** paleta neutra com azul genérico e fundo branco.

**Implementação:** paleta estruturada Midnight & Slate — primário `#0D1B2A`, secundário `#1B3A5C`, accent `#2E6DA4`, superfície `#E8EFF7`, fundo `#E2EAF4`, tints `#D6E8F5` e `#B8D4EC`.

**Justificativa:** A identidade visual do Banco PAN é predominantemente navy/azul-escuro. A paleta adotada reforça essa identidade com hierarquia de cores clara, melhorando legibilidade e consistência com o brandbook.

---

#### Navbar flutuante com scroll-shrink

**Wireframe:** barra superior simples e estática.

**Implementação:** navbar fixa com gradiente `#2E6DA4 → #1B3A5C`, que encolhe de `h-16` para `h-12` ao rolar a página. Logo e nome do banco funcionam como link para o Dashboard.

**Justificativa:** Melhora a experiência em telas longas, preservando espaço vertical sem perder o acesso à navegação.

---

#### Tipografia Druk Heavy

**Wireframe:** tipografia padrão (Inter/system).

**Implementação:** Druk Heavy aplicada em todos os títulos de página (`h1`), valores numéricos dos KPI cards e contadores de cluster.

**Justificativa:** Confere identidade tipográfica forte, compatível com o estilo editorial do PAN e comum em sistemas financeiros de alta performance.

---

#### Estilo visual totalmente quadrado (sem bordas arredondadas)

**Wireframe:** elementos com bordas levemente arredondadas.

**Implementação:** todos os elementos usam cantos retos — cards, botões, inputs, badges, tabelas, modal.

**Justificativa:** Transmite seriedade e precisão, adequadas ao contexto bancário/corporativo. Alinhado à linguagem visual de produtos financeiros institucionais.

---

#### Seção de comparação Simplex vs PuLP

**Wireframe:** não prevista.

**Implementação:** a página *Resultados* inclui uma seção "Comparação de Solvers: Simplex vs PuLP" com cards de métricas agregadas (tempo de execução, valor da função objetivo, match de soluções) e tabela cluster-a-cluster com ∆z e status de convergência.

**Justificativa:** Atende diretamente ao requisito acadêmico de validar o Simplex próprio contra uma biblioteca estabelecida (PuLP/CBC). Permite ao time de Data Science (Larissa) auditar a qualidade do solver implementado sem depender do time técnico.

---

#### Estado vazio em Resultados

**Wireframe:** não previa estado inicial sem dados.

**Implementação:** quando nenhuma simulação foi executada, a página *Resultados* exibe um estado vazio com ícone, mensagem explicativa e botão de CTA para *Gerar Limites*.

**Justificativa:** Evita exibir dados mock descontextualizados ao usuário que ainda não rodou o modelo, seguindo a heurística de Nielsen de "visibilidade do status do sistema".

---

#### Barra de score com cores semânticas

**Wireframe:** coluna Score exibia apenas o valor numérico.

**Implementação:** componente `ScoreBar` renderiza uma barra de progresso proporcional ao score (0–1000) com cor semântica: verde `#67DE98` (≥ 750), amarelo `#FAE95D` (550–749), vermelho `#FF5D5C` (< 550).

**Justificativa:** Leitura visual imediata da qualidade de crédito do cliente sem necessidade de processar o número, reduzindo carga cognitiva.

---

#### Exportação client-side via Blob

**Wireframe:** botão Exportar previsto sem detalhe técnico.

**Implementação:** exportação totalmente client-side usando `Blob` + `URL.createObjectURL` + `<a download>`, sem dependência de servidor. Dashboard exporta `clientes.csv`; Resultados exporta `limites_clusters.csv` com comparação Simplex/PuLP.

**Justificativa:** Permite usar o front-end standalone (sem back-end) e valida o fluxo completo da US07 desde já.

---

### 3.2 Funcionalidades do wireframe não implementadas nesta entrega

| Funcionalidade | Motivo do adiamento |
|---|---|
| Validação real das colunas do CSV | Requer integração com back-end Python |
| Execução real do algoritmo Simplex | Requer integração com back-end Python |
| Consulta de restrições ativas (US05) | Requer endpoint de detalhamento por cluster |
| Persistência das configurações | Requer API de configuração no back-end |

---

## 4. Visualizações de Dados Implementadas

Todas as visualizações são implementadas em SVG puro, sem biblioteca externa de charting, garantindo controle total sobre estilo e interatividade.

| Componente | Tipo | Localização | Dados exibidos |
|---|---|---|---|
| `BarChartSVG` | Barras verticais | Resultados | Limite sugerido por cluster |
| `DonutChart` | Rosca | Resultados | Distribuição por status (Ativo / Pendente / Inativo) |
| `LineChartSVG` | Linha | Resultados | Evolução temporal dos limites (Jan–Jun) |
| `AreaChartSVG` | Área preenchida | Resultados | Distribuição por faixa de score |
| `ScoreBar` | Barra de progresso inline | Dashboard | Score individual de cada cliente |

Interações disponíveis: hover com tooltip nos gráficos de barras e linha; legenda no DonutChart; animação de entrada nos cards de KPI.
