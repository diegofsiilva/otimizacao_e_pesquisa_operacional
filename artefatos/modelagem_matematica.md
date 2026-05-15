# Modelagem Matemática

## Sumário

O documento é organizado em quatro partes principais. A primeira apresenta a formulação da modelagem matemática, com contexto, dados, variáveis, parâmetros, função objetivo e restrições. A segunda discute as limitações e pontos de atenção do modelo. A terceira traz uma versão reduzida e visual do problema para ajudar na interpretação geométrica. A quarta mostra como a solução reage a mudanças nos parâmetros e como isso apoia a tomada de decisão no ambiente real. Ao final, são listadas as fontes de referência utilizadas.

## 1. Modelagem matemática do problema

### 1.1 Contexto do problema

O Banco Pan precisa definir, para cada cliente correntista elegível, qual limite pré-aprovado de cartão de crédito oferecer. Trata-se de um problema mono-produto: o escopo é exclusivamente o cartão de crédito pré-aprovado, sem considerar outros produtos de crédito da instituição. A prática vigente combina modelos de scoring com tabelas fixas de política de crédito, uma abordagem que trata de forma homogênea clientes com perfis de risco e capacidade de pagamento distintos. Isso significa que o risco agregado da carteira não é controlado diretamente pela decisão de limite, e que o potencial de retorno de parte da base elegível não é aproveitado. A validação do modelo desenvolvido neste projeto será feita pelo parceiro comparando a rentabilidade esperada entre o `limite_ofertado` praticado atualmente e o limite sugerido pelo modelo otimizado.

O núcleo do problema é um trade-off entre duas forças opostas. Um limite alto demais aumenta a receita de interchange, mas eleva a exposição à inadimplência e pode comprometer a saúde financeira do cliente. Um limite baixo demais reduz o risco, mas diminui a receita e pode frustrar o cliente a ponto de migrá-lo para um concorrente. A tabela abaixo resume esse trade-off:

| Decisão   | Se o limite for alto demais               | Se o limite for baixo demais           |
| :-------- | :---------------------------------------- | :------------------------------------- |
| _Receita_ | Mais interchange, maior retorno potencial | Menos uso do cartão, menos receita     |
| _Risco_   | Maior exposição, inadimplência sobe       | Menor inadimplência, carteira mais sã  |
| _Cliente_ | Risco de superendividamento               | Frustração, migração para concorrentes |
| _Banco_   | Provisão maior, NPL sobe                  | Perda de competitividade no produto    |

Esse equilíbrio entre retorno esperado e risco é amplamente estudado na literatura de otimização de crédito ao consumidor. Instituições como FICO (2021), Experian (2024) e Moody's Analytics (2020) tratam a definição de limite como um problema de otimização, onde a rentabilidade esperada é maximizada sujeita a restrições de risco da carteira e capacidade de pagamento individual.

Este problema é formulado como um **problema de programação linear (LP) de alocação de crédito**, no qual a variável de decisão é o limite contínuo atribuído a cada cluster de clientes, a função objetivo maximiza o retorno líquido esperado (receita de interchange menos perda esperada por inadimplência), e as restrições impõem tetos de inadimplência agregada, capacidade de pagamento por cluster e regras operacionais do banco. Idealmente, este problema seria formulado como programação inteira mista (MIP), o que permitiria modelar a discretização dos limites em múltiplos de R\$ 50 e a seleção de clientes diretamente como variáveis do modelo. Entretanto, a orientação do parceiro é por uma abordagem LP, e o escopo atual prioriza uma formulação simples e funcional, viável no momento e suficiente para capturar a estrutura essencial do problema. Na Etapa 1 (pré-processamento), os clientes elegíveis são agrupados em clusters; na Etapa 2, o LP otimiza os limites $L_k$ para todos os clusters simultaneamente. Em pós-otimização, clusters cujo limite resultar abaixo de R\$ 200 são interpretados como "sem oferta", e os demais são arredondados para múltiplos de R\$ 50.

### 1.2 Dados disponíveis relevantes

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
| `score_interno`              | Score de crédito interno                      | min=54, med=292, max=975                                           | Não utilizado diretamente no modelo; serve apenas como input interno do banco para gerar `pd_produto`                                                                                                             |
| `pd_produto`                 | Probabilidade de default no produto           | min=0,025, med=0,71, max=0,946                                     | **Parâmetro central da FO (termo B) e da restrição R1**, via média por cluster ($PD_k$). Mediana de 0,71 indica que a maioria da base elegível tem PD alta, indicando que a seleção de quais clusters recebem oferta é tão importante quanto a calibração do limite |
| `score_generico_1`           | Score de bureau (bureau 1)                    | min=49, med=409, max=995. Nulls: 0,1%                              | Pode compor o perfil de risco para cálculo de $m_k$; variável de segmentação para clusterização                                                                                                            |
| `score_generico_2`           | Score de bureau (bureau 2)                    | min=1, med=713, max=942. Nulls: <0,01%                             | Pode compor o perfil de risco para cálculo de $m_k$; variável de segmentação para clusterização                                                                                                            |
| `capacidade_pagamento`       | Estimativa interna de capacidade de pagamento | min=0, med=548, max=25.000. **Nulls: 0,3% M1; 42,2% M2; 43,5% M3** | **Restrição R2 (alavancagem).** Nulls em M2/M3 são limitação severa (ver Análise Crítica)                                                                                                                                |
| `delta_capacidade_pagamento` | Capacidade deduzida dos saldos a vencer       | min=−25.000, med=55, max=25.000. Nulls: idem                       | Versão conservadora da capacidade; valores negativos indicam comprometimento além da capacidade                                                                                                                   |
| `renda_estimada`             | Estimativa interna de renda                   | min=1.275, med=1.908, max=17.950. Nulls: 0,3%                      | Proxy alternativa para R2 quando `capacidade_pagamento` é null ($CP_i = \text{renda\_estimada}_i \times 0{,}30$); usado no cálculo de $CP_k$                                                                                                   |
| `fx_idade`                   | Faixa etária                                  | 9 faixas: 21-30 (35,5%), 31-40 (31,1%), 41-50 (18,8%)              | Perfil de consumo e risco; variável de segmentação para análise de resultados                                                                                                                                      |
| `flag_filtros`               | Indicador de perfil restrito                  | **0 = elegível** (1,84M), **1 = restrito** (12,73M)                | Restrição hard: clientes com `flag_filtros = 1` são excluídos da otimização                                                                                                                                        |
| `score_propensao_contrato`   | Score de propensão à conversão                | min=3, med=315, max=846                                            | Parâmetro $\pi_k$ na FO (termo A), via média do cluster. **Range [3, 846], não [0,1]**, requer normalização min-max                                                                                                                     |
| `score_credito_cross`        | Score de crédito multiproduto                 | min=103, med=706, max=954                                          | Determina a faixa de alavancagem $m_k$ do cluster (ver tabela de faixas na Seção 1.5)                                                                                                                                      |
| `limite_ofertado`            | Limite ofertado na política atual             | min=200, med=806, max=20.000. **99,2% null**                       | Baseline para backtesting (apenas 117K têm referência)                                                                                                                                                             |
| `flag_contrato`              | Indicadora de contratação (1 = contratou)     | 6.506 (0,04%)                                                      | Backtesting. Taxa de conversão ~5,5% entre os que receberam oferta                                                                                                                                                 |
| `flag_ativacao`              | Indicadora de ativação (1 = ativou)           | 5.704 (87,7% dos que contrataram)                                  | Backtesting                                                                                                                                                                                                        |
| `over30mob3`                 | Atraso >30 dias nas 3 primeiras parcelas      | 4.966 válidos, **377 eventos** (7,6%). 99,97% null                 | Inadimplência realizada. Viés de seleção severo (só observável para quem ativou)                                                                                                                                   |

**Observações críticas sobre os dados:**

**Funil de conversão (M1):** Dos 14,5M clientes, ~1,8M são elegíveis. Desses, 117K receberam oferta (6,4% dos elegíveis). Dos que receberam, 6.506 contrataram (5,5%) e 5.704 ativaram (87,7%). Apenas 4.966 têm `over30mob3` observado, dos quais 377 (7,6%) tiveram evento de inadimplência. Esse funil confirma que a **seleção de quem recebe oferta** é tão relevante quanto a **definição do limite**.

**PD da base é alta:** A mediana de `pd_produto` é 0,71 nas três safras, ou seja, a maioria da base tem PD > 50%. Isso é esperado: a base inclui todos os correntistas, não apenas os pré-aprovados. Clientes de baixo risco são minoria. Implicação: o modelo precisa ser eficiente na seleção (quais clientes recebem oferta), não apenas na calibração do limite.

