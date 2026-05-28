# Front-end da Aplicação

## 1. Visão Geral

O front-end é uma SPA (Single Page Application) sem etapa de build, baseada em React 18 + Babel Standalone + Tailwind CSS, todos carregados via CDN. A identidade visual segue o brandbook do Banco PAN: paleta primária em tons de azul escuro (`#0D1B2A`, `#1B3A5C`, `#2E6DA4`), gradiente de navbar `#07B2FD` para `#005AEA`, arestas retas sem `border-radius`, tipografia Circular (com fallback para Inter).

Todos os dados exibidos vêm da API do backend via `api.js`. Não há dados mockados na aplicação.

A aplicação é organizada em **quatro fluxos principais** acessíveis pela navbar fixa:

| Estado `page` | Componente        | Responsabilidade                                                  |
| ------------- | ----------------- | ----------------------------------------------------------------- |
| `cockpit`     | `Cockpit.js`      | Visão geral da última simulação concluída e tabela de clusters    |
| `gerar`       | `GerarLimites.js` | Upload de base `.parquet`, monitoramento do pipeline e resultados |
| `resultados`  | `Resultados.js`   | Histórico de simulações com gráficos e exportação                 |
| modal         | `ConfigModal.js`  | Edição dos parâmetros do modelo de otimização                     |

A aplicação não usa React Router. O estado `page` em `App` (definido em `index.html`) controla qual componente é renderizado. A troca de tela é instantânea, sem recarregamento de página. O `ErrorBoundary` com `key={page}` força a remontagem completa a cada navegação, garantindo que os dados sejam sempre recarregados da API.

---

## 2. Estrutura de Arquivos

```
apps/frontend/
├── index.html              # Entry point, App root, ErrorBoundary
├── api.js                  # Cliente HTTP para o backend FastAPI
├── data.js                 # Helpers de formatação e metadados de UI
├── styles.css              # Estilos globais, fonte Circular, animações
├── assets/
│   ├── Logo_PAN.jpg
│   └── fonts/
│       ├── lineto-circular-bold.ttf
│       ├── lineto-circular-book.ttf
│       └── lineto-circular-medium.ttf
└── pages/
    ├── Navbar.js            # Navbar fixa com gradiente PAN
    ├── Cockpit.js         # Componente Cockpit
    ├── GerarLimites.js      # Upload, monitoramento e resultados inline
    ├── Resultados.js        # Componentes SVG de gráficos + página de histórico
    └── ConfigModal.js       # Modal de configuração dos parâmetros do modelo
```

---

## 3. api.js

Centraliza todas as chamadas ao backend. Não há `fetch` em nenhum outro arquivo.

| Método | Função                        | Endpoint                              |
| ------ | ----------------------------- | ------------------------------------- |
| `GET`  | `health()`                    | `/api/health`                         |
| `GET`  | `listSafras()`                | `/api/safras`                         |
| `GET`  | `listConsultas()`             | `/api/consultas`                      |
| `POST` | `createConsulta(...)`         | `/api/consultas`                      |
| `GET`  | `getConsulta(id)`             | `/api/consultas/{id}`                 |
| `GET`  | `getClusters(id)`             | `/api/consultas/{id}/clusters`        |
| `GET`  | `getClientes(id, limit, off)` | `/api/consultas/{id}/clientes`        |
| `GET`  | `exportClientes(id)`          | `/api/consultas/{id}/clientes/export` |
| `GET`  | `getHistoricoCliente(token)`  | `/api/clientes/{token}`               |
| `GET`  | `getConfig()`                 | `/api/config`                         |
| `PUT`  | `updateConfig(params)`        | `/api/config`                         |

`pollConsulta(id, onUpdate, intervalMs)` é um utilitário que chama `getConsulta` em loop até o status ser `concluido` ou `erro`, resolvendo a Promise com o resultado final. Retorna um objeto com método `cancel()` para interromper o polling.

---

