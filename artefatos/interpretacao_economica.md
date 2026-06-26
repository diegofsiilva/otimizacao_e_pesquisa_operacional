# Interpretação Econômica

## Sumário
Este documento interpreta o modelo de otimização sob a ótica econômica e estratégica do Banco Pan. A análise está organizada em quatro frentes: função objetivo, restrições como políticas de negócio, leitura econômica das decisões do modelo e implicações estratégicas para adoção. O foco não é descrever a matemática do modelo, mas traduzir o que ele decide e quais consequências econômicas essas decisões produzem.

## 1. Interpretação Econômica da Função Objetivo

Esta seção lê a função objetivo como uma decisão de negócio, não como uma equação. Antes de interpretar, vale fixar o objeto: a FO condensa o trade-off central do projeto (quanto limite dar a cada perfil para capturar receita sem assumir perda excessiva) em uma única expressão monetária que o otimizador maximiza (formulação completa em `modelagem_matematica.md §1.6`):

$$\max_{L_k}\; Z \;=\; \sum_{k=1}^{K} n_k \,\pi_k \,\Big(\underbrace{T\,\bar{u}\,t}_{\text{receita unitária}} \;-\; \underbrace{PD_k\,\gamma_{d(k)}\,\text{LGD}}_{\text{perda unitária}}\Big)\,L_k$$

Cada símbolo, e o que significa em termos de negócio:

- **$L_k$**: variável de decisão, o limite (R\$) ofertado a todos os clientes do segmento $k$ e que o modelo escolhe.
- **$k$, $K$**: cada um dos $K \geq 100$ segmentos (perfis) de clientes elegíveis.
- **$n_k$**: número de clientes no segmento; dá a cada perfil peso proporcional ao seu tamanho.
- **$\pi_k$**: propensão à contratação (0 a 1), a chance de o cliente aceitar a oferta; pondera receita e perda, que só ocorrem se ele contratar.
- **$T = 22$ meses**: horizonte de uso do limite.
- **$\bar{u} = 0{,}75$**: utilização, a fração do limite efetivamente gasta (75%).
- **$t = 0{,}0175$**: taxa de interchange, o que o banco ganha por real transacionado (1,75%).
- **$PD_k$**: probabilidade de default do perfil.
- **$\gamma_{d(k)}$**: fator que calibra a PD do scoring ao default efetivamente observado, por decil de risco.
- **$\text{LGD} = 0{,}80$**: *Loss Given Default*, a fração perdida em caso de default (recupera-se ~20%).
- **$c_k = \pi_k\,(T\bar{u}t - PD_k\gamma_{d(k)}\,\text{LGD})$**: retorno líquido por real de limite no segmento, o "spread de risco" do perfil e o que de fato orienta a decisão.

### 1.1 O que a função objetivo representa economicamente?
A função objetivo escolhe os limites que maximizam o **retorno líquido esperado da carteira** de cartão pré-aprovado: a receita de interchange que o banco ganha sobre o volume transacionado, menos a perda esperada quando o cliente entra em default. Não é maximizar receita bruta nem minimizar risco, e sim **margem ajustada à perda esperada**. Como o produto é mono-produto, receita e risco moram no mesmo lugar: o limite. Tanto a receita quanto a perda só se concretizam se o cliente aceitar a oferta, por isso entram ponderadas pela propensão à contratação $\pi_k$: a FO é, no fundo, um valor esperado sobre a conversão.

A unidade econômica é **R\$ de retorno acumulado no horizonte de uso do limite (22 meses)**: como $L_k$ é um estoque rotativo (sem dimensão temporal), o ótimo $Z^*$ é o retorno da carteira nesse horizonte: ≈ R\$ 36,2 M no ótimo contínuo da safra M1, ou ≈ R\$ 32,9 M na carteira efetivamente recomendada após a discretização operacional (`artigo.md §4.1`). Na margem, cada real adicional de limite a um perfil rende o seu $c_k$.

### 1.2 Qual é a lógica de geração de valor?
O valor não vem de conceder mais crédito, e sim de **alocar melhor o limite entre perfis**. No lugar da régua fixa atual, o modelo direciona cada real para os segmentos de spread líquido positivo ($c_k > 0$) e o retira de onde destrói valor. É a lógica de **perda esperada (PD × LGD × exposição)** descontada da receita, a mesma adotada por FICO (2021), Experian (2024) e Moody's (2020) (`modelagem_matematica.md §1.1`). Na solução de referência da safra M1, isso aparece como retorno líquido positivo sobre uma exposição recomendada de ≈ R\$ 1,12 bilhão, sem deteriorar o risco agregado (`artigo.md §4.1`).

