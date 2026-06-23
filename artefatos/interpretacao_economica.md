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
[Analisar incentivos perversos estruturais da própria FO: ela é monótona crescente em $L_k$ — sozinha, "empurraria" o limite ao infinito (é cega ao risco; quem segura são as restrições); não desconta custo de capital nem funding; e embute miopia temporal (capta só 22 meses). As distorções que vêm de premissas/parâmetros (LGD uniforme etc.) ficam na Seção 6, para não repetir.]

[Indicar se a função objetivo favorece volume, margem ou segurança, e em que cenário isso é um problema.]

[Ir além: reler a FO sob a ótica de métricas de valor do cliente — ela maximiza margem de 22 meses, não o LTV. Um limite baixo demais frustra e gera churn (LTV perdido que a FO não enxerga); um alto demais gera superendividamento. Esboçar como uma FO madura incorporaria LTV − CAC líquido de churn.]

### 1.4 Leitura executiva da função objetivo
[Fechar com uma frase de negócio: o que o modelo está tentando fazer pela carteira, em linguagem de decisão executiva.]

## 2. Interpretação das Restrições como Políticas de Negócio

### 2.1 Restrição R1 — Teto de inadimplência financeira
[Política representada: o apetite de risco da instituição — a carteira otimizada não pode ter PD ponderada por exposição maior que a da carteira aprovada vigente.]

[Risco controlado: deterioração da qualidade financeira da carteira (risco ponderado pelo valor exposto).]

[Se relaxada: mais retorno, mais inadimplência e provisão. Ancorar no preço-sombra — cada ponto percentual adicional de tolerância vale ≈ R\$ 1,2 M/ano de retorno.]

[Se apertada: carteira mais sã, porém menos volume rentável e menor receita.]

### 2.2 Restrição R2 — Capacidade de pagamento (alavancagem diferenciada)
[Política representada: crédito responsável — o limite de cada perfil é amarrado à capacidade de pagamento ($L_k \leq m_k \cdot CP_k$), com alavancagem $m_k$ crescente no score.]

[Risco controlado: superendividamento individual e exposição além do que o cliente suporta — é o freio prudencial por cliente da carteira.]

[Impacto econômico de mudar a rigidez: é o maior gargalo de retorno marginal do modelo (preço-sombra de até ≈ R\$ 67,6 mil). Relaxar (elevar $m_k$ ou melhorar a medição de $CP_k$) aumenta retorno, mas deve ser lido junto de R1.]

### 2.3 Restrição R3 — Teto máximo de limite
[Política representada: teto absoluto definido pelo parceiro (R\$ 25 mil) — salvaguarda prudencial/operacional.]

[Risco controlado: exposição unitária extrema. Na prática quase nunca é ativa, porque R2 já limita os $L_k$ bem abaixo do teto; atua como rede de segurança.]

### 2.4 Demais restrições do modelo
[**R4 — Teto de inadimplência física (headcount):** controla a fração de clientes inadimplentes, independentemente do limite; protege custo de cobrança, reputação e compliance (CMN 4.966/2021). Apertar reduz a base atendida; relaxar aumenta clientes e custo operacional.]

[**R5 — Concentração máxima por cluster:** política de diversificação — nenhum perfil pode concentrar mais que $\alpha$ da exposição. Controla risco sistêmico/setorial. Relaxar eleva retorno mas fragiliza a carteira (preço-sombra de R5 em D1 ≈ 0,1052).]

[**R6 — Meta de produção mínima:** piso comercial de volume. Evita uma solução ótima em margem mas inviável comercialmente; se o LP fica infactível com $V^{min}$, isso sinaliza negociação entre as áreas comercial e de risco.]

### 2.5 Trade-offs econômicos explícitos
[Explicar, com número dos dois lados, os trade-offs que o modelo resolve: rentabilidade vs inadimplência (R1); conversão/atratividade vs risco (R2); escala vs precisão — servir ~1,8M elegíveis por clusters de limite único em vez do limite individual ótimo, inviável com ~1,8M variáveis; escala/volume vs seletividade (R6 vs R1/R4); e proteção/diversificação vs agressividade comercial (R5).]

[Indicar qual lado o modelo privilegia e em que condições isso é justificável.]

[Ir além: como R1 e R4 estão ancoradas na carteira *atual*, a política é pró-cíclica (Minsky — "a estabilidade gera instabilidade"): em bonança o teto afrouxa e o modelo concede mais justamente antes de uma virada de ciclo. Usar o cenário de estresse já calculado (Selic ↑ → R2 e R1 apertam, ≈ −R\$ 4,3 M no retorno) e propor um teto dinâmico indexado ao ciclo.]

## 3. Leitura Econômica das Decisões do Modelo

### 3.1 Que tipo de cliente recebe mais limite?
[Descrever o perfil favorecido: maior capacidade de pagamento, menor PD e score mais alto (que dá alavancagem $m_k$ maior). Explicar que a decisão de "quanto" é governada principalmente por R2, não pela FO pura — o modelo dá mais limite a quem comprovadamente pode pagar.]

[Ir além: tratar os clusters atendidos (decis D1–D7) como o ICP revelado pelo modelo e defini-lo explicitamente.]

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
