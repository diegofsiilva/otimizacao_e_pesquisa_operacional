# Front-end da Aplicação

## 1. Visão Geral

O front-end é uma SPA (Single Page Application) sem etapa de build, baseada em React 18 + Babel Standalone + Tailwind CSS, todos carregados via CDN. A identidade visual segue o brandbook do Banco PAN: paleta primária em tons de azul escuro (`#0D1B2A`, `#1B3A5C`, `#2E6DA4`), gradiente de navbar `#07B2FD -> #005AEA`, arestas retas sem `border-radius`, tipografia Circular (com fallback para Inter).

A aplicação é organizada em **três fluxos principais** acessíveis pela navbar fixa:

| Rota (estado `page`) | Componente | Responsabilidade |
|---|---|---|
| `dashboard` | `Dashboard.js` | Visão geral da última safra + tabela de clusters históricos |
| `gerar` | `GerarLimites.js` | Upload de base CSV, execução do Simplex, resultados inline |
| modal (overlay) | `ConfigModal.js` | Edição dos parâmetros do modelo |

> **Nota de roteamento:** A aplicação não usa React Router. O estado `page` em `App` (em `index.html`) controla qual componente é renderizado. A troca de tela é instantânea, sem recarregamento de página.

---

## 2. Estrutura de Arquivos

```
apps/frontend/
├── index.html              # Entry point + App root + ErrorBoundary
├── data.js                 # Dados globais de referência
├── styles.css              # Estilos globais, fonte Circular, animação upload-zone
├── assets/
│   ├── Logo_PAN.jpg
│   └── fonts/
│       ├── lineto-circular-bold.ttf
│       ├── lineto-circular-book.ttf
│       └── lineto-circular-medium.ttf
└── pages/
    ├── Navbar.js            # Navbar fixa, gradiente PAN, links de navegação
    ├── Dashboard.js         # KPIs + tabela de clusters da última safra
    ├── GerarLimites.js      # Upload + execução + resultados completos inline
    ├── Resultados.js        # Componentes SVG de gráficos (globais) + página legada
    └── ConfigModal.js       # Modal de configuração de parâmetros do modelo
```

---

## 3. Fluxo 1 — Home (Dashboard)

### 3.1 Objetivo

A Home é a tela de entrada da aplicação. Sua função é dar ao usuário (perfil Rodinei — Estratégia de Crédito) uma leitura rápida do estado atual da carteira e do histórico de simulações executadas.

### 3.2 Composição da tela

**Cabeçalho**

Título "Home" com sublinhado azul PAN de 2 px e data da última safra carregada. Botão "Nova Simulação" no canto direito navega para `gerar`.

**KPIs (4 cards)**

| Card | Dado |
|---|---|
| Total de Clientes | Contagem total da base da safra |
| Clusters Identificados | Número de clusters gerados pelo CART |
| Score Médio | Média ponderada do `score_credito_cross` |
| Clientes Elegíveis | Clientes com `flag_filtros = 0` |

Cada card exibe valor principal, badge de variação (alta/queda/neutro) e ícone temático. As cores dos badges seguem a paleta terciária PAN: verde `#67DE98` para alta, vermelho `#FF5D5C` para queda, azul claro neutro para estável.

**Tabela de Clusters Identificados**

Exibe o resultado agregado da última execução do algoritmo. Colunas: **Cluster ID**, **Limite Sugerido** (formatado em R$) e **Status** (badge "Solução Viável" verde ou "Sem Solução" vermelho).

- Campo de busca filtra por Cluster ID em tempo real (case-insensitive)
- Botão **Exportar** gera `clusters.csv` com as colunas `cluster_id`, `limite_sugerido`, `status` via `Blob` + `URL.createObjectURL`, sem depender de servidor
- Paginação visual (Anterior / 1 2 3 / Próximo)

---

## 4. Fluxo 2 — Gerar Limites + Resultados

Este é o fluxo central da aplicação. O protótipo original tratava "Gerar Limites" e "Resultados" como duas telas separadas — o usuário fazia o upload em uma tela e navegava para outra para ver os gráficos. Na implementação final, as duas telas foram **fundidas em uma só página com dois estados visuais**.

### 4.1 Estado inicial — Instruções e Upload

Quando o usuário acessa "Gerar Limites" sem ter rodado uma simulação, a página exibe:

**Tabela de estrutura esperada do CSV**