Os parâmetros se dividem em dois grupos quanto ao efeito no retorno:

- **Puxam a rentabilidade para cima:** a propensão $\pi_k$, a taxa de interchange $t$ (1,75%), o horizonte $T$ (22 meses) e a utilização $\bar{u}$ (75%).
- **Puxam para baixo:** a PD, a calibração $\gamma_d$ e a LGD (80%).

O ganho frente à política vigente é medido por backtesting (rentabilidade do `limite_ofertado` atual contra o limite otimizado nas safras M1–M3), e é aí que se comprova geração de valor, não apenas números diferentes.

### 1.3 Quais distorções econômicas a função objetivo pode induzir?
A própria forma da FO embute incentivos que **as restrições precisam disciplinar**. Ela considera risco via perda esperada, mas não é uma função de utilidade prudencial completa; por isso, o "ótimo" financeiro pode divergir do ótimo estratégico se as políticas de risco forem mal calibradas.

- **Linearidade e exposição máxima.** Como o retorno cresce linearmente com $L_k$ sempre que $c_k > 0$, a FO empurra cada segmento rentável até algum teto. Sem R1, R2, R3 e diversificação, a solução natural seria maximizar exposição nos perfis de maior retorno marginal, mesmo que isso elevasse concentração, capital consumido ou fragilidade em cenário adverso.
- **Risco médio, não risco de cauda.** A perda esperada penaliza $PD \times LGD$, mas não captura volatilidade, correlação entre defaults, stress macroeconômico nem perda extrema. Dois segmentos com mesmo retorno esperado podem ter riscos de cauda muito diferentes, e a FO atual os trataria como equivalentes se $c_k$ fosse igual.
- **Margem acima de estratégia comercial.** Por maximizar $c_k$ por real, tende a concentrar nos perfis mais rentáveis e a excluir perfis de maior PD. Numa base elegível cuja PD média é 0,197, isso protege margem, mas pode reduzir inclusão financeira e limitar objetivos comerciais de aquisição.

Há ainda **duas simplificações que as restrições não corrigem**, e que mudariam não o valor de $Z$, mas *quem* recebe limite:

- **Custo de capital (RAROC).** Cada real de limite consome capital regulatório (ativo ponderado pelo risco, sob Basileia), e a FO não o desconta. O objetivo economicamente correto seria o retorno sobre o capital alocado (RAROC), e não o retorno bruto: por essa ótica, um segmento de margem alta porém PD alta, que prende muito capital, vale menos do que a FO atual sugere.
- **Horizonte (LTV).** A margem de interchange de 22 meses é uma fatia do LTV. Como ignora CAC e churn (um limite baixo demais frustra e empurra ao concorrente; um alto demais superendivida), a FO supervaloriza perfis de margem alta agora porém churn alto e subvaloriza os de margem fina mas fiéis. Um objetivo em LTV − CAC líquido de churn deslocaria limite para quem vale mais ao longo do tempo (Instrução 3).

Nenhuma das duas invalida a FO atual: ela é uma v1 deliberadamente simples (tudo em R\$, na mesma unidade, auditável), e essas são a sua evolução natural. As distorções que vêm de premissas/parâmetros (como a LGD uniforme) estão na Seção 6.

### 1.4 Leitura executiva da função objetivo
O modelo transforma a definição de limite de uma regra fixa em uma **otimização de margem ajustada ao risco**: aloca cada real de limite onde ele rende mais, líquido de perda esperada, sem piorar o risco da carteira, qualificando a decisão do analista de crédito em vez de substituí-la.

## 2. Interpretação das Restrições como Políticas de Negócio

Cada restrição traduz uma política de crédito do Banco Pan em um corte no espaço de soluções factíveis. O modelo implementado tem três restrições no LP, R1 (teto de inadimplência financeira), R2 (capacidade de pagamento) e R3 (teto operacional), além da não-negatividade, e uma regra de diversificação verificada após a otimização (`artigo.md §2.3`). Para cada uma respondemos três perguntas: qual política representa, qual risco controla e o que acontece economicamente se for relaxada ou apertada. As respostas se apoiam na execução do pipeline sobre a base real da safra M1, com 1.836.085 clientes elegíveis agregados em 800 segmentos (`artigo.md §4.1`).

