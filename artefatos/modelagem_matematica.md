# Modelagem Matemática

## a) Modelagem matemática do problema (Peso 6)

### Contexto do problema

O Banco Pan precisa definir, para cada cliente correntista elegível, qual limite pré-aprovado de cartão de crédito oferecer. Trata-se de um problema mono-produto: o escopo é exclusivamente o cartão de crédito pré-aprovado, sem considerar outros produtos de crédito da instituição. A prática vigente combina modelos de scoring com tabelas fixas de política de crédito, uma abordagem que trata de forma homogênea clientes com perfis de risco e capacidade de pagamento distintos. Isso significa que o risco agregado da carteira não é controlado diretamente pela decisão de limite, e que o potencial de retorno de parte da base elegível não é aproveitado. A validação do modelo desenvolvido neste projeto será feita pelo parceiro comparando a rentabilidade esperada entre o `limite_ofertado` praticado atualmente e o limite sugerido pelo modelo otimizado.

O núcleo do problema é um trade-off entre duas forças opostas. Um limite alto demais aumenta a receita de interchange, mas eleva a exposição à inadimplência e pode comprometer a saúde financeira do cliente. Um limite baixo demais reduz o risco, mas diminui a receita e pode frustrar o cliente a ponto de migrá-lo para um concorrente. A tabela abaixo resume esse trade-off:

| Decisão   | Se o limite for alto demais               | Se o limite for baixo demais           |
| :-------- | :---------------------------------------- | :------------------------------------- |
| _Receita_ | Mais interchange, maior retorno potencial | Menos uso do cartão, menos receita     |
| _Risco_   | Maior exposição, inadimplência sobe       | Menor inadimplência, carteira mais sã  |
| _Cliente_ | Risco de superendividamento               | Frustração, migração para concorrentes |
| _Banco_   | Provisão maior, NPL sobe                  | Perda de competitividade no produto    |

Esse equilíbrio entre retorno esperado e risco é amplamente estudado na literatura de otimização de crédito ao consumidor. Instituições como FICO (2021), Experian (2024) e Moody's Analytics (2020) tratam a definição de limite como um problema de otimização, onde a rentabilidade esperada é maximizada sujeita a restrições de risco da carteira e capacidade de pagamento individual.

Este problema é formulado como um **problema de programação linear (LP) de alocação de crédito**, no qual a variável de decisão é o limite contínuo por cliente individual, a função objetivo maximiza o retorno líquido esperado (receita de interchange menos perda esperada por inadimplência), e as restrições impõem tetos de inadimplência agregada, capacidade de pagamento individual e regras operacionais do banco. A formulação adota uma **abordagem em duas etapas**: na Etapa 1 (pré-processamento), os clientes são rankeados e selecionados, fixando o parâmetro $z_i \in \{0,1\}$; na Etapa 2 (LP), os limites $L_i$ são otimizados apenas para os clientes selecionados. Essa separação mantém a formulação como LP puro, conforme orientação do TAPI. A discretização dos limites em múltiplos de R$ 50 é aplicada em pós-processamento ($L_i^{\text{final}} = 50 \cdot \lceil L_i / 50 \rceil$, com piso de R$ 200).

### Dados disponíveis relevantes

O parceiro forneceu três bases de dados em formato Parquet, correspondentes a três safras temporais (M1, M2, M3), contendo o universo de correntistas do Banco Pan. A tabela abaixo resume a dimensão e o funil de conversão de cada safra:

| Safra | Clientes totais | Elegíveis (`flag_filtros = 0`) | Receberam oferta | Contrataram | Ativaram | `over30mob3` observado |
| :---: | --------------: | -----------------------------: | ---------------: | ----------: | -------: | ---------------------: |
|  M1   |      14.569.142 |                      1.836.085 |          117.367 |       6.506 |    5.704 |    4.966 (377 eventos) |
|  M2   |      13.808.309 |                      1.805.274 |          120.573 |       6.684 |    5.642 |    4.959 (372 eventos) |
|  M3   |      13.868.729 |                      3.137.258 |          382.692 |       9.930 |    8.347 |    7.465 (556 eventos) |

A tabela a seguir detalha as 17 variáveis fornecidas, com estatísticas descritivas reais da safra M1 e o papel de cada uma no modelo.

