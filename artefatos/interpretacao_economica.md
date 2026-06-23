# Interpretação Econômica

## Sumário
Este documento interpreta o modelo de otimização sob a ótica econômica e estratégica do Banco Pan. A análise está organizada em quatro frentes: função objetivo, restrições como políticas de negócio, leitura econômica das decisões do modelo e implicações estratégicas para adoção. O foco não é descrever a matemática do modelo, mas traduzir o que ele decide e quais consequências econômicas essas decisões produzem.

_Diretrizes de escrita: ancorar cada afirmação em número, com a fonte no próprio texto (TAPI, base Parquet, `modelagem_matematica.md §X`); preferir síntese a parágrafos longos; referir riscos ao próprio modelo, não a riscos acadêmicos; e fechar cada frente com um diferencial ("ir além") que extrapola o solicitado._

## 1. Interpretação Econômica da Função Objetivo

Esta seção lê a função objetivo como uma decisão de negócio, não como uma equação. Antes de interpretar, vale fixar o objeto: a FO condensa o trade-off central do projeto (quanto limite dar a cada perfil para capturar receita sem assumir perda excessiva) em uma única expressão monetária que o otimizador maximiza (formulação completa em `modelagem_matematica.md §1.6`):

$$\max_{L_k}\; Z \;=\; \sum_{k=1}^{K} n_k \,\pi_k \,\Big(\underbrace{T\,\bar{u}\,t}_{\text{receita unitária}} \;-\; \underbrace{PD_k\,\gamma_{d(k)}\,\text{LGD}}_{\text{perda unitária}}\Big)\,L_k$$

Cada símbolo, e o que significa em termos de negócio:

- **$L_k$**: variável de decisão, o limite (R\$) ofertado a todos os clientes do cluster $k$ e que o modelo escolhe.
- **$k$, $K$**: cada um dos $K \geq 100$ clusters (perfis) de clientes elegíveis.
- **$n_k$**: número de clientes no cluster; dá a cada perfil peso proporcional ao seu tamanho.
- **$\pi_k$**: propensão à contratação (0 a 1), a chance de o cliente aceitar a oferta; pondera receita e perda, que só ocorrem se ele contratar.
- **$T = 22$ meses**: horizonte de uso do limite.
- **$\bar{u} = 0{,}75$**: utilização, a fração do limite efetivamente gasta (75%).
- **$t = 0{,}0175$**: taxa de interchange, o que o banco ganha por real transacionado (1,75%).
- **$PD_k$**: probabilidade de default do perfil.
- **$\gamma_{d(k)}$**: fator que calibra a PD do scoring ao default efetivamente observado, por decil de risco.
- **$\text{LGD} = 0{,}80$**: *Loss Given Default*, a fração perdida em caso de default (recupera-se ~20%).
- **$c_k = \pi_k\,(T\bar{u}t - PD_k\gamma_{d(k)}\,\text{LGD})$**: retorno líquido por real de limite no cluster, o "spread de risco" do perfil e o que de fato orienta a decisão.

### 1.1 O que a função objetivo representa economicamente?
A função objetivo escolhe os limites que maximizam o **retorno líquido esperado da carteira** de cartão pré-aprovado: a receita de interchange que o banco ganha sobre o volume transacionado, menos a perda esperada quando o cliente entra em default. Não é maximizar receita bruta nem minimizar risco, e sim **margem ajustada à perda esperada**. Como o produto é mono-produto, receita e risco moram no mesmo lugar: o limite. Tanto a receita quanto a perda só se concretizam se o cliente aceitar a oferta, por isso entram ponderadas pela propensão à contratação $\pi_k$: a FO é, no fundo, um valor esperado sobre a conversão.

A unidade econômica é **R\$ de retorno acumulado no horizonte de uso do limite (22 meses)**: como $L_k$ é um estoque rotativo (sem dimensão temporal), o ótimo $Z^*$ é o retorno da carteira nesse horizonte: ≈ R\$ 30,1 M em 22 meses, ou ≈ R\$ 16,4 M/ano (`modelagem_matematica.md §4`). Na margem, cada real adicional de limite a um perfil rende o seu $c_k$.

### 1.2 Qual é a lógica de geração de valor?
O valor não vem de conceder mais crédito, e sim de **alocar melhor o limite entre perfis**. No lugar da régua fixa atual, o modelo direciona cada real para os clusters de spread líquido positivo ($c_k > 0$) e o retira de onde destrói valor. É a lógica de **perda esperada (PD × LGD × exposição)** descontada da receita, a mesma adotada por FICO (2021), Experian (2024) e Moody's (2020) (`modelagem_matematica.md §1.1`). Na solução de referência isso se traduz em ≈ R\$ 16,4 M/ano de retorno líquido sobre ≈ R\$ 613 M de volume ofertado.

