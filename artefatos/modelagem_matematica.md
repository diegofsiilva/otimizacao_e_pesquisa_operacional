# Modelagem Matemática

**Guia de uso deste template:**
- Trechos em *itálico entre colchetes* `[...]` são instruções — substituir pelo conteúdo do grupo
- Blocos **PROFESSORA**, **TAPI**, **PARA NOTA 10** e **NÃO FAZER** são lembretes internos — **remover antes de entregar**

---

### Perfil da professora (análise de 4 feedbacks do módulo passado, notas 7,5 a 9,0)

**O que ela mais valoriza (aparece em TODO feedback positivo):**
1. **Classificar o tipo clássico de problema** — ela quer ler "este é um problema de [tipo]" (G01: cobrou ausência disso)
2. **Variáveis segmentadas** — flaggeou variável agregada em **3 de 4 grupos**. É o ponto #1 dela. Neste projeto: por cluster, não por produto.
3. **Formulação limpa e legível** — G03 perdeu pontos por "fórmulas difíceis de ler"
4. **Tabela de trade-offs** mostrando entendimento real do problema (G01: "excelente")
5. **Consistência conceitual** entre texto e modelo — G01 perdeu 2pts por contradição texto↔modelo
6. **MVP vs Target** e análise de sensibilidade — elogiou explicitamente no G06
7. **Grafo presente e coerente** com o modelo — G03 perdeu pontos por grafo ausente (NÃO é obrigatório no roteiro novo, mas a professora claramente valoriza — forte candidato a **ir além**)

**O que ela penaliza (padrões de desconto):**
1. ~~Variável agregada quando deveria ser segmentada~~ — cobrou em G02, G03, G06
2. ~~FO com escalas misturadas sem normalização~~ — G02 (tempo + km + R$ + índice)
3. ~~FO descrita em texto mas não formalizada em equação~~ — G01
4. ~~Binária desnecessária quando fluxo já indica uso~~ — G02
5. ~~Proxy não marcada como simplificação~~ — G06
6. ~~Inconsistência entre texto descritivo e formulação matemática~~ — G01 perdeu 2pts
7. ~~FO com muitos parâmetros difíceis de calibrar~~ — G02: "terão dificuldade em calibrar os pesos"

**Conclusão para nota 10:**
- Nomear o tipo de problema logo no começo
- Variáveis **sempre** segmentadas (por cluster neste projeto)
- FO com termos **na mesma escala** (tudo em R$) e separados com labels claros
- Cada proxy marcada explicitamente
- Fórmulas **legíveis** (não amontoar tudo em uma linha)
- Texto e modelo **dizem a mesma coisa** — se o texto diz "por cluster", a variável é $L_k$, não $L_i$

---

### ALERTA CRÍTICO — LP, NÃO MIP

O TAPI diz textualmente:
- *"Todas as soluções apresentadas devem ser consideradas como problemas de **otimização linear**."*
- *"Restrições que comprometam a linearidade **e/ou a continuidade** do modelo poderão ser simplificadas, aproximadas ou adaptadas."*

Isso significa:
- **Variáveis contínuas** — não usar inteiras ($\mathbb{Z}$) na formulação principal
- **Discretização (R$ 50) é pós-processamento**, não restrição do modelo
- A decisão binária ($z_k$: oferecer ou não) pode ser **relaxada para [0,1]** no LP — ou resolvida em duas etapas (primeiro selecionar clusters, depois otimizar limites)
- No mundo ideal, MIP capturaria melhor a realidade (limite discreto + seleção binária). Mas a escala (~1,8M elegíveis) e a orientação do TAPI direcionam para **LP contínuo com arredondamento posterior**

---

### ESTRUTURA DO ARTEFATO (roteiro atualizado)

O artefato tem **duas seções** com pesos distintos:

| Seção | Peso | O que pede |
|:---|:---:|:---|
| **(a) Modelagem matemática** | 6 | Contexto + dados + variáveis de decisão + formulação (FO + ≥2 restrições) + objetivo |
| **(b) Análise crítica** | 4 | ≥2 limitações + sensibilidade de ≥1 parâmetro. **MÁXIMO 12 LINHAS.** |

**Atenção:** O roteiro NÃO pede mais grafos nem MVP vs Target como itens separados. Esses podem ser **ir além** (a professora valoriza ambos nos feedbacks).

**CUIDADO com o item (b):** 12 linhas é MUITO pouco. Cada limitação precisa de ~3 linhas (descrição + impacto + tratamento) e a sensibilidade ~3-4 linhas. Ser cirúrgico.

---

## a) Modelagem matemática do problema (Peso 6)

**O que o roteiro pede, na ordem:**
1. Contexto do problema a ser modelado
2. Dados disponíveis relevantes
3. Definição das variáveis de decisão
4. Formulação matemática da tomada de decisão da empresa
5. Objetivo do modelo
6. Pelo menos duas restrições que impactem a solução ótima

Tudo em uma única seção integrada. A professora quer ver **coesão** — não 6 blocos desconectados, mas um texto que flui do problema para a formulação.

### Contexto do problema

*Descrever o problema do Banco Pan e explicar **por que ele é um problema de otimização**.*

*Deve responder:*
- *Qual é o problema? → Definir limite pré-aprovado de cartão de crédito por cliente/cluster*
- *Por que a prática atual é insuficiente? → Scoring + tabela fixa ignora heterogeneidade, não controla risco agregado*
- *Qual é o trade-off? → Receita (interchange) vs. risco (inadimplência)*

**PROFESSORA — OBRIGATÓRIO (G01 perdeu pontos por não fazer):**
Incluir uma frase explícita classificando o tipo de problema. Exemplo:
*"Este problema pode ser formulado como um problema de **programação linear (LP) de alocação de crédito**, no qual a variável de decisão é o limite (contínuo) por cluster de clientes, a função objetivo maximiza o retorno líquido (receita de interchange menos perda esperada), e as restrições impõem tetos de inadimplência agregada, capacidade de pagamento individual e regras operacionais."*

**TAPI — pontos que devem aparecer no contexto:**
- Mono-produto (cartão de crédito pré-aprovado)
- Correntistas elegíveis à concessão
- **Otimização linear** — não-linear, estocástica e inteira fora do escopo (TAPI: "restrições que comprometam a continuidade poderão ser simplificadas")
- O parceiro avalia comparando rentabilidade entre `limite_ofertado` (atual) e limite sugerido

**Frase sugerida sobre LP vs MIP:**
*"O TAPI orienta que o problema seja tratado como programação linear, permitindo simplificação de restrições que comprometam a continuidade do modelo. Embora a discretização dos limites em múltiplos de R$ 50 e a decisão binária de oferta tornem o problema naturalmente misto-inteiro, a escala da base (~1,8M elegíveis) e o escopo do curso direcionam para uma formulação LP contínua, com arredondamento dos limites em etapa de pós-processamento."*

**PARA NOTA 10:**
- Dimensionar com dados reais: ~14,5M clientes, **~1,8M elegíveis** (`flag_filtros = 0`)
- Apresentar uma **tabela de trade-offs** (professora elogiou em G01 como "excelente"):

| Decisão | Se limite alto demais... | Se limite baixo demais... |
|:---|:---|:---|
| Receita | ↑ Mais interchange | ↓ Menos uso, menos receita |
| Risco | ↑ Mais exposição, mais inadimplência | ↓ Menor inadimplência |
| Cliente | Risco de sobre-endividamento | Frustração, migração pra concorrente |
| Banco | Provisão maior, NPL sobe | Perda de competitividade |

