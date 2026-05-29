# Front-end da Aplicação

## 1. Visão Geral

O front-end é uma SPA (Single Page Application) sem etapa de build, baseada em React 18 + Babel Standalone + Tailwind CSS, todos carregados via CDN. A identidade visual segue o brandbook do Banco PAN: paleta primária em tons de azul escuro (`#0D1B2A`, `#1B3A5C`, `#2E6DA4`), gradiente de navbar `#07B2FD` para `#005AEA`, arestas retas sem `border-radius`, tipografia Circular (com fallback para Inter).

Todos os dados exibidos vêm da API do backend via `api.js`. Não há dados mockados na aplicação.

A aplicação é organizada em cinco fluxos acessíveis pela navbar fixa:

| Estado `page` | Componente        | Responsabilidade                                                  |
| ------------- | ----------------- | ----------------------------------------------------------------- |
| `dashboard`   | `Cockpit.js`      | Visão geral da última simulação concluída e tabela de clusters    |
| `gerar`       | `GerarLimites.js` | Upload de base `.parquet`, monitoramento do pipeline e resultados |
| `resultados`  | `Resultados.js`   | Histórico de simulações com gráficos e exportação                 |
| `clientes`    | `Clientes.js`     | Busca de cliente por token e histórico de limites entre safras    |
| modal         | `ConfigModal.js`  | Edição dos parâmetros do modelo de otimização                     |

A aplicação não usa React Router. O estado `page` em `App` (definido em `index.html`) controla qual componente é renderizado. A troca de tela é instantânea, sem recarregamento de página. O `ErrorBoundary` com `key={page}` força a remontagem completa a cada navegação, garantindo que os dados sejam sempre recarregados da API.

---

## 2. User Stories Priorizadas

Ordenadas por prioridade de negócio (P1 = crítico para o fluxo principal, P3 = melhoria).

| Prioridade | ID   | Título                                 | Componente                   | Status       | Observação                                                                                               |
| ---------- | ---- | -------------------------------------- | ---------------------------- | ------------ | -------------------------------------------------------------------------------------------------------- |
| P1         | US01 | Enviar base de clientes para simulação | `GerarLimites`               | Implementado | Upload `.parquet` com chunked transfer e modal de progresso por etapas                                   |
| P1         | US02 | Monitorar execução do pipeline         | `GerarLimites`               | Implementado | Polling automático com etapas animadas (Calibração → Clustering → Simplex); botão "Verificar agora"      |
| P1         | US03 | Visualizar resultado da simulação      | `GerarLimites`               | Implementado | Resultados inline pós-conclusão: KPIs, gráficos de barras e donut, tabela de clusters paginada           |
| P1         | US04 | Consultar cockpit da última safra      | `Cockpit`                    | Implementado | KPIs com delta vs simulação anterior; tabela de clusters; CTA para nova simulação quando não há dados    |
| P2         | US05 | Consultar histórico de simulações      | `Resultados`                 | Implementado | Seletor de simulação concluída; gráfico de evolução do `z_otimo`; histograma de risco por PD             |
| P2         | US06 | Exportar clientes para CSV             | `GerarLimites`, `Resultados` | Implementado | `Api.exportClientes(id)` - arquivo gerado pelo backend com todos os campos de `ClienteResultadoResponse` |
| P2         | US07 | Configurar parâmetros do modelo        | `ConfigModal`                | Implementado | Sliders com sync em tempo real; salvar via `PUT /api/config`; restaurar padrões com confirmação          |
| P3         | US08 | Buscar cliente individual por token    | `Clientes`                   | Implementado | Histórico entre safras: cluster, limite, PD, score cross por período                                     |
| P3         | US09 | Auditar parâmetros de uma simulação    | `Resultados`                 | Implementado | Seção colapsável com `t`, `LGD`, `u_bar`, `L_max`, `T` da consulta selecionada                           |

---

## 3. Como Executar

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

---

## 4. Estrutura de Arquivos

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
    ├── Cockpit.js           # Visão geral da última simulação concluída
    ├── GerarLimites.js      # Upload, monitoramento e resultados inline
    ├── Resultados.js        # Componentes SVG de gráficos + página de histórico
    ├── Clientes.js          # Busca por token e histórico individual entre safras
    └── ConfigModal.js       # Modal de configuração dos parâmetros do modelo
