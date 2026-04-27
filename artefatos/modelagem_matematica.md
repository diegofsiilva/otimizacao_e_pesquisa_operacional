# Modelagem Matemática

**Guia de uso deste template:**

- Trechos em _itálico entre colchetes_ `[...]` são instruções — substituir pelo conteúdo do grupo
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

- _"Todas as soluções apresentadas devem ser consideradas como problemas de **otimização linear**."_
- _"Restrições que comprometam a linearidade **e/ou a continuidade** do modelo poderão ser simplificadas, aproximadas ou adaptadas."_

Isso significa:

- **Variáveis contínuas** — não usar inteiras ($\mathbb{Z}$) na formulação principal
- **Discretização (R$ 50) é pós-processamento**, não restrição do modelo
- A decisão binária ($z_k$: oferecer ou não) pode ser **relaxada para [0,1]** no LP — ou resolvida em duas etapas (primeiro selecionar clusters, depois otimizar limites)
- No mundo ideal, MIP capturaria melhor a realidade (limite discreto + seleção binária). Mas a escala (~1,8M elegíveis) e a orientação do TAPI direcionam para **LP contínuo com arredondamento posterior**

---

### ESTRUTURA DO ARTEFATO (roteiro atualizado)

O artefato tem **duas seções** com pesos distintos:

| Seção                        | Peso | O que pede                                                                           |
| :--------------------------- | :--: | :----------------------------------------------------------------------------------- |
| **(a) Modelagem matemática** |  6   | Contexto + dados + variáveis de decisão + formulação (FO + ≥2 restrições) + objetivo |
| **(b) Análise crítica**      |  4   | ≥2 limitações + sensibilidade de ≥1 parâmetro. **MÁXIMO 12 LINHAS.**                 |

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

O Banco Pan precisa definir, para cada cliente correntista elegível, qual limite pré-aprovado de cartão de crédito oferecer. Trata-se de um problema mono-produto: o escopo é exclusivamente o cartão de crédito pré-aprovado, sem considerar outros produtos de crédito da instituição. A prática vigente combina modelos de scoring com tabelas fixas de política de crédito, uma abordagem que trata de forma homogênea clientes com perfis de risco e capacidade de pagamento distintos. Isso significa que o risco agregado da carteira não é controlado diretamente pela decisão de limite, e que o potencial de retorno de parte da base elegível não é aproveitado. A validação do modelo desenvolvido neste projeto será feita pelo parceiro comparando a rentabilidade esperada entre o limite_ofertado praticado atualmente e o limite sugerido pelo modelo otimizado.

O núcleo do problema é um trade-off entre duas forças opostas. Um limite alto demais aumenta a receita de interchange, mas eleva a exposição à inadimplência e pode comprometer a saúde financeira do cliente. Um limite baixo demais reduz o risco, mas diminui a receita e pode frustrar o cliente a ponto de migrá-lo para um concorrente. A tabela abaixo resume esse trade-off:

| Decisão   | Se o limite for alto demais               | Se o limite for baixo demais           |
| :-------- | :---------------------------------------- | :------------------------------------- |
| _Receita_ | Mais interchange, maior retorno potencial | Menos uso do cartão, menos receita     |
| _Risco_   | Maior exposição, inadimplência sobe       | Menor inadimplência, carteira mais sã  |
| _Cliente_ | Risco de superendividamento               | Frustração, migração para concorrentes |
| _Banco_   | Provisão maior, NPL sobe                  | Perda de competitividade no produto    |

Esse equilíbrio entre retorno esperado e risco é amplamente estudado na literatura de otimização de crédito ao consumidor. Instituições como FICO (2021), Experian (2022) e Moody's Analytics (2020) tratam a definição de limite como um problema de otimização, onde a rentabilidade esperada é maximizada sujeita a restrições de risco da carteira e capacidade de pagamento individual.

Este problema pode ser formulado como um _problema de programação linear (LP) de alocação de crédito_, no qual a variável de decisão é o limite contínuo por cluster de clientes, a função objetivo maximiza o retorno líquido esperado (receita de interchange menos perda esperada por inadimplência), e as restrições impõem tetos de inadimplência agregada, capacidade de pagamento individual e regras operacionais do banco. Embora a discretização em múltiplos de R$ 50 e a seleção de quais clusters recebem oferta tornem o problema naturalmente misto-inteiro, o escopo do curso e a escala da base direcionam para uma formulação LP contínua, com arredondamento dos limites aplicado em pós-processamento ($L_k^{\text{final}} = 50 \cdot \lceil L_k / 50 \rceil$, com piso de R$ 200).

