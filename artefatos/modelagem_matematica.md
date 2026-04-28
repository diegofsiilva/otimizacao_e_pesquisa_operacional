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

### Pré-processamento: Clusterização dos clientes elegíveis

O modelo de otimização opera sobre **clusters de clientes**, não sobre indivíduos — cada cluster $k$ recebe um único limite $L_k$. A clusterização é uma etapa de pré-processamento que agrupa clientes com perfil de risco e comportamento semelhantes, reduzindo a dimensionalidade do problema de ~1,8M variáveis individuais para $K \geq 100$ variáveis de cluster (conforme TAPI).

**Status atual:** A clusterização ainda não foi implementada. A definição a seguir descreve a abordagem planejada.

**Variáveis de entrada para clusterização:**

| Variável               | Justificativa                                                                                                           |
| :--------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| `pd_produto`           | Risco de default — dimensão central para segmentar perfis                                                               |
| `score_generico_1`     | Score de bureau 1 — proxy de histórico de crédito externo                                                               |
| `score_generico_2`     | Score de bureau 2 — complementa bureau 1 com fonte distinta                                                             |
| `fx_idade`             | Faixa etária — correlacionada com perfil de consumo e risco                                                             |
| `score_credito_cross`  | Score multiproduto — captura risco cross-selling                                                                        |
| `capacidade_pagamento` | Capacidade de pagamento — define teto de alavancagem (R3). Para nulls em M2/M3, usar `renda_estimada × 0,30` como proxy |

**Abordagem planejada:**

- **Algoritmo:** K-Means como baseline (escalável para a dimensão da base), com avaliação de alternativas como DBSCAN ou clusterização hierárquica caso os clusters apresentem formatos não-esféricos.
- **Normalização:** As variáveis possuem escalas distintas (PD em [0,1], scores em [0, ~1000], capacidade em R$). Será aplicada normalização z-score ou min-max antes da clusterização.
- **Número de clusters ($K$):** Mínimo 100 (TAPI). O valor final será definido via método do cotovelo (elbow method) e silhouette score, testando $K \in \{100, 200, 500, 1000\}$.
- **Tratamento de variáveis categóricas:** `fx_idade` é ordinal (9 faixas) — será codificada como inteiro ordenado.
- **Ferramenta:** scikit-learn (`sklearn.cluster.KMeans`), com pré-processamento via `sklearn.preprocessing`.

**Saídas da clusterização (parâmetros do modelo):**

Para cada cluster $k$, serão calculados os parâmetros agregados que alimentam a função objetivo e as restrições:

| Parâmetro agregado                 | Cálculo                                  | Usado em             |
| :--------------------------------- | :--------------------------------------- | :------------------- |
| $\sum_{i \in \mathcal{C}_k} PD_i$  | Soma das PDs dos clientes do cluster     | FO (termo B), R1, R2 |
| $\sum_{i \in \mathcal{C}_k} \pi_i$ | Soma das propensões normalizadas         | FO (termo A)         |
| $\min_{i \in \mathcal{C}_k} CP_i$  | Menor capacidade de pagamento do cluster | R3 (alavancagem)     |
| $\|\mathcal{C}_k\|$                | Número de clientes no cluster            | R1, R5, R6           |

Dessa forma, a clusterização transforma os dados brutos individuais nos parâmetros agregados que o LP consome — sem ela, o modelo não tem inputs.

---

### Variáveis de decisão

O modelo possui duas variáveis de decisão, uma para cada aspecto da escolha que o banco precisa fazer: se oferece o cartão para um determinado grupo de clientes, e quanto de limite oferece caso decida ofertar.

**$z_k$ — Decisão de oferta (variável binária)**

$z_k$ representa se o cluster $k$ receberá ou não uma oferta de cartão de crédito. Ela assume apenas dois valores possíveis: $z_k = 1$ se o cluster recebe oferta, e $z_k = 0$ caso contrário. Por natureza, essa é uma variável binária — não faz sentido dizer que um cluster "recebe metade de uma oferta". No entanto, variáveis binárias pertencem ao domínio da programação inteira mista (MIP), que foge ao escopo do curso. Por isso, $z_k$ é tratada em etapa separada ao problema de otimização: antes de rodar o LP, os clusters são ordenados por retorno líquido unitário esperado (retorno total do cluster dividido pelo número de clientes) e os de maior retorno são selecionados até que as restrições de produção sejam satisfeitas. Feita essa seleção, $z_k$ assume valor fixo — 1 para os selecionados e 0 para os demais — e deixa de ser variável, passando a ser um parâmetro conhecido. Apenas então o LP é executado para otimizar $L_k$.

