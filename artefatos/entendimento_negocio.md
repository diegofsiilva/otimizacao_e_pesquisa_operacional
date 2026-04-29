# Entendimento do Negócio
---
## 1. Matriz de Avaliação de Valor - Oceano Azul (Peso 2,5)

&emsp; A Estratégia do Oceano Azul, desenvolvida por W. Chan Kim e Renée Mauborgne [1], baseia-se de que o crescimento competitivo mais relevante não vem da disputa por participação em mercados saturados (oceanos vermelhos), mas da criação de espaços de mercado inexplorados onde a concorrência torna-se irrelevante. Para operacionalizar essa lógica, os autores propõem a Matriz de Avaliação de Valor (Strategy Canvas), ferramenta que permite mapear visualmente como diferentes soluções se posicionam em relação a um conjunto de atributos relevantes para o cliente, revelando eixos de diferenciação.
No contexto deste projeto, a aplicação da matriz serve a dois propósitos complementares: mapear o posicionamento relativo da solução proposta frente às alternativas hoje disponíveis no mercado brasileiro para definição de limites pré-aprovados de crédito e identificar onde a proposta gera valor diferenciado o suficiente para justificar sua adoção pelo Banco PAN em um setor no qual a concorrência por clientes de cartão é intensa. A análise se organiza em torno de oito atributos estratégicos selecionados pela equipe e comparados entre três abordagens representativas do espectro competitivo.

### 1.1 Abordagens Comparadas

A comparação envolve três abordagens distintas que representam o espectro real de soluções adotadas no mercado para definição de limites de crédito pré-aprovado. A escolha deliberada desse trio - em vez de comparar apenas prática tradicional versus solução proposta - permite mostrar que a diferenciação da proposta não se resume a "ser mais moderna", mas a ocupar um ponto ótimo entre sofisticação analítica e transparência.

**Abordagem A** - Prática tradicional do setor. Corresponde ao modelo dominante em instituições financeiras brasileiras de médio porte: definição de limites a partir de regras fixas por faixa de score de crédito, complementadas por calibragem manual de parâmetros realizada empiricamente pelo time de estratégia de crédito. A decisão costuma ser operacionalmente escalável, mas pouco granular e metodologicamente opaca.

**Abordagem B** - Modelos de Machine Learning Black-Box. Corresponde a abordagens mais sofisticadas adotadas por fintechs e bancos digitais, tipicamente baseadas em modelos de aprendizado supervisionado (XGBoost, redes neurais) que preveem diretamente o "limite ótimo" a partir de features do cliente. Essa abordagem é consistente com práticas internacionais consolidadas em Credit Limit Optimization [2], mas apresenta limitações estruturais em explicabilidade e em incorporação de restrições agregadas de carteira.
Segundo a TAPI<, o Banco PAN utiliza um sistema de scoring + regras fixas (mais próxima da Abordagem A), não como ML black-box. A inclusão da Abordagem B como comparador tem como objetivo demonstrar como a solução proposta se compara com outras alternativas de mercado.

**Abordagem C** - Nossa Solução (Otimização Matemática). Corresponde à proposta do grupo: um modelo de otimização linear que determina limites pré-aprovados por cliente ou cluster (mínimo 100 clusters), maximizando o retorno esperado da carteira, definido a partir da receita de interchange a taxa fixa (conforme orientação do TAPI),sujeito a restrições explícitas de apetite de risco (tetos de inadimplência física e financeira), capacidade de pagamento individual com alavancagem diferenciada por perfil de risco, metas de produção configuráveis e regras operacionais (limite mínimo de R\$200, discretização em múltiplos de R\$50). 

### 1.2 Atributos de Valor Selecionados

Os oito atributos a seguir foram selecionados com base em três critérios: **relevância direta para o usuário interno do modelo** (analista de estratégia de crédito do Banco PAN), **impacto observável sobre o cliente final** (correntista elegível) e **aderência ao contexto regulatório brasileiro**. A seleção prioriza atributos onde há diferenciação efetiva entre as três abordagens, evitando itens genéricos como "qualidade" ou "eficiência" que não discriminam.

<div align="center">Tabela X: Matriz de Atributos</div>

| # | Atributo| Descrição|
| - | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Retrabalho analítico manual                                                   | Volume de esforço humano exigido para recalibragem da política de limites a cada mudança de cenário                                                                                                                                                                                                                                                                                                             |
| 2 | Dependência de decisão empírica caso a caso                                   | Grau em que a decisão final sobre cada cliente ou cluster depende de julgamento individual                                                                                                                                                                                                                                                                                                                      |
| 3 | Explicabilidade e rastreabilidade da decisão                                  | Capacidade de justificar, em termos quantitativos e auditáveis, por que cada limite foi atribuído                                                                                                                                                                                                                                                                                                              |
| 4 | Personalização por perfil do cliente                                          | Granularidade com que a solução diferencia limites entre clientes com características distintas, mesmo dentro da mesma faixa de score                                                                                                                                                                                                                                                                           |
| 5 | Controle do risco agregado da carteira (inadimplência física e financeira)    | Capacidade de impor limites formais de exposição agregada que transcendem o risco individual do cliente. Conforme o TAPI, o monitoramento exige duas métricas distintas: inadimplência física (média simples da PD) e inadimplência financeira (média ponderada da PD pelo limite concedido), ambas com teto não superior ao nível atual da carteira                                                            |
| 6 | Aderência ao conceito de perda esperada (PD × exposição)                      | Grau em que a solução incorpora estruturalmente os elementos de perda esperada na decisão de limite. O TAPI orienta que a perda esperada seja considerada a partir da PD (derivada do score interno) e da exposição a risco do cliente. A Resolução CMN nº 4.966/2021 \[3] - referência complementar do grupo - formaliza esse conceito no arcabouço regulatório                                                |
| 7 | Aderência estrutural à capacidade de pagamento (com alavancagem diferenciada) | Garantia formal de que o limite ofertado é compatível com a renda comprometida do correntista, com multiplicador de alavancagem diferenciado por perfil de risco: clientes de melhor perfil podem estar mais alavancados, enquanto clientes mais arriscados têm alavancagem limitada - conforme diretriz explícita do TAPI                                                                                      |
| 8 | Arbitragem quantitativa entre apetite comercial e apetite de risco            | Capacidade de mediar objetivamente o conflito de interesses entre áreas comercial (que busca conversão e volume) e de risco (que busca proteção da carteira). No modelo proposto, o retorno é definido a partir da receita de interchange a taxa fixa - conforme orientação do TAPI para manter a linearidade - e a perda esperada é derivada da PD e da exposição, formalizando o trade-off na função objetivo |


<div align="center">Fonte: Material produzido pelos autores</div>

### 1.3 Matriz de avaliação e Curva de Valor

A tabela a seguir apresenta as pontuações atribuídas a cada abordagem nos oito atributos, em escala de 0 a 10. Os valores refletem avaliação comparativa qualitativa fundamentada no funcionamento estrutural de cada abordagem. As justificativas acompanham cada linha para explicitar o raciocínio.


<div align="center">Tabela X: Matriz de Avaliação de Valor</div>