## 4. data.js

Contém apenas helpers de apresentação e metadados de UI. Não há dados mockados.

**Helpers de formatação**

- `fmt(v)`: formata número como moeda sem casas decimais. Exemplo: `4500` vira `R$ 4.500`.
- `fmtZ(v)`: formata número como moeda com duas casas decimais. Usado para o valor objetivo `z`.

**`PARAMS_EDITAVEIS`**

Metadados dos controles do `ConfigModal`: chave, label em português, valor de fallback, limites e passo do slider. Os valores reais vêm sempre de `GET /api/config`. Os `value` aqui são apenas fallbacks exibidos antes da API responder.

| Chave   | Label                          | Faixa                | Default   |
| ------- | ------------------------------ | -------------------- | --------- |
| `t`     | Taxa de interchange            | 0,5% a 5%            | 1,75%     |
| `LGD`   | Loss Given Default             | 30% a 100%           | 80%       |
| `u_bar` | Utilização esperada do limite  | 30% a 100%           | 75%       |
| `L_max` | Limite máximo por cluster (R$) | R$ 5.000 a R$ 50.000 | R$ 25.000 |
| `T`     | Horizonte de uso (meses)       | 6 a 60               | 22        |

**`PARAMS_NAO_EDITAVEIS`**

Array de pares `{ label, value }` exibidos como somente leitura no `ConfigModal`. São parâmetros fixados pela modelagem ou pelo regulador.

---

## 5. Fluxo 1 - Cockpit (Cockpit.js)

### 5.1 Objetivo

Tela de entrada da aplicação. Apresenta a visão consolidada da última simulação concluída e a tabela de clusters correspondente.

### 5.2 Carregamento de dados

Ao montar, o componente executa `listConsultas()` e `listSafras()` em paralelo. Filtra as consultas com `status_consulta === "concluido"` e seleciona a mais recente como consulta atual e a segunda como consulta anterior (usada para calcular deltas). Em seguida, carrega os clusters da consulta atual via `getClusters(id)`.

### 5.3 Estados de render

**Carregando:** spinner centralizado enquanto as chamadas respondem.

**Vazio:** exibido quando não há nenhuma consulta concluída. Mostra CTA para Gerar Limites.

**Normal:** KPIs, banner de referência e tabela de clusters.

### 5.4 KPIs

| Card                   | Campo na API           | Delta                           |
| ---------------------- | ---------------------- | ------------------------------- |
| Total de Clientes      | `n_clientes_total`     | Absoluto vs consulta anterior   |
| Clusters Identificados | `n_clusters`           | Absoluto vs consulta anterior   |
| Clientes Elegíveis     | `n_clientes_elegiveis` | Absoluto vs consulta anterior   |
| Valor Objetivo (z)     | `z_otimo`              | Percentual vs consulta anterior |

Quando não há consulta anterior, o badge de delta não é exibido.

### 5.5 Tabela de clusters

Exibe os dados de `ClusterResultadoResponse` da consulta mais recente. Colunas: Cluster ID, Clientes, PD Média, Score Cross Médio, Fator de Alavancagem, Limite Otimizado e Status (Viável / Sem Solução).

- Busca filtra por `CLU-{cluster_id}` em tempo real
- Paginação de 15 registros por página
- Exportar gera `clusters_{safra}.csv` no browser via `Blob`, sem chamar a API

---

## 6. Fluxo 2 - Gerar Limites (GerarLimites.js)

### 6.1 Upload

Aceita exclusivamente arquivos `.parquet`. A tentativa de upload de qualquer outro formato exibe erro de validação antes de qualquer requisição.

A dropzone suporta drag-and-drop e clique. O campo `safra_numero` fica oculto em "Opções avançadas" e é opcional: quando omitido, o backend auto-incrementa o número da safra.

### 6.2 Colunas esperadas no .parquet