$$z_k \in \{0, 1\}, \quad \forall k \in \{1, \dots, K\}$$

**$L_k$ — Limite de crédito por cluster (variável contínua)**

$L_k$ representa o valor do limite de crédito, em reais, atribuído a todos os clientes do cluster $k$ que receberem oferta (ou seja, para os clusters onde $z_k = 1$). Como todos os clientes de um mesmo cluster recebem o mesmo limite, o modelo precisa encontrar apenas $K$ valores de limite — um por cluster — em vez de um valor individual para cada um dos milhões de clientes elegíveis. Essa é a principal variável de decisão do LP: o solver determina o valor de $L_k$ para cada cluster selecionado que maximiza o retorno líquido total, respeitando todas as restrições.

$L_k$ é definida como variável contínua, podendo assumir qualquer valor real não-negativo, o que mantém o problema na categoria de programação linear. Os limites finais sugeridos ao banco são obtidos arredondando $L_k$ para o múltiplo de R$ 50 mais próximo acima em pós-processamento, aplicando também o piso mínimo de R$ 200 exigido pelo banco:

$$L_k^{\text{final}} = \max\!\left(200,\; 50 \cdot \left\lceil \frac{L_k}{50} \right\rceil\right), \quad \forall k \in \{1, \dots, K\}$$

$$L_k \in \mathbb{R}^+, \quad \forall k \in \{1, \dots, K\}$$

| Símbolo                 | Descrição                                        | Domínio                                             |
| :---------------------- | :----------------------------------------------- | :-------------------------------------------------- |
| $z_k$                   | Indicador de oferta para o cluster $k$           | $\{0, 1\}$, tratado como parâmetro fixo antes do LP |
| $L_k$                   | Limite de crédito atribuído ao cluster $k$       | $\mathbb{R}^+$ (contínuo, otimizado pelo LP)        |
| $k \in \{1, \dots, K\}$ | Índice de cluster, com $K \geq 100$              | —                                                   |
| $\mathcal{C}_k$         | Conjunto de clientes pertencentes ao cluster $k$ | —                                                   |

### Parâmetros (dados de entrada)

_Para cada parâmetro: símbolo, descrição, unidade, fonte._

**TAPI — parâmetros obrigatórios:**

- $PD_i$ ← `pd_produto`
- $CP_i$ ← `capacidade_pagamento`
- $\pi_i$ ← `score_propensao_contrato`, normalizado de [4, 840] para [0,1]
- Teto inadimplência física e financeira (atuais da carteira aprovada)
- Multiplicador de alavancagem $m_k \in [0{,}3;\; 1{,}8]$ por perfil de risco (fornecido pelo parceiro)
- $L^{min} = 200$ (TAPI)
- Taxa de interchange $t = 0{,}0175$ (fornecida pelo parceiro)
- Utilização $\bar{u}$ (**proxy:** ~0,40)
- Metas de produção opcionais

| Símbolo       | Descrição | Unidade | Fonte |
| :------------ | :-------- | :------ | :---- |
| _[Preencher]_ |           |         |       |

**PROFESSORA:** Ela quer ver a **legenda completa**. Todo símbolo que aparece na FO ou restrição deve estar nesta tabela. Não deixar nenhum "solto".

---

### Objetivo do modelo e função objetivo

O banco precisa de uma regra que diga, de forma sistemática, qual limite atribuir a cada cluster de clientes. Sem um critério formal, a decisão se baseia em tabelas fixas que não consideram a heterogeneidade entre perfis e não controlam o risco agregado da carteira. O objetivo do modelo é substituir essa regra empírica por uma decisão matemática: encontrar o conjunto de limites $L_k$ que maximize o retorno líquido total esperado do banco, entendido como a soma da receita esperada de interchange menos a perda esperada por inadimplência, sobre todos os clusters que recebem oferta.

Em termos de negócio, maximizar o retorno líquido é a métrica correta porque o produto em análise é exclusivamente o cartão de crédito pré-aprovado, onde toda a receita relevante vem do uso do cartão e toda a perda relevante vem do default do cliente. Minimizar inadimplência pura levaria o modelo a oferecer limites mínimos a todos os clientes — trivialmente seguro, mas sem valor comercial. Maximizar receita bruta ignoraria o risco e deterioraria a qualidade da carteira. O retorno líquido captura esse equilíbrio diretamente, e é também a métrica pela qual o parceiro avaliará o modelo: comparando a rentabilidade esperada entre o `limite_ofertado` praticado atualmente e o limite sugerido pelo modelo para cada cluster.