**`capacidade_pagamento` null em M2/M3:** Em M1, apenas 0,3% dos registros não têm essa variável. Porém, **em M2 o percentual sobe para 42,2% e em M3 para 43,5%**, quase metade da base. Isso é uma limitação severa para a restrição R2 (alavancagem), discutida na Análise Crítica.

**Clusterização dos clientes:** A base elegível contém aproximadamente 1,8 milhão de clientes na safra M1. Otimizar um limite individual $L_i$ para cada cliente resultaria em um LP com ~1,8M variáveis de decisão e número equivalente de restrições individuais (capacidade de pagamento), o que tornaria o tempo de resolução proibitivo para solvers open-source como CBC. Por essa razão, o modelo agrupa os clientes elegíveis em $K$ clusters (mínimo 100, conforme orientação do TAPI) com base em variáveis de perfil de risco e capacidade de pagamento, como `pd_produto`, `capacidade_pagamento`, `score_credito_cross` e `fx_idade`. A técnica de clusterização (e.g., K-Means ou segmentação por faixas) será definida na etapa de implementação. Para cada cluster $k$, os parâmetros representativos ($PD_k$, $\pi_k$, $CP_k$, $m_k$) são calculados como médias dos clientes do grupo, exceto $CP_k$ que usa o percentil 5 ($p5$) do cluster para garantir robustez sem que outliers com capacidade atipicamente baixa inviabilizem a alocação de todo o grupo. Todos os $n_k$ clientes de um mesmo cluster recebem o mesmo limite $L_k$. Idealmente, cada cliente receberia um limite individual, mas a abordagem por clusters é o que viabiliza a resolução com os recursos computacionais disponíveis.

**Parâmetros fornecidos pelo parceiro:**

- **Taxa de interchange:** $t = 0{,}0175$ (1,75% sobre volume transacionado).
- **LGD (Loss Given Default):** $\text{LGD} = 0{,}80$, indicando que, em caso de default, o banco perde 80% do saldo exposto (recuperando 20% via cobrança ou cessão de carteira). Esse valor é uma simplificação uniforme para todos os clusters, conservador em relação à média de mercado para cartão de crédito sem garantia. Idealmente, a LGD seria diferenciada por perfil de risco, mas essa granularidade ainda não está disponível.
- **Utilização esperada do limite:** Constante $\bar{u} = 0{,}75$ (75% do limite concedido). Esse valor reflete uma estimativa conservadora de uso efetivo do cartão. Idealmente, $\bar{u}_k$ seria estimada por perfil de cluster a partir de dados de ativação, mas esses dados ainda não estão disponíveis.

---

### 1.3 Estrutura do modelo

O modelo opera sobre **clusters de clientes**: os clientes elegíveis são agrupados em $K$ clusters (mínimo 100), e cada cluster $k$ recebe um limite único $L_k$ atribuído a todos os seus $n_k$ membros.

**Etapa 1 - Pré-processamento e clusterização** FALAR MAIS SOBRE A CLSUTERIZACAo AGORA QUE JA FIZEMOS


Antes da clusterização, são removidos da base todos os clientes com `flag_filtros = 1`, que representam perfis restritos e não podem receber crédito (aproximadamente 12,7M dos 14,5M na safra M1). Apenas os clientes elegíveis (`flag_filtros = 0`, ~1,8M em M1) seguem para a etapa seguinte. Esses clientes elegíveis são então agrupados em $K$ clusters com base em variáveis de perfil de risco e capacidade de pagamento. Para cada cluster $k$, calculam-se os parâmetros representativos: $PD_k$ e $\pi_k$ como médias dos clientes do grupo, e $CP_k$ como o percentil 5 de capacidade de pagamento do cluster.

**Etapa 2 - Otimização de limites (LP)**

O LP otimiza os valores de $L_k$ para todos os $K$ clusters simultaneamente, maximizando o retorno líquido total sujeito às restrições R1–R3. O LP tem $K$ variáveis (uma por cluster), tornando a resolução computacionalmente viável mesmo com solvers open-source. Clusters onde o retorno líquido não justifica concessão recebem naturalmente $L_k$ próximo de zero pelo solver, e são filtrados no pós-otimização (limites abaixo de R\$ 200 são convertidos em "sem oferta").

**Sobre pré-seleção de clusters:** Uma abordagem alternativa seria rankear clusters por retorno líquido unitário $c_k$ e pré-selecionar apenas os rentáveis antes do LP, o que permitiria incorporar restrições como tetos de inadimplência física já na seleção. Entendemos que essa sofisticação pode ser necessária futuramente caso o modelo precise de controles adicionais na composição da carteira, mas por enquanto a abordagem direta (LP sobre todos os clusters + pós-otimização) é suficiente e mais simples.

---

### 1.4 Variáveis de decisão

O modelo possui uma única variável de decisão no LP:

**$L_k \in \mathbb{R}^+$ - Limite de crédito por cluster (variável contínua)**

$L_k$ representa o valor do limite de crédito, em reais, atribuído a todos os clientes do cluster $k$. A variável é contínua, coerente com a formulação LP. Idealmente, $L_k$ seria definida como inteira ($L_k \in \mathbb{Z}^+$, múltiplos de R\$ 50) em uma formulação MIP, eliminando a necessidade de arredondamento, mas a formulação contínua é o que é viável no momento. O LP determina o valor de $L_k$ para cada cluster que maximiza o retorno líquido total, respeitando todas as restrições. Os limites finais sugeridos ao banco são obtidos em pós-otimização: clusters com $L_k \geq 200$ têm o limite arredondado para o múltiplo de R\$ 50 mais próximo acima; clusters com $L_k < 200$ não recebem oferta (ver seção Domínio e não-negatividade).

| Símbolo | Tipo | Descrição | Domínio |
| :------ | :--- | :-------- | :------ |
| $L_k$ | Variável de decisão | Limite de crédito atribuído ao cluster $k$ | $\mathbb{R}^+$ (contínuo, otimizado pelo LP) |
| $k \in \{1, \dots, K\}$ | Índice | Cluster de clientes elegíveis ($K \geq 100$) | - |
| $n_k$ | Parâmetro | Número de clientes no cluster $k$ | inteiro positivo |

---

### 1.5 Parâmetros (dados de entrada)

| Símbolo | Descrição | Unidade / Domínio | Fonte |
| :------ | :-------- | :---------------- | :---- |
| $K$ | Número total de clusters | inteiro ($\geq 100$) | Definido na clusterização (Etapa 1) |
| $n_k$ | Número de clientes no cluster $k$ | inteiro positivo | Resultado da clusterização |
| $PD_k$ | Probabilidade de default representativa do cluster $k$ | [0, 1] | Média de `pd_produto` dos clientes do cluster |
| $\pi_k$ | Propensão à contratação do cluster $k$, normalizada | [0, 1] | Média de `score_propensao_contrato` normalizado min-max: $\pi_i = \frac{score_i - 3}{843}$ |
| $CP_k$ | Capacidade de pagamento do cluster $k$ | R\$ | Percentil 5 ($p5$) de `capacidade_pagamento` no cluster. Proxy: `renda_estimada × 0,30` quando null |
| $m_k$ | Multiplicador de alavancagem do cluster $k$ | [0,20; 0,45] | Determinado pela faixa de `score_credito_cross` médio do cluster (ver tabela de faixas abaixo) |
| $t$ | Taxa de interchange (mensal) | adimensional | 0,0175 (fornecido pelo parceiro) |
| $T$ | Horizonte de receita | meses | 22 (período médio de uso do limite no produto, fornecido pelo parceiro) |
| $\text{LGD}$ | Loss Given Default | [0, 1] | 0,80 (constante para todos os clusters) |
| $\bar{u}$ | Utilização esperada do limite | [0, 1] | 0,75 (constante para todos os clusters) |
| $\gamma_d$ | Fator de calibração da PD no decil $d$ | [0,20; 0,45] | Razão empírica $\frac{\text{over30mob3}}{\text{pd\_produto}}$ por decil de PD bruta (ver tabela na Seção 1.5.1) |
| $PD_k^{cal}$ | Probabilidade de default calibrada do cluster $k$ | [0, 1] | $PD_k^{cal} = PD_k \cdot \gamma_{d(k)}$, onde $d(k)$ é o decil de $PD_k$ |
| $\overline{PD}_{fin}^{atual}$ | Teto de inadimplência financeira | [0, 1] | Média ponderada (por limite) de PD da carteira aprovada vigente |
| $L^{max}$ | Teto máximo de limite | R\$ | 25.000 (diretriz do parceiro) |
| $\overline{PD}_{fis}^{atual}$ | Teto de inadimplência física | [0, 1] | Média simples de PD da carteira aprovada vigente (headcount, sem ponderar por limite) |
| $\alpha$ | Concentração máxima por cluster | [0, 1] | Fração máxima da exposição total que um único cluster pode concentrar. Valor sugerido: $\alpha = 0{,}05$ (5%) |
| $V^{min}$ | Volume mínimo de produção | R\$ | Piso de volume total de limite ofertado, definido pelo parceiro com base em metas comerciais. Ordem de grandeza típica: centenas de milhões de reais (o cenário de referência da Seção 4 adota $V^{min} = 0$ por simplicidade, mas o valor operacional plausível seria $V^{min} \in [\text{R\$ 100 M};\; \text{R\$ 500 M}]$ considerando o volume potencial máximo de R\$ 689 M observado quando apenas R2 é ativa) |
| $c_k$ | Coeficiente de retorno líquido unitário do cluster $k$ | R\$/R\$ | $c_k = \pi_k \cdot (T \cdot \bar{u} \cdot t - PD_k^{cal} \cdot \text{LGD})$ |