| Variável                     | Descrição                                     | Estatísticas (M1)                                                  | Papel no modelo                                                                                                                                                                                                    |
| :--------------------------- | :-------------------------------------------- | :----------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `token`                      | Identificador anônimo por safra               | 0 a 14.569.141                                                     | Chave de identificação                                                                                                                                                                                             |
| `safra_ref_uso`              | Safra de referência                           | M1, M2, M3                                                         | Permite backtesting entre safras                                                                                                                                                                                   |
| `score_interno`              | Score de crédito interno                      | min=54, med=292, max=975                                           | Não utilizado diretamente no modelo — serve apenas como input interno do banco para gerar `pd_produto`                                                                                                             |
| `pd_produto`                 | Probabilidade de default no produto           | min=0,025, med=0,71, max=0,946                                     | **Parâmetro central da FO (termo B) e das restrições R1 e R2.** Mediana de 0,71 indica que a maioria da base elegível tem PD alta — a seleção de quem recebe oferta é tão importante quanto a calibração do limite |
| `score_generico_1`           | Score de bureau (bureau 1)                    | min=49, med=409, max=995. Nulls: 0,1%                              | Pode compor o perfil de risco para cálculo de $m_i$; variável de segmentação para análise de resultados                                                                                                            |
| `score_generico_2`           | Score de bureau (bureau 2)                    | min=1, med=713, max=942. Nulls: <0,01%                             | Pode compor o perfil de risco para cálculo de $m_i$; variável de segmentação para análise de resultados                                                                                                            |
| `capacidade_pagamento`       | Estimativa interna de capacidade de pagamento | min=0, med=548, max=25.000. **Nulls: 0,3% M1; 42,2% M2; 43,5% M3** | **Restrição R3 (alavancagem).** Nulls em M2/M3 são limitação severa — ver seção (b)                                                                                                                                |
| `delta_capacidade_pagamento` | Capacidade deduzida dos saldos a vencer       | min=−25.000, med=55, max=25.000. Nulls: idem                       | Versão conservadora da capacidade — valores negativos indicam comprometimento além da capacidade                                                                                                                   |
| `renda_estimada`             | Estimativa interna de renda                   | min=1.275, med=1.908, max=17.950. Nulls: 0,3%                      | Proxy alternativa para R3 quando `capacidade_pagamento` é null ($CP_i = \text{renda\_estimada}_i \times 0{,}30$)                                                                                                   |
| `fx_idade`                   | Faixa etária                                  | 9 faixas: 21-30 (35,5%), 31-40 (31,1%), 41-50 (18,8%)              | Perfil de consumo e risco; variável de segmentação para análise de resultados                                                                                                                                      |
| `flag_filtros`               | Indicador de perfil restrito                  | **0 = elegível** (1,84M), **1 = restrito** (12,73M)                | Restrição hard: clientes com `flag_filtros = 1` são excluídos da otimização                                                                                                                                        |
| `score_propensao_contrato`   | Score de propensão à conversão                | min=3, med=315, max=846                                            | Parâmetro $\pi_i$ na FO (termo A). **Range [3, 846], não [0,1]** — requer normalização min-max                                                                                                                     |
| `score_credito_cross`        | Score de crédito multiproduto                 | min=103, med=706, max=954                                          | Informa o multiplicador de alavancagem $m_i$ (interpolação por score de risco)                                                                                                                                      |
| `limite_ofertado`            | Limite ofertado na política atual             | min=200, med=806, max=20.000. **99,2% null**                       | Baseline para backtesting — apenas 117K têm referência                                                                                                                                                             |
| `flag_contrato`              | Indicadora de contratação (1 = contratou)     | 6.506 (0,04%)                                                      | Backtesting. Taxa de conversão ~5,5% entre os que receberam oferta                                                                                                                                                 |
| `flag_ativacao`              | Indicadora de ativação (1 = ativou)           | 5.704 (87,7% dos que contrataram)                                  | Backtesting                                                                                                                                                                                                        |
| `over30mob3`                 | Atraso >30 dias nas 3 primeiras parcelas      | 4.966 válidos, **377 eventos** (7,6%). 99,97% null                 | Inadimplência realizada. Viés de seleção severo — só observável para quem ativou                                                                                                                                   |