Puxam a rentabilidade para cima a propensão $\pi_k$, a taxa de interchange $t$ (1,75%), o horizonte $T$ (22 meses) e a utilização $\bar{u}$ (75%); puxam para baixo a PD, a calibração $\gamma_d$ e a LGD (80%). O ganho frente à política vigente é medido por backtesting (rentabilidade do `limite_ofertado` atual contra o limite otimizado nas safras M1–M3), e é aí que se comprova geração de valor, não apenas números diferentes.

### 1.3 Quais distorções econômicas a função objetivo pode induzir?
A própria forma da FO embute incentivos que **as restrições conseguem conter**:

- **Cega ao risco.** É crescente em $L_k$ e não tem ponderador de risco ($\lambda$): sozinha, empurraria o limite ao infinito. Todo o controle de risco é delegado a R1–R6, ou seja, o objetivo isolado incentiva exposição máxima.
- **Margem acima de tudo.** Por maximizar $c_k$ por real, tende a concentrar nos clusters mais rentáveis; numa base cuja PD mediana é 0,71, isso seria perigoso sem o freio de R1/R4/R5.

Há ainda **duas simplificações que as restrições não corrigem**, e que mudariam não o valor de $Z$, mas *quem* recebe limite:

- **Custo de capital (RAROC).** Cada real de limite consome capital regulatório (ativo ponderado pelo risco, sob Basileia), e a FO não o desconta. O objetivo economicamente correto seria o retorno sobre o capital alocado (RAROC), e não o retorno bruto: por essa ótica, um cluster de margem alta porém PD alta, que prende muito capital, vale menos do que a FO atual sugere.
- **Horizonte (LTV).** A margem de interchange de 22 meses é uma fatia do LTV. Como ignora CAC e churn (um limite baixo demais frustra e empurra ao concorrente; um alto demais superendivida), a FO supervaloriza perfis de margem alta agora porém churn alto e subvaloriza os de margem fina mas fiéis. Um objetivo em LTV − CAC líquido de churn deslocaria limite para quem vale mais ao longo do tempo (Instrução 3).

Nenhuma das duas invalida a FO atual: ela é uma v1 deliberadamente simples (tudo em R\$, na mesma unidade, auditável), e essas são a sua evolução natural. As distorções que vêm de premissas/parâmetros (como a LGD uniforme) estão na Seção 6.

### 1.4 Leitura executiva da função objetivo
O modelo transforma a definição de limite de uma regra fixa em uma **otimização de margem ajustada ao risco**: aloca cada real de limite onde ele rende mais, líquido de perda esperada, sem piorar o risco da carteira, qualificando a decisão do analista de crédito em vez de substituí-la.

## 2. Interpretação das Restrições como Políticas de Negócio

Cada restrição traduz uma política de crédito do Banco Pan em um corte no espaço de soluções factíveis. Para cada uma, respondemos três perguntas:

- qual política representa
- qual risco controla
- o que acontece economicamente se for relaxada ou apertada

As respostas se apoiam nos preços-sombra do LP resolvido sobre a base real, agregada em 10 clusters por decil de `pd_produto` (`modelagem_matematica.md §4.3`).

### 2.1 Restrição R1: Teto de inadimplência financeira

R1 representa o apetite de risco financeiro da instituição: a carteira otimizada não pode ter PD ponderada pela exposição ($\sum n_k PD_k L_k / \sum n_k L_k$) acima da carteira aprovada vigente, com teto $\overline{PD}_{fin}^{atual} = 0{,}32$ no cenário resolvido. O risco que ela controla é a deterioração da qualidade financeira da carteira ponderada pelo valor exposto: diferentemente de contar clientes inadimplentes, R1 pesa cada default pelo limite em risco e captura a perda esperada em reais.

É a restrição ativa no nível agregado, com preço-sombra de 0,1964 por unidade do termo de excesso. Relaxá-la de 0,32 para 0,33 equivale a elevar o RHS em $0{,}01 \cdot \sum n_k L_k^* \approx \text{R\$ 6,1 M}$ e rende cerca de R\$ 1,2 M/ano de retorno adicional, ao custo de mais provisão e capital regulatório sobre a inadimplência incremental. Apertá-la empurra a alocação para os clusters mais seguros e de menor margem, deixando a carteira mais sã e com menor provisão, porém com menos volume rentável e menor receita.