- Citar referências de Credit Limit Optimization (FICO, Moody's, Experian)
- Ir direto ao problema — **não** explicar "o que é otimização"

**NÃO FAZER:**
- ~~"Otimização é uma área da matemática que..."~~
- ~~Falar do setor bancário em geral sem conectar ao Pan~~
- ~~Tratar como multi-produto~~ — o TAPI é só cartão
- ~~Classificar como MIP sem justificar por que o TAPI aceita LP~~

*[Escrever 2-3 parágrafos + classificação do tipo de problema + tabela de trade-offs]*

---

### Dados disponíveis relevantes

*O parceiro forneceu 3 bases Parquet (safras M1, M2, M3) com 17 variáveis. Listar as que entram diretamente na FO ou nas restrições, com estatísticas reais.*

**Estatísticas-chave da base M1 (extraídas dos dados reais):**
- `pd_produto`: min=0,037, mediana=0,709, max=0,940 — **maioria da base tem PD alta**
- `capacidade_pagamento`: min=0, mediana=550, max=25.000. **Nulls: 0,3% em M1, ~22% em M2/M3**
- `score_propensao_contrato`: range [4, 840] — **não é [0,1]**, requer normalização
- `flag_filtros`: **1 = restrito** (12,7M), **0 = elegível** (~1,8M)
- `limite_ofertado`: **99,2% null** — só 117K receberam oferta
- `renda_estimada`: min=1.300, mediana=1.925, max=16.875
- Funil: 14,5M → 1,8M elegíveis → 117K com oferta → 6,5K contrataram → 5,7K ativaram

**PROFESSORA:** Ela valoriza quando o grupo mostra que **entende os dados de verdade**, não apenas lista. Dizer "mediana de PD é 0,71, portanto a maioria da base tem risco alto e a seleção de quem recebe oferta é tão importante quanto o limite" é o tipo de insight que impressiona.

| Variável | Descrição | Estatísticas (M1) | Papel no modelo |
|:---|:---|:---|:---|
| *[Preencher para cada variável que entra na FO ou restrições]* | | | |

*Focar nas que entram na FO ou nas restrições. Para cada uma, dizer **por que** é relevante e **como** entra.*

**PARA NOTA 10:**
- Explicitar variáveis **não fornecidas** que seriam úteis: LGD, taxa de interchange, utilização
- Documentar o problema de `capacidade_pagamento` null em M2/M3 (~22%)
- Mostrar que entende o viés de seleção: `over30mob3` só existe para ~5K que ativaram

---

### Variáveis de decisão

**TAPI — LP contínuo:**
- O TAPI exige "otimização linear" e permite simplificar restrições que comprometam continuidade
- Portanto: variável de limite é **contínua** ($L_k \in \mathbb{R}^+$), não inteira
- A discretização (R$ 50) é aplicada em **pós-processamento**, não como restrição do modelo
- A variável de seleção $z_k$ pode ser relaxada para $[0,1]$ ou tratada em etapa separada

**PROFESSORA (padrões do feedback):**
- Variáveis **segmentadas** ($L_k$, não $L$ genérico) — cobrado em 3 de 4 grupos
- **Não forçar binária** se não for necessário (G02). Neste projeto, $z_k$ é justificável mas deve ser justificada
- Usar domínio contínuo para manter LP conforme TAPI

| Símbolo | Descrição | Domínio | Justificativa do tipo |
|:---|:---|:---|:---|
| *$L_k$* | *[Limite por cluster]* | *$L_k \in \mathbb{R}^+$ (contínuo, ≥ 0)* | *[Contínua: TAPI exige LP. Discretização em múltiplos de R$ 50 é pós-processamento: $L_k^{final} = 50 \cdot \lceil L_k / 50 \rceil$, com piso de R$ 200]* |
| *$z_k$* | *[Cluster k recebe oferta?]* | *$z_k \in [0, 1]$ (relaxação LP) ou fixado em pré-seleção* | *[Decisão de oferta é genuinamente binária; no LP, tratada como contínua e arredondada em pós-processamento, ou resolvida via ranking por retorno unitário em etapa prévia]* |

**Conjuntos e índices (legenda obrigatória):**

| Símbolo | Descrição |
|:---|:---|
| *$i \in \{1, \dots, n\}$* | *Clientes elegíveis. n ≈ 1,8M em M1* |
| *$k \in \{1, \dots, K\}$* | *Clusters de risco, K ≥ 100* |
| *$\mathcal{C}_k$* | *Clientes pertencentes ao cluster k* |

**CONSISTÊNCIA (G01 perdeu pontos por isso):** Se a variável de decisão é $L_k$ (por cluster), TUDO usa $k$, não $i$. Se depois individualizar ($L_i$), atualizar conjuntos, parâmetros, FO e restrições.

---

### Parâmetros (dados de entrada)

*Para cada parâmetro: símbolo, descrição, unidade, fonte.*

**TAPI — parâmetros obrigatórios:**
- $PD_i$ ← `pd_produto`
- $CP_i$ ← `capacidade_pagamento`
- $\pi_i$ ← `score_propensao_contrato`, normalizado de [4, 840] para [0,1]
- Teto inadimplência física e financeira (atuais da carteira aprovada)
- Multiplicador de alavancagem $m_k$ por perfil de risco
- $L^{min} = 200$ (TAPI)
- Taxa de interchange $t$ (**proxy:** ~1,5%)
- Utilização $\bar{u}$ (**proxy:** ~0,40)
- Metas de produção opcionais

| Símbolo | Descrição | Unidade | Fonte |
|:---|:---|:---|:---|
| *[Preencher]* | | | |

**PROFESSORA:** Ela quer ver a **legenda completa**. Todo símbolo que aparece na FO ou restrição deve estar nesta tabela. Não deixar nenhum "solto".

---

### Objetivo do modelo e função objetivo

**PROFESSORA — OBRIGATÓRIO (G01 perdeu pontos):**
O objetivo deve estar **formalizado matematicamente**, não apenas descrito em texto.

**TAPI — definição do objetivo:**
- **Maximizar retorno esperado** sujeito a restrições
- Receita = **interchange a taxa fixa** (NÃO rotativo) — mantém linearidade
- Perda = **PD × exposição** (limite)
- Parceiro avalia comparando rentabilidade entre limite atual e sugerido

**Decisão de design — controle de risco:**
Duas abordagens válidas:
- **(a) FO = receita − λ·perda** — ponderação explícita na FO
- **(b) FO = receita − perda** — risco controlado via restrições (mais alinhado ao TAPI)

*Escolha uma e **justifique**.*

**Regras da professora para a FO (feedbacks):**
1. **Separar termos** com labels claros: (A) Receita, (B) Perda (G06: elogiado)
2. **Mesma escala/unidade** em todos os termos — neste projeto ambos são R$, ok (G02: perdeu pontos por misturar)
3. **Formalizar matematicamente**, não só descrever (G01: perdeu pontos)
4. **Marcar proxies**: "utilização constante é proxy" (G06: perdeu pontos por omitir)
5. **FO simples** — poucos parâmetros calibráveis (G02: penalizado por excesso)

**Dica de apresentação (G03 perdeu pontos por fórmulas difíceis de ler):**
Escrever a FO em forma expandida com labels:

$$\max \underbrace{\sum_{k} [\text{receita}_k]}_{\text{(A)}} - \underbrace{\sum_{k} [\text{perda}_k]}_{\text{(B)}}$$

E depois expandir cada termo separadamente, com explicação abaixo.

$$
\max \underbrace{[\text{termo de receita}]}_{\text{(A) Receita esperada de interchange}} \; - \; \underbrace{[\text{termo de perda}]}_{\text{(B) Perda esperada por inadimplência}}
$$

*[Expandir cada termo. Abaixo, explicar o que (A) e (B) representam e marcar proxies.]*

**Onde:**
- *(A) = ... **Proxy:** utilização constante $\bar{u}$ = 0,40*
- *(B) = ... **Proxy:** LGD = 1 (sem recuperação)*

**Nota sobre linearidade:**
A FO é linear em $L_k$ porque todos os demais termos ($\pi_i$, $\bar{u}$, $t$, $PD_i$) são **parâmetros**, não variáveis de decisão. O produto $z_k \cdot L_k$ é bilinear se ambos forem variáveis — tratar via abordagem em duas etapas (fixar $z_k$ primeiro, depois otimizar $L_k$) para manter LP puro.

---

### Restrições (pelo menos 2 obrigatórias)

*Para cada restrição: expressão + explicação em linguagem de negócio.*

**PROFESSORA:** Ela quer ver a restrição **e** a explicação de negócio. Se a restrição é **não-linear** (como razão), **documentar a linearização** (G06 elogiado).

**TAPI — restrições obrigatórias:**

| Restrição | Exigência do TAPI | Formulação |
|:---|:---|:---|
| **R1: Inadimplência física** | Média simples da PD ≤ nível atual | Razão → linearizar multiplicando pelo denominador |
| **R2: Inadimplência financeira** | Média PD ponderada por limite ≤ nível atual | Ponderada por $L_k$. Contém produto $z_k \cdot L_k$ — tratar via duas etapas |
| **R3: Capacidade de pagamento** | Limite ≤ multiplicador × capacidade. Multiplicador **diferenciado** por perfil de risco | $L_k \leq m_k \cdot \min_{i \in C_k} CP_i$ |
| **R4: Limite mínimo** | ≥ R$200 | $L_k \geq 200$ (para clusters selecionados). Discretização R$ 50 é **pós-processamento** |
| **R5-R7: Metas de produção** | Quantidade aprovados, volume, rentabilidade (opcionais) | Restrições de piso configuráveis |

**Sobre bilinearidade ($z_k \cdot L_k$) dentro do LP:**
Os termos da FO e de R2/R6/R7 contêm o produto $z_k \cdot L_k$. Se ambos forem variáveis, isso é bilinear. Tratamento recomendado para LP:
**Duas etapas:** Etapa 1 — selecionar clusters (fixar $z_k$) via ranking de retorno unitário. Etapa 2 — otimizar $L_k$ para os selecionados (LP puro, todas as variáveis contínuas).

**CONSISTÊNCIA:** Verificar que **cada variável na restrição existe na tabela de parâmetros ou variáveis de decisão**. Se $m_k$ aparece em R3, ele deve estar definido na tabela de parâmetros.

#### R1 — *[Nome: Teto de inadimplência física]*

$$
\text{[expressão — legível, não amontoada]}
$$

*[Explicação de negócio: o que garante]*

*[Se linearizou: mostrar versão original (razão) → versão linearizada, com o passo]*

#### R2 — *[Nome: Teto de inadimplência financeira]*

$$
\text{[expressão]}
$$

*[Explicação + linearização + tratamento da bilinearidade]*

*[Continuar para R3, R4, R5... R1-R4 são as restrições do TAPI. Pelo menos 2 obrigatórias pelo roteiro.]*

---

## b) Análise crítica (Peso 4 — MÁXIMO 12 LINHAS)

**ATENÇÃO: O roteiro exige objetividade — máximo 12 linhas.**
São ~4 linhas por limitação (2 limitações) + ~4 linhas para sensibilidade. Cada linha deve contar.

**Estrutura recomendada:**
- Limitação 1: [nome] — [impacto em 1 frase] — [como tratar em 1 frase]
- Limitação 2: [nome] — [impacto] — [tratamento]
- Sensibilidade: variar [parâmetro] de [X a Y] → impacto em [métrica]: [resultado qualitativo]

**PROFESSORA — o que diferencia nota 8 de nota 10 aqui:**
- G01 (8,0): listou limitações mas não conectou ao modelo
- G06 (9,0): discutiu MVP vs Target, marcou proxies
- **Nota 10:** cada limitação conecta diretamente a uma equação da seção (a) e a sensibilidade mostra direção do impacto

**Limitações concretas deste projeto (escolher pelo menos 2):**
1. **Receita restrita a interchange** — TAPI exige. Subestima receita real. Impacto: FO conservadora, limites tendem a ser mais baixos que o ótimo real.
2. **LGD = 1 (sem recuperação)** — Superestima perda. Impacto: modelo rejeita clusters que seriam rentáveis com recuperação parcial. **Proxy.**
3. **Utilização constante** — Ignora heterogeneidade de uso entre perfis. Impacto: receita estimada uniformemente, distorcendo alocação entre clusters de alto e baixo uso.
4. **Relaxação LP (TAPI)** — Perda de otimalidade pelo arredondamento. Impacto: marginal (~R$ 25 por cliente na média).
5. **`capacidade_pagamento` null ~22% em M2/M3** — Restrição R3 inaplicável para esses clientes. Tratamento: proxy via `renda_estimada`.

**Parâmetros para sensibilidade (escolher pelo menos 1):**
- Teto de inadimplência (±1-2pp) → impacto em número de aprovados e retorno total
- Utilização $\bar{u}$ (0,20 a 0,50) → alta sensibilidade na receita
- Multiplicador $m_k$ → impacto direto no teto de limite individual
- Taxa de interchange $t$ (1,0% a 2,0%) → impacto linear na receita

*[Escrever EXATAMENTE o texto final aqui — máximo 12 linhas, contando cada quebra de linha. Ser cirúrgico.]*

**NÃO FAZER:**
- ~~Explicar o que é "análise de sensibilidade"~~
- ~~Repetir a formulação da seção (a)~~
- ~~Ultrapassar 12 linhas~~ — a professora pode penalizar
- ~~Listar limitações genéricas ("dados podem ter ruído")~~ — cada limitação deve referenciar um parâmetro ou equação específica do modelo

---

## Ir Além (não obrigatório — mas a professora valoriza)

O roteiro novo é mais enxuto que o anterior (2 itens vs 5). Isso abre espaço para diferenciação via ir além. Com base nos feedbacks, os itens abaixo são os que mais impressionam a professora:

### Candidato 1: Representação em grafos

**PROFESSORA:** G03 perdeu pontos por grafo ausente no módulo passado. G01 e G06 foram elogiados. Mesmo que o roteiro novo não peça explicitamente, a professora claramente valoriza.

**Sugestão:** Grafo bipartido — Clusters (A) × Intervalos de limite (B). Aresta = factibilidade (R3, R4). Peso = retorno líquido. Coerente com formulação LP (intervalos contínuos, não pontos discretos).

![Representação em Grafos](assets/grafo_representacao.png)

*[Se fizer: criar diagrama visual + tabela mapeando elementos do grafo → elementos do problema]*

| Elemento do grafo | Representa no problema |
|:---|:---|
| *[Nós A]* | *[Clusters de clientes]* |
| *[Nós B]* | *[Intervalos de limite factível]* |
| *[Arestas]* | *[Factibilidade (cluster k pode receber limite no intervalo [200, $m_k \cdot \min CP_k$])]* |
| *[Peso]* | *[Retorno líquido = receita − perda]* |
| *[Restrições globais]* | *[R1, R2: inadimplência; R5-R7: metas]* |

### Candidato 2: Tabela MVP vs Target

**PROFESSORA:** Elogiou explicitamente no G06.

| Componente | MVP (Sprint 1-3) | Target (Sprint 4-5) |
|:---|:---|:---|
| **Formulação** | *LP contínuo (exigência TAPI)* | *MIP se solver suportar escala* |
| **Granularidade** | *Por cluster, ≥ 100 clusters* | *Por cliente, individualizado* |
| **Variáveis** | *$L_k \in \mathbb{R}^+$ (contínua)* | *$L_i \in \mathbb{Z}^+$ (inteira, múltiplos R$ 50)* |
| **Seleção** | *Pré-processamento (ranking)* | *Integrada via $z_k$ binária* |
| **Discretização** | *Pós-processamento (arredondamento R$ 50)* | *Restrição inteira no modelo* |
| **Utilização** | *Constante 0,40. **Proxy.*** | *Estimada por cluster* |
| **Receita** | *Interchange taxa fixa ~1,5%. **Proxy.*** | *Taxa calibrada com parceiro* |
| **Perda** | *PD × L (LGD=1). **Proxy.*** | *PD × LGD × L se LGD fornecida* |
| **Solver** | *SciPy linprog ou PuLP + CBC* | *OR-Tools ou Gurobi* |

### Candidato 3: Análise de sensibilidade expandida

Ir além das 12 linhas com tabela de parâmetros, valores testados e hipóteses de impacto. A professora elogiou no G06.
**Dica LP:** explorar **preços-sombra** das restrições R1 e R2 — quanto retorno o banco "paga" por cada ponto de inadimplência de folga.

---

## Checklist pré-entrega

### Item (a) — Modelagem (peso 6)
- [ ] **Tipo de problema classificado** ("este é um problema de [tipo clássico]") — G01 perdeu por omitir
- [ ] **Tipo = LP** (programação linear), com justificativa de por que não MIP (TAPI + escala)
- [ ] **Tabela de trade-offs** presente no contexto — G01: "excelente"
- [ ] **Dados com estatísticas reais** e insight (não só listar)
- [ ] **Variáveis segmentadas** por cluster ($L_k$), não agregadas — cobrado em 3/4 grupos
- [ ] **Variáveis contínuas** ($L_k \in \mathbb{R}^+$) — coerente com LP do TAPI
- [ ] **Pós-processamento documentado** — discretização R$ 50 e seleção de clusters após LP
- [ ] **FO com termos na mesma escala** (R$) e labels (A), (B) — G02 perdeu pontos
- [ ] **FO formalizada em equação** — G01 perdeu pontos
- [ ] **Proxies marcadas** em toda ocorrência ($\bar{u}$, $t$, LGD=1) — G06 perdeu pontos
- [ ] **Fórmulas legíveis** — G03 perdeu pontos
- [ ] **Consistência texto ↔ modelo** — G01: -2pts
- [ ] **Bilinearidade tratada** ($z_k \cdot L_k$) — documentar abordagem em duas etapas
- [ ] **Linearização documentada** para restrições não-lineares (razão de inadimplência)
- [ ] **Legenda completa** — todo símbolo definido

### Item (b) — Análise crítica (peso 4)
- [ ] **≥ 2 limitações** identificadas com impacto concreto no modelo
- [ ] **≥ 1 parâmetro** com análise de sensibilidade (direção do impacto)
- [ ] **≤ 12 linhas** — contar antes de entregar!
- [ ] Cada limitação **referencia** uma equação ou parâmetro da seção (a)
- [ ] Sem explicações conceituais ("sensibilidade é quando...")

### Alinhamento TAPI
- [ ] Mono-produto (cartão)
- [ ] **Otimização linear** (LP) — NÃO MIP como formulação principal
- [ ] Receita = interchange a taxa fixa (não rotativo)
- [ ] Perda = PD × exposição
- [ ] Inadimplência **física** (média simples PD) como restrição
- [ ] Inadimplência **financeira** (média PD ponderada por limite) como restrição
- [ ] Alavancagem **diferenciada** por perfil de risco
- [ ] Limite mínimo R$ 200
- [ ] Preferência por múltiplos de R$ 50 (pós-processamento)
- [ ] Metas de produção configuráveis
- [ ] ≥ 100 clusters ou individualizado
- [ ] Output Python

---

## Fontes

1. *[Referências de Credit Limit Optimization: FICO, Moody's, Experian]*
2. *[Referências acadêmicas: Hillier & Lieberman, artigos de otimização de crédito]*
3. *[Dados do parceiro: RI Banco Pan, TAPI]*
4. *[Metodologia de sensibilidade: Pannell (1997), Saltelli et al. (2000)]*