### Dados disponíveis relevantes

O parceiro forneceu três bases de dados em formato Parquet, correspondentes a três safras temporais (M1, M2, M3), contendo o universo de correntistas do Banco Pan. A tabela abaixo resume a dimensão e o funil de conversão de cada safra:

| Safra | Clientes totais | Elegíveis (`flag_filtros = 0`) | Receberam oferta | Contrataram | Ativaram | `over30mob3` observado |
|:---:|---:|---:|---:|---:|---:|---:|
| M1 | 14.569.142 | 1.836.085 | 117.367 | 6.506 | 5.704 | 4.966 (377 eventos) |
| M2 | 13.808.309 | 1.805.274 | 120.573 | 6.684 | 5.642 | 4.959 (372 eventos) |
| M3 | 13.868.729 | 3.137.258 | 382.692 | 9.930 | 8.347 | 7.465 (556 eventos) |

A tabela a seguir detalha as 17 variáveis fornecidas, com estatísticas descritivas reais da safra M1 e o papel de cada uma no modelo.

| Variável | Descrição | Estatísticas (M1) | Papel no modelo |
|:---|:---|:---|:---|
| `token` | Identificador anônimo por safra | 0 a 14.569.141 | Chave de identificação |
| `safra_ref_uso` | Safra de referência | M1, M2, M3 | Permite backtesting entre safras |
| `score_interno` | Score de crédito interno | min=54, med=292, max=975 | Não utilizado diretamente no modelo — serve apenas como input interno do banco para gerar `pd_produto` |
| `pd_produto` | Probabilidade de default no produto | min=0,025, med=0,71, max=0,946 | **Parâmetro central da FO (termo B) e das restrições R1 e R2.** Mediana de 0,71 indica que a maioria da base elegível tem PD alta — a seleção de quem recebe oferta é tão importante quanto a calibração do limite |
| `score_generico_1` | Score de bureau (bureau 1) | min=49, med=409, max=995. Nulls: 0,1% | Variável de entrada para clusterização (ver seção Pré-processamento) |
| `score_generico_2` | Score de bureau (bureau 2) | min=1, med=713, max=942. Nulls: <0,01% | Variável de entrada para clusterização (ver seção Pré-processamento) |
| `capacidade_pagamento` | Estimativa interna de capacidade de pagamento | min=0, med=548, max=25.000. **Nulls: 0,3% M1; 42,2% M2; 43,5% M3** | **Restrição R3 (alavancagem).** Nulls em M2/M3 são limitação severa — ver seção (b) |
| `delta_capacidade_pagamento` | Capacidade deduzida dos saldos a vencer | min=−25.000, med=55, max=25.000. Nulls: idem | Versão conservadora da capacidade — valores negativos indicam comprometimento além da capacidade |
| `renda_estimada` | Estimativa interna de renda | min=1.275, med=1.908, max=17.950. Nulls: 0,3% | Proxy alternativa para R3 quando `capacidade_pagamento` é null |
| `fx_idade` | Faixa etária | 9 faixas: 21-30 (35,5%), 31-40 (31,1%), 41-50 (18,8%) | Variável de entrada para clusterização (ver seção Pré-processamento) |
| `flag_filtros` | Indicador de perfil restrito | **0 = elegível** (1,84M), **1 = restrito** (12,73M) | Restrição hard: clientes com `flag_filtros = 1` são excluídos da otimização |
| `score_propensao_contrato` | Score de propensão à conversão | min=3, med=315, max=846 | Parâmetro $\pi_i$ na FO (termo A). **Range [3, 846], não [0,1]** — requer normalização min-max |
| `score_credito_cross` | Score de crédito multiproduto | min=103, med=706, max=954 | Variável de entrada para clusterização (ver seção Pré-processamento); pode informar o multiplicador de alavancagem $m_k$ |
| `limite_ofertado` | Limite ofertado na política atual | min=200, med=806, max=20.000. **99,2% null** | Baseline para backtesting — apenas 117K têm referência |
| `flag_contrato` | Indicadora de contratação (1 = contratou) | 6.506 (0,04%) | Backtesting. Taxa de conversão ~5,5% entre os que receberam oferta |
| `flag_ativacao` | Indicadora de ativação (1 = ativou) | 5.704 (87,7% dos que contrataram) | Backtesting |
| `over30mob3` | Atraso >30 dias nas 3 primeiras parcelas | 4.966 válidos, **377 eventos** (7,6%). 99,97% null | Inadimplência realizada. Viés de seleção severo — só observável para quem ativou |