**Justificativa da formulação escolhida:** A função objetivo adota a forma **FO = receita − perda** (sem ponderador $\lambda$), delegando o controle de risco inteiramente às restrições (R1–R4). Essa separação é preferível por três razões: (i) o parceiro define explicitamente os tetos de inadimplência como restrições, não como penalidades na FO; (ii) um ponderador $\lambda$ entre receita e perda introduziria um hiperparâmetro difícil de calibrar sem dados históricos de recuperação — justamente um dado que o parceiro não forneceu; (iii) manter a FO como lucro líquido puro (R$) garante que todos os termos estejam na mesma unidade e escala, evitando a mistura de escalas. Dessa forma, a FO responde a uma única pergunta: _"qual alocação de limites gera o maior retorno esperado?"_, enquanto as restrições garantem que esse retorno não viole os limiares de risco aceitáveis pelo banco.

A receita é restrita a interchange sobre o volume transacionado, à taxa fixa de 1,75% fornecida pelo parceiro. Embora existam outras fontes de receita (como rotativo), a modelagem por interchange mantém a linearidade da FO e elimina a necessidade de modelar comportamento de parcelamento ou rolagem de dívida. Isso torna a FO conservadora (subestima a receita real) mas simplifica a formulação sem comprometer a direção da solução ótima.

$$\max \sum_{k=1}^{K} z_k \cdot \left[ \underbrace{\left(\sum_{i \in \mathcal{C}_k} \pi_i \right) \cdot \bar{u} \cdot t \cdot L_k}_{\text{(A) Receita esperada de interchange}} \; - \; \underbrace{\left(\sum_{i \in \mathcal{C}_k} PD_i \right) \cdot L_k}_{\text{(B) Perda esperada}} \right]$$

#### Interpretação da função objetivo

Para entender o que a fórmula calcula, é útil analisá-la de dentro para fora, começando pelos termos mais internos.

##### O que é $\pi_i$?

$\pi_i$ é a probabilidade de o cliente $i$ contratar o cartão caso receba a oferta. Antes de qualquer coisa, vale esclarecer que o símbolo $\pi$ aqui não tem nenhuma relação com o número 3,14159 da geometria — é apenas uma letra grega escolhida por convenção para dar nome a essa variável, assim como se usaria $x$ ou $p$. Poderia ser qualquer letra; a área de crédito convencionou usar $\pi$ para probabilidade de conversão e $PD$ para probabilidade de default, justamente para não confundir as duas.

Ela é derivada diretamente da variável `score_propensao_contrato` da base de dados, que originalmente varia entre 3 e 846. Como probabilidade precisa estar entre 0 e 1, essa variável é normalizada via min-max antes de entrar no modelo. Essa transformação é simples: pega o valor do cliente, subtrai o mínimo (3) e divide pela diferença entre o máximo e o mínimo (846 − 3 = 843):

$$\pi_i = \frac{\text{score}_i - 3}{843}$$

Um cliente com score 3 vira $\pi_i = 0$ (praticamente nenhuma chance de contratar). Um cliente com score 846 vira $\pi_i = 1$ (certeza de contratar). Um cliente com score 424 vira $\pi_i \approx 0{,}50$ (50% de chance). Depois dessa transformação, o nome que damos ao resultado é $\pi_i$ — e é esse valor que entra na fórmula. A soma $\sum_{i \in \mathcal{C}_k} \pi_i$ acumula essa probabilidade para todos os clientes do cluster $k$, funcionando como uma estimativa do número esperado de contratantes dentro daquele grupo.

##### O que é o termo (A) — Receita esperada de interchange?

$$\left(\sum_{i \in \mathcal{C}_k} \pi_i \right) \cdot \bar{u} \cdot t \cdot L_k$$

Esse termo calcula a receita total esperada de interchange para o cluster $k$. O raciocínio é: dos clientes do cluster $k$, espera-se que $\sum_{i \in \mathcal{C}_k} \pi_i$ deles contratem o cartão. Cada contratante utilizará, em média, uma fração $\bar{u}$ do limite $L_k$ — ou seja, o volume transacionado esperado por cliente é $\bar{u} \cdot L_k$. Sobre esse volume, o banco recebe uma taxa de interchange $t$, que representa a receita obtida a cada real gasto pelo cliente no cartão. Multiplicando tudo: número esperado de contratantes × volume transacionado esperado × taxa de interchange = receita esperada de interchange do cluster $k$.