### 2.1 Restrição R1: Teto de inadimplência financeira

R1 representa o apetite de risco financeiro da instituição: a carteira otimizada não pode ter PD ponderada pela exposição ($\sum n_k PD_k L_k / \sum n_k L_k$) acima do teto $\overline{PD}_{fin}^{atual}$, calculado como a inadimplência da base elegível vigente. O risco que ela controla é a deterioração da qualidade financeira da carteira ponderada pelo valor exposto: diferentemente de contar clientes inadimplentes, R1 pesa cada default pelo limite em risco e captura a perda esperada em reais.

Na solução, R1 fica com folga: a PD ponderada da carteira otimizada é 0,067, bem abaixo do teto de 0,197 (`artigo.md §4.1`). Ela não morde porque a própria função objetivo já elimina parte do risco que destrói valor, antes que o teto agregado precise atuar: no resultado reportado no artigo, o coeficiente $c_k$ fica negativo quando a PD calibrada efetiva ultrapassa 0,361, e 123 dos 800 segmentos caíram nessa faixa e receberam limite zero naturalmente. A consequência econômica é que relaxar R1 hoje não rende nada, porque ela não está limitando a solução; apertá-la teria efeito só se descesse abaixo de 0,067, ponto em que passaria a forçar a saída dos segmentos rentáveis mas de maior PD, reduzindo retorno em troca de uma carteira ainda mais conservadora.

### 2.2 Restrição R2: Capacidade de pagamento (alavancagem diferenciada)

R2 traduz a política de crédito responsável: o limite de cada perfil é amarrado à capacidade de pagamento ($L_k \leq m_k \cdot CP_k$), com a alavancagem $m_k$ crescente no score e $CP_k$ medido no percentil 5, uma escolha prudencial sobre a média. O risco controlado é o superendividamento individual, isto é, conceder acima do que o cliente comprovadamente sustenta, causa-raiz do default no nível do cliente. É o freio prudencial por cliente da carteira.

É a restrição que de fato governa a solução: fica ativa em 677 dos 800 segmentos, e nos segmentos rentáveis o limite recomendado coincide com o teto $m_k \cdot CP_k$ (correlação de 0,996), confirmando que é a capacidade de pagamento, e não o teto de risco agregado, que define quanto cada perfil recebe (`artigo.md §4.1`). Por isso é também a alavanca de maior retorno: relaxá-la, elevando $m_k$ ou medindo melhor $CP_k$, é o que mais aumenta o retorno da carteira; apertá-la reduz diretamente o limite por perfil. Há aqui uma fragilidade do próprio modelo: 42–43% dos registros em M2/M3 têm `capacidade_pagamento` nula e usam o proxy `renda_estimada × 0,30` (Seção 6 deste documento), de modo que o gargalo mais caro do modelo repousa sobre uma medição imperfeita.

### 2.3 Restrição R3: Teto máximo de limite

R3 é o teto absoluto definido pelo parceiro ($L^{max} = \text{R\$ 25 mil}$), uma salvaguarda prudencial e operacional que controla a exposição unitária extrema e funciona como rede de segurança caso R2 falhe ou seja mal calibrada.

Na prática, nenhum segmento atinge o teto (`artigo.md §4.1`): R2 já limita os limites à casa das centenas de reais (limite médio recomendado de R\$ 607 por cliente), bem abaixo dos R\$ 25 mil. Relaxá-la ou apertá-la não altera a solução; só passaria a morder num cenário hipotético de R2 muito frouxa.

### 2.4 Regra de concentração (pós-otimização)

A diversificação da carteira é tratada como uma regra de pós-otimização, e não como restrição do LP: por incidir sobre os limites já discretizados, ela é verificada após a otimização (`artigo.md §2.3`). A diretriz é que nenhum segmento concentre mais que $\alpha = 5\%$ da exposição total. A política que ela representa é a de evitar uma carteira rentável porém dependente de um único perfil, vulnerável a choques setoriais ou regionais que atinjam justamente aquele segmento.