### 2.2 Restrição R2: Capacidade de pagamento (alavancagem diferenciada)

R2 traduz a política de crédito responsável: o limite de cada perfil é amarrado à capacidade de pagamento ($L_k \leq m_k \cdot CP_k$), com a alavancagem $m_k$ crescente no score e $CP_k$ medido no percentil 5, uma escolha prudencial sobre o p50/p90 (`§1.5`). O risco controlado é o superendividamento individual, isto é, conceder acima do que o cliente comprovadamente sustenta, causa-raiz do default no nível do cliente. É o freio prudencial por cliente da carteira.

É também o maior gargalo de retorno marginal do modelo: está ativa em seis dos dez clusters, com preço-sombra de até R\$ 67.633 por R\$ 1 de $m_k \cdot CP_k$ em D2 (R\$ 63.064 em D3 e R\$ 54.333 em D4). Relaxá-la, seja elevando $m_k$ ou medindo melhor $CP_k$, é a alavanca de maior retorno, mas deve ser lida junto de R1, pois mais limite a perfis de PD alta pressiona o teto agregado; apertá-la reduz diretamente o retorno por cluster. Há ainda uma fragilidade do próprio modelo: 42–43% dos registros em M2/M3 têm `capacidade_pagamento` nula e usam o proxy `renda_estimada × 0,30` (`§6`), de modo que o gargalo mais caro repousa sobre uma medição imperfeita.

### 2.3 Restrição R3: Teto máximo de limite

R3 é o teto absoluto definido pelo parceiro ($L^{max} = \text{R\$ 25 mil}$), uma salvaguarda prudencial e operacional que controla a exposição unitária extrema e funciona como rede de segurança caso R2 falhe ou seja mal calibrada.

Na prática, nunca é ativa no cenário atual: o preço-sombra é zero porque R2 já limita os $L_k$ à casa das centenas de reais, bem abaixo dos R\$ 25 mil. Relaxá-la ou apertá-la não altera a solução; só passaria a morder num cenário hipotético de R2 muito frouxa.

### 2.4 Restrição R4: Teto de inadimplência física

R4 representa o apetite de risco por headcount: limita a fração de clientes inadimplentes entre os clusters com oferta, independentemente do limite concedido, em linha com a CMN 4.966/2021. Complementa R1, que olha os reais expostos enquanto R4 olha o número de clientes, e controla o risco operacional e reputacional, isto é, custo de cobrança, compliance e imagem, que escalam com a quantidade de inadimplentes e não com o valor exposto.

Por envolver indicadoras de cluster ativo, opera em pós-otimização, removendo iterativamente os clusters de maior $PD_k$ e menor $c_k$ até satisfazer o teto. Apertá-la reduz a base atendida e a receita; relaxá-la amplia a base e, com ela, o custo operacional de cobrança.

### 2.5 Restrição R5: Concentração máxima por cluster

R5 traduz a política de diversificação da carteira: nenhum perfil pode concentrar mais que $\alpha$ da exposição total ($n_k L_k \leq \alpha \sum n_j L_j$). Controla o risco sistêmico e de concentração, já que uma carteira rentável porém dependente de um único perfil fica vulnerável a choques setoriais ou regionais que atinjam justamente aquele cluster.

No cenário resolvido, R5 é ativa em D1, no teto de concentração, com preço-sombra de 0,1052: cada R\$ 1 adicional de concentração em D1 vale +R\$ 0,1052 de $Z$. Relaxá-la rende retorno e fragiliza a carteira; apertá-la dispersa o limite e protege contra choques.

### 2.6 Restrição R6: Meta de produção mínima

R6 é o piso comercial de volume ($\sum n_k L_k \geq V^{min}$), que garante que a solução ótima em margem também seja viável comercialmente. Controla o risco de subprodução, isto é, o de o modelo entregar uma carteira matematicamente ótima mas pequena demais para sustentar as metas do negócio.

Não é ativa no cenário-base ($V^{min} = 0$). Com um $V^{min}$ operacional, da ordem de R\$ 100–500 M, apertá-la pode tornar o LP infactível, sinalizando que R1 e R4 estão restritivas demais para o volume desejado e informando diretamente uma negociação entre as áreas comercial e de risco; relaxá-la devolve ao solver a liberdade de priorizar margem sobre volume.

### 2.7 Trade-offs econômicos explícitos

As restrições materializam dois trade-offs centrais da gestão de crédito, cada um com número dos dois lados:

- **Rentabilidade vs inadimplência** (R1): cada ponto percentual de apetite de risco vale ≈ R\$ 1,2 M/ano de retorno, contra a provisão e o capital regulatório sobre a inadimplência incremental.
- **Conversão vs risco** (R2): relaxar o freio de capacidade rende até R\$ 67,6 mil de retorno marginal por cluster e torna a oferta mais atrativa, contra o risco de superendividamento do cliente.

No cenário-base o modelo **pende para a segurança**: prefere abrir mão de retorno a piorar a qualidade da carteira vigente.

**Pró-ciclicidade.** Como R1 e R4 estão ancoradas na carteira *atual*, a política é estruturalmente pró-cíclica (Minsky: "a estabilidade gera instabilidade"). Geralmente, a inadimplência vigente é baixa, o teto afrouxa e o modelo concede mais limite justamente antes de uma virada de ciclo. O cenário de estresse já calculado confirma o risco: uma alta de Selic que reduz $CP_k$ em 10% e eleva $PD_k$ em 5% aperta R2 e R1 ao mesmo tempo e custa ≈ **−R\$ 4,3 M** de retorno (`§4.4`). A mitigação é um **teto dinâmico indexado ao ciclo** — ancorar $\overline{PD}_{fin}^{atual}$ em uma média de ciclo ou fator macro, e não no nível corrente, para que o apetite de risco não se expanda no pior momento.

## 3. Leitura Econômica das Decisões do Modelo

### 3.1 Que tipo de cliente recebe mais limite?

O cliente que recebe mais limite é aquele que combina **baixo risco calibrado, capacidade de pagamento comprovada e retorno líquido positivo por real de exposição**. Em termos operacionais, isso aparece em três sinais: $PD_k$ menor, $CP_k$ maior e multiplicador de alavancagem $m_k$ suficiente para permitir que R2 não estrangule o limite. Na solução por decis, o maior limite individual aparece em D1, com $PD_k = 0{,}156$, $CP_{p5} = \text{R\$ 800}$ e $L_1^* \approx \text{R\$ 258}$; depois o limite cai para D2 ($L_2^* = \text{R\$ 162{,}75}$), D3 ($\text{R\$ 135}$), D4 ($\text{R\$ 132{,}75}$), D5 ($\text{R\$ 106{,}84}$), D6 ($\text{R\$ 62{,}50}$) e D7 ($\text{R\$ 9{,}17}$), zerando em D8-D10 (`modelagem_matematica.md §4`).

O ponto econômico central é que o modelo não dá mais limite apenas para quem tem maior margem $c_k$. D4, por exemplo, tem o maior coeficiente unitário entre os decis atendidos ($c_k = 0{,}06323$), mas recebe menos limite que D1 porque sua capacidade de pagamento prudencial é menor e sua alavancagem é mais restrita. A decisão de "quanto" é governada principalmente por R2: na execução com 800 segmentos da safra M1, a restrição de capacidade de pagamento ficou ativa em 677 de 800 segmentos, e o limite recomendado teve correlação de 0,996 com o teto $m_k \cdot CP_k$ (`artigo.md §4.1`). Assim, o modelo favorece o cliente que **pode pagar**, não apenas o cliente que parece rentável.

Essa leitura revela o ICP (*Ideal Customer Profile*) implícito do modelo: correntistas elegíveis com PD calibrada abaixo do limiar de destruição de valor, capacidade de pagamento mensurável, score de crédito suficiente para sustentar alavancagem e propensão positiva à contratação. No recorte por decis, esse ICP corresponde a D1-D7; na execução completa de M1, ele se materializa em 382 de 800 segmentos com oferta efetiva, cobrindo 876.520 clientes, ou 47,7% dos elegíveis (`artigo.md §4.1`). D8-D10 ficam fora não por uma regra fixa de score, mas porque incluir esses perfis consome orçamento de risco e reduz o retorno esperado da carteira.

### 3.2 O modelo prioriza volume, margem ou segurança?
[Interpretar a partir dos resultados: a FO é margem-orientada, mas a solução é governada por segurança (R1/R4/R5) e tem piso de volume (R6). No cenário-base pende para seletividade.]

[Relacionar com a distribuição dos limites entre os clusters/decis e classificar a solução como agressiva, conservadora ou equilibrada.]

### 3.3 Há evidência de seleção adversa ou exclusão de perfis?
[Discutir a exclusão dos decis de PD mais alta (D8–D10 ficam sem oferta — racional pelo custo reduzido negativo, de até ≈ −R\$ 37,2 mil, mas é exclusão de perfis de maior risco/menor renda, com tensão de inclusão financeira).]