**Observações críticas sobre os dados:**

**Funil de conversão (M1):** Dos 14,5M clientes, ~1,8M são elegíveis. Desses, 117K receberam oferta (6,4% dos elegíveis). Dos que receberam, 6.506 contrataram (5,5%) e 5.704 ativaram (87,7%). Apenas 4.966 têm `over30mob3` observado, dos quais 377 (7,6%) tiveram evento de inadimplência. Esse funil confirma que a **seleção de quem recebe oferta** é tão relevante quanto a **definição do limite**.

**PD da base é alta:** A mediana de `pd_produto` é 0,71 nas três safras — a maioria da base tem PD > 50%. Isso é esperado: a base inclui todos os correntistas, não apenas os pré-aprovados. Clientes de baixo risco são minoria. Implicação: o modelo precisa ser eficiente na seleção (quais clusters recebem oferta), não apenas na calibração do limite.

**`capacidade_pagamento` null em M2/M3:** Em M1, apenas 0,3% dos registros não têm essa variável. Porém, **em M2 o percentual sobe para 42,2% e em M3 para 43,5%** — quase metade da base. Isso é uma limitação severa para a restrição R3 (alavancagem), discutida na seção (b).

**Variáveis não fornecidas que seriam relevantes:**
- **LGD (Loss Given Default):** Não fornecida. Perda = PD × limite (LGD = 1). **Simplificação MVP** — assumimos perda total em caso de default (conservador). No Target, substituir por LGD calibrada com dados de recuperação do parceiro.
- **Taxa de interchange:** Valor exato não fornecido. **Simplificação MVP:** $t$ = 1,5% sobre volume transacionado (média de mercado brasileiro para cartão de crédito). No Target, validar taxa real com o parceiro.
- **Utilização esperada do limite:** Não fornecida. **Simplificação MVP:** constante $\bar{u}$ = 0,40. Parâmetro de **alta sensibilidade** (ver Análise de Sensibilidade) — variação de 0,20 a 0,50 altera a receita em ~150%. No Target, estimar $\bar{u}$ por cluster a partir de dados de ativação.

---

### Pré-processamento: Clusterização dos clientes elegíveis

O modelo de otimização opera sobre **clusters de clientes**, não sobre indivíduos — cada cluster $k$ recebe um único limite $L_k$. A clusterização é uma etapa de pré-processamento que agrupa clientes com perfil de risco e comportamento semelhantes, reduzindo a dimensionalidade do problema de ~1,8M variáveis individuais para $K \geq 100$ variáveis de cluster (conforme TAPI).

**Status atual:** A clusterização ainda não foi implementada. A definição a seguir descreve a abordagem planejada.

**Variáveis de entrada para clusterização:**

| Variável | Justificativa |
|:---|:---|
| `pd_produto` | Risco de default — dimensão central para segmentar perfis |
| `score_generico_1` | Score de bureau 1 — proxy de histórico de crédito externo |
| `score_generico_2` | Score de bureau 2 — complementa bureau 1 com fonte distinta |
| `fx_idade` | Faixa etária — correlacionada com perfil de consumo e risco |
| `score_credito_cross` | Score multiproduto — captura risco cross-selling |
| `capacidade_pagamento` | Capacidade de pagamento — define teto de alavancagem (R3). Para nulls em M2/M3, usar `renda_estimada × 0,30` como proxy |

**Abordagem planejada:**

- **Algoritmo:** K-Means como baseline (escalável para a dimensão da base), com avaliação de alternativas como DBSCAN ou clusterização hierárquica caso os clusters apresentem formatos não-esféricos.
- **Normalização:** As variáveis possuem escalas distintas (PD em [0,1], scores em [0, ~1000], capacidade em R$). Será aplicada normalização z-score ou min-max antes da clusterização.
- **Número de clusters ($K$):** Mínimo 100 (TAPI). O valor final será definido via método do cotovelo (elbow method) e silhouette score, testando $K \in \{100, 200, 500, 1000\}$.
- **Tratamento de variáveis categóricas:** `fx_idade` é ordinal (9 faixas) — será codificada como inteiro ordenado.
- **Ferramenta:** scikit-learn (`sklearn.cluster.KMeans`), com pré-processamento via `sklearn.preprocessing`.