Duas simplificações estão embutidas nesse termo e precisam ser declaradas explicitamente:

- **Utilização constante** $\bar{u} = 0{,}40$ _(proxy)_: assume-se que todos os clientes de todos os clusters utilizam, em média, 40% do limite disponível. Na realidade, clientes de perfis distintos têm comportamentos de uso muito diferentes. Essa simplificação é necessária porque a base não fornece dados de utilização histórica para os clientes elegíveis, apenas para uma fração pequena que já ativou o cartão, o que introduziria viés de seleção severo caso fosse usada. O impacto dessa proxy é discutido na análise de sensibilidade.

- **Taxa de interchange** $t = 0{,}0175$ _(fornecida pelo parceiro)_: o banco recebe 1,75% sobre cada real transacionado. Essa taxa é fixa e independente do perfil do cliente, o que mantém a linearidade da função objetivo. Modelar receita de rotativo (juros sobre saldo devedor) tornaria o problema não-linear e foge ao escopo.

##### O que é o termo (B) — Perda esperada por inadimplência?

$$\left(\sum_{i \in \mathcal{C}_k} PD_i \right) \cdot L_k$$

Esse termo calcula a perda financeira esperada do cluster $k$ em caso de inadimplência. $PD_i$ é a probabilidade de default do cliente $i$, fornecida diretamente pela variável `pd_produto` da base. A soma $\sum_{i \in \mathcal{C}_k} PD_i$ representa o número esperado de clientes do cluster $k$ que entrarão em default. Cada cliente inadimplente gera uma perda igual ao limite que recebeu, $L_k$, pois assumimos que o banco não recupera nenhum valor. Multiplicando: número esperado de inadimplentes × perda por inadimplente = perda esperada total do cluster $k$.

Uma simplificação central está embutida aqui:

- **LGD = 1** _(proxy)_: LGD significa _Loss Given Default_, ou seja, a fração do valor devido que o banco efetivamente perde quando um cliente entra em default. Assumir LGD = 1 significa dizer que o banco não recupera absolutamente nada — nem via cobrança, nem via venda da dívida para terceiros. Na realidade, bancos tipicamente recuperam entre 20% e 50% do valor em default. Essa simplificação é conservadora: superestima a perda, tornando o modelo mais cauteloso ao alocar limites altos para clusters de risco elevado.

##### O que é $z_k$ e por que aparece na fórmula?

$z_k$ é a variável de seleção definida na seção anterior: vale 1 se o cluster $k$ recebe oferta e 0 caso contrário. Na fórmula, ela garante que apenas os clusters selecionados contribuam para o somatório — clusters com $z_k = 0$ têm sua parcela zerada automaticamente. Como explicado na seção de variáveis de decisão, $z_k$ é fixado antes do LP via ranking de retorno unitário, o que elimina o produto $z_k \cdot L_k$ da otimização e mantém a formulação linear.

##### Juntando tudo

Para cada cluster $k$ selecionado ($z_k = 1$), a função objetivo calcula o retorno líquido como receita (A) menos perda (B). O $\max$ instrui o solver a encontrar os valores de $L_k$ que tornam essa soma total a maior possível, dentro dos limites impostos pelas restrições R1 a R5. Em outras palavras: o modelo procura os limites que maximizam o quanto o banco ganha com interchange, descontando o quanto pode perder com inadimplência, garantindo ao mesmo tempo que a carteira resultante respeite os critérios de risco e capacidade de pagamento exigidos pelo banco.

### Restrições

As restrições do modelo traduzem as políticas de crédito do Banco Pan em limites matemáticos para o espaço de soluções factíveis. Elas se dividem em três grupos: (i) **controle de risco da carteira** (R1 e R2), que impedem que a maximização do lucro deteriore a qualidade de crédito agregada; (ii) **proteção individual** (R3 e R4), que garantem que nenhum cliente receba um limite incompatível com sua capacidade de pagamento ou abaixo do piso operacional do produto; e (iii) **metas de produção** (R5–R7), configuráveis conforme a estratégia comercial do banco.