Na solução da M1, a concentração máxima de um segmento ficou em 3,6%, dentro do limite de 5%, então a regra não precisou ser acionada (`artigo.md §4.1`). Caso fosse violada, a abordagem do pipeline é sinalizar para revisão de parâmetros e reexecução, mantendo o LP estritamente linear. Apertar $\alpha$ forçaria mais dispersão e protegeria contra choques; afrouxá-lo permitiria carteiras mais concentradas e potencialmente mais rentáveis, ao custo de diversificação.

### 2.5 Trade-offs econômicos explícitos

A solução expõe dois trade-offs centrais da gestão de crédito, e a leitura econômica importante é que apenas um deles está ativo hoje:

- **Conversão vs risco** (R2): é o trade-off que governa a solução. O limite atrelado à capacidade de pagamento contém o superendividamento, mas é também o que mais segura o retorno; relaxá-lo aumentaria limite, conversão e receita, ao custo de mais risco por cliente. Por estar ativo em 677 de 800 segmentos, é aqui que mora o retorno marginal do modelo.
- **Rentabilidade vs inadimplência** (R1): é o trade-off latente. O teto de risco existe, mas hoje não morde, porque a própria função objetivo já descarta os segmentos que destroem valor (PD calibrada efetiva acima de 0,361). Só voltaria a ser tensão se o apetite de risco fosse apertado abaixo da PD atual da carteira (0,067) ou se o perfil de risco da base piorasse.
- **Escala vs precisão** (segmentação): é o trade-off estrutural da escolha por clusters. Agrupar clientes permite resolver milhões de casos com rastreabilidade e custo computacional viável, mas sacrifica precisão individual: todos os clientes de um mesmo segmento recebem o mesmo limite, mesmo que haja diferenças internas de renda, propensão e risco. O banco ganha escala operacional e auditabilidade, mas perde ajuste fino na concessão.

No conjunto, o modelo pende para a segurança: amplia a cobertura, mas mantém o risco agregado abaixo do teto e subordina cada limite à capacidade de pagamento.

**Pró-ciclicidade.** Como o teto de R1 é ancorado na inadimplência da carteira *vigente*, a política é estruturalmente pró-cíclica (Minsky: "a estabilidade gera instabilidade"): em bonança, a inadimplência observada é baixa, o teto afrouxa e o modelo se autoriza a conceder mais justamente antes de uma virada de ciclo. O próprio backtest evidencia que o teto flutua com a carteira, subindo de 0,197 na M1 para 0,209 na M3 (`artigo.md §4.3`). A mitigação é um teto dinâmico indexado ao ciclo: ancorar $\overline{PD}_{fin}^{atual}$ em uma média de ciclo ou fator macro, e não no nível corrente, para que o apetite de risco não se expanda no pior momento.

## 3. Leitura Econômica das Decisões do Modelo

### 3.1 Que tipo de cliente recebe mais limite?

O perfil que recebe maior limite é aquele que combina **baixo risco calibrado, capacidade de pagamento observável e retorno líquido positivo por real de exposição**. Em termos operacionais, essa combinação se expressa em três variáveis: menor $PD_k$, maior $CP_k$ e multiplicador de alavancagem $m_k$ compatível com a política prudencial de R2. O limite médio recomendado é de R\$ 607 por cliente elegível, subindo para cerca de R\$ 1.272 entre os que efetivamente recebem oferta (`artigo.md §4.1`). A Figura 3 do artigo mostra o padrão: tanto a política vigente quanto o modelo reduzem o limite à medida que o risco do perfil aumenta, mas o modelo diferencia de forma mais acentuada, ampliando o limite sobretudo nos decis de risco baixo e intermediário (D3 a D6) e mantendo limites contidos nos perfis de maior risco (`artigo.md §4.2`).

Essa distribuição mostra que a concessão não é determinada apenas pela margem unitária $c_k$. A decisão sobre o **valor** do limite é fortemente condicionada por R2: na execução com 800 segmentos da safra M1, a restrição de capacidade de pagamento ficou ativa em 677 segmentos, e o limite recomendado apresentou correlação de 0,996 com o teto $m_k \cdot CP_k$ (`artigo.md §4.1`). Em termos econômicos, o modelo favorece clientes com capacidade verificável de absorver a exposição, e não apenas perfis com maior retorno esperado.