**Faixas de alavancagem $m_k$:** O multiplicador $m_k$ segue a média de `score_credito_cross` do cluster e foi calibrado pela alavancagem observada na política vigente, usando o percentil 75 como teto por faixa. A relação é monotônica: scores mais altos recebem $m_k$ maior, refletindo menor risco.

| Faixa de `score_credito_cross` | $m_k$ | PD mediana (base elegível) | Alavancagem mediana observada | Alavancagem p75 observada |
| :------------------------------ | :---- | :------------------------- | :---------------------------- | :------------------------ |
| 100 – 700 | 0,20 | 0,72 | 0,14 | 0,22 |
| 700 – 800 | 0,25 | 0,61 | 0,16 | 0,25 |
| 800 – 850 | 0,30 | 0,50 | 0,18 | 0,28 |
| 850 – 900 | 0,35 | 0,34 | 0,21 | 0,32 |
| 900 – 960 | 0,45 | 0,24 | 0,28 | 0,42 |

Em termos práticos, o p75 equilibra aderência à política atual e contenção da cauda mais agressiva: o p50 seria conservador demais e o p90 herdaria exceções que enfraquecem o papel prudencial de R2.

#### 1.5.1 Calibração da PD por decil ($\gamma_d$)

A variável `pd_produto` é uma PD anual do scoring interno. Como o modelo opera em $T = 22$ meses, ela é calibrada pela razão entre `over30mob3` e `pd_produto`; essa razão, $\gamma$, aproxima a perda efetiva observável e captura o caráter front-loaded do default em cartão.

A análise (detalhada em `scripts/analise_09_calibracao_final.py`, sobre 17.366 clientes com `over30mob3` observado e 5,9M de elegíveis amostrados nas safras M1, M2 e M3) revela três fatos:

1. **A razão $\gamma$ não é constante.** Globalmente $\gamma \approx 0{,}24$, mas ela cresce por decil de `pd_produto` (de 0,21 em D1 até 0,24 em D4), então o multiplicador uniforme 0,24 não representa bem os extremos da base.

2. **Para decis com PD acima de ~46% (D5 em diante) a amostra é pequena**, porque a política vigente quase não aprova esses perfis. Onde há observação, a razão sobe para ~0,44; por isso, de D6 a D10 adotamos $\gamma = 0{,}40$ como extrapolação conservadora.

3. **Calibração por `score_credito_cross` não discrimina bem.** As faixas 100–900 ficam quase no mesmo patamar de $\gamma$, então os decis de `pd_produto` continuam mais informativos.

A tabela abaixo apresenta a calibração final. Para o cluster $k$, o decil $d(k)$ é determinado pelo $PD_k$ representativo, e a PD calibrada é $PD_k^{cal} = PD_k \cdot \gamma_{d(k)}$.

| Decil $d$ | Faixa de `pd_produto` | $\overline{PD}_d$ | $N_{obs}$ | $\gamma_d$ empírico (IC95%) | $\gamma_d$ adotado | Fonte |
| :-------: | :-------------------- | :---------------: | --------: | :--------------------------: | :----------------: | :---- |
| D1  | 0,000 – 0,211 | 0,155 | 2.357 | 0,209 [0,164; 0,258] | 0,21 | empírico |
| D2  | 0,211 – 0,296 | 0,253 | 3.744 | 0,213 [0,187; 0,242] | 0,21 | empírico |
| D3  | 0,296 – 0,378 | 0,336 | 5.567 | 0,242 [0,220; 0,266] | 0,24 | empírico |
| D4  | 0,378 – 0,461 | 0,419 | 5.624 | 0,235 [0,218; 0,255] | 0,24 | empírico |
| D5  | 0,461 – 0,543 | 0,502 | 60   | 0,442 [0,239; 0,679] | 0,44 | empírico (amostra reduzida) |
| D6  | 0,543 – 0,619 | 0,581 | 8    | —                    | 0,40 | extrapolação linear |
| D7  | 0,619 – 0,687 | 0,653 | 5    | —                    | 0,40 | extrapolação linear |
| D8  | 0,687 – 0,746 | 0,717 | 0    | —                    | 0,40 | extrapolação linear |
| D9  | 0,746 – 0,804 | 0,774 | 0    | —                    | 0,40 | extrapolação linear |
| D10 | 0,804 – 1,000 | 0,841 | 1    | —                    | 0,40 | extrapolação linear |

**Por que decis e não um valor único:** o $\gamma$ uniforme representa bem o miolo da distribuição, mas distorce os extremos. A discretização por decis preserva a heterogeneidade observada sem exigir um hiperparâmetro contínuo, e o pipeline pode aplicar a regra por cliente ou por cluster; aqui usamos por cluster por consistência com o modelo.

**Periodicidade de revisão:** os valores de $\gamma_d$ devem ser recalculados a cada nova safra, idealmente trimestralmente. Mudanças na razão observada $\gamma$ sinalizam drift do modelo de scoring ou alteração no comportamento da carteira; em ambos os casos, são gatilho para reotimização do LP.

---

### 1.6 Objetivo do modelo e função objetivo

O objetivo do modelo é substituir a regra empírica por uma decisão matemática: encontrar os limites $L_k$ que maximizem o retorno líquido total esperado, isto é, receita de interchange menos perda esperada por inadimplência. Como o produto é apenas cartão pré-aprovado, receita e risco estão concentrados no próprio limite. A formulação usa **receita − perda** sem ponderador $\lambda$, deixando o controle de risco para as restrições e mantendo tudo na mesma unidade monetária.

**Coerência temporal:** $t = 0{,}0175$ é mensal e $T = 22$ deixa a receita no mesmo horizonte da perda calibrada. A PD continua vindo de uma janela anual, então o ajuste por $\gamma_{d(k)}$ corrige o mismatch entre receita acumulada e risco observado. A combinação $T = 22$ + calibração por decil torna a carteira aprovada consistente com o produto real.

O limiar de rentabilidade individual (PD bruta abaixo da qual $c_k > 0$) depende agora do decil:

$$PD_k < \frac{T \cdot \bar{u} \cdot t}{\gamma_{d(k)} \cdot \text{LGD}}$$

Para os parâmetros adotados, o limiar varia de **172%** em decis com $\gamma = 0{,}21$ a **90%** em decis com $\gamma = 0{,}40$. Mesmo assim, ele fica acima da PD média da base elegível, então a seleção de clusters é guiada principalmente por R1, R5 e R6.

$$\max \sum_{k=1}^{K} n_k \cdot \left[\underbrace{\pi_k \cdot T \cdot \bar{u} \cdot t \cdot L_k}_{\text{(A) Receita esperada em $T$ meses}} \; - \; \underbrace{\pi_k \cdot PD_k^{cal} \cdot \text{LGD} \cdot L_k}_{\text{(B) Perda esperada no horizonte}}\right]$$

Fatorando $L_k$ e $\pi_k$, e usando $PD_k^{cal} = PD_k \cdot \gamma_{d(k)}$:

$$\max \sum_{k=1}^{K} n_k \cdot \underbrace{\pi_k \cdot (T \cdot \bar{u} \cdot t - PD_k \cdot \gamma_{d(k)} \cdot \text{LGD})}_{c_k} \cdot L_k$$

onde $n_k$ é o número de clientes no cluster $k$ e $c_k$ é o **coeficiente de retorno líquido unitário** do cluster $k$. O fator $n_k$ garante que clusters maiores tenham peso proporcional ao número de clientes que representam.

#### Interpretação da função objetivo