As restrições R1 e R2 são naturalmente expressas como razões, uma de média simples e outra de média ponderada, o que as torna não-lineares. Para manter a formulação como programação linear, cada uma é apresentada primeiro na forma original e depois na forma linearizada, com o passo algébrico explícito. Além disso, as restrições R2, R6 e R7 contêm o produto $z_k \cdot L_k$, que é bilinear quando ambas são variáveis de decisão. Na abordagem em duas etapas adotada, primeiro fixa-se $z_k$ via ranking de retorno unitário e, depois, otimiza-se $L_k$; assim, esse produto se torna linear em $L_k$, pois $z_k$ passa a ser um parâmetro fixo (0 ou 1). Todo o desenvolvimento abaixo assume que $z_k$ já foi fixado na etapa de seleção.

#### R1 - Teto de inadimplência física

A inadimplência física mede o risco da carteira pela média simples da probabilidade de default dos clientes que recebem oferta, sem ponderar pelo volume de crédito concedido. Se o modelo selecionar apenas clusters de PD baixa, a inadimplência física cai, mas a carteira pode ficar pequena demais para atender as metas comerciais. Se selecionar clusters de PD alta, o lucro potencial é maior, mas o perfil médio de risco se deteriora.

O parceiro espera que a PD média da carteira ofertada pelo modelo não ultrapasse a inadimplência física observada na carteira atualmente aprovada ($\overline{PD}_{fis}^{atual}$). Isso garante que o modelo não piore o perfil médio de risco em relação à política vigente, um requisito mínimo de governança de crédito.

**Versão original (razão - não-linear):**

$$\frac{\sum_{k=1}^{K} z_k \cdot \sum_{i \in \mathcal{C}_k} PD_i}{\sum_{k=1}^{K} z_k \cdot |\mathcal{C}_k|} \leq \overline{PD}_{fis}^{atual}$$

**Linearização:** Multiplicando ambos os lados pelo denominador $\sum_{k} z_k \cdot |\mathcal{C}_k|$ (estritamente positivo, pois ao menos um cluster é selecionado), a razão se transforma em uma desigualdade linear:

$$\sum_{k=1}^{K} z_k \cdot \sum_{i \in \mathcal{C}_k} \left(PD_i - \overline{PD}_{fis}^{atual}\right) \leq 0$$

Nessa forma, cada cluster $k$ contribui com o excesso (ou déficit) de PD em relação ao teto. Clusters com PD média acima de $\overline{PD}_{fis}^{atual}$ contribuem positivamente (consumindo folga da restrição), enquanto clusters com PD abaixo do teto contribuem negativamente (gerando folga). A soma total precisa ser não-positiva para que a carteira como um todo respeite o limite de inadimplência física.

#### R2 - Teto de inadimplência financeira

Enquanto R1 trata cada cliente com o mesmo peso independentemente do limite que recebe, R2 pondera a PD pelo limite atribuído, ou seja, mede o risco em termos de exposição financeira. Um cluster pequeno com PD alta e limite elevado pode atender R1 (poucos clientes, baixo impacto na média simples), mas violar R2 porque a exposição financeira é desproporcional ao tamanho do grupo. Na prática, R2 é a restrição mais restritiva quando limites altos são atribuídos a clusters arriscados, impedindo que o modelo concentre crédito em segmentos de alto risco/alto retorno.

O parceiro exige que a inadimplência financeira (média da PD ponderada pelo limite concedido) da carteira ofertada não exceda o nível financeiro atual. Essa restrição complementa R1 ao controlar não apenas a frequência esperada de default, mas também a magnitude da perda.

**Versão original (razão - não-linear):**

$$\frac{\sum_{k=1}^{K} z_k \cdot L_k \cdot \sum_{i \in \mathcal{C}_k} PD_i}{\sum_{k=1}^{K} z_k \cdot L_k \cdot |\mathcal{C}_k|} \leq \overline{PD}_{fin}^{atual}$$

**Linearização:** Mesmo procedimento de R1 - multiplicando ambos os lados pelo denominador:

$$\sum_{k=1}^{K} z_k \cdot L_k \cdot \sum_{i \in \mathcal{C}_k} \left(PD_i - \overline{PD}_{fin}^{atual}\right) \leq 0$$

O termo $z_k \cdot L_k$ é bilinear quando ambas são variáveis de decisão. Na abordagem em duas etapas, com $z_k$ fixado na etapa de seleção, a expressão torna-se linear em $L_k$: para clusters não selecionados ($z_k = 0$), o termo desaparece; para os selecionados ($z_k = 1$), resta $L_k \cdot \sum_{i \in \mathcal{C}_k}(PD_i - \overline{PD}_{fin}^{atual})$, que é linear na variável de decisão.