**Observações críticas sobre os dados:**

**Funil de conversão (M1):** Dos 14,5M clientes, ~1,8M são elegíveis. Desses, 117K receberam oferta (6,4% dos elegíveis). Dos que receberam, 6.506 contrataram (5,5%) e 5.704 ativaram (87,7%). Apenas 4.966 têm `over30mob3` observado, dos quais 377 (7,6%) tiveram evento de inadimplência. Esse funil confirma que a **seleção de quem recebe oferta** é tão relevante quanto a **definição do limite**.

**PD da base é alta:** A mediana de `pd_produto` é 0,71 nas três safras — a maioria da base tem PD > 50%. Isso é esperado: a base inclui todos os correntistas, não apenas os pré-aprovados. Clientes de baixo risco são minoria. Implicação: o modelo precisa ser eficiente na seleção (quais clientes recebem oferta), não apenas na calibração do limite.

**`capacidade_pagamento` null em M2/M3:** Em M1, apenas 0,3% dos registros não têm essa variável. Porém, **em M2 o percentual sobe para 42,2% e em M3 para 43,5%** — quase metade da base. Isso é uma limitação severa para a restrição R3 (alavancagem), discutida na seção (b).

**Variáveis não fornecidas que seriam relevantes:**

- **LGD (Loss Given Default):** Não fornecida. Perda = PD × limite (LGD = 1). **Simplificação MVP** — assumimos perda total em caso de default (conservador). No Target, substituir por LGD calibrada com dados de recuperação do parceiro.
- **Taxa de interchange:** Fornecida pelo parceiro: $t = 0{,}0175$ (1,75% sobre volume transacionado).
- **Utilização esperada do limite:** Não fornecida. **Simplificação MVP:** constante $\bar{u}$ = 0,40. Parâmetro de **alta sensibilidade** (ver Análise de Sensibilidade) — variação de 0,20 a 0,50 altera a receita em ~150%. No Target, estimar $\bar{u}_i$ por perfil de cliente a partir de dados de ativação.

---

### Estrutura do modelo: abordagem em duas etapas

O modelo opera sobre **clientes individuais**: cada cliente elegível $i$ pode receber um limite $L_i$ próprio, sem necessidade de agrupamento prévio. A formulação adota uma abordagem em duas etapas para manter o problema como LP puro:

**Etapa 1 — Seleção de clientes (pré-processamento, fora do LP)**

Para cada cliente elegível $i$, calcula-se o coeficiente de retorno líquido unitário:

$$c_i = \pi_i \cdot \bar{u} \cdot t - PD_i$$

Clientes com $c_i > 0$ são potencialmente rentáveis. A seleção ordena os clientes por $c_i$ decrescente e inclui clientes até que as restrições da Etapa 1 sejam satisfeitas: R1 (teto de inadimplência física, $\overline{PD}$ média $\leq \overline{PD}_{fis}^{atual}$) e R6 (meta mínima de clientes aprovados, $|S| \geq N^{meta}$). O resultado é o parâmetro $z_i \in \{0,1\}$ fixo: $z_i = 1$ para clientes selecionados, $z_i = 0$ para os demais. O conjunto de clientes selecionados é $S = \{i : z_i = 1\}$.

**Etapa 2 — Otimização de limites (LP)**

Com $S$ fixo, o LP otimiza os valores de $L_i$ para cada $i \in S$, maximizando o retorno líquido total sujeito às restrições R2–R5, R7 e R8. Como $z_i$ é parâmetro fixo, o problema é estritamente linear em $L_i$ — não há produto de variáveis de decisão.

**Clusterização como ferramenta opcional de análise**

Embora o modelo otimize por cliente individual, para comunicar resultados ao time de negócios os clientes podem ser agrupados em clusters a posteriori (por faixa de PD, capacidade de pagamento ou perfil de risco), permitindo visualizações como "clientes do perfil X receberam limites na faixa Y". Essa clusterização é ferramenta de explicabilidade, não etapa do modelo.

---

### Variáveis de decisão

O modelo possui uma única variável de decisão no LP:

**$L_i \in \mathbb{R}^+$ — Limite de crédito por cliente (variável contínua)**