**Termo (A) - Receita:** $\pi_k \cdot T \cdot \bar{u} \cdot t \cdot L_k$ é a receita de interchange esperada por cliente do cluster $k$ ao longo do horizonte de uso de $T = 22$ meses. O cliente contrata com probabilidade $\pi_k$ (média do cluster, derivada de `score_propensao_contrato` normalizado via min-max). O contratante utiliza uma fração $\bar{u} = 0{,}75$ do limite a cada mês, o banco recebe taxa de interchange $t = 0{,}0175$ sobre o volume transacionado mensal, e a receita é acumulada ao longo do período de uso do limite.

**Termo (B) - Perda:** $\pi_k \cdot PD_k^{cal} \cdot \text{LGD} \cdot L_k$ é a perda esperada por inadimplência por cliente do cluster $k$ no horizonte considerado. A perda só se materializa para clientes que efetivamente contratam (com probabilidade $\pi_k$), e entre estes, uma fração $PD_k^{cal} = PD_k \cdot \gamma_{d(k)}$ é a estimativa calibrada da probabilidade de default efetivo, ajustada do viés de horizonte do scoring interno. $\text{LGD} = 0{,}80$ é a fração do saldo exposto que o banco perde em caso de default (os 20% restantes são recuperados via cobrança ou cessão), e $L_k$ é a exposição. Note que a perda utiliza $L_k$ integral (sem o fator $\bar{u}$), diferentemente da receita. Isso é intencional: a exposição no momento do default (EAD) considera o limite inteiro porque, na prática, clientes inadimplentes tendem a utilizar uma fração do limite significativamente superior à média antes de cessar pagamentos. Essa é uma premissa padrão em modelos de risco de crédito para cartão (Resolução CMN 4.966/2021). Em sprints futuros, essa premissa pode ser refinada com um fator de utilização pré-default ($\bar{u}_{default}$) calibrado a partir de dados da carteira.

**Coeficiente $c_k$:** O retorno líquido unitário $c_k = \pi_k \cdot (T \cdot \bar{u} \cdot t - PD_k \cdot \gamma_{d(k)} \cdot \text{LGD})$ resume a rentabilidade marginal de cada real alocado ao cluster $k$. Como $\pi_k > 0$, o sinal de $c_k$ depende do balanço entre $T \cdot \bar{u} \cdot t$ (receita unitária no horizonte) e $PD_k \cdot \gamma_{d(k)} \cdot \text{LGD}$ (perda unitária calibrada): clusters com $PD_k < \frac{T \cdot \bar{u} \cdot t}{\gamma_{d(k)} \cdot \text{LGD}}$ são rentáveis. Clusters com $c_k > 0$ são rentáveis; clusters com $c_k \leq 0$ destroem valor a cada real adicional de limite; para estes, o solver naturalmente atribui $L_k = 0$. O coeficiente $n_k \cdot c_k$ é o coeficiente objetivo do LP: o solver tende a maximizar $L_k$ para clusters com maior $c_k$, limitado pelas restrições.

A FO é linear em $L_k$: todos os demais termos ($n_k$, $\pi_k$, $T$, $\bar{u}$, $t$, $PD_k$, $\gamma_{d(k)}$, $\text{LGD}$) são parâmetros, não há produto de variáveis de decisão, e o problema é um LP puro.

**Unidades dos resultados.** A variável de decisão $L_k^*$ é um estoque em R\$ (limite revolvente de cartão), sem dimensão temporal. O coeficiente $c_k$ é retorno líquido por R\$ de exposição ao longo dos $T = 22$ meses de uso do limite, e portanto $Z^*$ representa o retorno acumulado da carteira no mesmo horizonte, não retorno anual nem mensal. Para comparar com indicadores anualizados da operação (ROA, NIM), basta dividir $Z^*$ por $T/12 \approx 1{,}83$: no caso da solução de referência da Seção 4 ($Z^* = \text{R\$ 30{,}12 M}$ em 22 meses), o equivalente anualizado fica em torno de $\text{R\$ 16{,}4 M}$/ano.

### 1.7 Restrições

As restrições traduzem as políticas de crédito do Banco Pan em limites matemáticos para o espaço de soluções factíveis. Dividem-se em três categorias: (i) **controle de risco da carteira**, com R1 (inadimplência financeira) e R4 (inadimplência física); (ii) **proteção por cluster e bounds**, com R2 (capacidade de pagamento) e R3 (teto máximo); e (iii) **diversificação e viabilidade comercial**, com R5 (concentração máxima) e R6 (meta de produção). R1, R2, R3, R5 e R6 são incorporadas diretamente no LP; R4 é tratada em pós-otimização por envolver indicadoras de cluster ativo.

#### R1 - Teto de inadimplência financeira (LP)

A inadimplência financeira pondera a PD pelo limite atribuído, medindo o risco da carteira em termos de exposição financeira. A decisão de **quanto** limite conceder a cada cluster impacta diretamente essa métrica.

**Versão original (razão, não-linear):**

$$\frac{\sum_{k=1}^{K} n_k \cdot PD_k \cdot L_k}{\sum_{k=1}^{K} n_k \cdot L_k} \leq \overline{PD}_{fin}^{atual}$$

**Versão linearizada** (multiplicando ambos os lados pelo denominador, estritamente positivo para qualquer solução não-trivial; se todos os $L_k = 0$, a restrição é satisfeita trivialmente e o retorno é zero):

$$\sum_{k=1}^{K} n_k \cdot (PD_k - \overline{PD}_{fin}^{atual}) \cdot L_k \leq 0$$

Cada cluster $k$ contribui com um excesso ou déficit de inadimplência: clusters com $PD_k > \overline{PD}_{fin}^{atual}$ consomem folga (coeficiente positivo), enquanto clusters com $PD_k < \overline{PD}_{fin}^{atual}$ geram folga (coeficiente negativo). A restrição é linear em $L_k$.

#### R2 - Capacidade de pagamento com alavancagem diferenciada (LP)

$$L_k \leq m_k \cdot CP_k, \quad \forall k \in \{1, \dots, K\}$$

O limite de cada cluster é limitado pelo percentil 5 de capacidade de pagamento dos seus membros ($CP_k = p5_{i \in C_k}(CP_i)$), multiplicado pelo fator de alavancagem $m_k \in [0{,}20;\; 0{,}45]$, determinado pela faixa de `score_credito_cross` médio do cluster (ver tabela de faixas na Seção 1.5). As faixas foram calibradas a partir da alavancagem observada na política vigente (p75 por faixa de score, sobre 480 mil registros elegíveis com oferta em M1–M3): clusters com score mais alto recebem $m_k$ maior (até 0,45), e clusters com score mais baixo recebem $m_k$ menor (0,20). O uso do percentil 5 (em vez do mínimo) evita que um único outlier com $CP$ atipicamente baixo inviabilize o limite de todo o cluster, mantendo a proteção para 95% dos membros.

#### R3 - Teto máximo de limite (LP)

$$L_k \leq L^{max}, \quad \forall k \in \{1, \dots, K\}$$

Teto absoluto definido pelo parceiro ($L^{max} = 25\,000$). Na prática, R2 é a restrição ativa para a maioria dos clusters (pois $m_k \cdot CP_k < L^{max}$ para quase todos), e R3 atua apenas como salvaguarda.

#### R4 - Teto de inadimplência física (LP)

A inadimplência física mede o risco da carteira por **headcount**: qual fração dos clientes que receberam oferta se torna inadimplente, independentemente do limite concedido. Enquanto R1 pondera a PD pelo limite (capturando o risco financeiro), R4 controla a quantidade de clientes em default, que impacta custo operacional de cobrança, reputação e compliance regulatório.

$$\frac{\sum_{k=1}^{K} n_k \cdot PD_k \cdot \mathbb{1}[L_k > 0]}{\sum_{k=1}^{K} n_k \cdot \mathbb{1}[L_k > 0]} \leq \overline{PD}_{fis}^{atual}$$

Essa formulação com indicadoras $\mathbb{1}[L_k > 0]$ não é linear. Na prática, como o LP atribui $L_k > 0$ a todo cluster com $c_k > 0$ (e $L_k = 0$ aos demais), a inadimplência física é verificada em **pós-otimização** sobre o conjunto de clusters ativos ($\mathcal{A} = \{k : L_k^* \geq 200\}$):

$$\frac{\sum_{k \in \mathcal{A}} n_k \cdot PD_k}{\sum_{k \in \mathcal{A}} n_k} \leq \overline{PD}_{fis}^{atual}$$

Se violada, clusters com maior $PD_k$ e menor $c_k$ são removidos iterativamente de $\mathcal{A}$ (definindo $L_k = 0$) até que a restrição seja satisfeita. Essa abordagem mantém o LP puro e trata R4 como um filtro de viabilidade aplicado ao resultado.

#### R5 - Concentração máxima por cluster (LP)

