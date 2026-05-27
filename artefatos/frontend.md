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
Implementada na página *Resultados*. Contém quatro visualizações em SVG puro: gráfico de barras (Limites por Cluster), gráfico de rosca (Distribuição por Status), gráfico de linha (Evolução Temporal de Limites) e gráfico de barras (Distribuição por Faixa de Score). O gráfico de evolução suporta comparação entre duas simulações via toggle "Comparar simulação anterior".

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
cd apps/frontend

# Windows
start index.html

# macOS
open index.html

# Linux
xdg-open index.html
```

### Opção B — Servidor HTTP local (recomendado para evitar erros de CORS)

**Com Python:**
```bash
cd apps/frontend
python -m http.server 8080
# Acesse: http://localhost:8080
```

**Com Node.js:**
```bash
cd apps/frontend
npx serve .
```

**Com VS Code:** instale *Live Server*, clique com botão direito em `index.html` → *Open with Live Server*.

### Dependências (todas via CDN, sem instalação)

| Biblioteca | Versão | Finalidade |
|---|---|---|
| React | 18 | UI reativa |
| ReactDOM | 18 | Renderização no DOM |
| Babel Standalone | latest | Transpilação de JSX |
| Tailwind CSS | CDN | Estilização utilitária |
| Inter (Google Fonts) | — | Tipografia base |

### Estrutura de arquivos

```
apps/frontend/
├── index.html              # Entry point
├── data.js                 # Dados mock globais
├── assets/
│   └── Logo_PAN.jpg
└── pages/
    ├── Navbar.js            # Navbar fixa com scroll-shrink
    ├── Dashboard.js         # Visão geral da carteira + tabela de clientes
    ├── GerarLimites.js      # Upload de base + execução do Simplex
    ├── Resultados.js        # Visualizações gráficas + comparação Simplex vs PuLP
    └── ConfigModal.js       # Modal de configuração de parâmetros
```

---

## 3. Tela de Configurações — ConfigModal

A tela de Configurações é implementada como modal sobreposição (`ConfigModal.js`), acessível pelo ícone de engrenagem na navbar. Atende parcialmente às US02 e US03.

### Parâmetros Editáveis

| Parâmetro | Controle | Faixa |
|---|---|---|
| Taxa de Interchange | Slider + campo numérico | 0% – 5% |
| Loss Given Default (LGD) | Slider + campo numérico | 0% – 100% |
| Utilização Esperada do Limite | Slider + campo numérico | 0% – 100% |
| Teto Máximo de Limite (R$) | Slider + campo numérico | R$ 0 – R$ 50.000 |

**Parâmetros Não Editáveis** — exibidos para consulta sem campo de edição (ex.: número de clusters fixado pelo modelo).

### Fluxo de interação

1. Clique no ícone de configurações na navbar → modal abre com animação `fadeIn`.
2. Slider e campo numérico são sincronizados — mover um atualiza o outro em tempo real.
3. **Salvar** aplica os valores ao estado local.
4. **Cancelar** / clique fora / `Esc` fecha sem persistir alterações.

---

## 4. Diferenças em Relação ao Protótipo (Wireframes)

### 4.1 Melhorias implementadas

**Botões de ação funcionais no Dashboard**
O wireframe previa "Importar", "Adicionar" e "Filtrar" como elementos visuais. Na implementação todos são funcionais: Importar abre file picker e exibe toast de confirmação; Adicionar abre modal com formulário (ID, Score, Status, Limite, Cadastro) que insere o cliente na tabela; Filtrar expande painel com seleção de status (Todos / Ativo / Pendente / Inativo).

**Comparação de simulações no gráfico de evolução**
O wireframe previa apenas um gráfico de linha mostrando a evolução temporal. A implementação adiciona toggle "Comparar simulação anterior" que sobrepõe uma segunda série (linha tracejada em amarelo) representando o run anterior do algoritmo, com legenda discriminando as duas séries.

**Seção de comparação Simplex vs PuLP**
Não prevista no wireframe. A página Resultados inclui cards de métricas agregadas e tabela cluster-a-cluster comparando o solver próprio com PuLP/CBC.

**Estado vazio em Resultados**
Não previa estado inicial. Quando nenhuma simulação foi executada, a página exibe empty state com CTA para Gerar Limites.

**Barra de score com cores semânticas no Dashboard**
O wireframe exibia o score como valor numérico. A implementação usa `ScoreBar` com cor proporcional: verde (≥750), amarelo (550–749), vermelho (<550).

**Exportação client-side**
Exportação totalmente no browser via `Blob` + `URL.createObjectURL`, sem dependência de servidor.

### 4.2 Funcionalidades do wireframe não implementadas nesta entrega

| Funcionalidade | Motivo |
|---|---|
| Validação real das colunas do CSV | Requer back-end Python |
| Execução real do algoritmo Simplex | Requer back-end Python |
| Consulta de restrições ativas (US05) | Requer endpoint por cluster |
| Persistência das configurações | Requer API de configuração |

---

## 5. Visualizações de Dados Implementadas

Todas em SVG puro, sem biblioteca externa de charting.

| Componente | Tipo | Localização | Dados |
|---|---|---|---|
| `BarChartSVG` | Barras verticais | Resultados | Limite sugerido por cluster |
| `DonutChart` | Rosca | Resultados | Distribuição por status |
| `LineChartSVG` | Linha (+ linha comparativa) | Resultados | Evolução temporal de limites |
| `AreaChartSVG` | Barras de frequência | Resultados | Distribuição por faixa de score |
| `ScoreBar` | Barra de progresso inline | Dashboard | Score individual de cada cliente |

O `LineChartSVG` aceita prop `data2` opcional — quando fornecido renderiza segunda série em linha tracejada amarela com pontos sobrepostos, permitindo comparação visual direta entre duas execuções do algoritmo.