$L_i$ representa o valor do limite de crédito, em reais, atribuído ao cliente $i$ selecionado na Etapa 1. Essa é a variável que o solver otimiza na Etapa 2: para cada cliente $i \in S$, o LP determina o valor de $L_i$ que maximiza o retorno líquido total, respeitando todas as restrições. Os limites finais sugeridos ao banco são obtidos arredondando $L_i$ para o múltiplo de R$ 50 mais próximo acima em pós-processamento:

$$L_i^{\text{final}} = \max\!\left(200,\; 50 \cdot \left\lceil \frac{L_i}{50} \right\rceil\right), \quad \forall i \in S$$

**$z_i \in \{0,1\}$ — Indicador de seleção (parâmetro fixo, NÃO variável de decisão)**

$z_i$ indica se o cliente $i$ foi selecionado na Etapa 1 para receber oferta. Assume valor 1 se o cliente foi selecionado e 0 caso contrário. $z_i$ é determinado antes do LP via ranking de retorno unitário $c_i$ e **não participa da otimização** — é um dado de entrada do LP, não uma variável a ser otimizada.

| Símbolo | Tipo | Descrição | Domínio |
| :------ | :--- | :-------- | :------ |
| $L_i$ | Variável de decisão | Limite de crédito atribuído ao cliente $i$ | $\mathbb{R}^+$ (contínuo, otimizado pelo LP) |
| $z_i$ | Parâmetro fixo | Indicador de seleção do cliente $i$ (Etapa 1) | $\{0, 1\}$, fixado antes do LP |
| $i \in \{1, \dots, N\}$ | Índice | Cliente elegível ($N = 1\,836\,085$ em M1) | — |
| $S = \{i : z_i = 1\}$ | Conjunto | Clientes selecionados na Etapa 1 | — |

---

### Parâmetros (dados de entrada)

| Símbolo | Descrição | Unidade / Domínio | Fonte |
| :------ | :-------- | :---------------- | :---- |
| $PD_i$ | Probabilidade de default do cliente $i$ | [0, 1] | `pd_produto` (fornecida pelo parceiro) |
| $\pi_i$ | Propensão à contratação do cliente $i$, normalizada | [0, 1] | `score_propensao_contrato`, min-max: $\pi_i = \frac{score_i - 3}{843}$ |
| $CP_i$ | Capacidade de pagamento do cliente $i$ | R$ | `capacidade_pagamento`. Proxy: `renda_estimada × 0,30` quando null |
| $m_i$ | Multiplicador de alavancagem do cliente $i$ | [0,3; 1,8] | Interpolado pelo score de risco (`score_credito_cross`). Diretriz do parceiro |
| $t$ | Taxa de interchange | adimensional | 0,0175 (fornecido pelo parceiro) |
| $\bar{u}$ | Utilização esperada do limite | [0, 1] | **Proxy MVP:** 0,40 (constante). Alta sensibilidade |
| $\overline{PD}_{fis}^{atual}$ | Teto de inadimplência física | [0, 1] | Média simples de PD da carteira aprovada vigente |
| $\overline{PD}_{fin}^{atual}$ | Teto de inadimplência financeira | [0, 1] | Média ponderada (por limite) de PD da carteira aprovada vigente |
| $L^{min}$ | Piso mínimo de limite | R$ | 200 (TAPI) |
| $L^{max}$ | Teto máximo de limite | R$ | 25.000 (diretriz do parceiro) |
| $N^{meta}$ | Meta de clientes aprovados | inteiro | Configurável pelo parceiro |
| $V^{meta}$ | Meta de volume total de limite | R$ | Configurável pelo parceiro |
| $R^{meta}$ | Meta de rentabilidade mínima | R$ | Configurável pelo parceiro |
| $N$ | Total de clientes elegíveis | inteiro | $N = |\{i : \texttt{flag\_filtros}_i = 0\}|$ |
| $S$ | Conjunto de clientes selecionados | — | $S = \{i : z_i = 1\}$ (resultado da Etapa 1) |
| $c_i$ | Coeficiente de retorno líquido unitário | R$/R$ | $c_i = \pi_i \cdot \bar{u} \cdot t - PD_i$ |

---

### Objetivo do modelo e função objetivo