| Coluna                     | Tipo   | Descrição                                 |
| -------------------------- | ------ | ----------------------------------------- |
| `token`                    | int    | Identificador único do cliente            |
| `flag_filtros`             | int    | 0 = elegível / 1 = excluído da otimização |
| `score_interno`            | int    | Score interno do produto                  |
| `pd_produto`               | float  | Probabilidade de default do produto       |
| `score_credito_cross`      | int    | Score de crédito cross (300 a 900)        |
| `score_propensao_contrato` | float  | Score de propensão ao contrato (3 a 846)  |
| `capacidade_pagamento`     | float? | Capacidade de pagamento em R$ (opcional)  |
| `renda_estimada`           | float? | Renda estimada em R$ (opcional)           |
| `fx_idade`                 | string | Faixa etária categórica (ex: 26-35)       |
| `flag_contrato`            | int    | 1 = cliente com contrato ativo            |
| `flag_ativacao`            | int    | 1 = cliente ativado                       |

### 6.3 Modal de envio

Ao clicar em "Executar Simplex", um modal bloqueante cobre a tela enquanto o arquivo é enviado via `POST /api/consultas`. O modal exibe o nome e o tamanho do arquivo e não pode ser fechado pelo usuário. Fecha automaticamente quando o backend responde.

### 6.4 Tratamento do conflito 409

Se `safra_numero` for informado e a safra já existir, o backend retorna 409. O modal fecha e um aviso inline aparece com dois botões: "Usar safra existente" (reenvia com `usar_safra_existente=true`) e "Cancelar".

### 6.5 Monitoramento

Após receber a resposta `pendente` do backend, a consulta aparece na lista de simulações. O polling inicia com uma primeira verificação em 5 segundos (tempo para o background task iniciar) e depois a cada 60 segundos via `GET /api/consultas/{id}`.

Durante a execução, cada consulta exibe as três etapas do pipeline com animação de pulso: Calibração, Clustering (CART) e Otimização (Simplex). O botão "Verificar agora" cancela o timer pendente e consulta imediatamente.

Quando o status muda para `concluido`, o componente chama `getClusters(id)` e exibe os resultados abaixo da lista. Quando muda para `erro`, exibe `erro_etapa` e `erro_mensagem` do backend.

### 6.6 Resultados inline

Exibidos após a conclusão da consulta ativa ou ao clicar em "Ver resultados" em qualquer consulta concluída da lista.

**KPIs:** `n_clusters`, `z_otimo`, `n_clientes_elegiveis`, `n_clientes_ofertados` (com percentual calculado sobre elegíveis).

**Gráficos:**

- Barras verticais com os 15 clusters de maior limite otimizado
- Donut com distribuição de clientes: Com limite / Elegível sem limite / Inelegível

**Tabela de clusters:** paginada em 20 por página, com colunas PD Média, Score Cross Médio, Fator de Alavancagem, Limite Otimizado e Status.

**Exportar:** chama `Api.exportClientes(id)` que baixa o CSV completo de clientes gerado pelo backend.

---

## 7. Fluxo 3 - Resultados (Resultados.js)

Página independente acessível diretamente pela navbar. Ao montar, carrega todas as consultas concluídas e safras em paralelo e seleciona a mais recente por padrão.

### 7.1 Seletor de simulação

Dropdown no cabeçalho lista todas as consultas concluídas no formato `{safra} · {arquivo}`. Ao trocar a seleção, os clusters da nova consulta são carregados via `getClusters(id)`.

### 7.2 KPIs

Mesmos quatro campos de `ConsultaResponse`: `n_clusters`, `z_otimo`, `n_clientes_elegiveis`, `n_clientes_ofertados`.

### 7.3 Gráficos