Antes do campo de upload, há uma tabela de referência completa com as 8 colunas esperadas no arquivo:

| Coluna | Tipo | Descrição |
|---|---|---|
| `token` | string | Identificador único do cliente |
| `flag_filtros` | int | 0 = elegível / 1 = excluído da otimização |
| `pd_calibrada` | float | Probabilidade de default calibrada |
| `capacidade_pagamento` | float | Capacidade de pagamento em R$ |
| `renda_estimada` | float | Renda estimada (proxy quando capacidade_pagamento é nulo) |
| `score_credito_cross` | float | Score de crédito (escala 300-900) |
| `score_propensao_contrato` | float | Score de propensão ao contrato (escala 3-846) |
| `fx_idade` | string | Faixa etária categórica (opcional) |

Uma nota abaixo da tabela informa o mínimo recomendado de **500+ clientes com `flag_filtros = 0`** para que o CART gere clusters com `min_samples_leaf = 500`.

**Dropzone de upload**

Área clicável com suporte a drag-and-drop. Aceita `.csv` e `.xlsx`. Estados visuais:
- **Vazio:** borda tracejada cinza azulada, fundo branco
- **Drag sobre:** borda azul PAN sólida, fundo `#D6E8F5`
- **Arquivo carregado:** borda azul PAN, fundo `#D6E8F5/50`, nome do arquivo exibido

Após selecionar um arquivo, aparece o botão **Executar Simplex** com feedback de loading (ícone giratório + texto "Executando...") durante o processamento.

### 4.2 Estado pós-execução — Resultados inline

Após `ran = true`, o título da página muda para "Resultados da Simulação" e os seguintes blocos aparecem:

**Banner informativo**

Barra azul claro com ícone de informação indicando que os dados são da última execução. Link "carregar um novo arquivo" reseta `ran = false` e `file = null`, voltando ao estado de upload sem precisar navegar.

**KPIs de resultado (4 cards)**

| Card | Destaque |
|---|---|
| Total de Clusters | Neutro |
| Limite Total Aprovado | Destacado (fundo `#D6E8F5`, valor em azul PAN) |
| Clientes Ativos | Neutro |
| Taxa de Aprovação | Neutro |

**Mini-cards de viabilidade + Tabela de clusters**

Três cards horizontais: Total de Clusters, Com Solução Viável (borda verde), Sem Solução (borda amarela). Abaixo, a tabela completa com Cluster ID, Limite Sugerido e badge de status para cada cluster.

**Gráficos (linha 1)**

- **Limites por Cluster** — gráfico de barras verticais SVG. Barras azul PAN para clusters com limite; barras cinza `#E8EFF7` para clusters sem solução. Rótulos de valor acima de cada barra.
- **Distribuição por Status** — gráfico de rosca (donut) SVG com legenda lateral. Cores: verde `#67DE98` (Ativo), vermelho `#FF5D5C` (Inativo), amarelo `#FAE95D` (Pendente).

**Seção de comparação Simplex vs PuLP**

Seção exclusiva desta implementação, sem equivalente no protótipo. Dois cards lado a lado exibem métricas agregadas de cada solver (valor objetivo `z`, tempo de execução em ms, status de otimização). Abaixo, tabela cluster-a-cluster com as colunas Cluster, Simplex (R$), PuLP/CBC (R$) e Match (badge "Idêntico" verde ou "Diverge" amarelo). Rodapé exibe o delta `z` percentual e o PD financeiro atual.

**Gráficos (linha 2)**

- **Evolução do Limite Total** — gráfico de linha SVG com área sombreada. Toggle "Comparar simulação anterior" sobrepõe segunda série em linha tracejada amarela, com legenda discriminando as duas execuções.
- **Distribuição de Score** — histograma SVG de barras verticais por faixa de `score_credito_cross` (300-400, 400-500, ..., 900+).

**Botão Exportar CSV**

Posicionado no cabeçalho da seção de resultados. Gera `limites_clusters.csv` com as colunas Cluster, Simplex (R$), PuLP/CBC (R$), Match via `Blob` + `URL.createObjectURL`.

### 4.3 Diagrama de estados do fluxo