$$n_k \cdot L_k \leq \alpha \cdot \sum_{j=1}^{K} n_j \cdot L_j, \quad \forall k \in \{1, \dots, K\}$$

Nenhum cluster pode concentrar mais do que uma fração $\alpha$ da exposição total da carteira. Essa restrição impede que o solver despeje limite em um único cluster "ideal", forçando diversificação. Sem ela, um cluster com $c_k$ alto e $CP_k$ generoso absorveria a maior parte da folga de R1, gerando uma carteira rentável mas concentrada — vulnerável a choques setoriais ou regionais que afetem justamente esse perfil.

**Versão linearizada:** Reorganizando:

$$n_k \cdot L_k - \alpha \cdot \sum_{j=1}^{K} n_j \cdot L_j \leq 0, \quad \forall k$$

$$\sum_{j=1}^{K} n_j \cdot (\mathbb{1}[j = k] - \alpha) \cdot L_j \leq 0, \quad \forall k$$

Isso equivale a $K$ restrições lineares adicionais, uma por cluster. Para cada restrição $k$, o coeficiente de $L_j$ é $n_j \cdot (1 - \alpha)$ quando $j = k$ (positivo, penaliza concentração) e $-n_j \cdot \alpha$ quando $j \neq k$ (negativo, incentiva dispersão). O valor sugerido é $\alpha = 0{,}05$ (5%), ajustável pelo parceiro conforme o apetite por diversificação.

#### R6 - Meta de produção mínima (LP)

$$\sum_{k=1}^{K} n_k \cdot L_k \geq V^{min}$$

O volume total de limite ofertado deve atingir um piso $V^{min}$ definido pelo parceiro. Essa restrição garante que o modelo não produza uma solução excessivamente conservadora que, embora ótima no sentido de maximizar retorno por real, oferece volume insuficiente para justificar a operação comercial do produto. Sem essa restrição, o solver pode convergir para um cenário onde apenas poucos clusters de baixíssimo risco recebem ofertas modestas — financeiramente seguro, mas comercialmente inviável.

A restrição é linear em $L_k$. Se o LP for infactível com $V^{min}$, isso sinaliza que as demais restrições (especialmente R1 e R4) estão demasiadamente restritivas para o volume desejado, informando diretamente uma negociação entre área comercial e área de risco.

#### Domínio e não-negatividade

$$L_k \geq 0, \quad \forall k \in \{1, \dots, K\}$$

O limite é definido como variável não-negativa. O parceiro exige um piso mínimo de R\$ 200 para ofertas efetivas, mas essa regra é tratada em **pós-otimização**, não como restrição do LP: clusters cujo limite ótimo resultar em $L_k < 200$ são interpretados como "não conceder crédito", indicando que não há alocação rentável acima do piso para esse perfil. Essa abordagem evita forçar o solver a atribuir R\$ 200 a clusters onde o retorno líquido não justifica a concessão, e permite que o modelo comunique explicitamente quais perfis não devem receber oferta.

**Pós-otimização dos limites:**

$$L_k^{\text{final}} = \begin{cases} 50 \cdot \left\lceil \dfrac{L_k}{50} \right\rceil & \text{se } L_k \geq 200 \\[6pt] 0 \text{ (sem oferta)} & \text{se } L_k < 200 \end{cases}, \quad \forall k \in \{1, \dots, K\}$$

#### Resumo das restrições

| ID | Restrição | Tipo |
| :- | :-------- | :--- |
| R1 | Teto de inadimplência financeira ($\overline{PD}$ ponderada por $n_k \cdot L_k$ $\leq$ teto) | Linear (após linearização) |
| R2 | Capacidade de pagamento ($L_k \leq m_k \cdot CP_k$) | Linear |
| R3 | Teto máximo ($L_k \leq L^{max}$) | Bound |
| R4 | Teto de inadimplência física (média simples de $PD_k$ dos clusters ativos $\leq$ teto) | Pós-otimização |
| R5 | Concentração máxima por cluster ($n_k \cdot L_k \leq \alpha \cdot \sum n_j L_j$) | Linear |
| R6 | Meta de produção mínima ($\sum n_k \cdot L_k \geq V^{min}$) | Linear |

**Restrições futuras identificadas (não formalizadas nesta sprint):** Ao longo do projeto, espera-se incorporar restrições adicionais como rentabilidade mínima por cluster, tetos de exposição por faixa de risco, e número mínimo de clusters ativos. Essas restrições dependem de parâmetros que ainda serão definidos com o parceiro.

---

## 2. Análise crítica

**Limitação 1 (LGD uniforme).** O modelo adota $\text{LGD} = 0{,}80$ constante, mas a taxa de recuperação varia por perfil: clientes de renda alta tendem a apresentar LGD menor. Isso superestima a perda esperada nos decis de PD baixa e a subestima nos decis altos, distorcendo $c_k$ e a alocação ótima.

**Limitação 2 (`capacidade_pagamento` null em M2/M3).** A restrição R2 depende de $CP_k$, porém 42–43 % dos elegíveis em M2 e M3 não têm a variável preenchida. Adotamos o proxy $CP_i = \text{renda\_estimada}_i \times 0{,}30$, presente em 99,7 % da base, ciente de que subestima clientes com múltiplas fontes de renda e superestima os com alto comprometimento prévio.

**Análise de sensibilidade a $\gamma_d$ (exemplo numérico fechado).** Após a calibração temporal ($T = 22$, Seção 1.5.1), $\gamma_d$ é o parâmetro de maior sensibilidade do modelo. Aplicando uma elevação uniforme de **+25 %** sobre $\gamma_d$ em todos os decis (cenário de drift do scoring) sobre a solução base ($Z^* = \text{R\$ 30{,}12 M}$, 7 clusters ativos, volume R\$ 613 M), o LP reotimizado entrega $Z^* = \text{R\$ 26{,}65 M}$ (queda de **−11,5 %**), volume inalterado (R2 e R5 continuam binding nos mesmos clusters) e **mesma base ótima** (D1–D7 ativos). A robustez é maior do que sugere a inspeção visual de $c_k$: a base só muda a partir de **+60 %** em $\gamma_d$ (D7 sai, ficam 6 clusters; $Z^* = \text{R\$ 21,80 M}$) e o cenário extremo de +100 % derruba D6 e D7 simultaneamente, restando apenas D1–D4 com $Z^* = \text{R\$ 17,64 M}$ (−41 %). Isso indica que o gatilho de reotimização deve combinar o **drift observado** de $\gamma_d$ com a **proximidade dos clusters de fronteira** ($c_{D7}$, $c_{D8}$) do zero, e não apenas a magnitude percentual de variação. A análise detalhada de preços-sombra e custos reduzidos sob esse mesmo cenário consta da Seção 4 (Análise de Sensibilidade aplicada com 10 clusters reais via Solver/OpenSolver).

---

## 3. Análise gráfica do problema

Para complementar a formulação algébrica, esta seção usa um cenário reduzido com dois clusters representativos. O objetivo aqui não é reproduzir o LP completo, mas mostrar graficamente como a região factível surge da interação entre a restrição de inadimplência financeira e os limites de capacidade de pagamento.

### 3.1 Cenário reduzido

Os valores abaixo são ilustrativos e servem apenas para viabilizar a visualização em 2D. Os multiplicadores $m_k$ foram ampliados em relação à política real para que a fronteira factível fique visível no gráfico.

| Parâmetro | Cluster 1 (baixo risco) | Cluster 2 (risco moderado) |
| :-------- | :---------------------: | :------------------------: |
| $PD_k$ | 0,002 | 0,004 |
| $\pi_k$ | 0,80 | 0,70 |
| $CP_k$ | R\$ 4.000 | R\$ 1.500 |
| $m_k$ | 1,5 | 0,8 |
| $n_k$ | 500 | 300 |

Com $T = 22$, $\bar{u} = 0{,}75$, $t = 0{,}0175$, $\text{LGD} = 0{,}80$ e $\overline{PD}_{fin}^{atual} = 0{,}0022$, os coeficientes de retorno líquido unitário são:

- $c_1 = 0{,}80 \times (22 \times 0{,}75 \times 0{,}0175 - 0{,}002 \times 0{,}80) = 0{,}80 \times (0{,}28875 - 0{,}0016) = 0{,}80 \times 0{,}28715 = 0{,}22972$ (positivo, cluster rentável)
- $c_2 = 0{,}70 \times (22 \times 0{,}75 \times 0{,}0175 - 0{,}004 \times 0{,}80) = 0{,}70 \times (0{,}28875 - 0{,}0032) = 0{,}70 \times 0{,}28555 = 0{,}19989$ (positivo, menos rentável)

A função objetivo neste cenário reduzido é:

$$\max \; 500 \cdot 0{,}22972 \cdot L_1 + 300 \cdot 0{,}19989 \cdot L_2 = \max \; 114{,}86 \cdot L_1 + 59{,}97 \cdot L_2$$

### 3.2 Região factível

As restrições que aparecem no gráfico são:

- **R1 (inadimplência financeira):** define a reta inclinada $L_2 \leq 0{,}185 \cdot L_1$.
- **R2 (capacidade de pagamento):** impõe os cortes verticais e horizontais de $L_1 \leq 6\,000$ e $L_2 \leq 1\,200$.
- **Não-negatividade:** fecha a região no primeiro quadrante.

As demais restrições ficam fora da figura por motivo estrutural: **R3** não é ativa nesse cenário, **R4** é tratada em pós-otimização no modelo completo, e **R5/R6** são restrições de carteira agregada que não cabem num plano de dois clusters.

### 3.3 Visualização

O gráfico abaixo apresenta a região factível (área sombreada), as retas das restrições e as curvas de nível da função objetivo. A solução ótima encontra-se no vértice da região factível que maximiza o retorno líquido, indicado pelo ponto destacado.

<div align="center">

![Análise Gráfica do Problema de Otimização](assets/analise_grafica_otimizacao.png)

</div>

<div align="center">Fonte: Material produzido pelos autores</div>

### 3.4 Interpretação

A análise gráfica evidencia visualmente três pontos:

- **Trade-off entre clusters:** o coeficiente de $L_1$ é maior que o de $L_2$, então o modelo favorece o cluster 1.
- **Restrição ativa:** R1 é a fronteira que realmente limita a alocação do cluster 2.
- **Solução ótima:** o ótimo fica na interseção entre R2 em $L_1 = 6\,000$ e R1 em $L_2 \approx 1\,111$.

A região factível fica em formato triangular porque R1 é mais apertada que o limite horizontal de R2 para o cluster 2. A figura, portanto, ilustra um LP clássico: função objetivo linear, fronteira linear e solução ótima em um vértice.

---

### 4. Análise de Sensibilidade