**Saídas da clusterização (parâmetros do modelo):**

Para cada cluster $k$, serão calculados os parâmetros agregados que alimentam a função objetivo e as restrições:

| Parâmetro agregado | Cálculo | Usado em |
|:---|:---|:---|
| $\sum_{i \in \mathcal{C}_k} PD_i$ | Soma das PDs dos clientes do cluster | FO (termo B), R1, R2 |
| $\sum_{i \in \mathcal{C}_k} \pi_i$ | Soma das propensões normalizadas | FO (termo A) |
| $\min_{i \in \mathcal{C}_k} CP_i$ | Menor capacidade de pagamento do cluster | R3 (alavancagem) |
| $\|\mathcal{C}_k\|$ | Número de clientes no cluster | R1, R5, R6 |

Dessa forma, a clusterização transforma os dados brutos individuais nos parâmetros agregados que o LP consome — sem ela, o modelo não tem inputs.

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

| Símbolo | Descrição                    | Domínio                                                    | Justificativa do tipo                                                                                                                                                        |
| :------ | :--------------------------- | :--------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| _$L_k$_ | _[Limite por cluster]_       | _$L_k \in \mathbb{R}^+$ (contínuo, ≥ 0)_                   | _[Contínua: TAPI exige LP. Discretização em múltiplos de R$ 50 é pós-processamento: $L_k^{final} = 50 \cdot \lceil L_k / 50 \rceil$, com piso de R$ 200]_                    |
| _$z_k$_ | _[Cluster k recebe oferta?]_ | _$z_k \in [0, 1]$ (relaxação LP) ou fixado em pré-seleção_ | _[Decisão de oferta é genuinamente binária; no LP, tratada como contínua e arredondada em pós-processamento, ou resolvida via ranking por retorno unitário em etapa prévia]_ |

**Conjuntos e índices (legenda obrigatória):**

| Símbolo                   | Descrição                            |
| :------------------------ | :----------------------------------- |
| _$i \in \{1, \dots, n\}$_ | _Clientes elegíveis. n ≈ 1,8M em M1_ |
| _$k \in \{1, \dots, K\}$_ | _Clusters de risco, K ≥ 100_         |
| _$\mathcal{C}_k$_         | _Clientes pertencentes ao cluster k_ |

**CONSISTÊNCIA (G01 perdeu pontos por isso):** Se a variável de decisão é $L_k$ (por cluster), TUDO usa $k$, não $i$. Se depois individualizar ($L_i$), atualizar conjuntos, parâmetros, FO e restrições.

---

### Parâmetros (dados de entrada)

_Para cada parâmetro: símbolo, descrição, unidade, fonte._

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

| Símbolo       | Descrição | Unidade | Fonte |
| :------------ | :-------- | :------ | :---- |
| _[Preencher]_ |           |         |       |

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

_Escolha uma e **justifique**._

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

_[Expandir cada termo. Abaixo, explicar o que (A) e (B) representam e marcar proxies.]_

**Onde:**

- _(A) = ... **Proxy:** utilização constante $\bar{u}$ = 0,40_
- _(B) = ... **Proxy:** LGD = 1 (sem recuperação)_

**Nota sobre linearidade:**
A FO é linear em $L_k$ porque todos os demais termos ($\pi_i$, $\bar{u}$, $t$, $PD_i$) são **parâmetros**, não variáveis de decisão. O produto $z_k \cdot L_k$ é bilinear se ambos forem variáveis — tratar via abordagem em duas etapas (fixar $z_k$ primeiro, depois otimizar $L_k$) para manter LP puro.

---

### Restrições (pelo menos 2 obrigatórias)

_Para cada restrição: expressão + explicação em linguagem de negócio._

**PROFESSORA:** Ela quer ver a restrição **e** a explicação de negócio. Se a restrição é **não-linear** (como razão), **documentar a linearização** (G06 elogiado).

**TAPI — restrições obrigatórias:**

| Restrição                        | Exigência do TAPI                                                                       | Formulação                                                                               |
| :------------------------------- | :-------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------- |
| **R1: Inadimplência física**     | Média simples da PD ≤ nível atual                                                       | Razão → linearizar multiplicando pelo denominador                                        |
| **R2: Inadimplência financeira** | Média PD ponderada por limite ≤ nível atual                                             | Ponderada por $L_k$. Contém produto $z_k \cdot L_k$ — tratar via duas etapas             |
| **R3: Capacidade de pagamento**  | Limite ≤ multiplicador × capacidade. Multiplicador **diferenciado** por perfil de risco | $L_k \leq m_k \cdot \min_{i \in C_k} CP_i$                                               |
| **R4: Limite mínimo**            | ≥ R$200                                                                                 | $L_k \geq 200$ (para clusters selecionados). Discretização R$ 50 é **pós-processamento** |
| **R5-R7: Metas de produção**     | Quantidade aprovados, volume, rentabilidade (opcionais)                                 | Restrições de piso configuráveis                                                         |