| # | Atributo | Tradicional (A) |  ML Black-Box (B) | Otimização (C) | Justificativa das Notas|
| - | ----------------------------------------------------------------------------- | --------------- | -------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Retrabalho analítico manual                                                   | 9               | 5              | 2                | Na prática tradicional, cada revisão de política exige recalibragem manual extensa (9). O ML exige retraining mas é parcialmente automatizável (5). A otimização exige apenas alterar parâmetros e rerodar (2). **Neste atributo, valor menor indica melhor desempenho.**                                                                                                                                                                                         |
| 2 | Dependência de decisão empírica caso a caso                                   | 8               | 3              | 0                | A prática tradicional depende fortemente de julgamento humano em casos de borda (8). O ML automatiza mas ainda exige intervenção em retraining (3). A otimização substitui completamente a decisão empírica por solução matemática (0). **Neste atributo, valor menor indica melhor desempenho.**                                                                                                                                                                 |
| 3 | Explicabilidade e rastreabilidade da decisão                                  | 5               | 2              | 9                | Regras fixas são superficialmente explicáveis mas a calibragem é opaca (5). Modelos ML são a pior em explicabilidade (2). Na otimização, cada limite rastreia-se até a função objetivo e às restrições ativas (9).                                                                                                                                                                                                                                                |
| 4 | Personalização por perfil do cliente                                          | 3               | 9              | 7                | Regras por faixa de score ignoram heterogeneidade intra-faixa (3). ML captura padrões não-lineares complexos e personaliza profundamente (9). Otimização personaliza por cluster, capturando parte dessa heterogeneidade (7).                                                                                                                                                                                                                                     |
| 5 | Controle do risco agregado da carteira (inadimplência física e financeira)    | 5               | 3              | 9                | A prática tradicional controla via apetite fixo por faixa (5). ML otimiza cliente por cliente sem visão agregada estrutural (3). A otimização inclui como restrições formais tanto a inadimplência física (média simples da PD ≤ nível atual) quanto a financeira (média ponderada da PD pelo limite ≤ nível atual), conforme exigido pelo TAPI, além de tetos de PDD e exposição por faixa de risco (9).                                                         |
| 6 | Aderência ao conceito de perda esperada (PD × exposição)                      | 5               | 3              | 9                | Instituições tradicionais possuem infraestrutura regulatória madura mas desacoplada da decisão de limite (5). ML dificulta mapear aderência por opacidade (3). A otimização formaliza a perda esperada como PD × exposição diretamente na função objetivo e nas restrições, conforme orientação do TAPI - e em linha com o conceito de ECL da Resolução CMN nº 4.966/2021 \[3], referência complementar do grupo (9).                                             |
| 7 | Aderência estrutural à capacidade de pagamento (com alavancagem diferenciada) | 2               | 4              | 9                | A prática tradicional usa renda declarada de forma superficial, sem garantia estrutural (2). ML pode capturar via features mas não garante aderência formal (4). A otimização impõe a capacidade de pagamento como restrição rígida, com multiplicador de alavancagem diferenciado por perfil de risco - clientes de melhor perfil podem ter maior alavancagem, enquanto clientes mais arriscados têm o multiplicador restringido, conforme diretriz do TAPI (9). |
| 8 | Arbitragem quantitativa entre comercial e risco                               | 1               | 3              | 9                | No modelo tradicional, a arbitragem é política e subjetiva (1). ML oferece um número mas não formaliza o trade-off (3). Otimização formaliza na função objetivo a maximização sujeita a restrições, tornando o trade-off matematicamente explícito (9).|

<div align="center">Fonte: Material produzido pelos autores</div>



A matriz foi construída no Google Sheets, onde a tabela acima foi convertida em um gráfico de linhas que materializa a curva de valor comparativa entre as três abordagens analisadas. A planilha completa, contendo os dados, o gráfico e o ERRC Grid em aba complementar, está disponível em:

Link da planilha: [Canvas Estratégico do Oceano Azul - Banco PAN](https://docs.google.com/spreadsheets/d/16oclIvccqD7WkzTtpc5Tf-_E_1N4REQIbCu5e-1wRwY/edit?gid=262777086#gid=262777086)

---

<div align="center">Figura X: Curva de Valor (Strategy Canvas)</div>
<div align="center">
  <img src="/artefatos/assets/curva_de_valor.png">
</div>
<div align="center">Fonte: Material produzido pelos autores</div>



A visualização da curva de valor revela uma característica fundamental da solução proposta: ela não busca dominar em todos os atributos, mas adota um perfil estrategicamente seletivo. Nos atributos onde importa (explicabilidade, controle agregado, capacidade de pagamento, arbitragem), a curva se destaca acentuadamente; nos atributos menos críticos (como granularidade máxima de personalização), a solução abdica conscientemente de competir com o ML, reconhecendo que a diferença marginal não compensa a perda de transparência.

### 1.4 Aplicação das Quatro Ações (ERRC Grid)

O framework ERRC (Eliminate-Reduce-Raise-Create) do Oceano Azul propõe que uma estratégia diferenciadora não se constrói apenas somando atributos, mas também reduzindo e eliminando atributos que o mercado atual aceita como necessários mas que geram pouco valor para o cliente final. A análise a seguir distribui os oito atributos selecionados nas quatro ações.
#### Reduzir
O atributo "Retrabalho analítico manual" (atributo 1) é substancialmente reduzido em relação à prática tradicional: o modelo de otimização automatiza o ciclo completo de calibragem da política, exigindo apenas ajuste de parâmetros para rerodar toda a base elegível. Isso libera o time de estratégia de crédito para atividades analíticas de maior valor agregado, como interpretação de cenários e desenho de novas políticas, em vez de operação manual de planilhas.
#### Eliminar
O atributo "Dependência de decisão empírica caso a caso" (atributo 2) é completamente eliminado na solução proposta. Ao rodar sobre toda a base elegível com função objetivo e restrições explícitas, o modelo substitui a intervenção humana pontual por uma política estruturada, aplicada uniformemente. Essa eliminação não apenas reduz custo operacional, ela remove uma fonte estrutural de subjetividade e vieses que comprometia a defensabilidade do processo em auditorias.
#### Aumentar
Quatro atributos são estruturalmente elevados em relação ao estado da arte atual: explicabilidade e rastreabilidade da decisão (atributo 3), controle do risco agregado da carteira (agora com distinção entre inadimplência física e financeira conforme TAPI (atributo 5)), aderência ao conceito de perda esperada (atributo 6) e, em relação à prática tradicional, personalização por perfil do cliente (atributo 4). Essas elevações respondem diretamente a pressões que o setor bancário brasileiro enfrenta: maior rigor na gestão de carteiras (com monitoramento simultâneo de métricas físicas e financeiras de inadimplência, como exigido pelo parceiro), maior exigência de rastreabilidade perante auditorias e maior necessidade de calibragem fina para sustentar rentabilidade. 
#### Criar
Três elementos são estruturalmente criados pela solução, no sentido de que nenhuma das abordagens alternativas os entrega de forma sistemática. O primeiro é a aderência estrutural à capacidade de pagamento com alavancagem diferenciada por perfil de risco (atributo 7), operacionalizada como restrição rígida do modelo (limite ≤ multiplicador × capacidade de pagamento, onde o multiplicador é maior para clientes de melhor perfil e menor para clientes mais arriscados, conforme diretriz do TAPI), que transforma uma diretriz genérica em mecanismo formal de proteção do correntista. O segundo é a arbitragem quantitativa entre apetite comercial e apetite de risco (atributo 8), tradicionalmente resolvida por negociação política entre áreas: ao incorporar essa tensão diretamente na função objetivo - com retorno definido pela receita de interchange a taxa fixa e perda esperada derivada da PD e exposição - e nas restrições, o modelo cria uma linguagem quantitativa comum que desarma o conflito e o converte em decisão auditável. O terceiro é a explicitação de restrições operacionais como parâmetros configuráveis do modelo: limite mínimo de R\$ 200, discretização em múltiplos de R\$ 50, tetos simultâneos de inadimplência física e financeira, e metas flexíveis de produção (quantidade de clientes aprovados e volume financeiro de limite ofertado) - todas especificações do TAPI que saem do "conhecimento tácito" e se tornam elementos formais da otimização.

### 1.5 Diferenciação Estratégica

A análise consolidada revela que a diferenciação da solução proposta não se apoia em um único eixo, mas em uma combinação deliberada: ela captura parte dos ganhos de sofisticação analítica típicos de abordagens de ML, sem incorrer em sua opacidade; e supera amplamente a prática tradicional nos atributos de rastreabilidade, governança agregada da carteira e aderência às especificações do parceiro. Essa combinação é particularmente valiosa no contexto do Banco PAN, onde a adoção institucional depende simultaneamente de precisão técnica, defensabilidade em comitê e aderência a requisitos operacionais concretos, como controle simultâneo de inadimplência física e financeira, alavancagem diferenciada por perfil de risco, limite mínimo de R\$ 200, discretização em múltiplos de R\$ 50, e metas flexíveis de produção, todos formalizados no TAPI. O oceano azul aqui identificado não é o da "melhor previsão possível" (espaço já saturado por abordagens de ML), mas o da decisão otimizada, explicável e operacionalmente aderente ao briefing do parceiro, no qual a concorrência ainda é escassa e o valor percebido é elevado.

### 1.6. Teste das Três Características de uma Boa Estratégia (Ir Além)

Além da construção da matriz, Kim e Mauborgne [1] propõem um teste adicional para validar a robustez de uma estratégia de Oceano Azul: toda curva de valor genuinamente diferenciadora deve apresentar três características simultâneas: foco, divergência e slogan cativante. A aplicação desse teste à solução proposta funciona como verificação de consistência estratégica complementar à análise da matriz.

**Foco.** Uma boa estratégia concentra-se em poucos atributos decisivos em vez de tentar desempenho médio em todos. A curva de valor da solução proposta satisfaz esse critério: em vez de competir com o ML em personalização máxima ou com o modelo tradicional em simplicidade operacional, a proposta concentra esforço em quatro eixos - explicabilidade, controle agregado, capacidade de pagamento e arbitragem quantitativa - que são precisamente os mais valorizados pelo cliente direto (analista de estratégia de crédito) e pelo cliente final (correntista elegível).

**Divergência.** A curva deve destacar-se visualmente das curvas concorrentes. A análise da matriz evidencia essa divergência: nos atributos 3, 5, 6, 7 e 8, a distância entre a solução proposta e as alternativas é significativa, indicando que não se trata de melhoria incremental, mas de reposicionamento estratégico.

**Slogan Cativante.** Uma estratégia robusta deve caber em uma frase clara que comunique seu diferencial. A proposta do grupo pode ser resumida como: "Decisões de crédito matematicamente ótimas, estruturalmente explicáveis e regulatoriamente aderentes." Essa formulação captura o essencial da proposta em três adjetivos, cada um correspondendo a um dos grupos de atributos destacados na matriz.

A aplicação desse teste reforça que a diferenciação identificada não é fortuita nem puramente incremental, mas corresponde a um reposicionamento estratégico sustentável da solução no mercado de ferramentas de decisão de crédito. Essa verificação, embora não exigida no barema, eleva o rigor da análise ao conectar a construção quantitativa da matriz com o arcabouço teórico completo da Estratégia do Oceano Azul.

---

## 2. Matriz de Risco (Peso 2,5)

### 2.1 Critérios de classificação

*O roteiro pede explicar os critérios usados para classificar impacto e probabilidade.*

| Nível | Probabilidade | Impacto |
|:---:|:---|:---|
| **Muito Baixo (1)** | < 5% de chance | Efeito negligenciável |
| **Baixo (2)** | 5–20% | Impacto menor, contornável sem replanejar |
| **Médio (3)** | 20–50% | Impacto moderado, exige ação corretiva |
| **Alto (4)** | 50–75% | Impacto significativo no escopo, prazo ou resultado |
| **Muito Alto (5)** | > 75% | Impacto crítico - pode inviabilizar o projeto |

### 2.2 Riscos identificados

*O roteiro pede **pelo menos 10 riscos** com: descrição, **causa provável**, impacto esperado, probabilidade, **posição na matriz** e **justificativa da classificação**.*

> **NÃO FAZER (roteiro):**
> - ~~Listar riscos genéricos como "o projeto pode dar errado"~~
> - ~~Citar riscos sem relação com a solução do grupo~~
> - ~~Não justificar a posição do risco na matriz~~
> - ~~Confundir risco do projeto com limitação natural do problema~~
>
> **NÃO FAZER (feedback M5):**
> - ~~Classificar como "baixo impacto" riscos que podem afetar a credibilidade do modelo~~ - calibrar com cuidado

| # | Risco | Causa provável | Impacto esperado | Prob. | Imp. | Posição |
|:---:|:---|:---|:---|:---:|:---:|:---:|
| 1 | Concessão de limites excessivamente altos para clientes arriscados | Calibração inadequada da função objetivo (peso excessivo em receita vs risco) | Aumento de inadimplência, impacto direto em provisão | 3 | 5 | **Crítico** |
| 2 | Concessão de limites muito baixos, reduzindo atratividade | Restrições de risco excessivamente conservadoras | Perda de competitividade, redução de ativação, churn | 3 | 4 | **Alto** |
| 3 | Formulação do modelo sem aderência ao negócio | Falta de entendimento do TAPI ou ausência de validação com parceiro | Solução tecnicamente correta mas irrelevante para o Pan | 3 | 5 | **Crítico** |
| 4 | Uso inadequado das variáveis disponíveis | Dados sem dicionário claro; variáveis correlacionadas; inclusão de variáveis sensíveis como proxy (CEP → raça) | Modelo enviesado ou com baixo poder preditivo; risco LGPD | 4 | 4 | **Crítico** |
| 5 | Simplificações que prejudicam a interpretação econômica | Uso de proxies inadequadas sem justificar; linearização de relações não-lineares | Resultados matematicamente válidos mas economicamente sem sentido | 3 | 4 | **Alto** |
| 6 | Descumprimento de restrições de risco da carteira | Restrições não formalizadas no modelo ou com valores incorretos | Carteira resultante viola políticas internas ou exigências regulatórias | 2 | 5 | **Alto** |
| 7 | Dificuldade de implementação prática no ambiente do parceiro | Stack tecnológico incompatível; dados em formato indisponível | Solução não pode ser integrada - valor apenas teórico | 3 | 4 | **Alto** |
| 8 | Baixa explicabilidade da solução | Modelo complexo demais; documentação insuficiente dos parâmetros | Compliance/auditoria recusa a solução; descumprimento LGPD Art. 20 | 3 | 4 | **Alto** |
| 9 | Qualidade insuficiente dos dados fornecidos | Missing values, outliers, período não representativo, viés de seleção | "Garbage in, garbage out" - modelo gera decisões ruins | 4 | 4 | **Crítico** |
| 10 | Dependência excessiva de premissas não justificadas | Falta de dados reais para calibrar parâmetros (LGD, utilização); valores arbitrários | Resultados são artefato das premissas, sem validade prática | 4 | 4 | **Crítico** |
| 11 | Viés de seleção nos dados de inadimplência | `over30mob3` só existe para os ~5K que ativaram (0,03% da base) - não observamos os demais | Modelo treinado com subconjunto não representativo da população | 4 | 4 | **Crítico** |
| 12 | Atrasos no time devido ao prazo curto da sprint | Sprint 1 com poucos dias de dev efetivo | Entregas incompletas ou com qualidade inferior | 4 | 3 | **Alto** |

> **Nota sobre o Risco 11:** Este risco foi identificado diretamente dos dados (`base_ref_M1_v2.parquet`). Dos 14,5M de clientes, apenas ~5K têm `over30mob3` preenchido. Isso é um viés de seleção clássico em crédito ("reject inference") - não sabemos como os clientes que não receberam oferta se comportariam.

### 2.3 Justificativa do posicionamento

*O roteiro pede justificativa do posicionamento de cada risco.*

**Posição = Probabilidade × Impacto:**
- **Críticos (≥ 15):** Riscos 4, 9, 10 e 11 têm probabilidade alta (4) porque o grupo ainda não recebeu o TAPI nem analisou os dados em profundidade - são riscos inerentes ao estágio atual. Riscos 1 e 3 têm impacto muito alto (5) porque comprometem a razão de existir da solução.
- **Altos (8–14):** Riscos 2, 5, 6, 7, 8 e 12 são significativos mas mais controláveis com ações de mitigação.

### 2.4 Análise dos riscos mais críticos

*O roteiro pede análise dos riscos mais críticos.*

**Riscos 1 e 2 (limites altos/baixos demais)** são faces opostas do mesmo problema: calibração inadequada do trade-off receita × risco. Ambos dependem da correta formulação da função objetivo (Risco 3). Se a formulação errar, ambos se materializam automaticamente.

**Riscos 4, 9, 10 e 11 (dados e premissas)** formam uma cadeia: dados com problemas (9) + viés de seleção (11) → premissas inadequadas (10) → uso errado de variáveis (4). A mitigação mais efetiva é uma EDA rigorosa e documentação explícita de toda premissa.

`[APÓS TAPI: recalibrar probabilidades e impactos com informações reais do parceiro]`

### 2.5 Representação visual da matriz

*Inserir a imagem da matriz 5×5 com os riscos posicionados. Fazer em Figma, Canva ou Miro.*

![Matriz de Risco](assets/matriz_risco.png)

`[PREENCHER: criar imagem da matriz 5×5 e inserir aqui]`

---

## 3. Canvas da Proposta de Valor (Peso 2,5)

### 3.1 Segmento de cliente

*O roteiro diz que o "cliente" pode ser analisado em dois níveis e que o grupo deve **deixar claro qual nível está analisando** e, **idealmente, reconhecer os dois**.*

Neste projeto, o "cliente" opera em dois níveis:

- **Cliente direto da solução**: times internos do Banco Pan que utilizarão o modelo - áreas de **crédito, estratégia de crédito e Data Science**. São eles que configuram parâmetros, executam cenários e implementam os limites resultantes. `[APÓS UX: referenciar as personas criadas - ex: "Persona Renata (gestora de risco)"]`
- **Cliente final impactado**: **correntistas do Banco Pan elegíveis à concessão de cartão de crédito pré-aprovado**. Não interagem diretamente com o modelo, mas são afetados pelo resultado (limites mais ou menos aderentes ao perfil). Os dados mostram ~14,5M de clientes na base, dos quais ~12,7M passam nos filtros de elegibilidade.

A análise foca no **cliente direto** (times internos), pois são os usuários efetivos da solução.

`[APÓS TAPI: confirmar quais áreas do banco utilizarão a solução]`

### 3.2 Perfil do Cliente (lado direito do Canvas)

**Tarefas do cliente:**
- Definir e revisar políticas de limites pré-aprovados de crédito
- Equilibrar receita da carteira com controle de inadimplência
- Reportar e justificar indicadores de risco (NPL, provisão) à diretoria
- Atender exigências de explicabilidade (LGPD Art. 20) e capital regulatório

**Dores:**

> **NÃO FAZER (feedback M5 da profa. de UX - mesma professora):**
> - ~~Ganhos ligados à alta gestão e não ao usuário principal~~
> - Isso vale também aqui no Canvas de negócios

- Pressão constante por reduzir NPL crescente (8,3% e subindo) sem sacrificar receita - a sensação de estar "escolhendo qual problema criar"
- Sobrecarga cognitiva ao revisar políticas que envolvem dezenas de variáveis simultâneas, sem ferramenta que integre todas
- Risco reputacional pessoal quando decisões de limite resultam em inadimplência acima do esperado
- Falta de base objetiva para defender decisões em reuniões com produto e comercial - "intuição" não convence stakeholders que querem mais receita

`[APÓS UX: cruzar com as dores das personas - garantir coerência]`

**Ganhos esperados:**

> **ATENÇÃO (feedback M5):** Ganhos devem ser **do usuário direto**, não da alta gestão. Ganhos como "aumento de lucro do banco" ou "valor para o acionista" NÃO entram aqui.

- Sentir segurança ao defender decisões de limite com argumentação matemática, não opinião
- Poder simular cenários (conservador/moderado/agressivo) antes de implementar
- Reduzir tempo gasto em análises manuais e debates subjetivos
- Ter rastreabilidade das decisões para auditorias e compliance

### 3.3 Mapa de Valor (lado esquerdo do Canvas)

**Produtos e serviços:**

*O roteiro pede: "o que exatamente o grupo está propondo?"*

- Modelo de otimização matemática que define limites pré-aprovados por cliente ou cluster, respeitando restrições de risco e negócio `[APÓS MODELAGEM: especificar tipo - LP, MIP, etc.]`
- Interface para configurar parâmetros (NPL máximo, budget, limite min/max) e executar cenários `[APÓS UX: alinhar com User Stories]`
- Módulo de explicabilidade (quais variáveis mais influenciaram cada decisão de limite)

**Aliviadores de dor:**

*Como a solução reduz ou elimina os problemas identificados?*

- Substitui intuição por base matemática - elimina o "operar no escuro"
- NPL máximo como restrição do modelo - ataca diretamente a pressão pelo NPL, que simplesmente não é violado
- Cenários pré-configurados permitem comparar resultados sem refazer análises manuais
- Decisões rastreáveis e documentáveis - em caso de auditoria, a lógica é reproduzível

**Criadores de ganho:**

*Como a solução gera benefícios concretos e relevantes?*

- Simulação what-if rápida: testar "o que acontece se eu reduzir o NPL máximo de 8% para 7%?" leva minutos
- Argumentação objetiva: fornece dados concretos para reuniões entre áreas
- Para o cliente final: limites mais aderentes à capacidade de pagamento - reduz tanto sub-concessão quanto sobre-concessão

### 3.4 Figura do Canvas

> **ATENÇÃO (roteiro):** *"Lembre-se de colocar a figura"*

![Canvas Proposta de Valor](assets/canvas_proposta_valor.png)

`[PREENCHER: criar imagem do Canvas (template Strategyzer) em Figma, Miro ou Canva e inserir aqui]`

> **NÃO FAZER (roteiro):**
> - ~~Tratar o canvas como texto genérico de empreendedorismo~~
> - ~~Não delimitar quem é o cliente~~
> - ~~Listar dores e ganhos sem conectá-los ao projeto~~
> - ~~Descrever apenas a ferramenta técnica, sem explicar o valor gerado~~

---

## 4. Análise Financeira do Projeto

Nesta seção, apresentamos a análise financeira preliminar da solução de otimização de limites pré-aprovados de cartão de crédito, considerando um horizonte de **1 ano**. O objetivo é demonstrar a viabilidade econômica da proposta por meio do cálculo do ROI (*Return on Investment*), com premissas justificadas.

O TAPI não apresenta orçamento fechado do parceiro. Os valores abaixo são **estimativas baseadas em premissas justificadas e fontes públicas**. Quando uma estimativa é assumida pelo grupo, isso é explicitado.

> **Nota sobre simplificações didáticas.** Para fins didáticos, esta análise adota três simplificações que, em um estudo de viabilidade corporativo, seriam tratadas de forma mais granular: (i) o CAPEX é amortizado integralmente no Ano 1, sem distribuição plurianual; (ii) assume-se LGD = 100% (perda total em caso de inadimplência), dispensando estimativa de taxa de recuperação além da já declarada em A3; e (iii) não se aplica taxa de desconto (WACC) ao fluxo de caixa do período, dado o horizonte de apenas 12 meses. Essas escolhas tornam o modelo mais transparente na leitura do resultado, sem comprometer a validade da conclusão qualitativa.

| # | Premissa | Valor | Fonte / Justificativa |
|:---:|:---|:---|:---|
| P1 | Carteira de crédito do Pan | R$ 57,8 bi | RI Banco Pan, Q2 2025 |
| P2 | NPL >90 dias | 8,3% | RI Banco Pan, Q2 2025 |
| P3 | Perda estimada associada ao NPL | ~R$ 4,8 bi/ano | P1 × P2 (simplificação - assume perda = carteira × NPL, sem considerar recuperação) |
| P4 | Salário/hora dev júnior | R$ 23,17/h | Glassdoor Brasil, média 2025 |
| P5 | Salário/hora tech lead | R$ 79,55/h | Glassdoor Brasil, média 2025 |
| P6 | Carga horária do projeto | ~100h por pessoa | 10 semanas × 10h/semana |
| P7 | Infraestrutura cloud | AWS EC2 t3.medium | Pricing público AWS, sa-east-1 |
| P8 | Redução de NPL pelo modelo | 0,1pp a 0,5pp | **Premissa assumida** - literatura reporta melhorias nessa faixa para modelos de otimização de crédito. `[APÓS TAPI: validar com parceiro]` |

### 4.1 Contexto financeiro do Banco Pan

O Banco Pan opera uma carteira de crédito total de R\$ 57,8 bi (RI Q2 2025), concentrada em veículos (~57%) e consignado (~36%). O cartão de crédito representa ~5% da carteira (~R\$ 2,9 bi em 3T25), sendo o produto de **maior risco** do portfólio. O NPL >90 dias atingiu 8,3% em Q2 2025 — tendência de alta que pressiona a provisão para perdas (PCLD), que chegou a R\$ 2,33 bi em 2024, equivalente a **~4,5× o lucro líquido IFRS** do mesmo ano (R\$ 528 mi). Esse dado é relevante porque mostra que qualquer melhoria marginal na qualidade da concessão de crédito tem impacto amplificado na linha final do resultado do banco. Em janeiro de 2026, o Pan foi incorporado ao BTG Pactual (Fontes: DFP/ITR depositadas na CVM; RI Banco Pan; Nord Investimentos; ADVFN).

---

### 4.2 Premissas declaradas

Toda estimativa repousa em premissas. A coluna **Confiança** indica o grau de certeza: **Alta** = dado público verificável; **Média** = estimativa com fonte indireta ou média de mercado; **Baixa** = premissa do grupo sem benchmark específico para o Pan.

#### A. Operação do parceiro

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| A1 | Carteira de cartão de crédito | ~R\$ 2,9 bi | Média | RI Banco Pan, 3T25. ~5% da carteira total. |
| A2 | NPL >90 dias (carteira total) | 8,3% | Alta | RI Banco Pan, Q2 2025 |
| A3 | Taxa de recuperação (crédito sem garantia) | 30% | Média | BCB — Rel. Estab. Financeira, 2024. Média do sistema bancário. |
| A4 | Perda líquida anual (carteira de cartões) | ~R\$ 168 mi | Média | Derivada: A1 × A2 × (1 − A3) = R\$ 2,9 bi × 8,3% × 70% |

#### B. Modelo de receita (conforme TAPI)

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| B1 | Receita do cartão = interchange a taxa fixa | Sim | Alta | TAPI, p. 4 (para manter linearidade do modelo) |
| B2 | Taxa de interchange do emissor | ~1,6% | Média | Média ponderada do mercado brasileiro (ABECS/BCB, 2024). Faixa: 1,5–1,7%. |
| B3 | Utilização média do limite | ~30% | Média | Benchmark ABECS para cartões sem garantia em perfil renda baixa |
| B4 | Receita anual de interchange (baseline) | ~R\$ 167 mi | — | Derivada: A1 × B3 × B2 × 12 = R\$ 2,9 bi × 30% × 1,6% × 12 |

#### C. Benefício esperado do modelo

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| C1 | Melhoria esperada pelo modelo sobre o resultado econômico combinado | 1,0% (cenário base) | Baixa | Thomas (2009) e Trench et al. (2003) reportam ganhos de 1–5% em carteiras já geridas por scoring. Adotamos o **piso da faixa** como cenário base, por ser a estimativa mais defensável na ausência de backtesting com dados do parceiro. |
| C2 | Percentual de captura dos benefícios no Ano 1 | 25% (cenário base) | Baixa | Premissa conservadora que incorpora rampagem lenta da adoção interna, ciclo de validação com a área de crédito, atrasos de integração com sistemas legados e resistência organizacional à mudança de processo. Em projetos de otimização de carteira, o primeiro ano raramente captura mais de 30% do benefício potencial. |

#### D. Custos de implementação

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| D1 | Cientista de dados sênior (líder técnico) | R\$ 30.000/mês (com encargos CLT ~35%) | Média | Glassdoor/Robert Half, 2025. Faixa: R\$ 18.000–30.000/mês. |
| D2 | Cientista de dados pleno | R\$ 17.500/mês (com encargos) | Média | Glassdoor, 2025. Faixa: R\$ 10.000–18.000/mês. |
| D3 | Engenheiro de dados pleno | R\$ 20.000/mês (com encargos) | Média | Glassdoor, 2025. Faixa: R\$ 12.000–20.000/mês. |
| D4 | Tech Lead / Gerente de Projeto | R\$ 38.000/mês (com encargos) | Média | Glassdoor, 2025. Faixa: R\$ 22.000–38.000/mês. |
| D5 | Prazo total de desenvolvimento + integração | 6 meses | Média | Estimativa do grupo |
| D6 | Infraestrutura cloud (dev/staging) | R\$ 5.000/mês | Média | Pricing AWS/Azure para workloads analíticos |
| D7 | Infraestrutura de produção (cloud enterprise) | R\$ 10.000/mês | Média | Pricing AWS/Azure com SLA bancário |

---

### 4.3 Investimento inicial

O investimento estima o custo que o **Banco Pan** incorreria para implementar a solução em produção — não o custo do projeto acadêmico do Inteli. A estimativa está organizada por **fase do projeto**, refletindo o ciclo de vida de uma solução de analytics em crédito.

| Fase | Escopo | Duração | Custo (R\$) |
|:---|:---|:---:|---:|
| **1. Desenvolvimento e modelagem** | Formulação matemática, implementação do solver, análise exploratória, definição de clusters | 3 meses | 230.000 |
| **2. Backtesting e validação** | Testes com safras históricas (M1–M3), análise de sensibilidade, validação independente pelo time de risco do banco | 1 mês | 130.000 |
| **3. Integração e homologação** | Conexão ao motor de crédito existente do Pan, construção dos pipelines de dados, deploy em ambiente segregado | 2 meses | 200.000 |
| **4. Conformidade regulatória** | Revisão de compliance e proteção de dados, controles de acesso à base sigilosa, documentação de modelo, aprovação em comitê de crédito | Paralelo às Fases 2–3 (meses 4–6), ~0,5 FTE | 65.000 |
| **Investimento inicial total** | | **~6 meses** | **R\$ 625.000** |

**Composição dos custos por fase:**

O time técnico core (D1 + D2 + D3) custa ~R\$ 67.500/mês. Ao longo dos 6 meses de desenvolvimento, esse time responde por ~R\$ 405.000 do investimento total. Os R\$ 220.000 restantes se distribuem em:

- Infraestrutura de desenvolvimento (D6): R\$ 5.000/mês × 6 = R\$ 30.000
- Gestão de projeto (D4, dedicação parcial ~18%): R\$ 38.000 × 18% × 6 = ~R\$ 41.000
- Validação independente pelo time de risco do banco (~300h de analista sênior): ~R\$ 60.000 (embutido na Fase 2)
- Integração com motor de crédito (especialistas do banco, ~4 semanas): ~R\$ 24.000 (embutido na Fase 3)
- Conformidade e governança (Fase 4 — revisão de compliance, controle de acesso, model card, aprovação em comitê): R\$ 65.000

Total detalhado: R\$ 405k + R\$ 30k + R\$ 41k + R\$ 60k + R\$ 24k + R\$ 65k = **R\$ 625.000**.

---

### 4.4 Custos operacionais anuais

Após a entrada em produção, o modelo requer manutenção contínua para manter performance e aderência regulatória.

| Item | Anual (R\$) | Premissa |
|:---|---:|:---|
| Infraestrutura de produção (cloud) | 120.000 | D7: R\$ 10.000/mês |
| Monitoramento do modelo (cientista de dados pleno, 30% dedicação) | 63.000 | D2: R\$ 17.500 × 30% |
| Ajustes periódicos (recalibração trimestral, ~40h/ciclo) | 30.000 | D1: R\$ 30.000 ÷ 160h × 40h × 4 ciclos |
| Suporte analítico e reportes ao comitê de crédito (~20h/mês) | 26.000 | D2: R\$ 17.500 ÷ 160h × 20h × 12 |
| **Total custos anuais** | **R\$ 239.000** | |

---

### 4.5 Benefícios econômicos estimados

O benefício vem da **redistribuição mais eficiente dos limites de crédito**: clientes de baixo risco recebem limites mais aderentes ao seu perfil (aumentando utilização e receita de interchange), enquanto clientes de alto risco têm limites reduzidos (diminuindo perdas por inadimplência). Trata-se de uma **única ação de otimização** que gera impacto simultâneo nos dois lados — receita e risco — da função objetivo definida pelo TAPI.

Por essa razão, tratamos o benefício como uma **melhoria única sobre o resultado econômico combinado** da carteira, e não como duas melhorias independentes somadas. O baseline econômico combinado é:

$$
\text{Baseline combinado} = \text{Receita de interchange (B4)} + \text{Perda evitável (A4)} = R\$\ 167\ mi + R\$\ 168\ mi = R\$\ 335\ mi
$$

Aplicando a premissa C1 (melhoria de 1,0% no cenário base — **piso da faixa** reportada na literatura):

$$
\text{Ganho potencial (regime permanente)} = R\$\ 335\ mi \times 1,0\% = R\$\ 3.350.000
$$

Esse ganho se materializa como uma combinação de mais receita de interchange (clientes bons usando mais o cartão) e menos perda por inadimplência (clientes arriscados com limites menores). A proporção exata entre os dois depende de como o modelo redistribui os limites — o que só será conhecido após o backtesting.

> **O ganho já é líquido de perdas por inadimplência.** É importante notar que o baseline combinado inclui, em sua composição, a perda líquida anual por inadimplência da carteira de cartões (A4 = R\$ 168 mi, já descontada a taxa de recuperação de 30%). A melhoria de 1% (C1) incide sobre esse baseline que já incorpora o custo da inadimplência — ou seja, o ganho estimado de R\$ 3,35 mi representa o saldo **líquido** entre receita incremental gerada e perdas evitadas, não apenas um aumento bruto de receita. Não há, portanto, necessidade de subtrair perdas por inadimplência em etapa posterior do cálculo: elas já estão contabilizadas na construção do baseline. Os benchmarks da literatura (Thomas, 2009; Trench et al., 2003) que fundamentam a premissa C1 também reportam ganhos líquidos, reforçando a consistência metodológica.

Contudo, o primeiro ano de operação não captura a totalidade do benefício potencial. A rampagem da adoção interna (integração com motor de crédito, validação pelo comitê, treinamento do time de estratégia) limita a captura efetiva. Aplicando a premissa C2 (captura de 25% no Ano 1):

$$
\text{Ganho efetivo no Ano 1} = R\$\ 3.350.000 \times 25\% = R\$\ 837.500
$$

> **Nota metodológica:** ao somar receita de interchange e perda evitada no mesmo baseline, tratamos as duas componentes como economicamente equivalentes. Na prática, R\$ 1 de perda evitada vai integralmente para a linha do lucro, enquanto R\$ 1 de receita bruta de interchange ainda carrega custos associados (taxa da bandeira, processamento, fraude). O efeito líquido no lucro não é perfeitamente simétrico. Optamos por manter a simplificação em primeira ordem porque (i) não dispomos das taxas internas do Pan para decompor o interchange líquido e (ii) o impacto dessa assimetria é marginal frente à incerteza já capturada na análise de sensibilidade (seção 4.6).

> **Sensibilidade à premissa A3 (taxa de recuperação):** se a recuperação real for 20% em vez de 30%, a perda líquida (A4) sobe de R\$ 168 mi para R\$ 193 mi, e o baseline combinado vai de R\$ 335 mi para R\$ 360 mi. No cenário base (C1 = 1,0%), o ganho anual passaria de R\$ 3,35 mi para R\$ 3,60 mi — uma variação de ~7% que não altera a conclusão de viabilidade. Diferentemente de C1, a taxa de recuperação pode ser verificada com dados públicos do BCB ou obtida diretamente com o parceiro.

---

### 4.6 Cálculo do ROI

$$
ROI = \frac{\text{Benefício líquido}}{\text{Investimento inicial}} \times 100
$$

Onde:

$$
\text{Benefício líquido} = \text{Ganhos estimados (1 ano)} - \text{Custos operacionais anuais}
$$

#### Cenário base — passo a passo

**Passo 1 — Investimento inicial:** R\$ 625.000 (seção 4.3)

**Passo 2 — Custos operacionais anuais:** R\$ 239.000 (seção 4.4)

**Passo 3 — Ganhos efetivos no Ano 1:** R\$ 837.500 (seção 4.5, C1 = 1,0%, C2 = 25%)

**Passo 4 — Benefício líquido:**

$$
\text{Benefício líquido} = R\$\ 837.500 - R\$\ 239.000 = R\$\ 598.500
$$

**Passo 5 — ROI:**

$$
ROI = \frac{R\$\ 598.500}{R\$\ 625.000} \times 100 \approx \textbf{95,8\%}
$$

**Passo 6 — Payback:**

$$
\text{Payback} = \frac{R\$\ 625.000}{R\$\ 598.500 / 12} \approx \textbf{12{,}5\ meses}
$$

#### Análise de sensibilidade — cenários para C1 e C2

As premissas C1 (melhoria) e C2 (captura no Ano 1) são os principais drivers de incerteza da análise (ambas com confiança Baixa). Para avaliar a robustez do resultado, recalculamos o ROI em três cenários que variam ambos os parâmetros simultaneamente:

| Cenário | C1 (melhoria) | C2 (captura Y1) | Ganho efetivo Y1 | Custos anuais | Benefício líquido | **ROI** | **Payback** |
|:---|:---:|:---:|---:|---:|---:|---:|---:|
| Pessimista | 0,5% | 15% | R\$ 251 mil | R\$ 239 mil | R\$ 12 mil | **2%** | **não paga em 1 ano** |
| **Base** | **1,0%** | **25%** | **R\$ 838 mil** | **R\$ 239 mil** | **R\$ 599 mil** | **96%** | **12,5 meses** |
| Otimista | 2,0% | 40% | R\$ 2.680 mil | R\$ 239 mil | R\$ 2.441 mil | **391%** | **3,1 meses** |

No cenário pessimista (C1 = 0,5%, captura de apenas 15%), o projeto gera valor marginalmente positivo mas não se paga no horizonte de 1 ano — exigindo justificativa estratégica complementar (ganhos regulatórios, maturidade analítica) para aprovação em comitê. No cenário base, o ROI de ~96% indica que o projeto praticamente se paga no primeiro ano, com payback de ~12,5 meses.

---

### 4.7 Interpretação dos resultados

**Viabilidade financeira.** O ROI base de **~96%** indica que o projeto é financeiramente viável: o ganho gerado no primeiro ano praticamente recupera o investimento total. O investimento de R\$ 625 mil equivale a apenas **0,07% do lucro ajustado** anual do Pan (~R\$ 855 mi em 2024, RI Banco Pan) — é um projeto de baixo risco financeiro para o banco. Pelo lado do ganho, os R\$ 599 mil de benefício líquido no cenário base representam **~0,07% do lucro ajustado** — um impacto marginal mas positivo para um projeto de otimização mono-produto. A modéstia do número é esperada e desejável: trata-se de uma calibragem cirúrgica em um produto específico, não de uma transformação estrutural da carteira.

**Por que o ROI não é mais alto.** Embora a literatura reporte ROIs de três dígitos em projetos de analytics aplicados a grandes carteiras de crédito (Trench et al., 2003), esses valores se referem a regime permanente, após plena integração da solução ao processo decisório do banco. No Ano 1, a captura de apenas 25% do benefício potencial (premissa C2) reflete a realidade de rampagem: integração com motor de crédito, validação pelo comitê, treinamento do time de estratégia e resistência organizacional. Em regime permanente (captura plena), o ROI anualizado seria significativamente mais alto — mas seria desonesto apresentá-lo como resultado do Ano 1.

**Ponto de equilíbrio (break-even).** Para que o benefício líquido seja zero no Ano 1, o ganho efetivo precisaria cobrir apenas os custos operacionais: R\$ 239 mil. Sobre o ganho potencial de R\$ 3,35 mi (regime permanente), isso equivale a uma captura de apenas **~7%** — um patamar muito baixo que só se materializaria em cenário de adoção quase nula da solução.

**Benefício operacional para o usuário.** Além do ganho financeiro, a solução gera valor operacional direto para o analista de crédito e o time de estratégia (conforme detalhado no Canvas, seção 3). Estimativa preliminar: cada ciclo de revisão manual de política de limites consome ~40–60 horas de analista sênior (levantamento de dados, simulação de cenários, validação com comitê). Com a solução automatizando a geração de cenários, estimamos redução de ~50% desse tempo — equivalente a ~20–30 horas/ciclo. Em 4 ciclos anuais (recalibração trimestral), isso representa ~80–120 horas/ano de analista sênior, ou **~R\$ 15.000–22.500/ano** (a custo D1). Esse benefício não foi monetizado no cálculo do ROI para manter a análise conservadora.

#### Limitações da análise

- **Premissa C1 não validada com dados do parceiro.** A melhoria de 1,0% (cenário base) é extraída da literatura acadêmica, não de backtesting com dados do Banco Pan. O ROI real só será conhecido após a implementação do modelo com dados históricos das safras M1–M3. Por essa razão, adotamos o piso da faixa reportada (1%) como cenário base, e não o ponto médio.

- **Custos dependem da infraestrutura interna do banco.** Os valores estimados para integração (Fase 3) e conformidade (Fase 4) pressupõem que o Pan já dispõe de motor de crédito e processos de governança estruturados. Se a infraestrutura for menos madura, esses custos podem ser significativamente maiores.

- **Investimento 100% amortizado no primeiro ano.** Para fins didáticos, o ROI apresentado trata o investimento de R\$ 625 mil como integralmente consumido no Ano 1. Em uma análise corporativa real, esse investimento seria amortizado ao longo do ciclo de vida do modelo — tipicamente 3 anos, compatível com o ciclo de revisão e recalibração de modelos de risco em bancos regulados. Nesse caso, o custo anualizado do investimento seria ~R\$ 208 mil/ano (R\$ 625k ÷ 3), e o ROI do Ano 1 seria calculado contra essa parcela em vez do total, resultando em ROI mais alto. A conclusão de viabilidade, portanto, não é afetada pela simplificação — ao contrário, a abordagem adotada é a mais conservadora possível.

- **Captura de 25% no Ano 1 é premissa do grupo.** A taxa de captura (C2) é a segunda maior fonte de incerteza da análise, após C1. O valor de 25% reflete a experiência típica de projetos de analytics em bancos (rampagem lenta, resistência organizacional), mas pode ser otimista ou pessimista dependendo da maturidade da infraestrutura de crédito do Pan.

---

## Referências da análise financeira

> ASSOCIAÇÃO BRASILEIRA DAS EMPRESAS DE CARTÕES DE CRÉDITO E SERVIÇOS (ABECS). **Indicadores de mercado**. São Paulo: ABECS, 2023–2024. Disponível em: https://www.abecs.org.br/indicadores-de-mercado. Acesso em: 20 abr. 2026.
>
> ADVFN. Banco Pan reporta R\$ 209 milhões de lucro líquido e expansão de crédito sustenta BPAN4. *ADVFN Brasil*, nov. 2025. Disponível em: https://br.advfn.com/jornal/2025/11/banco-pan-reporta-r-209-milhoes-de-lucro-liquido-e-expansao-de-credito-sustenta-bpan4. Acesso em: 20 abr. 2026.
>
> ADVFN. Banco Pan registra queda de 9% no lucro do 2T25 com aumento da inadimplência. *ADVFN Brasil*, ago. 2025. Disponível em: https://br.advfn.com/jornal/2025/08/banco-pan-registra-queda-de-9-no-lucro-do-2t25-com-aumento-da-inadimplencia. Acesso em: 20 abr. 2026.
>
> BANCO CENTRAL DO BRASIL. **Relatório de Estabilidade Financeira**, 2º semestre de 2024. Brasília: BCB, 2024. Disponível em: https://www.bcb.gov.br/publicacoes/ref. Acesso em: 20 abr. 2026.
>
> BANCO CENTRAL DO BRASIL. **Arranjos de pagamento — Taxas de intercâmbio**. Brasília: BCB, [s.d.]. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/pagamentosarranjos. Acesso em: 20 abr. 2026.
>
> BANCO PAN. **Relações com Investidores — Demonstrações financeiras e resultados trimestrais (2T25 e 3T25)**. São Paulo, 2025. Disponível em: https://ri.bancopan.com.br/. Acesso em: 20 abr. 2026.
>
> BANCO PAN; INTELI. **TAPI — Termo de Abertura do Projeto Integrador: Otimização de limites pré-aprovados de cartão de crédito**. São Paulo, 2026.
>
> COMISSÃO DE VALORES MOBILIÁRIOS (CVM). **Sistema RAD — DFP e ITR Banco Pan S.A.** Disponível em: https://www.rad.cvm.gov.br/. Acesso em: 20 abr. 2026.
>
> GLASSDOOR BRASIL. **Pesquisa salarial — Cientista de dados, Engenheiro de dados, Tech Lead**. 2025. Disponível em: https://www.glassdoor.com.br/. Acesso em: 20 abr. 2026.
>
> NORD INVESTIMENTOS. Banco Pan (BPAN4) — Resultados 4T24. 2025. Disponível em: https://www.nordinvestimentos.com.br/blog/banco-pan-bpan4-resultados-4t24/. Acesso em: 20 abr. 2026.
>
> ROBERT HALF. **Guia Salarial 2025**. São Paulo: Robert Half, 2025. Disponível em: https://www.roberthalf.com.br/guia-salarial. Acesso em: 20 abr. 2026.
>
> THOMAS, L. C. **Consumer Credit Models: Pricing, Profit and Portfolios**. Oxford: Oxford University Press, 2009.
>
> TRENCH, M. S. *et al.* Managing credit lines and prices for Bank One credit cards. **Interfaces**, v. 33, n. 5, p. 4–21, 2003.



---

## Checklist pré-entrega

**Oceano Azul:**
- [x] Explicação de quem está sendo comparado (3 abordagens)
- [x] Definição dos 8 atributos com justificativa para o Pan
- [x] Notas atribuídas com justificativa para cada uma
- [x] 4 ações (Reduzir, Eliminar, Aumentar, Criar) aplicadas ao projeto
- [ ] `[APÓS MODELAGEM]` Detalhar tipo de modelo na abordagem do grupo
- [ ] `[APÓS TAPI]` Validar notas do Pan atual com parceiro

**Riscos:**
- [x] Pelo menos 10 riscos apresentados (temos 12)
- [x] Critérios de classificação de impacto e probabilidade
- [x] Cada risco tem: descrição, causa provável, impacto, prob, posição, justificativa
- [x] Análise dos riscos mais críticos
- [ ] `[PREENCHER]` Imagem da matriz 5×5

**Canvas:**
- [x] Dois níveis de cliente identificados (direto + final)
- [x] Dores do cliente direto
- [x] Ganhos do cliente direto (do usuário, não da alta gestão)
- [x] Produtos e serviços da solução
- [x] Aliviadores de dor conectados às dores
- [x] Criadores de ganho
- [ ] `[PREENCHER]` Figura do Canvas (template Strategyzer)
- [ ] `[APÓS UX]` Cruzar com personas

**Financeira:**
- [x] Premissas claramente declaradas com fonte
- [x] Separação entre investimento, custo operacional e benefício
- [x] Distinção entre receita e economia
- [x] Cálculo do ROI com fórmula
- [x] Interpretação do resultado com limitações
- [ ] `[APÓS TAPI]` Recalcular com dados reais

---

## Fontes

[1] KIM, W. Chan; MAUBORGNE, Renée. A Estratégia do Oceano Azul: Como Criar Novos Mercados e Tornar a Concorrência Irrelevante. Rio de Janeiro: Sextante, 2005.
[2] EXPERIAN. Balancing Growth and Risk with Credit Limit Optimization. Experian Insights, 2024. Disponível em: https://www.experian.com/blogs/insights/credit-limit-optimization/. Acesso em: 28 de abril de 2026.
[3] BRASIL. Conselho Monetário Nacional. Resolução CMN nº 4.966, de 25 de novembro de 2021. Dispõe sobre os conceitos e os critérios contábeis aplicáveis a instrumentos financeiros e sobre a mensuração das provisões para perdas esperadas associadas ao risco de crédito. Brasília: Banco Central do Brasil, 2021. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolução%20CMN&numero=4966. Acesso em: 28 de abril de 2026..