Essa leitura permite inferir o ICP (*Ideal Customer Profile*) revelado pelo próprio modelo: correntistas elegíveis com PD calibrada efetiva abaixo do limiar de destruição de valor (0,361 no resultado reportado), capacidade de pagamento mensurável, score de crédito suficiente para sustentar alavancagem e propensão positiva à contratação. Na execução completa de M1, esse perfil se materializa em 382 de 800 segmentos com oferta efetiva, cobrindo 876.520 clientes, ou 47,7% dos elegíveis (`artigo.md §4.1`). Os segmentos acima do limiar de risco ficam fora não por uma regra fixa de score, mas porque sua inclusão consumiria orçamento de risco e reduziria o retorno esperado da carteira: 123 dos 800 segmentos foram zerados pela própria otimização nessa faixa.

### 3.2 O modelo prioriza volume, margem ou segurança?

O modelo não prioriza volume bruto. Se esse fosse o critério dominante, a solução tenderia a ampliar a base atendida independentemente da qualidade do risco. O resultado observado indica o oposto: há expansão relevante de alcance, mas condicionada à viabilidade econômica da exposição e ao respeito ao teto de risco (`artigo.md §4.1-4.2`).

A função objetivo, por construção, é orientada por margem, pois maximiza o retorno líquido esperado da carteira: receita de interchange menos perda esperada. Essa orientação aparece no backtesting comparável da safra M1, sobre os mesmos 117.367 clientes já atendidos pela política vigente: o retorno líquido esperado sobe de R\$ 4,90 M para R\$ 5,06 M (+3,4%), enquanto a PD ponderada por exposição varia apenas de 0,0467 para 0,0486 (+0,2 p.p.) (`artigo.md §4.2`). Portanto, o ganho econômico decorre de uma realocação mais eficiente dos limites, e não de uma expansão indiscriminada da exposição.

Apesar disso, a solução final é governada por critérios de segurança. A principal evidência é R2: a capacidade de pagamento é a restrição que efetivamente limita a maior parte dos segmentos, enquanto o teto operacional não é atingido (`artigo.md §4.1`). Assim, a classificação mais adequada é **margem com postura defensiva**: o modelo busca retorno e amplia cobertura, mas subordina a concessão à capacidade de pagamento e ao risco calibrado.

### 3.3 Há evidência de seleção adversa ou exclusão de perfis?

Há evidência de **exclusão econômica deliberada** de perfis de maior risco. Os segmentos acima do limiar de rentabilidade recebem limite zero porque cada real adicional destruiria valor (`artigo.md §4.1`). Isso não é uma falha do modelo; é a consequência econômica de uma política que prioriza retorno líquido e qualidade de carteira.

Também há evidência de **seleção adversa potencial**: perfis mais arriscados podem ter alta propensão à contratação, então uma política guiada só por conversão tenderia a ofertar justamente para quem mais consome risco. O modelo mitiga esse mecanismo ao exigir que a propensão venha acompanhada de spread líquido positivo.

O risco estratégico é confundir exclusão econômica com neutralidade estatística. Como a inadimplência observada vem de uma base historicamente filtrada, os perfis de maior risco têm menos evidência empírica e podem carregar viés da política vigente. A resposta não deve ser forçar limite no produto tradicional, mas criar uma política complementar: limite educativo, produto garantido, régua gradual ou ações de redução de risco antes da elegibilidade ao cartão pré-aprovado.

## 4. Implicações Estratégicas para o Banco Pan

### 4.1 O modelo é conservador, agressivo ou balanceado?

O modelo adota uma **postura defensiva**, com expansão seletiva. Ele não é agressivo, porque não relaxa o crivo de risco para crescer; também não é puramente conservador, porque amplia a base atendida de forma relevante. A classificação mais precisa é: **balanceado na expansão e defensivo na política de risco**.

Essa leitura vem de três sinais econômicos já demonstrados nas seções anteriores:

- **Expande com filtro:** aumenta a cobertura frente à política vigente, mas preserva a qualidade de carteira.
- **Subordina crescimento à capacidade de pagamento:** R2 é o freio dominante, logo a concessão não cresce acima da capacidade estimada dos clientes.
- **Recusa risco que não se paga:** segmentos que destroem valor ficam sem oferta, mesmo que pudessem gerar volume ou conversão.