O banco precisa de uma regra que diga, de forma sistemática, qual limite atribuir a cada cliente. Sem um critério formal, a decisão se baseia em tabelas fixas que não consideram a heterogeneidade entre perfis e não controlam o risco agregado da carteira. O objetivo do modelo é substituir essa regra empírica por uma decisão matemática: encontrar o conjunto de limites $L_i$ que maximize o retorno líquido total esperado do banco, entendido como a soma da receita esperada de interchange menos a perda esperada por inadimplência, sobre todos os clientes selecionados.

Maximizar o retorno líquido é a métrica correta porque o produto em análise é exclusivamente o cartão de crédito pré-aprovado, onde toda a receita relevante vem do uso do cartão e toda a perda relevante vem do default. Minimizar inadimplência pura levaria o modelo a oferecer limites mínimos — trivialmente seguro, mas sem valor comercial. Maximizar receita bruta ignoraria o risco. O retorno líquido captura esse equilíbrio diretamente, e é também a métrica pela qual o parceiro avaliará o modelo: comparando a rentabilidade esperada entre o `limite_ofertado` praticado atualmente e o limite sugerido pelo modelo.

**Justificativa da formulação:** A FO adota a forma **receita − perda** (sem ponderador $\lambda$), delegando o controle de risco inteiramente às restrições (R1–R5). Essa separação é preferível por três razões: (i) o parceiro define explicitamente os tetos de inadimplência como restrições, não como penalidades na FO; (ii) um ponderador $\lambda$ entre receita e perda introduziria um hiperparâmetro difícil de calibrar sem dados históricos de recuperação — justamente um dado que o parceiro não forneceu; (iii) manter a FO como retorno líquido (R$) garante que todos os termos estejam na mesma unidade e escala. A receita é restrita a interchange sobre o volume transacionado, à taxa fixa de 1,75% fornecida pelo parceiro. Modelar receita de rotativo tornaria o problema não-linear e foge ao escopo.

$$\max \sum_{i \in S} \left[\underbrace{\pi_i \cdot \bar{u} \cdot t \cdot L_i}_{\text{(A) Receita esperada}} \; - \; \underbrace{PD_i \cdot L_i}_{\text{(B) Perda esperada}}\right]$$

Fatorando $L_i$:

$$\max \sum_{i \in S} \underbrace{(\pi_i \cdot \bar{u} \cdot t - PD_i)}_{c_i} \cdot L_i$$

onde $S = \{i : z_i = 1\}$ é o conjunto de clientes selecionados na Etapa 1 e $c_i$ é o **coeficiente de retorno líquido unitário** do cliente $i$.

#### Interpretação da função objetivo

**Termo (A) — Receita:** $\pi_i \cdot \bar{u} \cdot t \cdot L_i$ é a receita de interchange esperada do cliente $i$. O cliente contrata com probabilidade $\pi_i$, derivada de `score_propensao_contrato` normalizado via min-max ($\pi_i = \frac{score_i - 3}{843}$, mapeando o range [3, 846] para [0, 1]). O contratante utiliza uma fração $\bar{u}$ do limite, e o banco recebe taxa de interchange $t$ sobre o volume transacionado. Proxies embutidas: $\bar{u} = 0{,}40$ _(constante, proxy MVP)_ e $t = 0{,}0175$ _(fornecida pelo parceiro)_.

**Termo (B) — Perda:** $PD_i \cdot L_i$ é a perda esperada por inadimplência do cliente $i$. $PD_i$ é a probabilidade de default (variável `pd_produto`), e $L_i$ é a exposição total. Proxy embutida: **LGD = 1** _(perda total em caso de default, sem recuperação — simplificação conservadora. Bancos tipicamente recuperam 20–50% do valor em default)_.

**Coeficiente $c_i$:** O retorno líquido unitário $c_i = \pi_i \cdot \bar{u} \cdot t - PD_i$ resume a rentabilidade marginal de cada real alocado ao cliente $i$. Clientes com $c_i > 0$ são rentáveis; clientes com $c_i \leq 0$ destroem valor a cada real adicional de limite. Na Etapa 1, $c_i$ é o critério de ranking para seleção; na Etapa 2, $c_i$ é o coeficiente objetivo do LP — o solver tende a maximizar $L_i$ para clientes com maior $c_i$, limitado pelas restrições.