#### R3 - Capacidade de pagamento com alavancagem diferenciada

O parceiro exige que o limite respeite a capacidade de pagamento do cliente e que o grau de alavancagem permitido seja diferenciado por perfil de risco. Conforme dados fornecidos pelo parceiro, clientes com score alto podem receber até 1,8 vezes sua capacidade de pagamento ($m_k = 1{,}8$), enquanto clientes com score baixo são limitados a 0,3 vezes ($m_k = 0{,}3$). Essa diferenciação evita tanto o superendividamento de clientes vulneráveis quanto a subutilização do potencial de clientes de baixo risco.

Como todos os clientes de um mesmo cluster recebem o mesmo limite $L_k$, a formulação usa o mínimo da capacidade de pagamento dentro do cluster como referência. Essa é uma abordagem conservadora: garante que mesmo o cliente com menor capacidade do grupo não seja exposto a um limite incompatível.

$$L_k \leq m_k \cdot \min_{i \in \mathcal{C}_k} CP_i, \quad \forall k$$

O multiplicador $m_k$ varia continuamente entre 0,3 e 1,8 conforme o perfil de risco do cluster. Na implementação, $m_k$ é interpolado a partir do score médio do cluster: clusters de menor risco recebem $m_k$ próximo de 1,8, e clusters de maior risco recebem $m_k$ próximo de 0,3. Esta restrição é linear em $L_k$ e não envolve bilinearidade.

#### R4 - Limite mínimo

O parceiro estabelece um piso de R\$ 200 para qualquer limite de cartão de crédito ofertado. Abaixo desse valor, o cartão perde competitividade frente a concorrentes e o custo operacional de emissão, manutenção e processamento não se justifica pela receita gerada. A formulação vincula o piso à variável de seleção $z_k$: quando o cluster recebe oferta ($z_k = 1$), o limite deve ser ao menos R\$ 200; quando não recebe ($z_k = 0$), o limite é livre para ser zero.

$$L_k \geq L^{min} \cdot z_k = 200 \cdot z_k, \quad \forall k$$

A discretização em múltiplos de R\$ 50 ($L_k^{final} = 50 \cdot \lceil L_k / 50 \rceil$) é aplicada em pós-processamento, não como restrição do modelo, de modo a preservar a continuidade da formulação LP.

#### R5 - Teto máximo de limite

O parceiro indicou um teto absoluto de R\$ 25.000 para o limite ofertado. Contudo, na prática esse teto não é fixo: ele varia conforme o perfil de risco do cliente — clientes de maior risco devem ter tetos substancialmente menores. A restrição R3 (alavancagem) já captura essa diferenciação, pois o produto $m_k \cdot \min CP_i$ gera tetos naturalmente mais baixos para clusters de alto risco. O teto de R\$ 25.000 funciona como um limite absoluto que impede valores extremos mesmo para clusters de baixo risco com alta capacidade de pagamento.

$$L_k \leq L^{max} = 25000, \quad \forall k$$

Na prática, R3 é a restrição ativa para a maioria dos clusters (pois $m_k \cdot \min CP_i < 25000$ para quase todos), e R5 atua apenas como salvaguarda nos casos em que a capacidade de pagamento é excepcionalmente alta.

#### Restrições adicionais de produção

Além das quatro restrições acima, o parceiro indicou que o modelo deve suportar metas de produção configuráveis, que podem ser ativadas ou desativadas conforme a estratégia comercial de cada safra. São elas: (i) **quantidade mínima de clientes aprovados** ($N^{meta}$), para evitar que o modelo concentre a oferta em poucos clusters de perfil ideal; (ii) **volume mínimo de limite total** ($V^{meta}$), para garantir massa financeira suficiente na carteira; e (iii) **rentabilidade mínima** ($R^{meta}$), para impedir soluções de alto volume mas baixa margem. Essas restrições são lineares em $L_k$ (após fixar $z_k$ na etapa de seleção) e serão formalizadas na implementação conforme os valores definidos pelo parceiro.

#### Restrições de domínio

$$L_k \geq 0, \quad z_k \in [0, 1], \quad \forall k$$

Limites não podem ser negativos. A variável $z_k$ é naturalmente binária (oferta ou não oferta), mas relaxada para o intervalo contínuo $[0, 1]$ para manter a formulação como programação linear. Na abordagem em duas etapas, $z_k$ é fixado em 0 ou 1 antes da otimização de limites, de modo que a relaxação não afeta a solução final.

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