[Analisar o viés de seleção dos dados: a inadimplência observada (`over30mob3`) só existe para quem ativou, então a PD é calibrada sobre um público já filtrado pela régua atual — risco de perpetuar o viés vigente.]

### 3.4 O que o modelo está de fato decidindo?
[Traduzir a solução em decisão de carteira: o limite cai de ≈ R\$ 258 (D1) até ≈ R\$ 9 (D7) e zera de D8 a D10. Dizer quem entra, quem recebe mais, quem recebe menos e quem fica sem oferta.]

[Comparar com a política vigente (backtesting): confrontar o limite e a rentabilidade sugeridos com o `limite_ofertado` atual nas safras M1–M3 — o quanto a alocação muda, quais perfis ganham ou perdem limite e qual o ganho de retorno frente à régua de hoje. É a evidência mais forte de que o modelo decide melhor, não apenas diferente.]

[Fechar com a consequência econômica dessa escolha sobre carteira, risco e retorno.]

## 4. Implicações Estratégicas para o Banco Pan

### 4.1 O modelo é conservador, agressivo ou balanceado?
[Classificar (sugestão: balanceado com viés conservador) e provar com 2–3 números: FO agressiva, mas R1/R4 não pioram a carteira atual, R5 diversifica, R2 usa percentil 5 e $m_k$ prudente, e 3 de 10 decis ficam sem oferta.]

### 4.2 Em que contexto o modelo deveria ser utilizado?
[Definir o cenário recomendado: apoio a comitê e calibragem periódica (não decisão automatizada), em macro estável, com recalibração trimestral — o modelo qualifica a decisão do Analista de Estratégia de Crédito, não a substitui.]

[Ir além: propor um Índice de Pressão de Crédito (early-warning, na lógica do GSCPI) que sintetize drift de $\gamma_d$, % de dado faltante, distância dos clusters de fronteira ao zero e um fator macro (Selic), disparando reotimização — e definir no máximo 5 KPIs para o painel do comitê.]

### 4.3 Quais são os principais riscos estratégicos da adoção?
[Discutir riscos de adoção em nível executivo — distintos das ressalvas técnicas da Seção 6, que não devem ser repetidas aqui: excesso de conservadorismo no cenário-base (perda de receita e baixa aderência comercial); dependência de uma governança de recalibração disciplinada — se a revisão trimestral falhar, a política vira subótima sem aviso; dificuldade de explicar e defender a decisão em comitê e auditoria; fragilidade estratégica diante de virada de cenário macro (a leitura pró-cíclica da Seção 2.5); e excesso de confiança no resultado "ótimo" — o modelo qualifica, não substitui o decisor.]

### 4.4 O modelo deve ser implementado?
[Responder de forma objetiva e com justificativa econômica.]

[Se positiva, dizer em que condições (ex.: recalibração trimestral, LGD diferenciada por perfil, overlay de cenário macro, supervisão humana) e ancorar no ganho (≈ R\$ 16,4 M/ano com risco não superior ao atual) e no ROI de `entendimento_negocio.md §4.6`.]

[Se negativa ou parcial, explicar o que ainda precisa ser ajustado antes da adoção.]

## 5. Conclusão
[Fechar com uma síntese curta e forte.]

[Reforçar a principal contribuição econômica do modelo (decisão de limite ajustada ao risco e à capacidade de pagamento, rastreável e auditável).]

[Reforçar a principal limitação ou cuidado estratégico (calibração/dados e leitura pró-cíclica).]

## 6. Limitações e Cuidados
[LGD uniforme (0,80) para todos os perfis, distorcendo o retorno unitário entre decis.]

[Simplificação da capacidade de pagamento: 42–43% de `capacidade_pagamento` nula em M2/M3, substituída por proxy (`renda_estimada × 0,30`).]

[Calibração $\gamma_d$ extrapolada nos decis altos (D6–D10) por escassez de observações; sensível a drift entre safras.]

[Viés de seleção na inadimplência observada; abordagem por clusters (e LP contínuo em vez de MIP) em lugar de limite individual; e diferença entre simulação e produção.]

## 7. Referências
[Documentos internos: `modelagem_matematica.md` (função objetivo, restrições, análise de sensibilidade), `back-end.md`, `aplicacao.md` (resultados), `comparacao_simplex.md`, `entendimento_negocio.md`.]

[Fontes externas e do parceiro: TAPI Banco Pan; bases Parquet (safras M1–M3); DFP 2024; Instruções de Negócio I1–I4 (Kloeckner, 2026); FICO (2021), Experian (2024), Moody's Analytics (2020); Resolução CMN 4.966/2021.]