A FO é linear em $L_i$: todos os demais termos ($\pi_i$, $\bar{u}$, $t$, $PD_i$) são parâmetros. Como $z_i$ é fixado na Etapa 1, não há produto de variáveis de decisão — o problema é um LP puro.

### Restrições

As restrições traduzem as políticas de crédito do Banco Pan em limites matemáticos para o espaço de soluções factíveis. Dividem-se em três categorias: (i) **controle de risco da carteira** (R1, R2), (ii) **proteção individual e bounds** (R3–R5), e (iii) **metas de produção** (R6–R8). As restrições R1 e R6 são garantidas na Etapa 1 (seleção de clientes); as demais entram no LP da Etapa 2.

#### R1 — Teto de inadimplência física (Etapa 1)

A inadimplência física mede o risco da carteira pela média simples da probabilidade de default dos clientes selecionados, sem ponderar pelo volume de crédito concedido. Essa métrica depende de **quem** é selecionado, não de **quanto** limite recebe — por isso é controlada na Etapa 1, não no LP.

$$\frac{\sum_{i \in S} PD_i}{|S|} \leq \overline{PD}_{fis}^{atual}$$

A seleção via ranking de $c_i$ na Etapa 1 garante essa restrição: clientes são incluídos em $S$ em ordem decrescente de $c_i$ (que penaliza PD alta), e a inclusão para quando a PD média atinge o teto $\overline{PD}_{fis}^{atual}$. O parceiro espera que a PD média da carteira ofertada pelo modelo não ultrapasse a inadimplência física observada na carteira atualmente aprovada, garantindo que o modelo não piore o perfil médio de risco em relação à política vigente.

#### R2 — Teto de inadimplência financeira (LP)

Enquanto R1 trata cada cliente com o mesmo peso, R2 pondera a PD pelo limite atribuído, medindo o risco em termos de exposição financeira. A decisão de **quanto** limite conceder impacta diretamente essa métrica — por isso entra no LP, diferente de R1.

**Versão original (razão — não-linear):**

$$\frac{\sum_{i \in S} PD_i \cdot L_i}{\sum_{i \in S} L_i} \leq \overline{PD}_{fin}^{atual}$$

**Versão linearizada** (multiplicando ambos os lados pelo denominador, estritamente positivo pois $L_i \geq 200$ para todo $i \in S$):

$$\sum_{i \in S} (PD_i - \overline{PD}_{fin}^{atual}) \cdot L_i \leq 0$$

Cada cliente $i$ contribui com um excesso ou déficit de inadimplência: clientes com $PD_i > \overline{PD}_{fin}^{atual}$ consomem folga (coeficiente positivo), enquanto clientes com $PD_i < \overline{PD}_{fin}^{atual}$ geram folga (coeficiente negativo). A restrição é naturalmente linear em $L_i$. R2 é tipicamente a restrição mais restritiva quando limites altos são atribuídos a clientes arriscados — controla o risco "em reais".

#### R3 — Capacidade de pagamento com alavancagem diferenciada (LP)

$$L_i \leq m_i \cdot CP_i, \quad \forall i \in S$$

O limite de cada cliente é limitado pela sua capacidade de pagamento, multiplicada pelo fator de alavancagem $m_i \in [0{,}3;\; 1{,}8]$, interpolado pelo score de risco (`score_credito_cross`): clientes de menor risco recebem $m_i$ próximo de 1,8, e clientes de maior risco recebem $m_i$ próximo de 0,3. Essa diferenciação evita tanto o superendividamento de clientes vulneráveis quanto a subutilização do potencial de clientes de baixo risco.

A restrição é individual — cada cliente é limitado pela **sua própria** capacidade, não pela de outros clientes. Em uma formulação clusterizada, essa restrição usaria $\min_{i \in C_k} CP_i$, penalizando todo o grupo pelo cliente com menor capacidade; a formulação individual elimina essa penalização e permite alocação estritamente mais precisa.

#### R4 — Limite mínimo (LP)

$$L_i \geq 200, \quad \forall i \in S$$

Piso operacional: nenhum limite ofertado pode ser inferior a R$ 200 (TAPI). Como o LP opera apenas sobre clientes selecionados ($i \in S$), essa restrição é um bound simples na variável $L_i$, sem necessidade de variável binária. A discretização em múltiplos de R$ 50 é aplicada em pós-processamento, preservando a continuidade da formulação LP.