| Componente     | Dados                                                                                   |
| -------------- | --------------------------------------------------------------------------------------- |
| `BarChartSVG`  | Top 15 clusters por `limite_otimizado`, ordenados decrescentemente                      |
| `DonutChart`   | Distribuição de clientes: Com limite / Elegível sem limite / Inelegível                 |
| `LineChartSVG` | Evolução do `z_otimo` entre consultas concluídas, ordenadas cronologicamente            |
| `RiskHistSVG`  | Histograma de clusters por faixa de PD média: 0-5%, 5-10%, 10-15%, 15-20%, 20-25%, 25%+ |

### 7.4 Parâmetros utilizados

Seção colapsável exibindo os parâmetros exatos da consulta selecionada (`t`, `LGD`, `u_bar`, `L_max`, `T`). Útil para auditoria e reprodução dos resultados.

### 7.5 Exportação

Botão "Exportar clientes CSV" chama `Api.exportClientes(id)`, que retorna o arquivo gerado pelo backend com todos os campos de `ClienteResultadoResponse`.

---

## 8. Fluxo 4 - Configurações (ConfigModal.js)

### 8.1 Acesso

Disparado pelo último item da navbar (identificado como `isConfig: true`). Sobrepõe a página ativa com fundo semi-transparente. Ao abrir, carrega os valores atuais via `GET /api/config`.

### 8.2 Parâmetros editáveis

Cada parâmetro é exibido como um card com valor atual e botão de edição. Ao clicar em editar, o card expande com um slider cujos limites e passo são definidos em `PARAMS_EDITAVEIS` em `data.js`.

Salvar envia `PUT /api/config` com o payload `{ t, LGD, u_bar, L_max, T }` e atualiza o estado local. Cancelar restaura o valor que veio da API na abertura do modal (não o fallback local de `data.js`).

### 8.3 Restaurar padrões

Botão no rodapé do modal. Exibe `window.confirm` antes de executar. Envia `PUT /api/config` com os valores de fábrica definidos em `PARAMS_EDITAVEIS.value` e atualiza o banco.

### 8.4 Parâmetros não editáveis

Grid de dois cards por linha exibindo os parâmetros fixados pela modelagem ou pelo regulador.

---

## 9. Visualizações de Dados

Todos os gráficos são componentes SVG puros definidos em `Resultados.js` como variáveis globais (`var`), acessíveis por `GerarLimites.js` após o carregamento dos scripts. Não há bibliotecas externas de charting.

| Componente     | Tipo                | Descrição                                                                                                                                                             |
| -------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BarChartSVG`  | Barras verticais    | Barras azul PAN para clusters com limite, cinza `#E8EFF7` para clusters sem solução. Rótulo de valor acima de cada barra. Eixo Y com escala automática em R$k ou R$M. |
| `LineChartSVG` | Linha com área      | Área sombreada azul, pontos com rótulo de valor alternados. Requer no mínimo 2 pontos; exibe aviso quando há apenas uma consulta.                                     |
| `DonutChart`   | Rosca               | Fatias calculadas a partir das contagens da `ConsultaResponse`. Legenda lateral com valores absolutos.                                                                |
| `RiskHistSVG`  | Histograma de risco | Seis faixas de PD média com gradiente visual de verde (baixo risco) a vermelho (alto risco). Conta clusters por faixa.                                                |

Todas as visualizações usam exclusivamente cores da paleta PAN: azul `#2E6DA4` como cor principal, `#E8EFF7` para linhas de grade, paleta terciária (verde/amarelo/vermelho) para status e risco.

---

## 10. Como Executar

O front-end sobe automaticamente junto com o backend via `run_server.py`:

```bash
cd apps/backend
python run_server.py
```

Para subir somente o front-end de forma isolada:

```bash
cd apps/frontend
python -m http.server 5500
```

### Dependências (via CDN)

| Biblioteca       | Versão | Finalidade                     |
| ---------------- | ------ | ------------------------------ |
| React            | 18     | UI reativa                     |
| ReactDOM         | 18     | Renderização no DOM            |
| Babel Standalone | latest | Transpilação de JSX no browser |
| Tailwind CSS     | CDN    | Estilização utilitária         |