**Sobre bilinearidade ($z_k \cdot L_k$) dentro do LP:**
Os termos da FO e de R2/R6/R7 contêm o produto $z_k \cdot L_k$. Se ambos forem variáveis, isso é bilinear. Tratamento recomendado para LP:
**Duas etapas:** Etapa 1 — selecionar clusters (fixar $z_k$) via ranking de retorno unitário. Etapa 2 — otimizar $L_k$ para os selecionados (LP puro, todas as variáveis contínuas).

**CONSISTÊNCIA:** Verificar que **cada variável na restrição existe na tabela de parâmetros ou variáveis de decisão**. Se $m_k$ aparece em R3, ele deve estar definido na tabela de parâmetros.

#### R1 — _[Nome: Teto de inadimplência física]_

$$
\text{[expressão — legível, não amontoada]}
$$

_[Explicação de negócio: o que garante]_

_[Se linearizou: mostrar versão original (razão) → versão linearizada, com o passo]_

#### R2 — _[Nome: Teto de inadimplência financeira]_

$$
\text{[expressão]}
$$

_[Explicação + linearização + tratamento da bilinearidade]_

_[Continuar para R3, R4, R5... R1-R4 são as restrições do TAPI. Pelo menos 2 obrigatórias pelo roteiro.]_

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

_[Escrever EXATAMENTE o texto final aqui — máximo 12 linhas, contando cada quebra de linha. Ser cirúrgico.]_

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

_[Se fizer: criar diagrama visual + tabela mapeando elementos do grafo → elementos do problema]_

| Elemento do grafo      | Representa no problema                                                                      |
| :--------------------- | :------------------------------------------------------------------------------------------ |
| _[Nós A]_              | _[Clusters de clientes]_                                                                    |
| _[Nós B]_              | _[Intervalos de limite factível]_                                                           |
| _[Arestas]_            | _[Factibilidade (cluster k pode receber limite no intervalo [200, $m_k \cdot \min CP_k$])]_ |
| _[Peso]_               | _[Retorno líquido = receita − perda]_                                                       |
| _[Restrições globais]_ | _[R1, R2: inadimplência; R5-R7: metas]_                                                     |

### Candidato 2: Tabela MVP vs Target

**PROFESSORA:** Elogiou explicitamente no G06.

| Componente        | MVP (Sprint 1-3)                            | Target (Sprint 4-5)                                 |
| :---------------- | :------------------------------------------ | :-------------------------------------------------- |
| **Formulação**    | _LP contínuo (exigência TAPI)_              | _MIP se solver suportar escala_                     |
| **Granularidade** | _Por cluster, ≥ 100 clusters_               | _Por cliente, individualizado_                      |
| **Variáveis**     | _$L_k \in \mathbb{R}^+$ (contínua)_         | _$L_i \in \mathbb{Z}^+$ (inteira, múltiplos R$ 50)_ |
| **Seleção**       | _Pré-processamento (ranking)_               | _Integrada via $z_k$ binária_                       |
| **Discretização** | _Pós-processamento (arredondamento R$ 50)_  | _Restrição inteira no modelo_                       |
| **Utilização**    | \*Constante 0,40. **Proxy.\***              | _Estimada por cluster_                              |
| **Receita**       | \*Interchange taxa fixa ~1,5%. **Proxy.\*** | _Taxa calibrada com parceiro_                       |
| **Perda**         | \*PD × L (LGD=1). **Proxy.\***              | _PD × LGD × L se LGD fornecida_                     |
| **Solver**        | _SciPy linprog ou PuLP + CBC_               | _OR-Tools ou Gurobi_                                |

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

1. _[Referências de Credit Limit Optimization: FICO, Moody's, Experian]_
2. _[Referências acadêmicas: Hillier & Lieberman, artigos de otimização de crédito]_
3. _[Dados do parceiro: RI Banco Pan, TAPI]_
4. _[Metodologia de sensibilidade: Pannell (1997), Saltelli et al. (2000)]_