A análise desta seção é aplicada **diretamente sobre a base real do Banco Pan**, agregada em 10 clusters por decil de `pd_produto` (≈ 6,7 milhões de elegíveis das safras M1, M2 e M3). O LP completo com as restrições R1 (teto de inadimplência financeira ponderada), R2 (capacidade de pagamento alavancada), R3 (teto absoluto), R5 (concentração máxima por cluster) e R6 (volume mínimo) foi resolvido no **OpenSolver com GLPK no Google Sheets** a partir da planilha compartilhada em [Google Sheets](https://docs.google.com/spreadsheets/d/1Je64KaMrVqcCnavN7nFpp5OqDzVSHnHKtmvkgQTjcJg/edit?usp=sharing). O mesmo modelo foi validado em paralelo via `scipy.optimize.linprog` (HiGHS), com diferença numérica nula. As instruções passo-a-passo para reproduzir a análise estão na aba **"Como_rodar_OpenSolver"** da própria planilha.

**Solução ótima de referência:**

| Indicador | Valor |
| :-------- | ----: |
| Função objetivo $Z^*$ | R$ 30.121.656 |
| Volume total ofertado $\sum n_k L_k^*$ | R$ 613.482.710 |
| PD financeira ponderada da carteira | 32,00 % |
| Clusters com oferta efetiva ($L_k^* > 0$) | 7 de 10 (D1–D7) |
| Clusters sem oferta ($L_k^* = 0$) | 3 de 10 (D8, D9, D10) |

A solução base abaixo serve de referência para todas as análises seguintes. A aba **"Relatorio_Sensibilidade"** da planilha apresenta os custos reduzidos e preços-sombra no formato padrão do Solver (Final Value / Reduced Cost / Objective Coefficient / Permissível Acréscimo+Decréscimo para variáveis, e Final Value / Shadow Price / R.H. Side / Permissível Acréscimo+Decréscimo para restrições). Os valores foram pré-calculados via `scipy.optimize.linprog` com o motor **HiGHS**, mesmo algoritmo de programação linear usado por baixo pelo GLPK/CBC do OpenSolver e pelo Simplex LP do Solver do Excel, de modo que são numericamente idênticos ao que essas ferramentas devolveriam. No **Excel desktop**, o relatório pode ser gerado nativamente pelo Solver (Resolver, marcar "Sensibilidade" na caixa de Relatórios); a versão atual do **OpenSolver para Google Sheets** resolve o LP normalmente (preenche $L_k^*$ e $Z^*$ na aba "Modelo") mas não emite o relatório formatado, função cumprida pela aba pré-preenchida.

| $k$ | Decil | $PD_k$ | $\pi_k$ | $CP_{p5}$ | $m_k$ | $\gamma_d$ | $c_k$ | $L_k^*$ (R$) | $n_k \cdot L_k^*$ (R$) | Custo Reduzido |
| :-: | :---: | -----: | -----: | --------: | ----: | --------: | -----: | -----------: | ---------------------: | -------------: |
| 1 | D1 | 0,156 | 0,158 | 800 | 0,35 | 0,21 | 0,04147 | 258,47 | 184.044.813 | 0 |
| 2 | D2 | 0,254 | 0,213 | 465 | 0,35 | 0,21 | 0,05246 | 162,75 | 113.571.995 | 0 |
| 3 | D3 | 0,336 | 0,260 | 450 | 0,30 | 0,24 | 0,05837 | 135,00 |  98.192.250 | 0 |
| 4 | D4 | 0,419 | 0,304 | 442 | 0,30 | 0,24 | 0,06323 | 132,75 |  95.815.366 | 0 |
| 5 | D5 | 0,503 | 0,346 | 427 | 0,25 | 0,44 | 0,03873 | 106,84 |  73.899.131 | 0 |
| 6 | D6 | 0,581 | 0,389 | 250 | 0,25 | 0,40 | 0,03996 |  62,50 |  41.847.438 | 0 |
| 7 | D7 | 0,653 | 0,425 | 150 | 0,25 | 0,40 | 0,03387 |   9,17 |   6.111.718 | 0 |
| 8 | D8 | 0,716 | 0,455 | 125 | 0,25 | 0,40 | 0,02707 |   **0,00** | 0 | **−12.310,50** |
| 9 | D9 | 0,774 | 0,479 | 100 | 0,20 | 0,40 | 0,01966 |   **0,00** | 0 | **−24.264,67** |
| 10 | D10 | 0,840 | 0,498 |  75 | 0,20 | 0,40 | 0,00987 |   **0,00** | 0 | **−37.201,42** |

#### 4.1 Aplicação prática

A solução ótima do LP é calculada com base em parâmetros que representam estimativas do comportamento esperado da carteira: probabilidade de default, propensão à contratação, taxa de utilização do limite e capacidade de pagamento. No mundo real, nenhum desses parâmetros é fixo — eles variam em função de ciclos econômicos, drift do modelo de scoring, pressões competitivas e decisões regulatórias. A análise de sensibilidade é parte integrante do processo de decisão, pois determina até onde os parâmetros podem se mover sem invalidar a política de limites vigente.

No caso específico do Banco Pan, a análise apoia a área de crédito em quatro decisões recorrentes: (i) **quais perfis (clusters) oferecer cartão pré-aprovado**, lendo diretamente os $L_k^*$ resultantes; (ii) **quais restrições políticas estão de fato limitando a rentabilidade**, lendo as restrições ativas e os preços-sombra; (iii) **quanto custaria, em R\$ de retorno, incluir um cluster atualmente descartado**, lendo o custo reduzido; (iv) **em que momento a política precisa ser revista**, lendo os intervalos de permissibilidade (acréscimo/decréscimo permitido em cada parâmetro sem mudança de base ótima).

A leitura desses indicadores transforma o LP de uma ferramenta de cálculo pontual em um instrumento de gestão dinâmica: enquanto os parâmetros observados permanecerem dentro dos intervalos de estabilidade, a política vigente continua ótima; quando cruzarem essas fronteiras, a reotimização é acionada de forma objetiva, antes que a degradação se materialize na inadimplência observada.

**Hierarquia de parâmetros críticos.** No regime calibrado ($T = 22$ + $\gamma_d$ por decil), o coeficiente $c_k = \pi_k \cdot (T \bar{u} t - PD_k \gamma_{d(k)} \text{LGD})$ é positivo em todos os clusters da base elegível, de modo que **a viabilidade individual deixa de ser o gargalo**. O monitoramento prioritário recai sobre: (a) o conjunto $\{\gamma_d\}_{d=1}^{10}$, recalculado a cada safra a partir da razão observada $\text{over30mob3}/\text{pd\_produto}$; (b) o teto $\overline{PD}_{fin}^{atual}$ que parametriza R1; e (c) a capacidade de pagamento $CP_k$ por cluster, especialmente em M2/M3 onde 42–43 % dos registros têm `capacidade_pagamento` nula e a restrição R2 opera sobre o proxy `renda_estimada × 0,30`.

#### 4.2 Variações na função objetivo

A análise dos coeficientes da FO determina o **intervalo de variação** dentro do qual cada $c_k$ pode se mover sem que a base ótima se altere. Enquanto $c_k$ permanece nesse intervalo, os mesmos clusters continuam recebendo oferta nos mesmos valores; apenas o valor numérico de $Z^*$ muda. Quando $c_k$ ultrapassa o limite, a base muda — algum cluster entra ou sai da solução.

No LP do Banco Pan, uma variação em $c_k$ pode decorrer de: (i) revisão da $PD_k$ por modelos de scoring atualizados; (ii) recalibração de $\gamma_d$ pela observação de novas safras; (iii) mudança na propensão $\pi_k$ por campanha de marketing; ou (iv) revisão da utilização $\bar{u}$ por análise de comportamento da carteira ativada. A tabela abaixo apresenta os intervalos de permissibilidade calculados via solver, lendo diretamente do Relatório de Sensibilidade gerado pelo OpenSolver/Solver:

| Cluster | $c_k$ atual | Permissível Acréscimo | Permissível Decréscimo | Faixa de estabilidade de $c_k$ |
| :-----: | ----------: | --------------------: | ---------------------: | :----------------------------- |
| D1 (básica) | 0,04147 | +0,4147 | −0,0581 | [−0,017 ; +0,456] |
| D2 (básica) | 0,05246 | +0,5246 | −0,0969 | [−0,044 ; +0,577] |
| D3 (básica) | 0,05837 | +0,5837 | −0,0867 | [−0,028 ; +0,642] |
| D4 (básica) | 0,06323 | +0,6323 | −0,0753 | [−0,012 ; +0,695] |
| D5 (básica) | 0,03873 | +0,3873 | −0,0344 | [+0,004 ; +0,426] |
| D6 (básica) | 0,03996 | +0,3996 | −0,0202 | [+0,020 ; +0,440] |
| D7 (básica) | 0,03387 | +0,0277 | −0,0155 | [+0,018 ; +0,062] |
| D8 (não-básica) | 0,02707 | +0,0192 | infinito | até $c_8 \leq 0{,}0463$ permanece fora |
| D9 (não-básica) | 0,01966 | +0,0379 | infinito | até $c_9 \leq 0{,}0576$ permanece fora |
| D10 (não-básica) | 0,00987 | +0,0608 | infinito | até $c_{10} \leq 0{,}0707$ permanece fora |

**Exemplo numérico aplicado — cluster D4 (variável básica).** Suponha que uma recalibração de $\gamma_4$ no próximo trimestre eleve $PD_4 \cdot \gamma_d$ de 0,1006 para 0,1106 (acréscimo de 1 ponto percentual, equivalente a +10 % no produto), o que reduz $c_4$ de 0,06323 para:

$$c_4' = \pi_4 \cdot (T \bar{u} t - 0{,}1106 \cdot \text{LGD}) = 0{,}304 \cdot (0{,}28875 - 0{,}1106 \cdot 0{,}80) = 0{,}304 \cdot 0{,}20027 = 0{,}06088$$

A variação $\Delta c_4 = -0{,}00235$ está confortavelmente dentro do intervalo de permissibilidade $[-0{,}075;\; +0{,}632]$, de modo que a base ótima permanece inalterada. O efeito é apenas sobre o valor de $Z$: $\Delta Z = n_4 \cdot \Delta c_4 \cdot L_4^* = 721{.}773 \cdot (-0{,}00235) \cdot 132{,}75 \approx -\text{R\$}\;225.000$ no retorno anualizado. A política não precisa ser revista; apenas o retorno esperado é ajustado para baixo. Esse é o uso típico do intervalo de permissibilidade: filtrar pequenas variações que não justificam reotimização.

**Exemplo numérico aplicado — cluster D8 (variável não-básica) e custo reduzido.** O cluster D8 (PD média 71,6 %) recebe $L_8^* = 0$ na solução ótima e tem **custo reduzido de −R\$ 12.310,50**. A leitura desse número segue exatamente a definição do slide da aula: **"o custo reduzido de uma variável não-básica é a quantidade pela qual o valor de Z vai diminuir (em um problema de máx) se insistirmos em incluir uma unidade da variável na base"**. Portanto, se forçássemos $L_8 = \text{R\$}\;1$ (uma unidade monetária de exposição por cliente de D8), o valor da FO cairia em R\$ 12.310,50 por causa do deslocamento de orçamento de risco de outros clusters mais rentáveis.

A leitura simétrica (também ensinada no slide) é o **valor que $c_k$ precisaria atingir para tornar a variável atrativa**. Como cada cluster tem $n_k$ clientes, o custo reduzido por cliente é $-12.310{,}50 / 640.559 = -0{,}01922$ por real de exposição. Portanto, para D8 entrar na base, $c_8$ teria que subir de 0,02707 para no mínimo $0{,}02707 + 0{,}01922 = 0{,}04629$, um aumento de 71 %. Equivalentemente, $\gamma_8$ teria que cair de 0,40 para aproximadamente 0,22 (uma melhora de calibração que dependeria de evidência empírica de over-prediction da PD nesse decil), ou $\pi_8$ teria que crescer 71 %. Enquanto nenhum desses movimentos ocorrer, é racional manter D8 fora da oferta.

O mesmo raciocínio aplica-se a D9 (custo reduzido $−$R\$ 24.264, $c_9$ precisaria subir para 0,058) e D10 ($−$R\$ 37.201, $c_{10}$ precisaria subir para 0,071) — ambos requereriam mudanças muito mais agressivas, consistente com o fato de que esses clusters têm PD acima de 77 % e estão claramente fora da fronteira de rentabilidade da política atual.

**Validação cruzada via solver.** Resolvendo o LP com $L_8 = 1$ forçado, o solver retorna $Z = 30.121.656 - 12.310{,}50 = 30.109.346$, confirmando exatamente o custo reduzido reportado.

#### 4.3 Restrições e preços-sombra

Cada restrição do LP representa uma escolha de política: R1 codifica o apetite de risco da instituição, R2 traduz a diretriz de proteção ao cliente (limite atrelado à capacidade de pagamento), R3 é o teto absoluto regulatório/operacional, R5 é o limite de concentração da carteira por perfil e R6 (não ativa neste cenário) é o piso comercial de produção.

**Informação obtida do RHS das restrições.** O lado direito de cada restrição expressa o "orçamento" daquele recurso, e o relatório de sensibilidade informa: (i) o **valor final do LHS**, que comparado ao RHS identifica restrições ativas (LHS = RHS) e folgadas (LHS < RHS); (ii) o **preço-sombra**, que quantifica em R\$ o valor marginal de relaxar a restrição em uma unidade; e (iii) o **intervalo de permissibilidade**, que delimita até onde o RHS pode ser alterado sem que o preço-sombra deixe de ser constante (ou seja, sem que a base ótima mude).

**Informação obtida dos preços-sombra.** O preço-sombra responde à pergunta gerencial *"quanto a mais de retorno o banco obteria se pudesse afrouxar essa política?"*. Valores altos indicam gargalos com maior retorno marginal; valores zero indicam folga.

Os preços-sombra do LP resolvido são:

| Restrição | Status | LHS (Final) | RHS | Preço-Sombra | Interpretação |
| :-------- | :----: | :---------: | :-: | -----------: | :------------ |
| **R1 — PD financeira** ($\leq 0{,}32$) | **ATIVA** | 0,3200 | 0,3200 | **R\$ 0,1964** por unidade de $\sum n_k L_k$ excedente | Apertar/afrouxar o teto altera $Z$ proporcionalmente ao volume |
| R2 — D1 ($L_1 \leq 280$) | folgada | 258,47 | 280,00 | 0 | Não é gargalo (R5 limita antes) |
| **R2 — D2** ($L_2 \leq 162{,}75$) | **ATIVA** | 162,75 | 162,75 | **R\$ 67.633** por R\$ 1 de $m_k CP_k$ | Maior gargalo da carteira |
| **R2 — D3** ($L_3 \leq 135{,}00$) | **ATIVA** | 135,00 | 135,00 | **R\$ 63.064** por R\$ 1 de $m_k CP_k$ | Segundo maior gargalo |
| **R2 — D4** ($L_4 \leq 132{,}75$) | **ATIVA** | 132,75 | 132,75 | **R\$ 54.333** | Gargalo relevante |
| **R2 — D5** ($L_5 \leq 106{,}84$) | **ATIVA** | 106,84 | 106,84 | **R\$ 23.807** | Gargalo moderado |
| **R2 — D6** ($L_6 \leq 62{,}50$) | **ATIVA** | 62,50 | 62,50 | **R\$ 13.507** | Gargalo menor |
| R2 — D7, D8, D9, D10 | folgadas | < RHS | varia | 0 | Não são gargalos individuais |
| R3 — todos os clusters ($\leq 25.000$) | folgadas | $\leq 280$ | 25.000 | 0 | R3 nunca é binding nesta carteira |
| **R5 — D1** (concentração $\leq 30\%$) | **ATIVA** | 0,00 | 0,00 | **R\$ 0,1052** por R\$ adicional de concentração | D1 está no teto de 30 % do volume |
| R5 — demais clusters | folgadas | < 0 | 0 | 0 | Nenhum outro cluster atinge 30 % |

**Exemplo numérico aplicado — R1 (teto de inadimplência financeira).** A restrição R1 ($\sum n_k \cdot PD_k \cdot L_k / \sum n_k \cdot L_k \leq 0{,}32$) está ativa exatamente em 0,32. O preço-sombra de 0,1964 informa que cada **unidade do termo de excesso** ($\sum n_k (PD_k - 0{,}32) L_k$) que pudermos tolerar gera +R\$ 0,1964 de $Z$. Traduzindo para a linguagem gerencial: relaxar $\overline{PD}_{fin}^{atual}$ de 0,32 para 0,33 (1 ponto percentual de tolerância adicional) equivale a aumentar o RHS em$0,01 \cdot \sum n_k L_k^* = 0,01 \cdot 613.482.710 = \text{R\$ 6.134.827}$. O ganho esperado em $Z$ é portanto $0,1964 \cdot 6.134.827 \approx \text{R\$ 1.205.000}$ de retorno adicional. Em outras palavras, **cada ponto percentual adicional de apetite de risco vale R\$ 1,2 milhões anuais para a carteira**. A decisão de ampliar esse apetite passa a ser uma comparação direta: o custo de provisão regulatória sobre a inadimplência incremental supera ou não esses R\$ 1,2 M?

**Exemplo numérico aplicado — R2 do cluster D2 (capacidade de pagamento).** A R2 de D2 está ativa em $L_2^* = 162{,}75$. O preço-sombra de R\$ 67.633 mostra que cada R\$ 1 adicional no termo $m_k \cdot CP_{p5}$ gera +R\$ 67.633 de $Z$. Na prática, isso pode vir de melhorar $CP_{p5}$ ou de elevar $m_2$; qualquer uma das alavancas aumenta retorno, mas também deve ser lida junto com R1.

**Exemplo numérico aplicado — R5 do cluster D1 (concentração).** A R5 de D1 está ativa: o cluster está no teto de 30 % da exposição total. O preço-sombra de 0,1052 indica que cada R\$ 1 adicional de concentração em D1 vale +R\$ 0,1052 de $Z$. Elevar o teto para 31 % aumenta o retorno, mas reduz a diversificação.

**Síntese gerencial.** R2 é o maior gargalo de retorno marginal, R1 é a alavanca de apetite de risco e R5 é a alavanca de diversificação. R3 permanece folgada porque R2 já limita os $L_k$ bem abaixo de R\$ 25.000.

#### 4.4 Tomada de decisão em ambiente real

No ambiente real de gestão de crédito, as variações nos parâmetros não ocorrem de forma isolada. Ciclos macroeconômicos, mudanças regulatórias e alterações no perfil da base movem múltiplos parâmetros simultaneamente e de forma correlacionada. A análise de sensibilidade permite integrar essas informações a um processo de decisão que convive permanentemente com incerteza.

**Cenário de variação de demanda.** A propensão $\pi_k$ muda com sazonalidade, campanhas e competição. Como entra linearmente em $c_k$, uma variação uniforme altera $Z$ mas não a ordem relativa dos clusters. Uma campanha segmentada pode elevar $\pi_5$ e manter o cluster na base, apenas com maior contribuição para o retorno.

**Cenário de estresse macroeconômico (custos/capacidade).** Em alta de Selic, renda comprometida sobe, $CP_k$ cai e R2 aperta; ao mesmo tempo, a inadimplência sobe e pressiona R1. A base real confirma a correlação negativa entre `capacidade_pagamento` e `pd_produto`, então os efeitos tendem a se amplificar.

Suponha um choque que reduz $CP_{p5}$ em 10 % em todos os clusters e eleva $PD_k$ em 5 %. Os efeitos isolados, lidos do relatório de sensibilidade:

- **Em R2 (D2):** $CP_{p5,2}$ cai de R\$ 465 para R\$ 418, reduzindo $m_2 CP_{p5,2}$ em R\$ 16,28. Pelo preço-sombra de R\$ 67.633/R\$, isso custa $\text{R\$ 67.633} \cdot 16{,}28 \approx \text{R\$ 1,1 M}$. Aplicando o mesmo raciocínio para D3 a D6 e somando, o impacto agregado é de aproximadamente **R\$ 4,3 M** de redução em $Z$.
- **Em R1:** $PD_k$ +5 % significa que cada cluster contribui mais para a inadimplência ponderada. Para manter R1 em 0,32, o solver precisa realocar volume — provavelmente reduzindo $L_k$ dos clusters de PD mais alta dentro da base (D5–D7). O impacto não é diretamente lido do preço-sombra (porque a mudança não é só no RHS, é estrutural), e exige reotimização do LP.

A área de crédito pode pré-rodar esse cenário combinado na própria planilha (alterando os valores das colunas $CP_{p5}$ e $PD$ e re-executando o Solver) e comparar o novo $Z^*$ e a nova alocação $L_k^*$ com a base. Se a mudança for significativa, o ambiente saiu do intervalo de estabilidade da política vigente e a reotimização deve ser oficializada. Se permanecer próxima, a política base é robusta ao cenário testado.

**Cenário de variação estrutural — calibração $\gamma_d$.** Diferentemente das variações conjunturais acima, uma recalibração de $\gamma_d$ por nova safra é um movimento previsível e regular. O protocolo recomendado é: (i) a cada trimestre, recalcular $\gamma_d$ empiricamente sobre o `over30mob3` da safra mais recente; (ii) comparar com os $\gamma_d$ vigentes no modelo; (iii) se algum $\gamma_d$ saiu do intervalo $\pm$ IC95% bootstrap (Seção 1.5.1), atualizar o parâmetro; (iv) re-rodar o LP e comparar a nova solução com a vigente. Esse ciclo trimestral integra a análise de sensibilidade ao processo de governança de risco do banco.

**Protocolo de decisão integrado.** O protocolo operacional derivado das análises anteriores pode ser sintetizado em três regras de gestão:

1. **Monitoramento contínuo dos parâmetros críticos.** A hierarquia de sensibilidade identificada ($\gamma_d > PD_k > CP_k > \pi_k > \bar{u} > t$) determina a frequência de revisão. Os $\gamma_d$ e $PD_k$ são acompanhados por safra e comparados aos intervalos de permissibilidade. Quando um parâmetro se aproxima do limite, a reotimização é acionada **antes** que a política se torne subótima.

2. **Uso dos preços-sombra como critério de investimento.** Os preços-sombra traduzem decisões qualitativas em análises de custo-benefício quantitativas. Investir em melhoria do modelo de $CP_k$ só se justifica se o ganho marginal (R\$ 67.633 por R\$ de $m_2 CP$ em D2, na carteira atual) superar o custo do investimento. Aceitar maior inadimplência agregada só é racional se o retorno incremental (R\$ 1,2 M por ponto percentual de R1) compensar o custo de provisão regulatória e capital alocado.

3. **Reotimização sob cenários combinados.** Em períodos de estresse, a área de crédito executa o LP sob cenários perturbados (e.g., $PD_k + 20\%$, $CP_k - 10\%$) **na própria planilha**, comparando a solução resultante com a política vigente. Se a nova solução diferir significativamente, o ambiente mudou além do intervalo de estabilidade e a política precisa ser atualizada. Se permanecer próxima, a política base é robusta ao cenário testado.

Esse protocolo transforma o modelo de otimização de uma ferramenta de cálculo pontual em um instrumento de gestão contínua. A análise de sensibilidade conecta a solução matemática ao processo decisório da instituição, e a planilha [no Google Sheets](https://docs.google.com/spreadsheets/d/1Je64KaMrVqcCnavN7nFpp5OqDzVSHnHKtmvkgQTjcJg/edit?usp=sharing) é a interface concreta para que a área de políticas de crédito execute essas decisões sem dependência da equipe de data science a cada iteração.


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
        