O contraponto é que a função objetivo, isolada, é agressiva no uso de exposição: todo segmento com retorno líquido positivo é levado até algum teto. A postura defensiva nasce do conjunto entre objetivo e restrições. Portanto, se R1 e R2 forem relaxadas sem governança, o mesmo motor pode migrar para uma política mais agressiva.

### 4.2 Em que contexto o modelo deveria ser utilizado?

O contexto certo é como ferramenta de apoio ao comitê de crédito, não como motor de decisão automatizada. O modelo deve gerar a recomendação de limites por perfil e a leitura de quais restrições estão de fato limitando a rentabilidade (no caso, R2), entregando isso ao Analista de Estratégia de Crédito, que valida, ajusta e leva ao comitê. A razão é econômica, não burocrática: o resultado "ótimo" depende de parâmetros calibrados sobre dados imperfeitos (capacidade de pagamento por proxy em 42–43% da base, $\gamma_d$ extrapolado nos perfis de maior risco), então tratá-lo como verdade automática transfere para a produção um risco que a supervisão humana absorve barato.

O regime de uso recomendado é macro relativamente estável e recalibração trimestral. A periodicidade não é arbitrária: ela acompanha a chegada de novas safras, que atualizam $\gamma_d$ e a capacidade de pagamento, mantendo a política aderente ao perfil de risco corrente da base. O backtest da M3 ilustra essa necessidade, já que o teto de risco e a PD da carteira se deslocam de uma safra para outra (`artigo.md §4.3`). Em janelas de instabilidade macro, o ciclo trimestral é insuficiente e a reotimização deve ser disparada por evento, não por calendário, pela razão de pró-ciclicidade discutida na Seção 2.5.

Indo além do solicitado, a forma madura de operacionalizar esse gatilho é um Índice de Pressão de Crédito, um indicador de *early-warning* na lógica do GSCPI, que sintetize em um único número o drift observado de $\gamma_d$ entre safras, o percentual de dado faltante em $CP_k$, a distância dos segmentos de fronteira ao limiar de rentabilidade (0,361) e um fator macro como a Selic. Quando o índice cruza um patamar, dispara a reotimização antes que a política vigente se torne subótima. Para o painel do comitê, bastam no máximo cinco KPIs: retorno líquido esperado da carteira, PD ponderada versus teto de R1, percentual de elegíveis com oferta, número de segmentos de fronteira próximos do zero e o próprio Índice de Pressão de Crédito.

### 4.3 Quais são os principais riscos estratégicos da adoção?
Os principais riscos estratégicos são de governança e uso gerencial, não de resolução matemática:

- **Risco comercial:** a postura defensiva pode ser lida como baixa ambição de crescimento, especialmente por áreas pressionadas por aquisição e ativação.
- **Risco de governança:** sem recalibração periódica, o modelo continua otimizando com parâmetros antigos e a degradação aparece tarde, já em perda ou auditoria.
- **Risco macroeconômico:** como o teto de risco se ancora na carteira vigente, o modelo pode se tornar pró-cíclico se não houver overlay de cenário.
- **Risco reputacional e regulatório:** excluir perfis por destruição de valor é economicamente defensável, mas precisa ser explicado como política de risco, não como exclusão arbitrária.
- **Risco de falsa precisão:** o resultado é ótimo dadas as premissas; tratá-lo como verdade automática transforma uma ferramenta de decisão em risco operacional.

### 4.4 O modelo deve ser implementado?
Sim, mas como **implementação assistida e condicionada**, não como motor automático de concessão. A justificativa econômica é clara: o backtesting comparável mostra mais retorno ao mesmo risco (Seção 3.2), e o caso de investimento fecha mesmo com premissas conservadoras: ROI de ~96% no primeiro ano, payback de ~12,5 meses e investimento de R\$ 625 mil, equivalente a ~0,07% do lucro ajustado anual do banco (`entendimento_negocio.md §4.6`). Vale distinguir as medidas: os ≈ R\$ 32,9 M são o retorno total da carteira otimizada no horizonte de 22 meses (`artigo.md §4.1`), enquanto o ROI parte do ganho incremental sobre a política vigente. O modelo ainda torna explícito qual restrição limita a rentabilidade, o que já é valor para o comitê de crédito.