```

---

## 5. api.js

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

## 6. data.js

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

## 7. Fluxo 1 - Cockpit (Cockpit.js)

### 7.1 Objetivo

Tela de entrada da aplicação. Apresenta a visão consolidada da última simulação concluída e a tabela de clusters correspondente.

### 7.2 Carregamento de dados

Ao montar, o componente executa `listConsultas()` e `listSafras()` em paralelo. Filtra as consultas com `status_consulta === "concluido"` e seleciona a mais recente como consulta atual e a segunda como consulta anterior (usada para calcular deltas). Em seguida, carrega os clusters da consulta atual via `getClusters(id)`.

### 7.3 Estados de render

**Carregando:** spinner centralizado enquanto as chamadas respondem.

**Vazio:** exibido quando não há nenhuma consulta concluída. Mostra CTA para Gerar Limites.

**Normal:** KPIs, banner de referência e tabela de clusters.

### 7.4 KPIs

| Card                   | Campo na API           | Delta                           |
| ---------------------- | ---------------------- | ------------------------------- |
| Total de Clientes      | `n_clientes_total`     | Absoluto vs consulta anterior   |
| Clusters Identificados | `n_clusters`           | Absoluto vs consulta anterior   |
| Clientes Elegíveis     | `n_clientes_elegiveis` | Absoluto vs consulta anterior   |
| Valor Objetivo (z)     | `z_otimo`              | Percentual vs consulta anterior |

Quando não há consulta anterior, o badge de delta não é exibido.

### 7.5 Tabela de clusters

Exibe os dados de `ClusterResultadoResponse` da consulta mais recente. Colunas: Cluster ID, Clientes, PD Média, Score Cross Médio, Fator de Alavancagem, Limite Otimizado e Status (Viável / Sem Solução).

- Busca filtra por `CLU-{cluster_id}` em tempo real
- Paginação de 15 registros por página
- Exportar gera `clusters_{safra}.csv` no browser via `Blob`, sem chamar a API

---

## 8. Fluxo 2 - Gerar Limites (GerarLimites.js)

### 8.1 Upload

Aceita exclusivamente arquivos `.parquet`. A tentativa de upload de qualquer outro formato exibe erro de validação antes de qualquer requisição.

A dropzone suporta drag-and-drop e clique. O campo `safra_numero` fica oculto em "Opções avançadas" e é opcional: quando omitido, o backend auto-incrementa o número da safra.

### 8.2 Colunas esperadas no .parquet

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

### 8.3 Modal de envio

Ao clicar em "Executar Simplex", um modal bloqueante cobre a tela enquanto o arquivo é enviado via `POST /api/consultas`. O modal exibe o nome e o tamanho do arquivo e não pode ser fechado pelo usuário. Fecha automaticamente quando o backend responde.

### 8.4 Tratamento do conflito 409

Se `safra_numero` for informado e a safra já existir, o backend retorna 409. O modal fecha e um aviso inline aparece com dois botões: "Usar safra existente" (reenvia com `usar_safra_existente=true`) e "Cancelar".

### 8.5 Monitoramento

Após receber a resposta `pendente` do backend, a consulta aparece na lista de simulações. O polling inicia com uma primeira verificação em 5 segundos (tempo para o background task iniciar) e depois a cada 60 segundos via `GET /api/consultas/{id}`.

Durante a execução, cada consulta exibe as três etapas do pipeline com animação de pulso: Calibração, Clustering (CART) e Otimização (Simplex). O botão "Verificar agora" cancela o timer pendente e consulta imediatamente.

Quando o status muda para `concluido`, o componente chama `getClusters(id)` e exibe os resultados abaixo da lista. Quando muda para `erro`, exibe `erro_etapa` e `erro_mensagem` do backend.

### 8.6 Resultados inline

Exibidos após a conclusão da consulta ativa ou ao clicar em "Ver resultados" em qualquer consulta concluída da lista.

**KPIs:** `n_clusters`, `z_otimo`, `n_clientes_elegiveis`, `n_clientes_ofertados` (com percentual calculado sobre elegíveis).

**Gráficos:**

- Barras verticais com os 15 clusters de maior limite otimizado
- Donut com distribuição de clientes: Com limite / Elegível sem limite / Inelegível

**Tabela de clusters:** paginada em 20 por página, com colunas PD Média, Score Cross Médio, Fator de Alavancagem, Limite Otimizado e Status.

**Exportar:** chama `Api.exportClientes(id)` que baixa o CSV completo de clientes gerado pelo backend.

---

## 9. Fluxo 3 - Resultados (Resultados.js)

Página independente acessível diretamente pela navbar. Ao montar, carrega todas as consultas concluídas e safras em paralelo e seleciona a mais recente por padrão.

### 9.1 Seletor de simulação

Dropdown no cabeçalho lista todas as consultas concluídas no formato `{safra} · {arquivo}`. Ao trocar a seleção, os clusters da nova consulta são carregados via `getClusters(id)`.

### 9.2 KPIs

Mesmos quatro campos de `ConsultaResponse`: `n_clusters`, `z_otimo`, `n_clientes_elegiveis`, `n_clientes_ofertados`.

### 9.3 Gráficos

| Componente     | Dados                                                                                   |
| -------------- | --------------------------------------------------------------------------------------- |
| `BarChartSVG`  | Top 15 clusters por `limite_otimizado`, ordenados decrescentemente                      |
| `DonutChart`   | Distribuição de clientes: Com limite / Elegível sem limite / Inelegível                 |
| `LineChartSVG` | Evolução do `z_otimo` entre consultas concluídas, ordenadas cronologicamente            |
| `RiskHistSVG`  | Histograma de clusters por faixa de PD média: 0-5%, 5-10%, 10-15%, 15-20%, 20-25%, 25%+ |

### 9.4 Parâmetros utilizados

Seção colapsável exibindo os parâmetros exatos da consulta selecionada (`t`, `LGD`, `u_bar`, `L_max`, `T`). Útil para auditoria e reprodução dos resultados.

### 9.5 Exportação

Botão "Exportar clientes CSV" chama `Api.exportClientes(id)`, que retorna o arquivo gerado pelo backend com todos os campos de `ClienteResultadoResponse`.

---

## 10. Fluxo 4 - Clientes (Clientes.js)

### 10.1 Objetivo

Permite ao analista localizar um cliente específico por token numérico e visualizar sua evolução entre safras: limite otimizado, PD calibrada, cluster atribuído e demais indicadores relevantes para análise individual de crédito.

### 10.2 Busca

Campo de texto aceita apenas tokens numéricos. A validação acontece no frontend antes da requisição. Ao submeter (Enter ou botão "Buscar"), chama `Api.getHistoricoCliente(token)` que mapeia para `GET /api/clientes/{token}`. Erro 404 exibe mensagem inline "Token não encontrado em nenhuma simulação." sem quebrar a tela.

### 10.3 Resultados

Exibidos quando a API retorna ao menos um registro histórico. Cada entrada corresponde a uma safra em que o cliente apareceu. Os dados são apresentados como cards de evolução cronológica, com os principais indicadores por safra: cluster atribuído, limite otimizado, PD calibrada, score cross e status.

---

## 11. Fluxo 5 - Configurações (ConfigModal.js)

### 11.1 Acesso

Disparado pelo último item da navbar (identificado como `isConfig: true`). Sobrepõe a página ativa com fundo semi-transparente. Ao abrir, carrega os valores atuais via `GET /api/config`.

### 11.2 Parâmetros editáveis

Cada parâmetro é exibido como um card com valor atual e botão de edição. Ao clicar em editar, o card expande com um slider cujos limites e passo são definidos em `PARAMS_EDITAVEIS` em `data.js`.

Salvar envia `PUT /api/config` com o payload `{ t, LGD, u_bar, L_max, T }` e atualiza o estado local. Cancelar restaura o valor que veio da API na abertura do modal (não o fallback local de `data.js`).

### 11.3 Restaurar padrões

Botão no rodapé do modal. Exibe `window.confirm` antes de executar. Envia `PUT /api/config` com os valores de fábrica definidos em `PARAMS_EDITAVEIS.value` e atualiza o banco.

### 11.4 Parâmetros não editáveis

Grid de dois cards por linha exibindo os parâmetros fixados pela modelagem ou pelo regulador.

---

## 12. Visualizações de Dados

Todos os gráficos são componentes SVG puros definidos em `Resultados.js` como variáveis globais (`var`), acessíveis por `GerarLimites.js` após o carregamento dos scripts. Não há bibliotecas externas de charting.

| Componente     | Tipo                | Descrição                                                                                                                                                             |
| -------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BarChartSVG`  | Barras verticais    | Barras azul PAN para clusters com limite, cinza `#E8EFF7` para clusters sem solução. Rótulo de valor acima de cada barra. Eixo Y com escala automática em R$k ou R$M. |
| `LineChartSVG` | Linha com área      | Área sombreada azul, pontos com rótulo de valor alternados. Requer no mínimo 2 pontos; exibe aviso quando há apenas uma consulta.                                     |
| `DonutChart`   | Rosca               | Fatias calculadas a partir das contagens da `ConsultaResponse`. Legenda lateral com valores absolutos.                                                                |
| `RiskHistSVG`  | Histograma de risco | Seis faixas de PD média com gradiente visual de verde (baixo risco) a vermelho (alto risco). Conta clusters por faixa.                                                |