#### R5 — Teto máximo de limite (LP)

$$L_i \leq 25\,000, \quad \forall i \in S$$

Teto absoluto definido pelo parceiro. Na prática, R3 é a restrição ativa para a maioria dos clientes (pois $m_i \cdot CP_i < 25\,000$ para quase todos), e R5 atua apenas como salvaguarda para clientes com capacidade de pagamento excepcionalmente alta.

#### R6 — Meta de clientes aprovados (Etapa 1)

$$|S| \geq N^{meta}$$

Número mínimo de clientes que devem receber oferta, para evitar que o modelo concentre a carteira em poucos clientes de perfil ideal. Garantida na Etapa 1: a seleção via ranking continua incluindo clientes até que $|S| \geq N^{meta}$, mesmo que isso exija incluir clientes com $c_i$ marginalmente positivo.

#### R7 — Meta de volume total de limite (LP)

$$\sum_{i \in S} L_i \geq V^{meta}$$

Volume financeiro mínimo de limite ofertado, garantindo massa suficiente na carteira. Restrição linear em $L_i$.

#### R8 — Rentabilidade mínima (LP)

$$\sum_{i \in S} c_i \cdot L_i \geq R^{meta}$$

Retorno líquido total mínimo, impedindo soluções de alto volume mas baixa margem. Como $c_i$ é parâmetro fixo, a restrição é linear em $L_i$.

#### Domínio

$$L_i \geq 0, \quad \forall i \in S$$

Na prática, R4 ($L_i \geq 200$) é mais restritivo, tornando o bound de não-negatividade redundante — mas incluído por completude formal.

#### Resumo das restrições

| ID | Restrição | Etapa | Tipo | Obrigatória? |
| :- | :-------- | :---- | :--- | :----------- |
| R1 | Teto de inadimplência física ($\overline{PD}$ média $\leq$ teto) | Etapa 1 | Seleção | Sim |
| R2 | Teto de inadimplência financeira ($\overline{PD}$ ponderada $\leq$ teto) | Etapa 2 (LP) | Linear (após linearização) | Sim |
| R3 | Capacidade de pagamento ($L_i \leq m_i \cdot CP_i$) | Etapa 2 (LP) | Linear | Sim |
| R4 | Limite mínimo ($L_i \geq 200$) | Etapa 2 (LP) | Bound | Sim |
| R5 | Teto máximo ($L_i \leq 25\,000$) | Etapa 2 (LP) | Bound | Sim |
| R6 | Meta de clientes ($|S| \geq N^{meta}$) | Etapa 1 | Seleção | Configurável |
| R7 | Meta de volume ($\sum L_i \geq V^{meta}$) | Etapa 2 (LP) | Linear | Configurável |
| R8 | Rentabilidade mínima ($\sum c_i L_i \geq R^{meta}$) | Etapa 2 (LP) | Linear | Configurável |

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

1. FICO. [How Decision Optimization Improves Credit Line Management](https://www.fico.com/blogs/how-decision-optimization-improves-credit-line-management). FICO Blog.
2. Moody's Analytics. [Determining the Optimal Dynamic Credit Card Limit](https://www.moodys.com/web/en/us/insights/resources/Determining-the-Optimal-Dynamic-Credit-Card-Limit.pdf). White Paper.
3. Experian. [Balancing Growth and Risk with Credit Limit Optimization](https://www.experian.com/blogs/insights/credit-limit-optimization/). Experian Insights, 2024.
4. Budd, J. K.; Taylor, P. G. [Calculating Optimal Limits for Transacting Credit Card Customers](https://arxiv.org/pdf/1506.05376). arXiv:1506.05376, 2015.
5. Hillier, F. S.; Lieberman, G. J. *Introduction to Operations Research*. 9th ed. McGraw-Hill, 2010.
6. Pannell, D. J. (1997). Sensitivity analysis of normative economic models. *Agricultural Economics*, 16, 139-152.
7. Banco Pan S.A. [Relações com Investidores](https://ri.bancopan.com.br/). Demonstrações Financeiras Padronizadas, 2024.
8. BRASIL. Conselho Monetário Nacional. Resolução CMN nº 4.966/2021. Perda esperada associada ao risco de crédito.