```
[Abre /gerar]
      |
      v
[Estado: upload]
  +-------------------------+
  |  Instruções CSV         |
  |  Dropzone               |
  +------------+------------+
               | seleciona arquivo
               v
         [file != null]
         Botao "Executar" aparece
               | clica Executar
               v
         [running = true]
         Processamento em execução
               |
               v
         [ran = true]
  +-------------------------+
  |  Resultados inline      |
  |  KPIs . Clusters        |
  |  Graficos . Comparacao  |
  |  Exportar CSV           |
  +------------+------------+
               | clica "carregar novo arquivo"
               v
         [ran=false, file=null]
         volta ao estado upload
```

---

## 5. Fluxo 3 — Alterar Parâmetros (ConfigModal)

### 5.1 Acesso

O modal é disparado pelo ícone de engrenagem na navbar (último item, identificado como `isConfig: true`). Não ocupa uma rota própria — é uma sobreposição sobre a página ativa com fundo semi-transparente `#0D1B2A/40`.

### 5.2 Parâmetros editáveis

Cada parâmetro é exibido como um controle composto: **slider** horizontal sincronizado com **campo numérico** editável. Mover o slider atualiza o campo e vice-versa em tempo real. Os limites de cada slider refletem os intervalos válidos do modelo:

| Parâmetro | Chave | Faixa | Default |
|---|---|---|---|
| Taxa de interchange | `t` | 0 – 5% | 1,75% |
| Loss Given Default (LGD) | `LGD` | 30% – 100% | 80% |
| Utilização esperada do limite | `u_bar` | 30% – 100% | 75% |
| Teto máximo de Limite (R$) | `L_max` | R$ 10.000 – R$ 50.000 | R$ 25.000 |

### 5.3 Parâmetros não editáveis

Exibidos em grid de 2 colunas como cards somente-leitura, com label e valor formatado. São parâmetros fixados pela equipe de modelagem ou pelo regulador:

| Parâmetro | Valor |
|---|---|
| Custo de capital (Ke) | 14,25% |
| Custo de funding (Kd) | 11,50% |
| Taxa de recuperação (RR) | 30% |
| Exposição padrão (EAD) | Limite |
| LGD | 80% |
| PD financeiro atual | 13,75% |

### 5.4 Fluxo de interação

```
[Clica engrenagem na navbar]
         |
         v
   Modal abre (overlay)
   Parametros carregados no estado local
         |
         +-- [ajusta slider ou campo numerico]
         |    +-- ambos se sincronizam em tempo real
         |
         +-- [clica Salvar]
         |    +-- parametros persistidos
         |    +-- modal fecha
         |
         +-- [clica Cancelar / clica fora / Esc]
              +-- descarta alteracoes -> modal fecha
```

---

## 6. Diferenças em Relação ao Protótipo Figma

### 6.1 Navbar e identidade visual

| Aspecto | Protótipo | Implementação |
|---|---|---|
| Marca | "Sistema de Crédito" (texto simples) | Logo `Logo_PAN.jpg` + "Banco PAN / Otimizador de Limites" |
| Cor da navbar | Branco/cinza claro | Gradiente `#07B2FD -> #005AEA` (identidade PAN) |
| Itens | Dashboard . Gerar Limites . Resultados | Home . Gerar Limites . Configurações |
| Item "Resultados" | Rota independente | Removido — conteúdo fundido em Gerar Limites |
| "Configurações" | Ícone de engrenagem flutuante (canto inferior esquerdo) | Item fixo na navbar, alinhado aos demais links |
| Border-radius | Botões e cards arredondados | Sem arredondamento — bordas retas conforme brandbook PAN |

### 6.2 Tela Home

| Aspecto | Protótipo | Implementação |
|---|---|---|
| Título da tabela principal | "Lista de Clientes" | "Clusters Identificados" |
| Colunas da tabela | Cluster . Score (barra) . Status . Limite . Cadastro . Ações | Cluster ID . Limite Sugerido . Status |
| Botões da tabela | Importar . Exportar . Adicionar | Somente Exportar |
| Status na tabela | Ativo / Em Análise / Inativo | Solução Viável / Sem Solução |
| KPIs | Total de Clientes . Clusters Ativos . Limite Total . Taxa de Aprovação | Total de Clientes . Clusters Identificados . Score Médio . Clientes Elegíveis |
| Score individual | Barra proporcional com cores verde/amarelo/vermelho | Não exibido (tabela é de clusters, não de clientes individuais) |