Todas as visualizações usam exclusivamente cores da paleta PAN: azul `#2E6DA4` como cor principal, `#E8EFF7` para linhas de grade, paleta terciária (verde/amarelo/vermelho) para status e risco.

## 13. Diferenças em Relação ao Protótipo

A implementação do front-end manteve os fluxos centrais definidos no protótipo: carregamento da base, geração de limites, acompanhamento dos resultados, visualização analítica e configuração dos parâmetros do modelo. No entanto, durante a integração com o back-end e com o otimizador, algumas decisões de implementação foram ajustadas para refletir melhor a arquitetura real da solução e as necessidades técnicas do pipeline de otimização.

| Item no protótipo | Implementação entregue | Justificativa |
| ----------------- | ---------------------- | ------------- |
| Upload de arquivo CSV/XLSX simulando uma base parquet | Upload real de arquivo `.parquet` | O `.parquet` é o formato utilizado pelo pipeline de dados e pelo back-end. A alteração aproxima a interface da operação real esperada em produção e reduz inconsistências entre protótipo e execução técnica. |
| Geração de limites apresentada como uma ação imediata após o upload | Execução assíncrona com criação de consulta, status pendente e acompanhamento por polling | O processo de otimização envolve leitura da base, calibração de PD, clusterização e execução do Simplex, etapas que podem demandar tempo. Por isso, a interface foi adaptada para acompanhar uma execução longa sem bloquear o uso da aplicação. |
| Upload simples de arquivo único | Upload em chunks com barra de progresso | A estratégia em chunks melhora a robustez para arquivos grandes, evita falhas por limite de payload e oferece feedback visual mais adequado ao usuário durante o envio da base. |
| Visualizações previstas de forma conceitual no protótipo | Gráficos SVG implementados no front-end: barras, rosca, linha temporal e histograma de risco | Os gráficos SVG funcionam como estrutura equivalente ao canvas, permitindo visualizações gráficas próprias, leves e sem dependência de bibliotecas externas de charting. A escolha também facilita o controle visual e a adaptação às métricas reais do modelo. |
| Tela de configurações com parâmetros gerais do modelo | Modal de configuração com os parâmetros utilizados pelo otimizador: `t`, `LGD`, `u_bar`, `L_max` e `T` | A implementação priorizou os parâmetros efetivamente consumidos pelo modelo de programação linear, garantindo consistência entre interface, back-end e otimizador. |
| Resultados exibidos principalmente por cluster | Resultados por cluster, indicadores consolidados, histórico de simulações e exportação de clientes | A entrega expande a análise planejada no protótipo, oferecendo uma visão mais completa para acompanhamento das safras e reutilização dos resultados em outros sistemas. |
| Não havia uma tela específica para análise individual de clientes | Inclusão da tela de busca por token e histórico do cliente | A nova tela melhora a capacidade de auditoria da solução, permitindo acompanhar a evolução de um cliente específico entre diferentes simulações e safras. |
| Protótipo focado na experiência visual da jornada | Front-end integrado aos contratos reais da API | A implementação deixou de ser apenas demonstrativa e passou a consumir os endpoints reais do back-end, aumentando a fidelidade técnica da entrega parcial. |

Essas diferenças foram incorporadas como melhorias de viabilidade técnica e aderência ao funcionamento real da aplicação. Assim, a entrega preserva a intenção original do protótipo, mas adapta a experiência para um cenário mais próximo da execução em produção, considerando arquivos grandes, processamento assíncrono, persistência dos resultados e integração com o otimizador.