Ainda assim, a recomendação não deve ser "trocar imediatamente o algoritmo vigente". O Banco Pan já possui uma política em operação, então a decisão correta é comparar os dois motores sob a mesma população, janela temporal e métrica de perda realizada. A adoção deve começar como camada de apoio: geração de cenários, leitura de restrições ativas e proposta de limites para validação humana.

A implementação só deveria avançar com quatro salvaguardas:

- **backtesting multissafra contra a política vigente;**
- **recalibração periódica de risco e capacidade de pagamento;**
- **overlay macroeconômico sobre o apetite de risco;**
- **aprovação humana nos segmentos de fronteira e nas exclusões de alto risco.**

Sem essas condições, a implementação deixa de ser uma decisão econômica disciplinada e vira uma aposta na estabilidade dos parâmetros. Com elas, a recomendação é favorável: usar o modelo como instrumento de decisão executiva, auditável e progressivamente incorporável à política de limites.

## 5. Conclusão

A contribuição econômica central do modelo é transformar a definição de limite de uma régua fixa em uma decisão de margem ajustada ao risco e à capacidade de pagamento, rastreável e auditável. Ele aloca cada real de limite onde rende mais líquido de perda esperada, amplia cobertura sem piorar a qualidade da carteira, e deixa explícito qual restrição limita a rentabilidade: a capacidade de pagamento. Não é um gerador de crédito mais agressivo, mas um instrumento que qualifica a decisão do comitê com números.

O cuidado estratégico que acompanha essa contribuição é igualmente claro: o resultado "ótimo" vale o que valem seus parâmetros. A calibração sobre dados imperfeitos (capacidade de pagamento por proxy, $\gamma_d$ extrapolado nos perfis de maior risco) e a ancoragem do teto de risco na carteira vigente tornam o modelo pró-cíclico e dependente de recalibração disciplinada. Implementá-lo como apoio à decisão, com revisão trimestral e overlay macro, captura o ganho; implementá-lo como verdade automática converte uma boa ferramenta em risco silencioso.

## 6. Limitações e Cuidados

A LGD é uniforme em 0,80 para todos os perfis. Como a perda em caso de default não varia entre segmentos, o retorno unitário $c_k$ fica distorcido: perfis que na prática recuperam mais (ou menos) do que 20% são avaliados pela mesma régua, e a ordenação de quem recebe limite herda esse erro. Uma LGD diferenciada por perfil é a evolução mais direta do modelo.

A capacidade de pagamento é parcialmente estimada. Em M2 e M3, 42–43% dos registros têm `capacidade_pagamento` nula e usam o proxy `renda_estimada × 0,30`. Como R2 é o gargalo mais caro do modelo (Seção 2.2), parte da decisão de maior impacto repousa sobre uma medição que subestima quem tem múltiplas fontes de renda e superestima quem já tem alto comprometimento.

A calibração $\gamma_d$ é extrapolada nos decis de maior risco por escassez de observações de default, e é sensível a drift entre safras. É um dos parâmetros de maior sensibilidade do modelo, o que reforça a necessidade do gatilho de recalibração discutido na Seção 4.2.

Há ainda três cuidados de natureza estrutural: o viés de seleção na inadimplência observada (`over30mob3` só existe para quem ativou, então a PD é calibrada sobre um público já filtrado pela régua atual); a abordagem por segmentos com LP contínuo, em vez de limite individual via MIP, que troca precisão por tratabilidade computacional; e a diferença esperada entre o resultado de simulação e o comportamento em produção, que só o backtesting com dados do parceiro fechará.

## 7. Referências

Documentos internos do projeto: `modelagem_matematica.md` (função objetivo, restrições e análise de sensibilidade), `artigo.md` (resultados das execuções M1), `entendimento_negocio.md` (análise financeira e ROI), `aplicacao.md`, `back-end.md` e `comparacao_simplex.md`.

Fontes do parceiro e externas: TAPI Banco Pan; bases Parquet das safras M1–M3; DFP 2024 do Banco Pan; Instruções de Negócio I1–I4 (Kloeckner, 2026); FICO (2021), Experian (2024) e Moody's Analytics (2020) para a metodologia de perda esperada e otimização de limite; e Resolução CMN nº 4.966/2021, sobre provisões para perdas esperadas associadas ao risco de crédito.