A mudança da tabela de clientes para clusters reflete a decisão de modelagem: a unidade de otimização é o cluster, não o cliente individual — o que é exibido são os clusters consolidados resultantes da execução do CART + Simplex.

### 6.3 Tela Gerar Limites

| Aspecto | Protótipo | Implementação |
|---|---|---|
| Conteúdo pré-upload | Apenas dropzone | Tabela de estrutura do CSV com 8 colunas + nota de mínimo recomendado |
| Pós-execução | Navega para tela "Resultados" separada | Resultados aparecem inline na mesma página |
| Botão de navegação | "Ver análise completa em Resultados" (CTA) | Removido — não há navegação separada |
| Reset | Navegar para outra tela | Link "carregar um novo arquivo" reseta o estado sem sair da página |

### 6.4 Tela Resultados (fundida em Gerar Limites)

| Aspecto | Protótipo | Implementação |
|---|---|---|
| Localização | Rota `/resultados` independente | Bloco condicional `{ran && ...}` dentro de `GerarLimites` |
| Estado vazio | Não previsto | Banner com CTA para upload quando `ran = false` |
| Seção Simplex vs PuLP | Não prevista | Cards de métricas agregadas + tabela cluster-a-cluster com delta `z` |
| Comparação entre runs | Não prevista | Toggle "Comparar simulação anterior" sobrepõe série tracejada amarela no gráfico de evolução |
| Exportação | Não prevista na tela | Botão "Exportar CSV" no cabeçalho dos resultados |

### 6.5 ConfigModal

| Aspecto | Protótipo | Implementação |
|---|---|---|
| Controle de edição | Ícone de lápis por parâmetro; expandia slider inline ao clicar | Todos os sliders visíveis simultaneamente |
| Salvar/Cancelar | Por parâmetro (dentro de cada card expandido) | Global — único par de botões no rodapé do modal |
| Tema | Branco com bordas arredondadas | Fundo `#E2EAF4` nos cards de parâmetros, bordas retas |

---

## 7. Visualizações de Dados

Todos os gráficos são componentes SVG puros definidos em `Resultados.js` como variáveis globais (`var`), acessíveis por `GerarLimites.js` após o carregamento de todos os scripts.

| Componente | Tipo | Dados exibidos |
|---|---|---|
| `BarChartSVG` | Barras verticais | Limite ótimo por cluster (R$) |
| `DonutChart` | Rosca com buraco | Proporção de clientes por status |
| `LineChartSVG` | Linha com área + série opcional | Evolução mensal do limite total (R$ milhões). Prop `data2` ativa série comparativa tracejada em amarelo |
| `AreaChartSVG` | Histograma de frequência | Distribuição de clientes por faixa de score |

Todas as visualizações usam exclusivamente as cores da paleta PAN: azul `#2E6DA4` como cor principal, `#E8EFF7` para linhas de grade e barras sem valor, paleta terciária (verde/amarelo/vermelho) para status. Sem bibliotecas externas de charting.

---

## 8. Como Executar

O front-end não possui build. Funciona diretamente no browser via `file://` ou servidor HTTP estático.

```bash
# Python (recomendado — evita restricoes de CORS no file://)
cd apps/frontend
python -m http.server 8080
# Acesse: http://localhost:8080

# Node.js
cd apps/frontend
npx serve .
```

### Dependências (todas via CDN)

| Biblioteca | Versão | Finalidade |
|---|---|---|
| React | 18 | UI reativa |
| ReactDOM | 18 | Renderização no DOM |
| Babel Standalone | latest | Transpilação de JSX no browser |
| Tailwind CSS | CDN | Estilização utilitária |

### User Stories atendidas

| ID | Título | Status |
|---|---|---|
| US01 | Carregar base de dados | Implementado — dropzone com drag-and-drop, feedback visual |
| US04 | Gerar limite por cluster | Implementado — upload de CSV + execução + resultados inline |
| US06 | Visualizar distribuição dos limites | Implementado — 4 gráficos SVG + seção Simplex vs PuLP |
| US07 | Exportar resultados | Implementado — CSV client-side em Dashboard e em Resultados |
| US02 | Ajustar clusterização | Implementado — parâmetros editáveis no ConfigModal |
| US03 | Configurar metas de produção | Implementado — modal funcional com sliders sincronizados |
| US05 | Consultar restrições ativas | Implementado — parâmetros não editáveis exibidos no ConfigModal |
